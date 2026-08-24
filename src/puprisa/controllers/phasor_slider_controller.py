# puprisa/controllers/phasor_frequency_controller.py
"""Controller for the phasor frequency slider and spin box.

The slider covers the commonly used frequency range 0.01–1.0 THz in
0.01 THz steps. The spin box allows a wider range (0.01–100 THz) so
users can type larger values manually. When the spin box value lies
outside the slider range, the slider thumb is clamped to the
corresponding extreme (left or right) while the spin box retains its
actual value.

Signals
-------
frequencyChanged : Signal(float)
    Emitted whenever the frequency changes (from either control).
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QSlider, QDoubleSpinBox


class PhasorFrequencyController(QObject):
    """Keep a QSlider and QDoubleSpinBox in sync for phasor frequency."""

    # Slider: 1 -> 0.01 THz, 100 -> 1.00 THz
    SLIDER_MIN = 1
    SLIDER_MAX = 100
    SLIDER_STEP = 0.01   # THz per slider unit

    # Spinbox: wider manual input range
    SPINBOX_MIN = 0.01   # 1e-2 THz
    SPINBOX_MAX = 100.0  # 1e2 THz

    frequencyChanged = Signal(float)

    def __init__(self, slider: QSlider, spinbox: QDoubleSpinBox):
        super().__init__()
        self.slider = slider
        self.spinbox = spinbox

        # --- Slider setup: 0.01–1.00 THz in 0.01 steps ---
        self.slider.setMinimum(self.SLIDER_MIN)
        self.slider.setMaximum(self.SLIDER_MAX)
        self.slider.setValue(25)   # 0.25 THz

        # --- Spinbox setup: 0.01–100 THz ---
        self.spinbox.setMinimum(self.SPINBOX_MIN)
        self.spinbox.setMaximum(self.SPINBOX_MAX)
        self.spinbox.setSingleStep(0.01)
        self.spinbox.setDecimals(3)
        self.spinbox.setValue(0.25)

        # --- Signals ---
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def frequency(self) -> float:
        """Return the current frequency in THz."""
        return self.spinbox.value()

    def set_frequency(self, freq: float):
        """Set both controls to the given frequency (in THz).

        The spin box is clamped to [0.01, 100] and the slider is
        clamped to [0.01, 1.0]. If ``freq`` lies outside the slider
        range, the slider will rest at the nearest extreme while the
        spin box shows the (clamped) actual value.
        """
        # Clamp to spinbox range (manual-entry range)
        freq = max(self.spinbox.minimum(), min(self.spinbox.maximum(), freq))

        # Compute slider position; clamp to slider range
        slider_int = int(round(freq / self.SLIDER_STEP))
        slider_int = max(self.slider.minimum(), min(self.slider.maximum(), slider_int))

        # Block signals to avoid feedback loops
        self.slider.blockSignals(True)
        self.spinbox.blockSignals(True)

        self.spinbox.setValue(freq)
        self.slider.setValue(slider_int)

        self.slider.blockSignals(False)
        self.spinbox.blockSignals(False)

        # Emit manually because signals were blocked
        self.frequencyChanged.emit(freq)

    def change_frequency_by_delta(self, delta: float):
        """Change frequency by a fixed step (0.01 THz) per delta unit.

        Positive delta increases frequency, negative decreases.
        """
        new_freq = self.frequency() + delta * self.SLIDER_STEP
        self.set_frequency(new_freq)

    # ------------------------------------------------------------------
    # Internal slots
    # ------------------------------------------------------------------
    def _on_slider_changed(self, slider_value: int):
        """Slider moved by user: update spinbox to matching frequency."""
        freq = slider_value * self.SLIDER_STEP

        # Update spinbox without triggering its signal
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(freq)
        self.spinbox.blockSignals(False)

        self.frequencyChanged.emit(freq)

    def _on_spinbox_changed(self, freq: float):
        """Spinbox edited by user: update slider position.

        If the frequency is outside the slider range, the slider thumb
        is moved to the nearest extreme (left or right).
        """
        # Compute raw slider position
        slider_int = int(round(freq / self.SLIDER_STEP))

        # Clamp to slider range; do not change the spinbox value itself
        slider_int = max(self.slider.minimum(), min(self.slider.maximum(), slider_int))

        # Update slider without triggering its signal
        self.slider.blockSignals(True)
        self.slider.setValue(slider_int)
        self.slider.blockSignals(False)

        # Emit the actual (possibly out-of-slider-range) frequency
        self.frequencyChanged.emit(freq)