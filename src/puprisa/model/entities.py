# puprisa/model/entities.py
"""Standard dataclass entities shared by all model managers."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import numpy as np
from puprisa.core.pps import PPS

@dataclass
class StackItem:
    """A loaded pump-probe stack and its UI metadata."""
    id: str
    pps: PPS
    name: str
    visible: bool = True
    color: str = "#000000"
    phasor_coords: np.ndarray | None = field(default=None, repr=False)

    @classmethod
    def from_pps(cls, stack_id: str, pps: Any, name: str | None = None, color: str = "#000000") -> "StackItem":
        if name is None:
            name = Path(pps.filename).stem if pps.filename else "Untitled"
        return cls(id=stack_id, pps=pps, name=name, color=color)

@dataclass
class MaskItem:
    """A single mask layer applied to a stack.
    ``mask`` is a keep mask: ``True`` marks pixels to retain; ``False`` marks pixels to exclude.
    """
    id: str
    stack_id: str
    label: str
    mask: np.ndarray       # True = keep
    enabled: bool = True

    def copy(self) -> "MaskItem":
        return MaskItem(
            id=self.id,
            stack_id=self.stack_id,
            label=self.label,
            mask=self.mask.copy(),
            enabled=self.enabled,
        )

    def to_serializable(self) -> dict:
        """Convert this mask to a JSON-friendly dictionary.

        Runtime-only fields (`id`, `stack_id`) are intentionally omitted
        because they must be regenerated or rebound when the mask is imported
        into a new stack/session.
        """
        return {
            "label": self.label,
            "mask": self.mask.tolist(),
            "enabled": self.enabled,
        }
    
@dataclass
class RoiItem:
    """A single ROI defined in pixel or phasor space."""

    id: str
    stack_id: str
    space: str    # "pixel" / "phasor"
    shape: str    # "rectangle" / "circle" / "ellipse" / "polygon"
    params: dict  # e.g. {"x": 10, "y": 20, "width": 30, "height": 40}
    label: str
    color: str
    visible: bool = True

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_serializable(self) -> dict:
        """Convert this ROI to a JSON-friendly dictionary.

        Runtime-only fields (`id`, `stack_id`) are
        intentionally omitted because they must be regenerated or rebound
        when the ROI is imported into a new stack/session.
        """
        return {
            "space": self.space,
            "shape": self.shape,
            "params": self.params,
            "label": self.label,
            "color": self.color,
            "visible": self.visible,
        }

    @classmethod
    def from_serializable(
        cls,
        data: dict,
        roi_id: str,
        stack_id: str,
    ) -> "RoiItem":
        """Create a new ROI from serialized data.

        Parameters
        ----------
        data : dict
            Dictionary previously produced by :meth:`to_serializable`.
        roi_id : str
            New runtime ID assigned by the caller (usually RoiManager).
        stack_id : str
            Stack this ROI will belong to.

        Raises
        ------
        ValueError
            If required fields are missing or invalid.
        """
        if not isinstance(data, dict):
            raise ValueError("ROI data must be a dictionary")

        space = data.get("space")
        if space not in ("pixel", "phasor"):
            raise ValueError(f"Invalid or missing ROI space: {space!r}")

        shape = data.get("shape")
        if shape not in ("rectangle", "circle", "ellipse", "polygon"):
            raise ValueError(f"Invalid or missing ROI shape: {shape!r}")

        params = data.get("params", {})
        if not isinstance(params, dict):
            raise ValueError("ROI params must be a dictionary")

        return cls(
            id=roi_id,
            stack_id=stack_id,
            space=space,
            shape=shape,
            params=params,
            label=str(data.get("label", "")),
            color=str(data.get("color", "#000000")),
            visible=bool(data.get("visible", True)),
        )


@dataclass
class CurveItem:
    """One computed ROI average curve."""
    stack_id: str
    roi_id: str
    x: np.ndarray
    y: np.ndarray
    label: str
    color: str