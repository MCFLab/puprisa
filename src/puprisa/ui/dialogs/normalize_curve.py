"""Dialog wrapper for selecting the curve normalization option."""

from PySide6.QtWidgets import QDialog, QWidget
from puprisa.ui.generated.dialog_normalize_option import Ui_NormalizeOptionDialog
from puprisa.utils.color_utils import format_decimal

class NormalizeOptionDialog(QDialog):
    """Select maximum or slice-based curve normalization."""

    def __init__(
        self,
        axis_values: list[float],
        axis_unit: str,
        axis_symbol: str,
        normalize_option: str | int = "max",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.ui = Ui_NormalizeOptionDialog()
        self.ui.setupUi(self)

        self._axis_values = axis_values
        self._axis_unit = axis_unit
        self._axis_symbol = axis_symbol

        number_of_slices = len(axis_values)

        if number_of_slices > 0:
            self.ui.sliceSpinBox.setRange(1, number_of_slices)
        else:
            self.ui.sliceSpinBox.setRange(1, 1)
            self.ui.sliceRadioButton.setEnabled(False)

        if (isinstance(normalize_option, int) and 0 <= normalize_option < number_of_slices):
            self.ui.sliceRadioButton.setChecked(True)
            self.ui.sliceSpinBox.setValue(normalize_option + 1)
        else:
            self.ui.maxAbsRadioButton.setChecked(True)
            self.ui.sliceSpinBox.setValue(1)

        self.ui.sliceRadioButton.toggled.connect(self._update_slice_controls)
        self.ui.sliceSpinBox.valueChanged.connect(self._update_slice_label)

        self._update_slice_controls(self.ui.sliceRadioButton.isChecked())
        self._update_slice_label(self.ui.sliceSpinBox.value())

    def _update_slice_controls(self, enabled: bool) -> None:
        """Enable slice controls only for slice normalization."""
        self.ui.sliceSpinBox.setEnabled(enabled)
        self.ui.sliceLabel.setEnabled(enabled)

    def _update_slice_label(self, displayed_slice: int) -> None:
        """Display the axis value corresponding to the selected slice."""
        if len(self._axis_values) == 0:
            self.ui.sliceLabel.clear()
            return

        slice_index = displayed_slice - 1
        axis_value = float(self._axis_values[slice_index])

        value_text = format_decimal(axis_value)
        if self._axis_unit:
            value_text = f"{value_text} {self._axis_unit}"

        self.ui.sliceLabel.setText(f"{self._axis_symbol} = {value_text}")

    def get_normalize_option(self) -> str | int:
        """Return 'max' or a zero-based slice index."""
        if self.ui.sliceRadioButton.isChecked():
            return self.ui.sliceSpinBox.value() - 1
        return "max"