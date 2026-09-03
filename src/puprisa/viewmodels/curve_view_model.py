# puprisa/viewmodels/curve_view_model.py
"""Qt view model for the embedded ROI curve plot."""
from __future__ import annotations

from PySide6.QtCore import QObject

from puprisa.model.curve_manager import CurveEvent, CurveManager
from puprisa.model.mask_manager import MaskEvent, MaskManager
from puprisa.model.processing_manager import ProcessingManager
from puprisa.model.roi_manager import RoiEvent, RoiManager
from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.ui.widgets.mpl_canvas import MatplotlibFigureCanvas
from puprisa.utils.curve_plot_utils import draw_roi_curves

class CurveViewModel(QObject):
    """Draw ROI average curves for a specific space on an embedded canvas.

    The ViewModel maintains its own normalization setting; the underlying
    CurveManager is stateless and simply computes the requested curves.
    """

    def __init__(self, curve_manager: CurveManager, roi_manager: RoiManager, stack_manager: StackManager, mask_manager: MaskManager, processing_manager: ProcessingManager, canvas: MatplotlibFigureCanvas, space: str, parent: QObject | None = None):
        super().__init__(parent)
        self._curve_manager = curve_manager
        self._roi_manager = roi_manager
        self._stack_manager = stack_manager
        self._mask_manager = mask_manager
        self._processing_manager = processing_manager
        self._canvas = canvas
        self._space = space
        self._normalize = False
        self._current_slice_index = 0

        if self._canvas is not None:
            self._canvas.figure.set_constrained_layout(True)

        self._curve_manager.add_listener(self._on_curve_event)
        self._roi_manager.add_listener(self._on_roi_event)
        self._stack_manager.add_listener(self._on_stack_event)
        self._mask_manager.add_listener(self._on_mask_event)
        self._processing_manager.add_listener(self._on_processing_event)

        self.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_normalize(self, enabled: bool) -> None:
        if self._normalize != enabled:
            self._normalize = enabled
            self.refresh()

    def set_current_slice(self, index: int) -> None:
        if self._current_slice_index != index:
            self._current_slice_index = index
            self.refresh()

    @property
    def normalize(self) -> bool:
        return self._normalize

    def refresh(self) -> None:
        if self._canvas is None:
            return

        curves = self._curve_manager.compute_curves(space=self._space, normalize=self._normalize)
        fig = self._canvas.figure
        ax = fig.axes[0] if fig.axes else fig.add_subplot(111)
        ax.clear()

        # Try to get the axis label and unit from the current stack item
        current_item = self._stack_manager.get_current_item()
        if current_item is not None:
            pps = current_item.pps
            xlabel = (f"{pps.get_axis_label()} ({pps.get_axis_unit()})")
            slice_x = None
            if self._space == "pixel":
                axis_values = pps.get_axis_values()
                if 0 <= self._current_slice_index < len(axis_values):
                    slice_x = axis_values[self._current_slice_index]
        else:
            slice_x = None
            xlabel = "Time delay (ps)"
        ylabel = "Normalized signal (a.u.)" if self._normalize else "Average signal (a.u.)"
        title = "ROI Averaged Curves"
        
        draw_roi_curves(ax, curves, xlabel=xlabel, ylabel=ylabel, title=title, current_slice_x=slice_x)
        
        ax.relim()
        ax.autoscale_view(tight=True)
        self._canvas.draw_idle()

    # ------------------------------------------------------------------
    # Model event handlers
    # ------------------------------------------------------------------
    def _on_curve_event(self, event: CurveEvent) -> None:
        if event.event == "computed":
            pass

    def _on_roi_event(self, event: RoiEvent) -> None:
        self.refresh()

    def _on_stack_event(self, event: StackEvent) -> None:
        if event.event in ("added", "removed", "visibility_changed"):
            self.refresh()

    def _on_mask_event(self, event: MaskEvent) -> None:
        if event.event == "effective_changed":
            self.refresh()

    def _on_processing_event(self, event) -> None:
        if event.event == "data_changed":
            self.refresh()