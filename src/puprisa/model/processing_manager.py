# puprisa/model/processing_manager.py
"""Qt-free, stack-addressed coordinator for destructive PPS operations.

Every operation is resolved through ``StackManager`` at call time.  There is
therefore no cached PPS reference that can become stale after the user changes
the active stack.
"""
from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np

from puprisa.core.pps import PPS
from puprisa.core.process import subtract_background
from puprisa.model.entities import StackItem
from puprisa.model.stack_manager import StackManager


@dataclass(frozen=True)
class ProcessingEvent:
    """Emitted whenever processing is applied to a stack."""
    event: str                            # "data_changed" / "stack_created"
    stack_id: str


class ProcessingManager:
    """Apply processing to a selected or explicitly addressed stack."""

    def __init__(self, stack_manager: StackManager):
        self._stack_manager = stack_manager
        self._listeners: list[Callable[[ProcessingEvent], None]] = []

    # ------------------------------------------------------------------
    # Listener management
    # ------------------------------------------------------------------

    def add_listener(self, callback: Callable[[ProcessingEvent], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[ProcessingEvent], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, event: ProcessingEvent) -> None:
        for cb in list(self._listeners):
            cb(event)

    # ------------------------------------------------------------------
    # Stack context helpers
    # ------------------------------------------------------------------

    def _get_stack_item(self, stack_id: str) -> StackItem:
        stack_item = self._stack_manager.get_item_by_id(stack_id)
        if stack_item is None:
            raise KeyError(f"Unknown stack_id: {stack_id!r}")
        return stack_item
    
    # ------------------------------------------------------------------
    # Background subtraction
    # ------------------------------------------------------------------
    def apply_background_subtraction(self, stack_id: str, indices: Iterable[int], pixelwise: bool = True) -> str:
        stack_item = self._get_stack_item(stack_id)
        selected = self._validate_indices(indices, stack_item.pps.images.shape[0])
        stack_item.pps.apply_background_subtraction(selected, pixelwise=bool(pixelwise))
        stack_item.phasor_coords = None
        self._notify(ProcessingEvent(event="data_changed", stack_id=stack_item.id))
        return stack_item.id

    def apply_background_subtraction_negative_delays(self, stack_id: str, pixelwise: bool = True) -> str:
        stack_item = self._get_stack_item(stack_id)
        if stack_item.pps.axis_type != "time":
            raise ValueError("Negative-delay background subtraction requires a time-axis stack")
        indices = np.flatnonzero(stack_item.pps.get_axis_values() < 0).tolist()
        if not indices:
            raise ValueError("The selected time-axis stack has no negative-delay frames")
        return self.apply_background_subtraction(stack_id=stack_item.id, indices=indices, pixelwise=pixelwise)

    def apply_background_subtraction_fixed_value(self, stack_id: str, value: float) -> str:
        value = float(value)
        if not np.isfinite(value):
            raise ValueError("Background value must be finite")
        stack_item = self._get_stack_item(stack_id)
        pps = stack_item.pps
        bg_map = np.full(pps.image_dimensions, value, dtype=np.float64)
        pps._background_map = bg_map
        pps.images = subtract_background(pps.images, bg_map)
        stack_item.phasor_coords = None
        self._notify(ProcessingEvent(event="data_changed", stack_id=stack_item.id))
        return stack_item.id

    def reset_background_subtraction(self, stack_id: str) -> str:
        stack_item = self._get_stack_item(stack_id)
        stack_item.pps.reset_background_subtraction()
        stack_item.phasor_coords = None
        self._notify(ProcessingEvent(event="data_changed", stack_id=stack_item.id))
        return stack_item.id

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def normalize(self, stack_id: str, norm: str = "minmax", mask_on: bool = True) -> str:
        stack_item = self._get_stack_item(stack_id)
        stack_item.pps.normalize(norm, mask_on=bool(mask_on))
        stack_item.phasor_coords = None
        self._notify(ProcessingEvent(event="data_changed", stack_id=stack_item.id))
        return stack_item.id

    # ------------------------------------------------------------------
    # SVD denoising
    # ------------------------------------------------------------------
    def svd_reconstruct(self, stack_id: str, n_components: int) -> str:
        stack_item = self._get_stack_item(stack_id)
        stack_item.pps.svd_reconstruct(n_components)
        stack_item.phasor_coords = None
        self._notify(ProcessingEvent(event="data_changed", stack_id=stack_item.id))
        return stack_item.id

    # ------------------------------------------------------------------
    # Downsampling (creates a new stack)
    # ------------------------------------------------------------------

    def downsample(self, stack_id: str, factor: int, name: str | None = None) -> str:
        """Create, register, and select a spatially downsampled derived stack."""
        if isinstance(factor, bool) or not isinstance(factor, (int, np.integer)) or factor <= 0:
            raise ValueError("factor must be a positive integer")
        stack_item = self._get_stack_item(stack_id)
        new_pps: PPS = stack_item.pps.downsample(int(factor))

        if name is None:
            new_name = f"{stack_item.name} (downsampled x{factor})"
        else:
            if not isinstance(name, str):
                raise TypeError("name must be a string")
            new_name = name.strip()
            if not new_name:
                raise ValueError("Derived stack name must not be empty")

        new_id = self._stack_manager.add_stack(new_pps, name=new_name)
        self._notify(ProcessingEvent(event="stack_created", stack_id=new_id))
        return new_id

    # ------------------------------------------------------------------
    # Math (creates a new stack)
    # ------------------------------------------------------------------
    def combine_stacks(
        self,
        first_stack_id: str,
        second_stack_id: str | None,
        operation: str,
        first_coefficient: float = 1.0,
        second_coefficient: float | None = 1.0,
        name: str | None = None,
    ) -> str:
        """Create a stack from a linear combination or scalar multiplication.

        ``multiply`` means ``first_coefficient * first`` only.  The other
        operations use ``first_coefficient * first operation
        second_coefficient * second``.  The two input stacks for those
        operations must have identical image shapes and compatible axes.
        Masks, background-subtraction state, and analysis results are not
        transferred, because there is no unambiguous way to combine them.
        """
        first = self._get_stack_item(first_stack_id)
        first_coefficient = float(first_coefficient)
        
        if operation == "multiply":
            new_pps = first.pps * first_coefficient
            generated_name = f"{first_coefficient:.2f} x {first.name}"
        else:
            if second_stack_id is None:
                raise ValueError("Select Stack 2")
            second = self._get_stack_item(second_stack_id)
            second_coefficient = float(second_coefficient)
            operations = {
                "add": ("+", lambda left, right: left + right),
                "subtract": ("-", lambda left, right: left - right),
                "divide": ("/", lambda left, right: left / right),
            }
            try:
                symbol, combine = operations[operation]
            except KeyError as exc:
                raise ValueError(f"Unsupported stack operation: {operation!r}") from exc
            new_pps = combine(first.pps * first_coefficient, second.pps * second_coefficient)
            generated_name = (
                f"{first_coefficient:.2f} x {first.name} {symbol} "
                f"{second_coefficient:.2f} x {second.name}"
            )

        if name is None:
            new_name = generated_name
        else:
            new_name = name.strip()
            if not new_name:
                raise ValueError("Derived stack name must not be empty")

        new_id = self._stack_manager.add_stack(new_pps, name=new_name)
        self._notify(ProcessingEvent(event="stack_created", stack_id=new_id))
        return new_id

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_indices(self, indices: Iterable[int], frame_count: int) -> list[int]:
        values = list(indices)
        if not values:
            raise ValueError("Select at least one background frame")
        if any(isinstance(i, bool) or not isinstance(i, (int, np.integer)) for i in values):
            raise TypeError("Background frame indices must be integers")
        if any(i < 0 or i >= frame_count for i in values):
            raise IndexError(f"Background frame indices must be in [0, {frame_count - 1}]")
        return [int(i) for i in values]