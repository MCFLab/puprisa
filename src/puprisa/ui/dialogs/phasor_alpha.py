# puprisa/ui/dialogs/phasor_alpha.py
"""Dialog for editing the phasor density alpha range."""
from PySide6.QtWidgets import QDialog

from puprisa.ui.generated.dialog_phasor_alpha import Ui_PhasorAlphaDialog


class PhasorAlphaDialog(QDialog):
    """Wrapper for the phasor alpha range UI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_PhasorAlphaDialog()
        self.ui.setupUi(self)
        self.ui.alphaMinDoubleSpinBox.setValue(0.0)
        self.ui.alphaMaxDoubleSpinBox.setValue(255.0)