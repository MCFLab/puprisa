# puprisa/controllers/phasor_frequency_controller.py
"""Qt controller for phasor frequency slider and spin box."""
from PySide6.QtCore import QObject, Signal, QSignalBlocker
from PySide6.QtWidgets import QDoubleSpinBox, QSlider


class PhasorFrequencyController(QObject):
    """Keep a QSlider and QDoubleSpinBox in sync for phasor frequency."""

    SLIDER_MIN = 1
    SLIDER_MAX = 100
    SLIDER_STEP = 0.01

    SPINBOX_MIN = 0.01
    SPINBOX_MAX = 100.0

    frequencyChanged = Signal(float)

    def __init__(self, slider: QSlider, spinbox: QDoubleSpinBox, parent: QObject | None = None):
        super().__init__(parent)
        self._slider = slider
        self._spinbox = spinbox

        self._slider.setMinimum(self.SLIDER_MIN)
        self._slider.setMaximum(self.SLIDER_MAX)
        self._slider.setValue(25)

        self._spinbox.setMinimum(self.SPINBOX_MIN)
        self._spinbox.setMaximum(self.SPINBOX_MAX)
        self._spinbox.setSingleStep(0.01)
        self._spinbox.setDecimals(3)
        self._spinbox.setValue(0.25)

        self._slider.valueChanged.connect(self._on_slider_changed)
        self._spinbox.valueChanged.connect(self._on_spinbox_changed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def frequency(self) -> float:
        return self._spinbox.value()

    def set_frequency(self, freq: float) -> None:
        freq = max(self.SPINBOX_MIN, min(self.SPINBOX_MAX, freq))
        slider_int = int(round(freq / self.SLIDER_STEP))
        slider_int = max(self.SLIDER_MIN, min(self.SLIDER_MAX, slider_int))

        with QSignalBlocker(self._slider), QSignalBlocker(self._spinbox):
            self._spinbox.setValue(freq)
            self._slider.setValue(slider_int)

        self.frequencyChanged.emit(freq)

    def change_frequency_by_delta(self, delta: float) -> None:
        self.set_frequency(self.frequency() + delta * self.SLIDER_STEP)

    # ------------------------------------------------------------------
    # Internal slots
    # ------------------------------------------------------------------
    def _on_slider_changed(self, value: int) -> None:
        freq = value * self.SLIDER_STEP
        with QSignalBlocker(self._spinbox):
            self._spinbox.setValue(freq)
        self.frequencyChanged.emit(freq)

    def _on_spinbox_changed(self, freq: float) -> None:
        slider_int = int(round(freq / self.SLIDER_STEP))
        slider_int = max(self.SLIDER_MIN, min(self.SLIDER_MAX, slider_int))
        with QSignalBlocker(self._slider):
            self._slider.setValue(slider_int)
        self.frequencyChanged.emit(freq)