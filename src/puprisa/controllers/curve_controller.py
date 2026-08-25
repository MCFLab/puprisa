# puprisa/controllers/curve_controller.py
"""Qt controller for curve-related user actions."""
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

import matplotlib.pyplot as plt

from puprisa.model.curve_manager import CurveManager


class CurveController(QObject):
    """Handle export / standalone view for curve data.

    The controller is stateless with respect to view options; the window
    passes the current space and normalization flag when invoking actions.
    """

    def __init__(self, curve_manager: CurveManager, parent_widget: QWidget | None):
        super().__init__()
        self._curve_manager = curve_manager
        self._parent = parent_widget

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def export_curve_dialog(self, space: str, normalize: bool) -> bool:
        curves = self._curve_manager.compute_curves(space=space, normalize=normalize)
        if not curves:
            QMessageBox.warning(self._parent, "Export Curves", "No curve data available.")
            return False

        path, _ = QFileDialog.getSaveFileName(self._parent, "Export Curve Data", "curves.csv", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return False

        try:
            self._curve_manager.export_to_csv(path, curves)
            return True
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self._parent, "Export Curves", f"Export failed:\n{exc}")
            return False

    def view_standalone(self, space: str, normalize: bool) -> None:
        curves = self._curve_manager.compute_curves(space=space, normalize=normalize)
        if not curves:
            QMessageBox.warning(self._parent, "View Curves", "No curve data available.")
            return

        fig, ax = plt.subplots(figsize=(10, 6), dpi=120, layout="constrained")
        for curve in curves:
            ax.plot(curve.x, curve.y, linewidth=2.0, label=curve.label, color=curve.color)

        current_item = self._curve_manager._stack_manager.get_current_item()
        if current_item is not None:
            pps = current_item.pps
            ax.set_xlabel(f"{pps.get_axis_label()} ({pps.get_axis_unit()})", fontsize=12)
        else:
            ax.set_xlabel("Time delay (ps)", fontsize=12)

        ax.set_ylabel("Normalized signal (a.u.)" if normalize else "Average signal (a.u.)", fontsize=12)
        ax.set_title("ROI Average Curves", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.4)
        ax.tick_params(labelsize=10)
        if curves:
            ax.legend(fontsize=10, loc="best", framealpha=0.9)

        fig.show()