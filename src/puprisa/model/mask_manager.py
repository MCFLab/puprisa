# puprisa/model/mask_manager.py
"""
Qt-free manager for analysis-mask layers across all stacks.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from puprisa.model.entities import MaskItem
from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.core.mask import gaussian_threshold_mask


@dataclass(frozen=True)
class MaskEvent:
    """Emitted whenever a mask is modified."""
    event: str                  # "added" / "removed" / "enabled_changed" /
                                # "label_changed" / "reversed" / "cleared" / "effective_changed"
    stack_id: str
    mask_id: str | None = None

class MaskManager:
    """Manage mask layers globally and keep each PPS.mask up to date."""

    def __init__(self, stack_manager: StackManager):
        self._stack_manager = stack_manager
        self._listeners: list[Callable[[MaskEvent], None]] = []
        self._items: list[MaskItem] = []
        self._id_counter = 0

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
    # Stack events
    # ------------------------------------------------------------------
    def handle_stack_event(self, event: StackEvent) -> None:
        if event.event == "removed":
            self.handle_stack_deleted(event.stack_id)
        elif event.event == "added":
            self.handle_stack_added(event.stack_id)

    def handle_stack_added(self, stack_id: str) -> None:
        """Handle the addition of a new stack."""
        # if the stack already has layers, don't add an initial layer
        if self._items_for_stack(stack_id):
            return
        pps = self._get_pps(stack_id)
        # if the stack has a non-trivial mask, add it as the initial layer
        if not np.all(pps.mask):
            self.add_mask(stack_id, pps.mask.copy(), label="Initial mask", enabled=True)

    def handle_stack_deleted(self, stack_id: str) -> int:
        """Remove all layers belonging to ``stack_id``. Returns count."""
        before = len(self._items)
        self._items = [item for item in self._items if item.stack_id != stack_id]
        removed = before - len(self._items)
        if removed:
            self._notify(MaskEvent(event="cleared", stack_id=stack_id))
            self._notify(MaskEvent(event="effective_changed", stack_id=stack_id))
        return removed

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------
    def add_mask(
        self,
        stack_id: str,
        mask: np.ndarray,
        label: str = "",
        enabled: bool = True,
        mask_id: str | None = None,
    ) -> str:
        """Add a keep-mask layer and refresh the effective mask."""
        pps = self._get_pps(stack_id)
        mask = self._validate_mask(mask, pps)

        if mask_id is None:
            mask_id = self._generate_mask_id()
        else:
            mask_id = str(mask_id)
            if self.get_mask(stack_id, mask_id) is not None:
                raise ValueError(f"Mask ID {mask_id!r} already exists")

        item = MaskItem(
            id=mask_id,
            stack_id=stack_id,
            label=str(label),
            mask=mask,
            enabled=bool(enabled),
        )
        self._items.append(item)
        self._sync_effective_mask(stack_id)

        self._notify(MaskEvent(event="added", stack_id=stack_id, mask_id=mask_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=mask_id))
        return mask_id

    def remove_mask(self, stack_id: str, mask_id: str) -> None:
        for i, item in enumerate(self._items_for_stack(stack_id)):
            if item.id == mask_id:
                del self._items[i]
                self._sync_effective_mask(stack_id)

                self._notify(MaskEvent(event="removed", stack_id=stack_id, mask_id=mask_id))
                self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=mask_id))
                return
        raise KeyError(f"No mask with id {mask_id!r}")

    def set_mask_enabled(self, stack_id: str, mask_id: str, enabled: bool) -> None:
        for item in self._items_for_stack(stack_id):
            if item.id == mask_id:
                if item.enabled != bool(enabled):
                    item.enabled = bool(enabled)
                    self._sync_effective_mask(stack_id)

                    self._notify(MaskEvent(event="enabled_changed", stack_id=stack_id, mask_id=mask_id))
                    self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=mask_id))
                return
        raise KeyError(f"No mask with id {mask_id!r}")

    def set_mask_label(self, stack_id: str, mask_id: str, label: str) -> None:
        for item in self._items_for_stack(stack_id):
            if item.id == mask_id:
                item.label = str(label)
                self._notify(MaskEvent(event="label_changed", stack_id=stack_id, mask_id=mask_id))
                return
        raise KeyError(f"No mask with id {mask_id!r}")

    def reverse_mask(self, stack_id: str, mask_id: str) -> None:
        for item in self._items_for_stack(stack_id):
            if item.id == mask_id:
                item.mask = ~item.mask
                self._sync_effective_mask(stack_id)

                self._notify(MaskEvent(event="reversed", stack_id=stack_id, mask_id=mask_id))
                self._notify(MaskEvent(event="effective_changed", stack_id=stack_id, mask_id=mask_id))
                return
        raise KeyError(f"No mask with id {mask_id!r}")

    def clear_all_masks(self, stack_id: str) -> None:
        if not self._items_for_stack(stack_id):
            return
        
        self._items = [item for item in self._items if item.stack_id != stack_id]
        self._sync_effective_mask(stack_id)

        self._notify(MaskEvent(event="cleared", stack_id=stack_id))
        self._notify(MaskEvent(event="effective_changed", stack_id=stack_id))

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------
    def get_all_masks(self, stack_id: str) -> list[MaskItem]:
        return [MaskItem(
            id=item.id,
            stack_id=item.stack_id,
            label=item.label,
            mask=item.mask.copy(),
            enabled=item.enabled,
        ) for item in self._items_for_stack(stack_id)]

    def get_mask(self, stack_id: str, mask_id: str) -> MaskItem | None:
        for item in self._items_for_stack(stack_id):
            if item.id == mask_id:
                return MaskItem(
                    id=item.id,
                    stack_id=item.stack_id,
                    label=item.label,
                    mask=item.mask.copy(),
                    enabled=item.enabled,
                )
        return None

    def get_effective_mask(self, stack_id: str) -> np.ndarray:
        return self._get_pps(stack_id).mask.copy()

    # ------------------------------------------------------------------
    # Mask math
    # ------------------------------------------------------------------
    def combine_masks(
        self,
        stack_id: str,
        first_mask_id: str,
        operation: str,
        second_mask_id: str | None = None,
        label: str | None = None,
    ) -> str:
        """Create a mask from boolean operations on stored keep-masks."""
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

        return self.add_mask(
            stack_id,
            result,
            label=label or default_label,
            enabled=True,
        )

    # ------------------------------------------------------------------
    # Threshold creation
    # ------------------------------------------------------------------
    def add_mask_from_threshold(
        self,
        stack_id: str,
        threshold: str | float = "Li",
        sigma: float = 5.0,
        mask_on: bool = False,
        label: str | None = None,
    ) -> str:
        """Create a keep-mask layer from intensity thresholding."""
        pps = self._get_pps(stack_id)
        projection = pps.project(mask_on=False)
        effective = np.asarray(pps.mask, dtype=bool) if mask_on else None
        keep_mask = gaussian_threshold_mask(
            projection,
            threshold=threshold,
            sigma=sigma,
            mask=effective,
        )
        default_label = label or f"Intensity threshold"
        return self.add_mask(stack_id, keep_mask, label=default_label, enabled=True)

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    def save_masks_to_json(self, stack_id: str, path: str | Path) -> None:
        items = self._items_for_stack(stack_id)
        if not items:
            raise ValueError("No mask layers to save")

        payload = {
            "masks": [
                item.to_serializable()
                for item in items
            ]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def load_masks_from_json(self, stack_id: str, path: str | Path) -> None:
        """Load layers from JSON and add them to ``stack_id``."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Mask file must contain a JSON object")
        items = data.get("masks", [])
        if not isinstance(items, list):
            raise ValueError("'masks' must be a list")

        for item in items:
            if not isinstance(item, dict) or "mask" not in item:
                raise ValueError("Every mask must contain 'mask'")
            keep_mask = np.asarray(item["mask"], dtype=bool)
            self.add_mask(
                stack_id,
                keep_mask,
                label=str(item.get("label", "")),
                enabled=bool(item.get("enabled", True)),
            )
        
    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_pps(self, stack_id: str):
        item = self._stack_manager.get_item_by_id(stack_id)
        if item is None:
            raise KeyError(f"Unknown stack_id: {stack_id!r}")
        return item.pps

    def _items_for_stack(self, stack_id: str) -> list[MaskItem]:
        return [item for item in self._items if item.stack_id == stack_id]

    def _validate_mask(self, mask: np.ndarray, pps) -> np.ndarray:
        mask = np.asarray(mask, dtype=bool)
        expected = tuple(pps.image_dimensions)
        if mask.shape != expected:
            raise ValueError(f"Mask shape {mask.shape} does not match image dimensions {expected}")
        return mask.copy()

    def _generate_mask_id(self) -> str:
        existing = {item.id for item in self._items}
        while True:
            self._id_counter += 1
            candidate = f"mask_{self._id_counter}"
            if candidate not in existing:
                return candidate

    def _sync_effective_mask(self, stack_id: str) -> None:
        """Set pps.mask to the AND of all enabled keep-mask layers."""
        pps = self._get_pps(stack_id)

        layers = self._items_for_stack(stack_id)
        if not layers:
            pps.mask = np.ones(pps.image_dimensions, dtype=bool)
            return

        keep = np.ones(pps.image_dimensions, dtype=bool)
        for item in layers:
            if item.enabled:
                keep &= item.mask
        pps.mask = keep