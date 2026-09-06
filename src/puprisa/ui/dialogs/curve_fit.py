# puprisa/ui/dialogs/curve_fit.py
"""Curve fitting dialog wrapper."""

from pathlib import Path
from importlib.resources import files

from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QDialog, QStyle, QLabel

import numpy as np

from puprisa.core.fit import FitOptions
from puprisa.ui.generated.dialog_curve_fit import Ui_curveFitDialog


class CurveFitDialog(QDialog):
    """Wrapper for the curve fitting UI, responsible for parameter retrieval and result display."""

    fitRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_curveFitDialog()
        self.ui.setupUi(self)

        # ---- Replace infoIcon with the Qt standard information icon ----
        self.ui.infoIcon.setText("")  # Clear the "info" text
        self.ui.infoIcon.setPixmap(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_MessageBoxInformation
            ).pixmap(16, 16)
        )

        # --- Load and set the SVG images for the fitting components ----
        resources = files("puprisa").joinpath("ui/resources")
        self._set_label_icon(self.ui.instPicture, resources / "instantaneous.svg")
        self._set_label_icon(self.ui.expDecayPicture, resources / "exp_decay.svg")
        self._set_label_icon(self.ui.expDecayInfPicture, resources / "exp_decay_inf.svg")

        # ---- Dynamically disable corresponding parameter sections based on checkboxes ----
        self.ui.instCheckBox.toggled.connect(self.ui.groupBox.setEnabled)
        self.ui.expDecay1CheckBox.toggled.connect(
            lambda checked: self.ui.ExpDecayTab.setTabEnabled(0, checked)
        )
        self.ui.expDecay2CheckBox.toggled.connect(
            lambda checked: self.ui.ExpDecayTab.setTabEnabled(1, checked)
        )
        self.ui.expDecay3CheckBox.toggled.connect(
            lambda checked: self.ui.ExpDecayTab.setTabEnabled(2, checked)
        )
        self.ui.expDecayInfCheckBox.toggled.connect(self.ui.groupBox_2.setEnabled)

        # ---- Pulse width mode switching ----
        self.ui.specifyPulseWidthRadioButton.toggled.connect(
            self._on_pulse_width_mode_changed
        )
        self.ui.fitPulseWidthRadioButton.toggled.connect(
            lambda checked: self._on_pulse_width_mode_changed(not checked)
        )

        # ---- Time shift (t0) mode switching ----
        self.ui.specifyt0RadioButton.toggled.connect(
            self._on_t0_mode_changed
        )
        self.ui.fitt0RadioButton.toggled.connect(
            lambda checked: self._on_t0_mode_changed(not checked)
        )

        # ---- Initialize enabled states ----
        self.ui.groupBox.setEnabled(self.ui.instCheckBox.isChecked())
        self.ui.ExpDecayTab.setTabEnabled(0, self.ui.expDecay1CheckBox.isChecked())
        self.ui.ExpDecayTab.setTabEnabled(1, self.ui.expDecay2CheckBox.isChecked())
        self.ui.ExpDecayTab.setTabEnabled(2, self.ui.expDecay3CheckBox.isChecked())
        self.ui.groupBox_2.setEnabled(self.ui.expDecayInfCheckBox.isChecked())
        self._on_pulse_width_mode_changed(self.ui.specifyPulseWidthRadioButton.isChecked())
        self._on_t0_mode_changed(self.ui.specifyt0RadioButton.isChecked())

        # ---- Button connections ----
        self.ui.fitPushButton.clicked.connect(self.fitRequested.emit)
        self.ui.exitPushButton.clicked.connect(self.reject)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _on_pulse_width_mode_changed(self, specify: bool) -> None:
        """Enable/disable the pulse width input controls based on mode."""
        # Specify mode: only allow a fixed value
        self.ui.pulseWidthLineEdit.setEnabled(specify)

        # Fit mode: enable initial value / lower bound / upper bound
        for edit in (
            self.ui.iniTpLineEdit,
            self.ui.lowerlimTpLineEdit,
            self.ui.upperlimTpLineEdit,
        ):
            edit.setEnabled(not specify)

    def _on_t0_mode_changed(self, specify: bool) -> None:
        """Enable/disable the time shift (t0) input controls based on mode."""
        # Specify mode: only allow a fixed value
        self.ui.t0LineEdit.setEnabled(specify)

        # Fit mode: enable initial value / lower bound / upper bound
        for edit in (
            self.ui.initt0LineEdit,
            self.ui.lowerlimt0LineEdit,
            self.ui.upperlimt0LineEdit,
        ):
            edit.setEnabled(not specify)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_fit_options(self) -> FitOptions:
        """Read all fitting parameters from the UI and return a FitOptions instance."""

        def parse_float(text: str, default: float) -> float:
            text = text.strip()
            if text.lower() in ("inf", "+inf"):
                return np.inf
            elif text.lower() == "-inf":
                return -np.inf
            try:
                return float(text)
            except ValueError:
                return default

        # ---- Pulse width ----
        pulse_specify = self.ui.specifyPulseWidthRadioButton.isChecked()
        pulse_width_fs = parse_float(self.ui.pulseWidthLineEdit.text(), 100.0)

        if pulse_specify:
            # Fixed pulse width: tp is fixed, but we still need dummy init/bounds for FitOptions
            tp_init = pulse_width_fs / 1000.0   # ps
            tp_lower = 1e-4
            tp_upper = 100.0
        else:
            # Fit pulse width: read init/bounds in fs -> ps
            tp_init = parse_float(self.ui.iniTpLineEdit.text(), 100.0) / 1000.0
            tp_lower = parse_float(self.ui.lowerlimTpLineEdit.text(), 0.0) / 1000.0
            tp_upper = parse_float(self.ui.upperlimTpLineEdit.text(), np.inf) / 1000.0

        # ---- Time shift (t0) ----
        t0_specify = self.ui.specifyt0RadioButton.isChecked()
        if t0_specify:
            time_shift = parse_float(self.ui.t0LineEdit.text(), 0.0)   # ps
            t0_init = time_shift
            t0_lower = -1.0
            t0_upper = 1.0
        else:
            # Fit t0: read init/bounds (already in ps)
            time_shift = 0.0   # not used when fitting
            t0_init = parse_float(self.ui.initt0LineEdit.text(), 0.0)
            t0_lower = parse_float(self.ui.lowerlimt0LineEdit.text(), -1.0)
            t0_upper = parse_float(self.ui.upperlimt0LineEdit.text(), 1.0)

        # ---- Build FitOptions ----
        return FitOptions(
            include_instantaneous=self.ui.instCheckBox.isChecked(),
            include_exp_decay_1=self.ui.expDecay1CheckBox.isChecked(),
            include_exp_decay_2=self.ui.expDecay2CheckBox.isChecked(),
            include_exp_decay_3=self.ui.expDecay3CheckBox.isChecked(),
            include_exp_decay_inf=self.ui.expDecayInfCheckBox.isChecked(),
            pulse_width_option="specify" if pulse_specify else "fit",
            pulse_width_fs=pulse_width_fs,
            t0_option="specify" if t0_specify else "fit",
            time_shift=time_shift,
            A0_init=parse_float(self.ui.iniA0LineEdit.text(), 1.0),
            A0_lower=parse_float(self.ui.lowerlimA0LineEdit.text(), -np.inf),
            A0_upper=parse_float(self.ui.upperlimA0LineEdit.text(), np.inf),
            A1_init=parse_float(self.ui.iniA1LineEdit.text(), 1.0),
            A1_lower=parse_float(self.ui.lowerlimA1LineEdit.text(), -np.inf),
            A1_upper=parse_float(self.ui.upperlimA1LineEdit.text(), np.inf),
            tau1_init=parse_float(self.ui.iniT1LineEdit.text(), 1.0),
            tau1_lower=parse_float(self.ui.lowerlimT1LineEdit.text(), 0.0),
            tau1_upper=parse_float(self.ui.upperlimT1LineEdit.text(), np.inf),
            A2_init=parse_float(self.ui.iniA2LineEdit.text(), 1.0),
            A2_lower=parse_float(self.ui.lowerlimA2LineEdit.text(), -np.inf),
            A2_upper=parse_float(self.ui.upperlimA2LineEdit.text(), np.inf),
            tau2_init=parse_float(self.ui.iniT2LineEdit.text(), 10.0),
            tau2_lower=parse_float(self.ui.lowerlimT2LineEdit.text(), 0.0),
            tau2_upper=parse_float(self.ui.upperlimT2LineEdit.text(), np.inf),
            A3_init=parse_float(self.ui.iniA3LineEdit.text(), 1.0),
            A3_lower=parse_float(self.ui.lowerlimA3LineEdit.text(), -np.inf),
            A3_upper=parse_float(self.ui.upperlimA3LineEdit.text(), np.inf),
            tau3_init=parse_float(self.ui.iniT3LineEdit.text(), 0.1),
            tau3_lower=parse_float(self.ui.lowerlimT3LineEdit.text(), 0.0),
            tau3_upper=parse_float(self.ui.upperlimT3LineEdit.text(), np.inf),
            A4_init=parse_float(self.ui.iniA4LineEdit.text(), 1.0),
            A4_lower=parse_float(self.ui.lowerlimA4LineEdit.text(), -np.inf),
            A4_upper=parse_float(self.ui.upperlimA4LineEdit.text(), np.inf),
            tp_init=tp_init,
            tp_lower=tp_lower,
            tp_upper=tp_upper,
            t0_init=t0_init,
            t0_lower=t0_lower,
            t0_upper=t0_upper,
        )

    def set_result_text(self, text: str) -> None:
        """Display text in the result area."""
        self.ui.resultPlainTextEdit.setPlainText(text)

    def _set_label_icon(self, label: QLabel, path: Path):
            if not path.exists():
                label.setText(f"Missing: {path.name}")
                return
            icon = QIcon(str(path))
            if icon.isNull():
                label.setText(f"Failed: {path.name}")
                return
            target_size = label.size()
            if target_size.width() <= 0 or target_size.height() <= 0:
                target_size = label.sizeHint()
            if target_size.width() <= 0 or target_size.height() <= 0:
                target_size = QSize(200, 150)
            pixmap = icon.pixmap(target_size)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)