# puprisa/model/mask_manager.py
"""Qt-free facade for exclude masks across all stacks."""
from dataclasses import dataclass
from typing import Callable
from pathlib import Path
import numpy as np

from puprisa.model.stack_manager import StackManager
from puprisa.core.mask import MaskItem

@dataclass(frozen=True)
class MaskEvent:
    """Emitted whenever a mask is modified."""
    event: str                  # "added" / "removed" / "enabled_changed" /
                                # "label_changed" / "reversed" / "cleared" / "effective_changed"
    stack_id: str
    mask_id: str | None = None


class MaskManager:
    """Aggregate mask operations across all stacks.

    Each PPS owns its own PPSMask internally. This facade exposes
    stack-scoped operations with typed change events.
    """

    def __init__(self, stack_manager: StackManager):
        self._stack_manager = stack_manager
        self._listeners: list[Callable[[MaskEvent], None]] = []

    # ------------------------------------------------------------------
    # Listener management
    # ------------------------------------------------------------------
    def add_listener(self, callback: Callable[[MaskEvent], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[MaskEvent], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, event: MaskEvent) -> None:
        for cb in list(self._listeners):
            cb(event)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_pps(self, stack_id: str):
        item = self._stack_manager.get_item_by_id(stack_id)
        if item is None:
            raise KeyError(f"Unknown stack_id: {stack_id!r}")
        return item.pps

    # ------------------------------------------------------------------
    # CRUD (delegating to PPS / PPSMask)
    # ------------------------------------------------------------------
    def get_all_masks(self, stack_id: str) -> list[MaskItem]:
        return self._get_pps(stack_id).get_all_masks()

    def get_mask(self, stack_id: str, mask_id: str) -> MaskItem | None:
        return self._get_pps(stack_id).get_mask(mask_id)

    def get_effective_mask(self, stack_id: str) -> np.ndarray:
        return self._get_pps(stack_id).get_effective_mask()

    def add_mask(self, stack_id: str, mask: np.ndarray,
                 label: str = "", enabled: bool = True, mask_id: str | None = None) -> str:
        new_id = self._get_pps(stack_id).add_mask(
            mask, label=label, enabled=enabled, mask_id=mask_id
        )
        self._notify(MaskEvent(event="added", stack_id=stack_id, mask_id=new_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=new_id))
        return new_id

    def remove_mask(self, stack_id: str, mask_id: str) -> None:
        self._get_pps(stack_id).remove_mask(mask_id)
        self._notify(MaskEvent(event="removed", stack_id=stack_id, mask_id=mask_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=mask_id))

    def set_mask_enabled(self, stack_id: str, mask_id: str, enabled: bool) -> None:
        self._get_pps(stack_id).set_mask_enabled(mask_id, enabled)
        self._notify(MaskEvent(event="enabled_changed", stack_id=stack_id, mask_id=mask_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=mask_id))

    def set_mask_label(self, stack_id: str, mask_id: str, label: str) -> None:
        self._get_pps(stack_id).set_mask_label(mask_id, label)
        self._notify(MaskEvent(event="label_changed", stack_id=stack_id, mask_id=mask_id))

    def reverse_mask(self, stack_id: str, mask_id: str) -> None:
        self._get_pps(stack_id).reverse_mask(mask_id)
        self._notify(MaskEvent(event="reversed", stack_id=stack_id, mask_id=mask_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=mask_id))

    def clear_all_masks(self, stack_id: str) -> None:
        self._get_pps(stack_id).clear_all_masks()
        self._notify(MaskEvent(event="cleared", stack_id=stack_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id))


    # ------------------------------------------------------------------
    # Mask math
    # ------------------------------------------------------------------
    def combine_masks(self, stack_id: str, first_mask_id: str, operation: str, second_mask_id: str | None = None, label: str | None = None) -> str:
        """Create a mask from boolean operations on stored exclude masks.

        ``True`` values mark excluded pixels, so the requested boolean
        operation is applied directly to the two stored mask arrays.  ``NOT``
        is unary and therefore does not require ``second_mask_id``.
        """
        first = self.get_mask(stack_id, first_mask_id)
        if first is None:
            raise KeyError(f"Unknown mask_id: {first_mask_id!r}")

        first_mask = first.mask
        first_label = first.label or first_mask_id

        if operation == "not":
            result = ~first_mask
            default_label = f"NOT {first_label}"
        else:
            if second_mask_id is None:
                raise ValueError("Select Mask 2")
            second = self.get_mask(stack_id, second_mask_id)
            if second is None:
                raise KeyError(f"Unknown mask_id: {second_mask_id!r}")
            second_mask = second.mask
            second_label = second.label or second_mask_id
            operations = {
                "and": ("AND", np.logical_and),
                "or": ("OR", np.logical_or),
                "xor": ("XOR", np.logical_xor),
            }
            try:
                symbol, combine = operations[operation]
            except KeyError as exc:
                raise ValueError(f"Unsupported mask operation: {operation!r}") from exc
            result = combine(first_mask, second_mask)
            default_label = f"{first_label} {symbol} {second_label}"

        return self.add_mask(stack_id, result, label=default_label if label is None else label, enabled=True)

    # ------------------------------------------------------------------
    # Threshold creation
    # ------------------------------------------------------------------
    def add_mask_from_threshold(self, stack_id: str,
                            threshold: str | float = "Li",
                            sigma: float = 5.0,
                            mask_on: bool = False,
                            label: str | None = None) -> str:
        """Add an exclude mask from intensity thresholding."""
        pps = self._get_pps(stack_id)
        try:
            mask_id = pps.add_mask_from_threshold(threshold=threshold, sigma=sigma, mask_on=mask_on, label=label)
        except Exception as exc:
            raise ValueError(f"Could not create mask from threshold: {exc}") from exc
        self._notify(MaskEvent(event="added", stack_id=stack_id, mask_id=mask_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=mask_id))
        return mask_id

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    def save_masks_to_json(self, stack_id: str, path: str | Path) -> None:
        self._get_pps(stack_id).save_mask(path, format="json")

    def load_masks_from_json(self, stack_id: str, path: str | Path) -> None:
        try:
            self._get_pps(stack_id).load_mask(path, format="json")
        except (OSError, UnicodeDecodeError, ValueError, TypeError) as exc:
            raise ValueError(f"Could not import masks from {path!s}: {exc}") from exc

        self._notify(MaskEvent(event="added", stack_id=stack_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id))