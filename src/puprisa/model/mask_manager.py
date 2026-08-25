# puprisa/model/mask_manager.py
"""Qt-free facade for exclude masks across all stacks."""
from dataclasses import dataclass
from typing import Callable
from pathlib import Path
import numpy as np

from puprisa.model.stack_manager import StackManager


@dataclass(frozen=True)
class MaskEvent:
    """Emitted whenever a mask is modified."""
    event: str                   # "added" / "removed" / "enabled_changed" /
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
    def get_all_masks(self, stack_id: str) -> list[dict]:
        return self._get_pps(stack_id).get_all_masks()

    def get_mask(self, stack_id: str, mask_id: str) -> dict | None:
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
        pps = self._get_pps(stack_id)
        removed = pps.remove_mask(mask_id)
        if not removed:
            raise KeyError(f"Unknown mask_id: {mask_id!r}")
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
        pps = self._get_pps(stack_id)
        reversed_ = pps.reverse_mask(mask_id)
        if not reversed_:
            raise KeyError(f"Unknown mask_id: {mask_id!r}")
        self._notify(MaskEvent(event="reversed", stack_id=stack_id, mask_id=mask_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=mask_id))

    def clear_all_masks(self, stack_id: str) -> None:
        self._get_pps(stack_id).clear_all_masks()
        self._notify(MaskEvent(event="cleared", stack_id=stack_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id))

    # ------------------------------------------------------------------
    # Threshold creation
    # ------------------------------------------------------------------
    def create_threshold_mask(self, stack_id: str,
                              threshold: str | float = "Li",
                              sigma: float = 5.0,
                              mask_on: bool = True,
                              label: str | None = None) -> str:
        """Create an exclude mask from intensity thresholding."""
        from puprisa.core.process import gaussian_threshold_mask

        pps = self._get_pps(stack_id)
        projection = pps.project(mask_on=mask_on)
        effective = np.asarray(pps.mask, dtype=bool) if mask_on else None

        keep_mask = gaussian_threshold_mask(
            projection, threshold=threshold, sigma=sigma, mask=effective
        )
        label = label or f"Intensity threshold ({threshold})"
        return self.add_mask(stack_id, ~keep_mask, label=label, enabled=True)

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    def save_masks_to_json(self, stack_id: str, path: str | Path) -> None:
        self._get_pps(stack_id).save_mask(path, format="json")

    def load_masks_from_json(self, stack_id: str, path: str | Path) -> None:
        import json
        with open(path, "r") as f:
            data = json.load(f)
        self._get_pps(stack_id).get_mask_handler().from_serializable(data)
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id))