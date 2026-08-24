# puprisa/controllers/pps_curve_controller.py
"""Controller for ROI average curve computation, serialisation, and viewing.

This controller is responsible for computing average signal curves for
all visible ROIs, optionally normalising them, and providing methods for
exporting the data and displaying it in a standalone matplotlib figure.

It does **not** own or operate on the embedded ``plotCanvas``; that
responsibility remains with :class:`~puprisa.controllers.pps_plot_controller.PPSPlotController`.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

import numpy as np

from puprisa.controllers.pps_roi_controller import PPSRoiController
from puprisa.model.stack_manager import StackManager
from puprisa.utils.geometry_utils import shape_to_mask



class PPSCurveController:
    """Compute ROI average curves and provide analysis/output helpers.

    Parameters
    ----------
    stack_manager : StackManager
        Shared stack model used to access stack data.
    roi_controller : PPSRoiController
        Controller that owns the ROI list and geometry.
    """

    def __init__(
        self,
        stack_manager: StackManager,
        roi_controller: PPSRoiController,
    ):
        self.stack_manager = stack_manager
        self.roi_controller = roi_controller

        # If True, each curve is scaled so its maximum absolute value is 1.
        self.normalize_curves = False

        # Cache of the most recently computed curves.
        # Each entry is ``(x, y, label, color)``.
        self._last_curves: list[tuple[np.ndarray, np.ndarray, str, str]] = []

    # ------------------------------------------------------------------
    # Curve computation
    # ------------------------------------------------------------------
    def compute_curves(self) -> list[tuple[np.ndarray, np.ndarray, str, str]]:
        """Compute average signal curves for all visible ROIs.

        Returns
        -------
        list of tuple
            Each tuple contains ``(x, y, label, color)`` where:

            - ``x``     : 1D array of axis values (time delay or z).
            - ``y``     : 1D array of average signal, optionally normalised.
            - ``label`` : ROI display label.
            - ``color`` : ROI colour string.
        """
        stack_items = self.stack_manager.get_all_items()
        rois = self.roi_controller.get_visible_rois()

        stack_by_id = {item["id"]: item for item in stack_items if item["visible"]}

        curves: list[tuple[np.ndarray, np.ndarray, str, str]] = []

        for roi in rois:
            stack_item = stack_by_id.get(roi["stack_id"])
            if stack_item is None:
                continue

            pps = stack_item["pps"]
            h, w = pps.image_dimensions
            xx, yy = np.meshgrid(np.arange(w), np.arange(h))
            mask_2d = shape_to_mask(roi["shape"], roi["params"], xx, yy)
            if mask_2d is None:
                continue

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

        # Cache the computed curves for later export/view operations.
        self._last_curves = curves
        return curves

    # ------------------------------------------------------------------
    # Serialisation / Export
    # ------------------------------------------------------------------
    def to_serializable(self) -> dict:
        """Return the most recently computed curves in JSON-friendly form.

        Returns
        -------
        dict
            Dictionary with keys ``"normalized"`` (bool) and ``"curves"``
            (list of dicts, each containing ``"x"``, ``"y"``, ``"label"``,
            and ``"color"``).
        """
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
        """Export the most recently computed curves to a CSV file.

        If ``path`` is ``None``, a save-file dialog is presented to the
        user.  The CSV contains one pair of columns per curve (x and y).

        Parameters
        ----------
        path : str or Path, optional
            Destination path.  If omitted, the user is prompted.

        Returns
        -------
        bool
            ``True`` if the file was written successfully, else ``False``.
        """
        curves = self._last_curves
        if not curves:
            print("No curves to export.")
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

                # Build header: x_1, y_<label>, x_2, y_<label>, ...
                header: list[str] = []
                for i, (x, y, label, _) in enumerate(curves):
                    header.append(f"x_{i + 1}")
                    header.append(f"y_{label}")
                writer.writerow(header)

                max_len = max(len(x) for x, _, _, _ in curves)

                for row_idx in range(max_len):
                    row: list[object] = []
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
        """Open a standalone matplotlib window showing the current curves.

        The window is created with a professional style: grid, legend,
        proper font sizes, and a descriptive title.  It is independent
        of the embedded ``plotCanvas`` and may be freely resized or saved
        by the user.
        """
        curves = self._last_curves
        if not curves:
            return

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 6), layout="constrained")

        for x, y, label, color in curves:
            ax.plot(x, y, linewidth=2.0, label=label, color=color)

        axis_label = "Time delay (ps)"
        ax.set_xlabel(axis_label)
        if self.normalize_curves:
            ax.set_ylabel("Normalized signal", fontsize=10)
        else:
            ax.set_ylabel("Average signal (arb. u.)", fontsize=10)

        ax.set_title("ROI Average Curves")
        ax.grid(True, alpha=0.4)
        ax.tick_params(labelsize=10)

        if curves:
            ax.legend(fontsize=10, loc="best", framealpha=0.9)

        fig.show()