# puprisa/model/curve_manager.py
"""Qt-free manager for ROI average curve computation."""
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from puprisa.model.entities import CurveItem
from puprisa.model.roi_manager import RoiManager
from puprisa.model.stack_manager import StackManager


@dataclass(frozen=True)
class CurveEvent:
    """Emitted after curves are computed."""
    event: str                   # "computed"
    curve_count: int = 0


class CurveManager:
    """Compute average signal curves for visible ROIs.

    The manager is stateless with respect to view options; ``space`` and
    ``normalize`` are passed explicitly so that each window can maintain
    its own presentation settings.
    """

    def __init__(self, stack_manager: StackManager, roi_manager: RoiManager):
        self._stack_manager = stack_manager
        self._roi_manager = roi_manager
        self._listeners: list[Callable[[CurveEvent], None]] = []

    # ------------------------------------------------------------------
    # Listener management
    # ------------------------------------------------------------------
    def add_listener(self, callback: Callable[[CurveEvent], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[CurveEvent], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, event: CurveEvent) -> None:
        for cb in list(self._listeners):
            cb(event)

    # ------------------------------------------------------------------
    # Computation
    # ------------------------------------------------------------------
    def compute_curves(self, space: str | None = None, normalize: bool = False) -> list[CurveItem]:
        """Compute curves for analysis-visible ROIs.

        Parameters
        ----------
        space : str or None
            If given, only ROIs of this space are considered.
        normalize : bool
            If True, each curve is scaled so its maximum absolute value is 1.
        """
        roi_items = self._roi_manager.get_analysis_visible_rois()
        if space is not None:
            roi_items = [r for r in roi_items if r.space == space]

        results: list[CurveItem] = []

        for roi in roi_items:
            stack_item = self._stack_manager.get_item_by_id(roi.stack_id)
            if stack_item is None:
                continue

            keep_mask = self._roi_manager.build_roi_mask(roi)
            if keep_mask is None:
                continue

            pps = stack_item.pps
            combined = keep_mask & pps.mask
            if not np.any(combined):
                continue

            signal = np.array([np.nanmean(img[combined]) for img in pps.images])
            x = pps.get_axis_values()

            if normalize:
                max_abs = float(np.max(np.abs(signal)))
                if max_abs > 1e-12:
                    signal = signal / max_abs

            results.append(CurveItem(stack_id=stack_item.id, roi_id=roi.id, x=x, y=signal, label=roi.label, color=roi.color))

        self._notify(CurveEvent(event="computed", curve_count=len(results)))
        return results

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------
    def export_to_csv(self, path: str | Path, results: list[CurveItem]) -> None:
        """Write curves to CSV. Raises ValueError if no data, OSError on write failure."""
        if not results:
            raise ValueError("No curve data available")

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            header = []
            for i, curve in enumerate(results):
                header.append(f"x_{i + 1}")
                header.append(f"y_{curve.label}")
            writer.writerow(header)

            max_len = max(len(curve.x) for curve in results)
            for row_idx in range(max_len):
                row = []
                for curve in results:
                    if row_idx < len(curve.x):
                        row.append(curve.x[row_idx])
                        row.append(curve.y[row_idx])
                    else:
                        row.append("")
                        row.append("")
                writer.writerow(row)