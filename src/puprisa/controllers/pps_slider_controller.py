# puprisa/controllers/pps_slider_controller.py
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QSlider, QLabel

from puprisa.core.pps import PPS
from puprisa.controllers.pps_plot_controller import PPSPlotController

class PPSSliderController(QObject):
    sliceChanged = Signal(int)

    def __init__(self, slider: QSlider, slice_label: QLabel, axis_label: QLabel, plot_controller: PPSPlotController):
        super().__init__()
        self.slider = slider
        self.slice_label = slice_label
        self.axis_label = axis_label
        self.plot_controller = plot_controller
        self.pps = None
        self.current_slice = 0

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.setEnabled(False)

    def set_pps(self, pps: PPS, reset_slice=True):
        self.pps = pps
        if pps is None or len(pps.images) == 0:
            self.slider.setEnabled(False)
            self.slider.setMaximum(0)
            self.slider.setValue(0)
            self.slice_label.setText("Slice")
            self.axis_label.setText("")
            return

        self.slider.blockSignals(True)
        self.slider.setEnabled(True)
        self.slider.setMaximum(len(pps.images) - 1)
        self.slider.setValue(0)
        self.slider.blockSignals(False)

        if reset_slice:
            self.current_slice = 0
        self._update_labels()

    def change_slice_by_delta(self, delta: int):
        """Change the current slice by a given delta, ensuring it stays within valid bounds."""
        if self.pps is None:
            return
        new_slice = max(0, min(self.current_slice + delta, len(self.pps.images) - 1))
        if new_slice != self.current_slice:
            self.current_slice = new_slice
            self.slider.setValue(new_slice)
            self._update_labels()
            self.sliceChanged.emit(new_slice)

    def _on_slider_changed(self, value):
        if self.pps is None:
            return
        self.current_slice = value
        self.plot_controller.display_slice(value)
        self._update_labels()
        self.sliceChanged.emit(value)

    def _update_labels(self):
        if self.pps is None:
            return
        total = len(self.pps.images)
        self.slice_label.setText(f"Slice {self.current_slice+1}/{total}")
        values = self.pps.get_axis_values()
        if self.current_slice < len(values):
            val = values[self.current_slice]
            unit = self.pps.get_axis_unit()
            prefix = "Time" if self.pps.axis_type == "time" else "Z"
            self.axis_label.setText(f"{prefix}: {val:.2f} {unit}")