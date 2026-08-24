# puprisa/ui/dialogs/intensity_threshold.py
"""Intensity threshold dialog.

Wraps ``Ui_intensityThresholdDialog`` and exposes parameters for
``PPSMaskController.create_mask_from_threshold``.
"""

from PySide6.QtWidgets import QDialog
from puprisa.ui.generated.dialog_intensity_threshold import Ui_intensityThresholdDialog


class IntensityThresholdDialog(QDialog):
    """Dialog for intensity-threshold mask parameters.

    Call ``get_params()`` after the dialog is accepted to obtain:

        ``(threshold, sigma, mask_on)``

    - ``threshold`` : float or ``"Li"``
    - ``sigma`` : float
    - ``mask_on`` : bool
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_intensityThresholdDialog()
        self.ui.setupUi(self)

        # Sigma: default 5.0
        self.ui.sigmaDoubleSpinBox.setRange(0.1, 100.0)
        self.ui.sigmaDoubleSpinBox.setValue(5.0)
        self.ui.sigmaDoubleSpinBox.setDecimals(1)

        # Manual threshold value: default 0.05
        self.ui.manualValueDoubleSpinBox.setRange(-1e9, 1e9)
        self.ui.manualValueDoubleSpinBox.setValue(0.05)
        self.ui.manualValueDoubleSpinBox.setDecimals(4)

        # Default state: Li selected, manual value disabled, mask checked
        self.ui.thresholdTypeComboBox.setCurrentIndex(0)
        self.ui.maskCheckBox.setChecked(True)
        self._update_manual_widgets("Li")

        # Enable manual widgets only when "Manual" is selected
        self.ui.thresholdTypeComboBox.currentTextChanged.connect(
            self._update_manual_widgets
        )

    def _update_manual_widgets(self, text: str):
        """Enable/disable manual threshold widgets based on combo selection."""
        is_manual = text == "Manual"
        self.ui.manualValueDoubleSpinBox.setEnabled(is_manual)
        self.ui.labelManual.setEnabled(is_manual)

    def get_params(self):
        """Return ``(threshold, sigma, mask_on)``."""
        if self.ui.thresholdTypeComboBox.currentText() == "Li":
            threshold = "Li"
        else:
            threshold = self.ui.manualValueDoubleSpinBox.value()

        return (
            threshold,
            self.ui.sigmaDoubleSpinBox.value(),
            self.ui.maskCheckBox.isChecked(),
        )