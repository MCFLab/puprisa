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
    graphics_item: Any = field(default=None, repr=False)


@dataclass
class CurveItem:
    """One computed ROI average curve."""
    stack_id: str
    roi_id: str
    x: np.ndarray
    y: np.ndarray
    label: str
    color: str