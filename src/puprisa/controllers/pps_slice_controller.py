# puprisa/controllers/pps_slice_controller.py
"""Qt controller for slice slider and labels."""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal, QSignalBlocker
from PySide6.QtWidgets import QLabel, QSlider

from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.viewmodels.pps_plot_view_model import PPSPlotViewModel


class PPSSliceController(QObject):
    """Keep the slice slider, labels, and plot viewmodel in sync."""

    sliceChanged = Signal(int)

    def __init__(
        self,
        stack_manager: StackManager,
        plot_viewmodel: PPSPlotViewModel,
        slider: QSlider,
        slice_label: QLabel,
        axis_label: QLabel,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._stack_manager = stack_manager
        self._plot_viewmodel = plot_viewmodel
        self._slider = slider
        self._slice_label = slice_label
        self._axis_label = axis_label
        self._current_slice = 0

        self._slider.valueChanged.connect(self._on_slider_changed)
        self._slider.setEnabled(False)

        self._stack_manager.add_listener(self._on_stack_event)

    # ------------------------------------------------------------------
    # Model -> View
    # ------------------------------------------------------------------
    def _on_stack_event(self, event: StackEvent) -> None:
        if event.event != "current_changed":
            return

        item = event.stack_item
        pps = item.pps if item else None
        if pps is None or len(pps.images) == 0:
            with QSignalBlocker(self._slider):
                self._slider.setEnabled(False)
                self._slider.setMaximum(0)
                self._slider.setValue(0)
            self._slice_label.setText("Slice")
            self._axis_label.setText("AxisLabel")
            self._current_slice = 0
            self.sliceChanged.emit(0)
            return

        new_slice = self._current_slice if self._current_slice < len(pps.images) else 0
        with QSignalBlocker(self._slider):
            self._slider.setEnabled(True)
            self._slider.setMaximum(len(pps.images) - 1)
            self._slider.setValue(new_slice)
        self._current_slice = new_slice
        self._update_labels()
        self.sliceChanged.emit(new_slice)

    # ------------------------------------------------------------------
    # View -> Model
    # ------------------------------------------------------------------
    def change_slice_by_delta(self, delta: int) -> None:
        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return
        pps = current_item.pps
        new_slice = max(0, min(self._current_slice + delta, len(pps.images) - 1))
        if new_slice != self._current_slice:
            self._current_slice = new_slice
            self._slider.setValue(new_slice)

    def _on_slider_changed(self, value: int) -> None:
        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return
        self._current_slice = value
        self._plot_viewmodel.display_slice(value)
        self._update_labels()
        self.sliceChanged.emit(value)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _update_labels(self) -> None:
        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return
        pps = current_item.pps
        total = len(pps.images)
        self._slice_label.setText(f"Slice {self._current_slice + 1}/{total}")

        values = pps.get_axis_values()
        if self._current_slice < len(values):
            val = values[self._current_slice]
            unit = pps.get_axis_unit()
            prefix = "Time" if pps.axis_type == "time" else "Z"
            self._axis_label.setText(f"{prefix}: {val:.2f} {unit}")