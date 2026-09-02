# puprisa/core/mask.py
from dataclasses import dataclass

import numpy as np

@dataclass(slots=True)
class MaskItem:
    """A single exclude-mask layer owned by a PPSMask instance."""
    id: str
    label: str
    mask: np.ndarray
    enabled: bool = True

    def copy(self) -> "MaskItem":
        return MaskItem(
            id=self.id,
            label=self.label,
            mask=self.mask.copy(),
            enabled=self.enabled,
        )

class PPSMask:
    """Manage analysis masks as ordered, toggleable exclude layers.

    Parameters
    ----------
    image_dimensions : tuple[int, int]
        (height, width) of the images these masks apply to.
    """

    def __init__(self, image_dimensions: tuple[int, int]):
        self.image_dimensions = tuple(int(v) for v in image_dimensions)
        self.masks: list[MaskItem] = []
        self.effective_mask = np.ones(self.image_dimensions, dtype=bool)

    # ------------------------------------------------------------------
    # Mask management
    # ------------------------------------------------------------------
    def add_mask(
        self,
        mask: np.ndarray,
        label: str = "",
        enabled: bool = True,
        mask_id: str | None = None,
    ) -> str:
        """Add an exclude mask and return its ID.

        Parameters
        ----------
        mask : np.ndarray, shape matches ``image_dimensions``
            Boolean mask where ``True`` marks pixels to exclude.
        label : str, optional
            User-friendly label.
        enabled : bool, optional
            Whether this mask contributes to the effective mask.
        mask_id : str or None, optional
            Unique identifier. Auto-generated if None.
        
        Returns
        -------
        str
            The ID of the newly added mask.
        """
        mask = self._validate_mask(mask)

        if mask_id is None:
            mask_id = self._generate_mask_id()
        else:
            mask_id = str(mask_id)
            if self._find_mask_index(mask_id) is not None:
                raise ValueError(f"Mask ID {mask_id!r} already exists")

        self.masks.append(
            MaskItem(
                id=mask_id,
                label=str(label),
                mask=mask,
                enabled=bool(enabled)
            )
        )

        self._sync_effective_mask()
        return mask_id

    def remove_mask(self, mask_id: str) -> None:
        """Remove a mask by ID."""
        idx = self._find_mask_index(mask_id)
        if idx is None:
            raise KeyError(f"No mask with id {mask_id!r}")

        del self.masks[idx]
        self._sync_effective_mask()

    def clear_all_masks(self) -> None:
        """Remove every mask. The effective mask returns to all-True."""
        if not self.masks:
            return
        self.masks.clear()
        self._sync_effective_mask()

    def set_mask_enabled(self, mask_id: str, enabled: bool) -> None:
        """Enable or disable a mask."""
        mask_item = self._get_mask_item_or_raise(mask_id)
        mask_item.enabled = bool(enabled)
        self._sync_effective_mask()

    def set_mask_label(self, mask_id: str, label: str) -> None:
        """Set the label of an existing mask."""
        mask_item = self._get_mask_item_or_raise(mask_id)
        mask_item.label = str(label)

    def reverse_mask(self, mask_id: str) -> None:
        """Reverse a mask by ID."""
        mask_item = self._get_mask_item_or_raise(mask_id)
        mask_item.mask = ~mask_item.mask
        self._sync_effective_mask()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------
    def get_mask(self, mask_id: str) -> MaskItem | None:
        """Return an independent copy of one mask item."""
        mask_item = self._get_mask_item(mask_id)
        return mask_item.copy() if mask_item is not None else None
    
    def get_all_mask_ids(self) -> list[str]:
        """Return list of all mask IDs, in insertion order."""
        return [mask.id for mask in self.masks]

    def get_all_masks(self) -> list[MaskItem]:
        """Return a copy list of all mask items."""
        return [mask_item.copy() for mask_item in self.masks]

    def get_effective_mask(self) -> np.ndarray:
        """Return a copy of the current effective mask."""
        return self.effective_mask.copy()

    def is_empty(self) -> bool:
        """True if no pixel is currently included."""
        return not bool(np.any(self.effective_mask))

    def copy(self) -> "PPSMask":
        copied = PPSMask(self.image_dimensions)
        copied.masks = [mask_item.copy() for mask_item in self.masks]
        copied._sync_effective_mask()
        return copied

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_serializable(self) -> dict:
        """Return JSON-friendly state for the current format only."""
        return {
            "masks": [
                {
                    "id": mask.id,
                    "label": mask.label,
                    "mask": mask.mask.tolist(),
                    "enabled": mask.enabled,
                }
                for mask in self.masks
            ],
        }
    
    def from_serializable(self, data: dict) -> None:
        """Append masks from JSON-friendly data, assigning fresh mask IDs.

        The serialized IDs are intentionally ignored: imported layers receive
        new IDs that are unique within this ``PPSMask`` instance.  Validation
        is completed before any layer is appended, so a malformed import does
        not partially modify the current masks.
        """
        if not isinstance(data, dict):
            raise ValueError("Mask data must be a dictionary")
        items = data.get("masks", [])
        if not isinstance(items, list):
            raise ValueError("'masks' must be a list")

        restored: list[MaskItem] = []
        existing_ids = {mask_item.id for mask_item in self.masks}
        next_id = 1
        for item in items:
            if not isinstance(item, dict) or "mask" not in item:
                raise ValueError("Every mask must contain 'mask'")
            mask = self._validate_mask(item["mask"])

            while f"mask_{next_id}" in existing_ids:
                next_id += 1
            mask_id = f"mask_{next_id}"
            existing_ids.add(mask_id)
            next_id += 1

            restored.append(
                MaskItem(
                    id=mask_id,
                    label=str(item.get("label", "")),
                    mask=mask,
                    enabled=bool(item.get("enabled", True)),
                )
            )

        self.masks.extend(restored)
        self._sync_effective_mask()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _sync_effective_mask(self) -> None:
        """Recompute the effective mask from enabled exclude masks."""
        out = np.ones(self.image_dimensions, dtype=bool)
        for mask_item in self.masks:
            if mask_item.enabled:
                out &= ~mask_item.mask
        self.effective_mask = out

    def _validate_mask(self, mask: np.ndarray) -> np.ndarray:
        mask = np.array(mask, dtype=bool, copy=True)
        if mask.shape != self.image_dimensions:
            raise ValueError(
                f"Mask shape {mask.shape} does not match "
                f"image dimensions {self.image_dimensions}"
            )
        return mask

    def _find_mask_index(self, mask_id: str) -> int | None:
        for i, mask in enumerate(self.masks):
            if mask.id == mask_id:
                return i
        return None

    def _get_mask_item(self, mask_id: str) -> MaskItem | None:
        idx = self._find_mask_index(mask_id)
        return self.masks[idx] if idx is not None else None

    def _get_mask_item_or_raise(self, mask_id: str) -> MaskItem:
        mask_item = self._get_mask_item(mask_id)
        if mask_item is None:
            raise KeyError(f"No mask with id {mask_id!r}")
        return mask_item

    def _generate_mask_id(self) -> str:
        existing = {m.id for m in self.masks}
        n = 1
        while f"mask_{n}" in existing:
            n += 1
        return f"mask_{n}"
