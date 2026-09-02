# puprisa/ui/dialogs/background_subtraction.py
from PySide6.QtWidgets import QDialog

from puprisa.ui.generated.dialog_bgsub_first_last import Ui_FirstLastBgSubDialog
from puprisa.ui.generated.dialog_bgsub_fixed_value import Ui_FixedValueBgSubDialog
from puprisa.ui.generated.dialog_bgsub_neg_delay import Ui_NegDelayBgSubDialog


class BgSubFirstLastDialog(QDialog):
    """Dialog for configuring background subtraction using first/last N frames."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_FirstLastBgSubDialog()
        self.ui.setupUi(self)
        self.ui.pixelwiseRadioButton.setChecked(True)
        
    def get_parameters(self) -> tuple[int, bool, bool, bool]:
        """Return (n_frames, is_first, pixelwise, apply_all)."""
        n = self.ui.imgNumberSpinBox.value()
        is_first = self.ui.subTypeComboBox.currentIndex() == 0
        pixelwise = self.ui.pixelwiseRadioButton.isChecked()
        apply_all = self.ui.applyAllCheckBox.isChecked()
        return n, is_first, pixelwise, apply_all


class BgSubFixedValueDialog(QDialog):
    """Dialog for subtracting a fixed value from stack."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_FixedValueBgSubDialog()
        self.ui.setupUi(self)

        # Configure the spin box
        self.ui.doubleSpinBox.setRange(-1e9, 1e9)
        self.ui.doubleSpinBox.setDecimals(6)
        self.ui.doubleSpinBox.setValue(0.0)

    def get_parameters(self) -> tuple[float, bool]:
        """Return (value, apply_all)."""
        return (
            self.ui.doubleSpinBox.value(),
            self.ui.checkBox.isChecked(),
        )


class BgSubNegDelayDialog(QDialog):
    """Dialog for subtracting negative-delay background."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_NegDelayBgSubDialog()
        self.ui.setupUi(self)

        # Default: pixel-wise
        self.ui.radioButton.setChecked(True)

    def get_parameters(self) -> tuple[bool, bool]:
        """Return (pixelwise, apply_all)."""
        pixelwise = self.ui.radioButton.isChecked()
        apply_all = self.ui.checkBox.isChecked()
        return pixelwise, apply_all