# puprisa/controllers/curve_controller.py
"""Qt controller for curve-related user actions."""
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from puprisa.model.stack_manager import StackManager
from puprisa.ui.dialogs.spectrum import SpectrumDialog
from shiboken6 import isValid
import matplotlib.pyplot as plt

from puprisa.model.curve_manager import CurveManager
from puprisa.core.fit import fit_curve
from puprisa.model.entities import CurveItem
from puprisa.ui.dialogs.curve_fit import CurveFitDialog

class CurveController(QObject):
    """Handle export / standalone view for curve data.

    The controller is stateless with respect to view options; the window
    passes the current space and normalization flag when invoking actions.
    """

    def __init__(self, curve_manager: CurveManager, stack_manager: StackManager, parent_widget: QWidget | None):
        super().__init__()
        self._curve_manager = curve_manager
        self._stack_manager = stack_manager
        self._parent = parent_widget
        self._fit_dialog: CurveFitDialog | None = None
        self._spectrum_dialog: SpectrumDialog | None = None

    # ------------------------------------------------------------------
    # Export Curve
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

    # ------------------------------------------------------------------
    # View Curve
    # ------------------------------------------------------------------
    def view_standalone(self, space: str, normalize: bool) -> None:
        curves = self._curve_manager.compute_curves(space=space, normalize=normalize)
        if not curves:
            QMessageBox.warning(self._parent, "View Curves", "No curve data available.")
            return

        fig, ax = plt.subplots(figsize=(4, 3), layout="constrained")
        for curve in curves:
            ax.plot(curve.x, curve.y, linewidth=2.0, label=curve.label, color=curve.color)

        current_item = self._stack_manager.get_current_item()
        if current_item is not None:
            pps = current_item.pps
            ax.set_xlabel(f"{pps.get_axis_label()} ({pps.get_axis_unit()})", fontsize=10)
        else:
            ax.set_xlabel("Time delay (ps)", fontsize=10)

        ax.set_ylabel("Normalized signal (a.u.)" if normalize else "Average signal (a.u.)", fontsize=10)
        ax.set_title("ROI Average Curves", fontsize=10)
        ax.grid(True, alpha=0.4)
        ax.tick_params(labelsize=10)
        if curves:
            ax.legend(fontsize=8, loc="best", framealpha=0.9)

        fig.show()

    # ------------------------------------------------------------------
    # Curve Fitting
    # ------------------------------------------------------------------
    def open_fit_dialog(self, space: str, normalize: bool) -> None:
        curves = self._curve_manager.compute_curves(space=space, normalize=normalize)
        if not curves:
            QMessageBox.warning(self._parent, "Curve Fitting", "No visible ROIs available.")
            return
        if self._fit_dialog is not None and isValid(self._fit_dialog):
            self._fit_dialog.close()
        self._fit_dialog = None
        dialog = CurveFitDialog(self._parent)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        dialog.fitRequested.connect(lambda: self._handle_fitRequested(dialog, curves, space, normalize))
        dialog.show()
        self._fit_dialog = dialog

    def _handle_fitRequested(self, dialog: CurveFitDialog, curves: list[CurveItem], space: str, normalize: bool) -> None:
        options = dialog.get_fit_options()
        fig, ax = plt.subplots(figsize=(8, 6), layout="constrained")
        result_text_lines = []
        success_count = 0
        for curve in curves:
            result = fit_curve(curve.x, curve.y, options)
            if not result.success:
                result_text_lines.append(f"{curve.label}: FAILED ({result.message})")
                continue
            ax.plot(result.x, result.y, 'o', markersize=3,
                    label=f"{curve.label} (data)", color=curve.color)
            ax.plot(result.x_fit, result.y_fit, '-', linewidth=1.5,
                    label=f"{curve.label} (fit)", color=curve.color, alpha=0.85)
            param_str = ", ".join(
                f"{name}={value:.4f}±{result.perr.get(name, float('nan')):.4f}"
                for name, value in result.popt.items()
            )
            result_text_lines.append(f"{curve.label}: {param_str}")
            success_count += 1
        if success_count == 0:
            QMessageBox.critical(self._parent, "Curve Fitting", "All fits failed.")
            return
        ax.set_xlabel("Time delay (ps)")
        ax.set_ylabel("Normalized signal (a.u.)" if normalize else "Average signal (a.u.)")
        ax.set_title("Curve Fitting Results")
        ax.grid(True, alpha=0.4)
        ax.legend(fontsize=8, loc="best")
        fig.show()
        dialog.set_result_text("\n".join(result_text_lines))

    # ------------------------------------------------------------------
    # Curve Spectrum Analysis
    # ------------------------------------------------------------------
    def open_spectrum_dialog(self, space: str = "pixel") -> None:
        dialog = SpectrumDialog(
            self._curve_manager,
            self._stack_manager,
            parent=self._parent,
            space=space,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        dialog.show()
        self._spectrum_dialog = dialog