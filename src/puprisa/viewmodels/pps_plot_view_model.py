# puprisa/viewmodels/pps_plot_view_model.py
"""Qt view model for pump-probe image display and colorbar.

Subscribes to StackManager / MaskManager / ProcessingManager events and
automatically renders the current slice.  No user-action handling lives
here — that belongs to controllers.
"""

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QGraphicsScene

import numpy as np

from puprisa.model.mask_manager import MaskEvent, MaskManager
from puprisa.model.processing_manager import ProcessingManager
from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.ui.widgets.mpl_canvas import MatplotlibFigureCanvas
from puprisa.ui.widgets.scrollable_graphics_view import ScrollableGraphicsView
from puprisa.utils.color_utils import apply_colormap


class PPSPlotViewModel(QObject):
    """Render the current stack slice into a graphics scene and manage colorbar."""

    MODE_STD_DEV = "std_dev"
    MODE_FULL_RANGE = "full_range"
    MODE_CUSTOM = "custom"

    def __init__(
        self,
        stack_manager: StackManager,
        mask_manager: MaskManager,
        processing_manager: ProcessingManager,
        graphics_view: ScrollableGraphicsView,
        colorbar: MatplotlibFigureCanvas | None = None,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._stack_manager = stack_manager
        self._mask_manager = mask_manager
        self._processing_manager = processing_manager
        self._graphics_view = graphics_view
        self._colorbar = colorbar

        self._scene = graphics_view.scene() or QGraphicsScene()
        self._graphics_view.setScene(self._scene)

        self._pixmap_item = None
        self._current_slice = 0
        self._colormap = "pumpprobe"
        self._color_scale_mode = self.MODE_STD_DEV
        self._vmin = None
        self._vmax = None
        self._custom_vmin = None
        self._custom_vmax = None
        self._last_pixmap_size = None

        # Model -> View
        self._stack_manager.add_listener(self._on_stack_event)
        self._mask_manager.add_listener(self._on_mask_event)
        self._processing_manager.add_listener(self._on_processing_event)

        self._initialize_from_current_stack()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _current_pps(self):
        item = self._stack_manager.get_current_item()
        return item.pps if item else None

    def _initialize_from_current_stack(self) -> None:
        pps = self._current_pps()
        if pps is None:
            self._clear()
            return
        self._current_slice = 0
        self._last_pixmap_size = None
        self._custom_vmin = None
        self._custom_vmax = None
        self.set_color_scale_mode(self.MODE_STD_DEV)

    # ------------------------------------------------------------------
    # Model event handlers
    # ------------------------------------------------------------------
    def _on_stack_event(self, event: StackEvent) -> None:
        if event.event == "current_changed":
            self._initialize_from_current_stack()

    def _on_mask_event(self, event: MaskEvent) -> None:
        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return
        if event.stack_id == current_item.id and event.event == "effective_changed":
            self.display_slice(self._current_slice)

    def _on_processing_event(self, event) -> None:
        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return
        if event.stack_id == current_item.id and event.event == "data_changed":
            self.set_color_scale_mode(self._color_scale_mode)  # 重算色标并重绘

    # ------------------------------------------------------------------
    # Public rendering API
    # ------------------------------------------------------------------
    def display_slice(self, index: int) -> None:
        pps = self._current_pps()
        if pps is None:
            return
        self._current_slice = max(0, min(index, len(pps.images) - 1))
        self._render_image(pps.images[self._current_slice])

    def fit_view(self) -> None:
        if self._pixmap_item is not None:
            self._graphics_view.fitInView(
                self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio
            )

    # ------------------------------------------------------------------
    # Colormap / color scale
    # ------------------------------------------------------------------
    def set_colormap(self, name: str) -> None:
        self._colormap = name
        if self._current_pps() is not None:
            self.display_slice(self._current_slice)

    def set_color_scale_mode(self, mode: str) -> None:
        self._color_scale_mode = mode
        self._recalculate_color_scale()
        if self._current_pps() is not None:
            self.display_slice(self._current_slice)

    def set_colorbar_range(self, vmin: float, vmax: float) -> None:
        self._custom_vmin = float(vmin)
        self._custom_vmax = float(vmax)
        if self._color_scale_mode == self.MODE_CUSTOM:
            self._recalculate_color_scale()
            if self._current_pps() is not None:
                self.display_slice(self._current_slice)

    def get_reference_ranges(self) -> dict:
        pps = self._current_pps()
        if pps is None:
            return {"std_min": None, "std_max": None, "full_min": None, "full_max": None}

        stats = pps.statistics(mask_on=False)
        mean = stats["mean"]
        std = stats["std"]
        abs_max = max(abs(mean - 4 * std), abs(mean + 4 * std))
        return {
            "std_min": -abs_max,
            "std_max": abs_max,
            "full_min": stats["min"],
            "full_max": stats["max"],
        }

    def _recalculate_color_scale(self) -> None:
        ref = self.get_reference_ranges()
        if self._color_scale_mode == self.MODE_FULL_RANGE:
            self._vmin = ref["full_min"]
            self._vmax = ref["full_max"]
        elif self._color_scale_mode == self.MODE_CUSTOM:
            if self._custom_vmin is not None and self._custom_vmax is not None:
                self._vmin = self._custom_vmin
                self._vmax = self._custom_vmax
            else:
                self._vmin = ref["std_min"]
                self._vmax = ref["std_max"]
        else:  # MODE_STD_DEV
            self._vmin = ref["std_min"]
            self._vmax = ref["std_max"]

    # ------------------------------------------------------------------
    # Internal rendering
    # ------------------------------------------------------------------
    def _clear(self) -> None:
        self._current_slice = 0
        if self._pixmap_item is not None:
            self._scene.removeItem(self._pixmap_item)
            self._pixmap_item = None

    def _render_image(self, image_data: np.ndarray) -> None:
        rgb, vmin_used, vmax_used = apply_colormap(
            image_data, vmin=self._vmin, vmax=self._vmax, cmap=self._colormap
        )

        pps = self._current_pps()
        if pps is not None:
            mask = np.asarray(pps.mask, dtype=bool)
            rgb[~mask] = [200, 200, 200]

        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
        h, w = rgb.shape[:2]
        qimage = QImage(rgb.tobytes(), w, h, rgb.strides[0], QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimage)

        if self._pixmap_item is None:
            self._pixmap_item = self._scene.addPixmap(pixmap)
        else:
            self._pixmap_item.setPixmap(pixmap)

        size = (pixmap.width(), pixmap.height())
        if size != self._last_pixmap_size:
            self._last_pixmap_size = size
            self.fit_view()

        if self._colorbar is not None:
            self._update_colorbar(vmin_used, vmax_used)

    def _update_colorbar(self, vmin: float, vmax: float) -> None:
        if self._colorbar is None:
            return

        gradient = np.linspace(vmin, vmax, 256).reshape(1, -1)
        rgb_gradient, vmin_used, vmax_used = apply_colormap(
            gradient, vmin=vmin, vmax=vmax, cmap=self._colormap
        )
        rgb_gradient = rgb_gradient.reshape(1, 256, 3)

        ax = self._colorbar.figure.axes[0] if self._colorbar.figure.axes else self._colorbar.figure.add_subplot(111)
        ax.clear()
        ax.imshow(rgb_gradient, aspect="auto", origin="lower", extent=[vmin_used, vmax_used, 0, 1])
        ax.set_yticks([])

        ticks = [vmin_used]
        if vmin_used < 0 < vmax_used:
            ticks.append(0.0)
        ticks.append(vmax_used)

        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{t:.2g}" for t in ticks], fontsize=8)
        ax.tick_params(axis="x", labelsize=10, pad=4)
        ax.set_xlim(vmin_used, vmax_used)
        ax.set_ylim(0, 1)

        self._colorbar.figure.subplots_adjust(left=0.1, right=0.9, bottom=0.45, top=0.9)
        self._colorbar.draw_idle()