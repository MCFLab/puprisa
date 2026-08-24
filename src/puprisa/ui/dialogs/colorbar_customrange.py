# puprisa/ui/dialogs/colorbar_customrange_dialog.py
from PySide6.QtWidgets import QDialog, QMessageBox
from puprisa.ui.generated.dialog_colorbar_customrange import Ui_colorbarCustomRangeDialog


class ColorbarCustomRangeDialog(QDialog):
    """Dialog for entering a custom colorbar range with reference information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_colorbarCustomRangeDialog()
        self.ui.setupUi(self)

        self.ui.minDoubleSpinBox.setRange(-1e12, 1e12)
        self.ui.maxDoubleSpinBox.setRange(-1e12, 1e12)

    def set_reference_ranges(self, ref: dict):
        """Update the reference labels showing std-dev and full-scale ranges.

        :param ref: dict with keys 'std_min', 'std_max', 'full_min', 'full_max'.
                    Values may be None (e.g., no stack loaded).
        """
        std_min = ref.get("std_min")
        std_max = ref.get("std_max")
        if std_min is not None and std_max is not None:
            self.ui.labelStdDev.setText(
                f"Std Dev Range: {std_min:.3g} to {std_max:.3g}"
            )
        else:
            self.ui.labelStdDev.setText("Std Dev Range: N/A")

        full_min = ref.get("full_min")
        full_max = ref.get("full_max")
        if full_min is not None and full_max is not None:
            self.ui.labelFullScale.setText(
                f"Full Scale Range: {full_min:.3g} to {full_max:.3g}"
            )
        else:
            self.ui.labelFullScale.setText("Full Scale Range: N/A")

    def set_range(self, vmin: float, vmax: float):
        """Set the initial values of the min/max spinboxes."""
        self.ui.minDoubleSpinBox.setValue(vmin)
        self.ui.maxDoubleSpinBox.setValue(vmax)

    def get_range(self) -> tuple[float, float]:
        """Return the current (vmin, vmax) values from the spinboxes."""
        return self.ui.minDoubleSpinBox.value(), self.ui.maxDoubleSpinBox.value()

    def accept(self) -> None:
        """Validate input before accepting the dialog."""
        vmin, vmax = self.get_range()
        if vmin >= vmax:
            QMessageBox.warning(
                self,
                "Invalid Range",
                "Minimum must be less than maximum.",
            )
            return
        super().accept()