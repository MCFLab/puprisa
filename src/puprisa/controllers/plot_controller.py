# puprisa/controllers/plot_controller.py
"""Controller for colormap and color-scale user actions.

Depends only on PlotManager (the Qt-free state holder) and UI dialogs,
never on ViewModel objects.
"""

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget

from puprisa.model.plot_manager import PlotManager
from puprisa.ui.dialogs.colorbar_custom_range import ColorbarCustomRangeDialog


class PlotController(QObject):
    def __init__(self, plot_manager: PlotManager, parent_widget: QWidget | None):
        super().__init__()
        self._plot_manager = plot_manager
        self._parent = parent_widget

    # ------------------------------------------------------------------
    # Menu actions
    # ------------------------------------------------------------------
    def set_std_dev(self) -> None:
        self._plot_manager.set_color_scale_mode(PlotManager.MODE_STD_DEV)

    def set_full_range(self) -> None:
        self._plot_manager.set_color_scale_mode(PlotManager.MODE_FULL_RANGE)

    def set_colormap(self, name: str) -> None:
        self._plot_manager.set_colormap(name)

    def show_custom_range_dialog(self) -> None:
        ref = self._plot_manager.get_reference_ranges()
        if ref["std_min"] is None:
            QMessageBox.information(self._parent, "Custom Range", "Please open a stack first.")
            return

        dialog = ColorbarCustomRangeDialog(self._parent)
        current_vmin, current_vmax = self._plot_manager.vmin, self._plot_manager.vmax
        if current_vmin is None:
            current_vmin = ref["std_min"]
            current_vmax = ref["std_max"]

        dialog.ui.minDoubleSpinBox.setValue(current_vmin)
        dialog.ui.maxDoubleSpinBox.setValue(current_vmax)
        dialog.ui.labelStdDev.setText(
            f"Std Dev Range: [{ref['std_min']:.3g}, {ref['std_max']:.3g}]"
        )
        dialog.ui.labelFullScale.setText(
            f"Full Scale Range: [{ref['full_min']:.3g}, {ref['full_max']:.3g}]"
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            vmin = dialog.ui.minDoubleSpinBox.value()
            vmax = dialog.ui.maxDoubleSpinBox.value()

            if vmin >= vmax:
                QMessageBox.warning(self._parent, "Custom Range",
                                    "Minimum must be less than maximum.")
                return

            try:
                self._plot_manager.set_custom_range(vmin, vmax)
            except ValueError as exc:
                QMessageBox.warning(self._parent, "Custom Range", str(exc))