# puprisa/core/mask.py
import numpy as np

class PPSMaskManager:
    """Manage analysis masks as ordered, toggleable exclude layers.

    Parameters
    ----------
    image_dimensions : tuple[int, int]
        (height, width) of the images these masks apply to.
    """

    def __init__(self, image_dimensions: tuple[int, int]):
        self.image_dimensions = tuple(int(v) for v in image_dimensions)
        self.masks: list[dict] = [] # Each dict has keys: "id", "label", "mask" (bool array), "enabled" (bool)
        self.effective_mask = np.ones(self.image_dimensions, dtype=bool)
        self._listeners: list = []  # List of functions to call when the effective mask changes

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
        """
        mask = self._validate_mask(mask)

        if mask_id is None:
            mask_id = self._generate_mask_id()
        else:
            mask_id = str(mask_id)
            if self._find_mask_index(mask_id) is not None:
                raise ValueError(f"Mask ID {mask_id!r} already exists")

        self.masks.append({
            "id": mask_id,
            "label": str(label),
            "mask": mask,
            "enabled": bool(enabled),
        })

        self._sync_effective_mask()
        return mask_id

    def remove_mask(self, mask_id: str) -> bool:
        """Remove a mask by ID. Returns True if removed."""
        idx = self._find_mask_index(mask_id)
        if idx is None:
            return False
        del self.masks[idx]
        self._sync_effective_mask()
        return True

    def clear_all_masks(self) -> None:
        """Remove every mask. The effective mask returns to all-True."""
        if not self.masks:
            return
        self.masks.clear()
        self._sync_effective_mask()

    def set_mask_enabled(self, mask_id: str, enabled: bool) -> None:
        """Enable or disable a mask."""
        mask_entry = self._get_mask_or_raise(mask_id)
        mask_entry["enabled"] = bool(enabled)
        self._sync_effective_mask()

    def set_mask_label(self, mask_id: str, label: str) -> None:
        """Set the label of an existing mask."""
        mask_entry = self._get_mask_or_raise(mask_id)
        mask_entry["label"] = str(label)
        self._notify()

    def reverse_mask(self, mask_id: str) -> bool:
        """Reverse the boolean values of a mask. Returns True if successful."""
        mask_entry = self._get_mask(mask_id)
        if mask_entry is None:
            return False
        mask_entry["mask"] = ~mask_entry["mask"]
        self._sync_effective_mask()
        return True

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------
    def get_mask(self, mask_id: str) -> dict | None:
        """Return a copy of the mask entry, or None if not found."""
        mask_entry = self._get_mask(mask_id)
        return dict(mask_entry) if mask_entry is not None else None

    def get_all_mask_ids(self) -> list[str]:
        """Return list of all mask IDs, in insertion order."""
        return [m["id"] for m in self.masks]

    def get_all_masks(self) -> list[dict]:
        """Return a shallow-copy list of all mask entries."""
        return [dict(m) for m in self.masks]

    def get_effective_mask(self) -> np.ndarray:
        """Return a copy of the current effective mask."""
        return self.effective_mask.copy()

    def is_empty(self) -> bool:
        """True if no pixel is currently included."""
        return not bool(np.any(self.effective_mask))

    # ------------------------------------------------------------------
    # Change notification (callbacks only, Qt-free)
    # ------------------------------------------------------------------
    def add_change_listener(self, callback) -> None:
        """Register a zero-argument callback fired after mask changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_change_listener(self, callback) -> None:
        try:
            self._listeners.remove(callback)
        except ValueError:
            pass

    def _notify(self) -> None:
        for cb in self._listeners:
            cb()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_serializable(self) -> dict:
        """Return JSON-friendly state for the current format only."""
        return {
            "masks": [
                {
                    "id": m["id"],
                    "label": m["label"],
                    "mask": m["mask"].tolist(),
                    "enabled": m["enabled"],
                }
                for m in self.masks
            ],
        }
    def from_serializable(self, data: dict) -> None:
        """
        Restore state from a JSON-friendly dict. Raises ValueError if invalid.
        """
        # Clear current masks without notifying listeners individually.
        self.masks = []
        self.effective_mask = np.ones(self.image_dimensions, dtype=bool)
        for item in data.get("masks", []):
            mask = self._validate_mask(item["mask"])
            self.masks.append({
                "id": str(item["id"]),
                "label": str(item.get("label", "")),
                "mask": mask,
                "enabled": bool(item.get("enabled", True)),
            })
        self._sync_effective_mask()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _sync_effective_mask(self) -> None:
        """Recompute the effective mask from enabled exclude masks."""
        out = np.ones(self.image_dimensions, dtype=bool)
        for mask_entry in self.masks:
            if mask_entry.get("enabled", True):
                out &= ~mask_entry["mask"]
        self.effective_mask = out
        self._notify()

    def _validate_mask(self, mask: np.ndarray) -> np.ndarray:
        mask = np.asarray(mask, dtype=bool)
        if mask.shape != self.image_dimensions:
            raise ValueError(
                f"Mask shape {mask.shape} does not match image dimensions {self.image_dimensions}"
            )
        return mask

    def _find_mask_index(self, mask_id: str) -> int | None:
        for i, mask in enumerate(self.masks):
            if mask["id"] == mask_id:
                return i
        return None

    def _get_mask(self, mask_id: str) -> dict | None:
        idx = self._find_mask_index(mask_id)
        return self.masks[idx] if idx is not None else None

    def _get_mask_or_raise(self, mask_id: str) -> dict:
        mask_entry = self._get_mask(mask_id)
        if mask_entry is None:
            raise KeyError(f"No mask with id {mask_id!r}")
        return mask_entry

    def _generate_mask_id(self) -> str:
        existing = {m["id"] for m in self.masks}
        n = 1
        while f"mask_{n}" in existing:
            n += 1
        return f"mask_{n}"