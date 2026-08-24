# puprisa/ui/dialogs/background_subtraction_dialog.py
from PySide6.QtWidgets import QDialog
from puprisa.ui.generated.dialog_background_subtraction import Ui_backgroundSubtractionDialog

class BackgroundSubtractionDialog(QDialog):
    """Dialog for configuring background subtraction using first/last N frames."""

    def __init__(self, n_total_frames: int, parent=None):
        super().__init__(parent)
        self.ui = Ui_backgroundSubtractionDialog()
        self.ui.setupUi(self)

        self._n_total_frames = n_total_frames

        # Set valid range for frame count
        self.ui.imgNumberSpinBox.setRange(1, n_total_frames)
        self.ui.imgNumberSpinBox.setValue(1)

        # Default: pixel-wise subtraction
        self.ui.pixelwiseRadioButton.setChecked(True)
        self.ui.wholeimgRadioButton.setChecked(False)

    def get_parameters(self) -> tuple[list[int], bool]:
        """Return (indices, pixelwise) based on current user selections."""
        n = self.ui.imgNumberSpinBox.value()
        is_first = self.ui.subTypeComboBox.currentText().strip().lower() == "first"
        pixelwise = self.ui.pixelwiseRadioButton.isChecked()

        if is_first:
            indices = list(range(n))
        else:
            # Last n frames
            start = max(0, self._n_total_frames - n)
            indices = list(range(start, self._n_total_frames))

        return indices, pixelwise