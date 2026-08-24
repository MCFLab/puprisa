"""Curve controller for the Phasor analysis window.

Computes average signal curves for phasor-space ROIs, supports optional
normalisation, and provides export / standalone viewing helpers.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import numpy as np

from puprisa.model.stack_manager import StackManager
from puprisa.utils.geometry_utils import shape_to_mask

if TYPE_CHECKING:
    from puprisa.controllers.phasor_roi_controller import PhasorRoiController


class PhasorCurveController:
    """Compute and manage ROI average curves for the Phasor window.

    Parameters
    ----------
    stack_manager : StackManager
        Shared stack model.
    roi_controller : PhasorRoiController
        Controller that owns the phasor-space ROI list.
    """

    def __init__(
        self,
        stack_manager: StackManager,
        roi_controller: PhasorRoiController,
    ):
        self.stack_manager = stack_manager
        self.roi_controller = roi_controller

        # If True, each curve is scaled so its maximum absolute value is 1.
        self.normalize_curves = False

        # Cache of the most recently computed curves.
        self._last_curves: list[tuple[np.ndarray, np.ndarray, str, str]] = []

    # ------------------------------------------------------------------
    # Curve computation
    # ------------------------------------------------------------------
    def compute_curves(self) -> list[tuple[np.ndarray, np.ndarray, str, str]]:
        """Compute average signal curves for all visible phasor ROIs.

        Returns
        -------
        list of tuple
            Each tuple is ``(x, y, label, color)`` where ``x`` is the axis
            values, ``y`` the average signal (optionally normalised),
            ``label`` the ROI label, and ``color`` the ROI colour.
        """
        stack_items = self.stack_manager.get_all_items()
        rois = self.roi_controller.get_visible_rois()

        # Only visible stacks are considered.
        stack_by_id = {item["id"]: item for item in stack_items if item["visible"]}

        curves: list[tuple[np.ndarray, np.ndarray, str, str]] = []

        for roi in rois:
            stack_item = stack_by_id.get(roi["stack_id"])
            if stack_item is None:
                continue

            pps = stack_item["pps"]
            coords = stack_item.get("phasor_coords")
            if coords is None:
                # The phasor coordinates are calculated in PhasorWindow.
                # If they are missing, skip the ROI.
                continue

            g = coords[:, 0]
            s = coords[:, 1]

            # Build a 1D mask from the ROI geometry in (g,s) space.
            mask_1d = shape_to_mask(roi["shape"], roi["params"], g, s)
            if mask_1d is None or not np.any(mask_1d):
                continue

            h, w = pps.image_dimensions
            mask_2d = mask_1d.reshape(h, w)
            combined = mask_2d & pps.mask
            if not np.any(combined):
                continue

            signal = np.array([np.mean(img[combined]) for img in pps.images])
            x = pps.get_axis_values()

            if self.normalize_curves:
                max_abs = float(np.max(np.abs(signal)))
                if max_abs > 1e-12:
                    signal = signal / max_abs

            curves.append((x, signal, roi["label"], roi["color"]))

        self._last_curves = curves
        return curves

    # ------------------------------------------------------------------
    # Serialisation / Export
    # ------------------------------------------------------------------
    def to_serializable(self) -> dict:
        """Return the last computed curves in JSON-friendly form."""
        return {
            "normalized": self.normalize_curves,
            "curves": [
                {
                    "x": np.asarray(x).tolist(),
                    "y": np.asarray(y).tolist(),
                    "label": label,
                    "color": color,
                }
                for x, y, label, color in self._last_curves
            ],
        }

    def export_to_csv(self, path: Optional[str | Path] = None) -> bool:
        """Export the most recently computed curves to a CSV file."""
        curves = self._last_curves
        if not curves:
            return False

        if path is None:
            from PySide6.QtWidgets import QFileDialog

            path, _ = QFileDialog.getSaveFileName(
                None,
                "Export Curve Data",
                "",
                "CSV Files (*.csv);;All Files (*)",
            )
            if not path:
                return False

        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                header = []
                for i, (x, y, label, _) in enumerate(curves):
                    header.append(f"x_{i + 1}")
                    header.append(f"y_{label}")
                writer.writerow(header)

                max_len = max(len(x) for x, _, _, _ in curves)
                for row_idx in range(max_len):
                    row = []
                    for x, y, _, _ in curves:
                        if row_idx < len(x):
                            row.append(x[row_idx])
                            row.append(y[row_idx])
                        else:
                            row.append("")
                            row.append("")
                    writer.writerow(row)

            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Standalone matplotlib window
    # ------------------------------------------------------------------
    def view_standalone(self) -> None:
        """Open a standalone matplotlib window showing the current curves."""
        curves = self._last_curves
        if not curves:
            return

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 6), layout="constrained")
        for x, y, label, color in curves:
            ax.plot(x, y, linewidth=2.0, label=label, color=color)

        ax.set_xlabel("Time delay (ps)", fontsize=10)
        ylabel = "Normalized signal" if self.normalize_curves else "Average signal (arb. u.)"
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title("ROI Average Curves", fontsize=10)
        ax.grid(True, alpha=0.4)
        ax.tick_params(labelsize=10)
        if curves:
            ax.legend(fontsize=10, loc="best", framealpha=0.9)

        fig.show()