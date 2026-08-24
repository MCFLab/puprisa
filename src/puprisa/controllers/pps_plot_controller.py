# puprisa/controllers/pps_plot_controller.py
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Signal, Qt, QObject, QRectF

import numpy as np

from puprisa.controllers.pps_curve_controller import PPSCurveController
from puprisa.core.pps import PPS
from puprisa.ui.widgets.scrollable_graphics_view import ScrollableGraphicsView
from puprisa.utils.color_utils import apply_colormap
from puprisa.utils.geometry_utils import shape_to_mask
from puprisa.ui.widgets.mpl_canvas import MatplotlibFigureCanvas


class PPSPlotController(QObject):
    MODE_STD_DEV = 'std_dev'
    MODE_FULL_RANGE = 'full_range'
    MODE_CUSTOM = 'custom'

    pixmapRectChanged = Signal(QRectF)

    def __init__(
        self,
        ppsGraphicsView: ScrollableGraphicsView,
        colorbar: MatplotlibFigureCanvas | None = None,
        plotCanvas: MatplotlibFigureCanvas | None = None,
        curve_controller: PPSCurveController | None = None,
    ):
        super().__init__()
        self.ppsGraphicsView = ppsGraphicsView
        self.scene = ppsGraphicsView.scene()
        if self.scene is None:
            self.scene = QGraphicsScene()
            self.ppsGraphicsView.setScene(self.scene)
        self.pixmap_item = None
        self.colorbar = colorbar
        self.plotCanvas = plotCanvas
        self.curve_controller = curve_controller

        if self.plotCanvas is not None:
            self.plotCanvas.figure.set_constrained_layout(True)

        # Current state
        self.pps: PPS | None = None
        self.current_slice = 0
        self.colormap = 'pumpprobe'
        self.color_scale_mode = self.MODE_STD_DEV
        self.vmin = None
        self.vmax = None
        self.custom_vmin = None
        self.custom_vmax = None

        self._last_pixmap_size = None

    # ------------------------------------------------------------------
    # PPS / Slice management
    # ------------------------------------------------------------------
    def set_pps(self, pps: PPS):
        """Set the current PPS object."""
        self.pps = pps
        if pps is None:
            self.current_slice = 0
            self._last_pixmap_size = None
            if self.pixmap_item is not None:
                self.scene.removeItem(self.pixmap_item)
                self.pixmap_item = None
            return
        self.current_slice = 0
        self._last_pixmap_size = None
        self.set_colorbar_scale_mode(self.MODE_STD_DEV)
        self.display_slice(0)

    def display_slice(self, index: int):
        """Show the frame at index (0-based)."""
        if self.pps is None:
            return
        self.current_slice = max(0, min(index, len(self.pps.images) - 1))
        self.render_image(
            self.pps.images[self.current_slice],
            vmin=self.vmin,
            vmax=self.vmax,
            colormap=self.colormap,
        )

    def fit_view(self):
        """Reset the view to fit the current pixmap."""
        if self.pixmap_item is not None:
            self.ppsGraphicsView.fitInView(
                self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio
            )

    def on_mask_changed(self):
        """Redisplay the current slice when the mask changes."""
        if self.pps is not None:
            self.display_slice(self.current_slice)

    # ------------------------------------------------------------------
    # ROI signal curves
    # ------------------------------------------------------------------
    def update_roi_plot(self):
        """Compute curve data via ``curve_controller`` and draw on the canvas.

        The embedded ``plotCanvas`` is cleared and repopulated with the curves
        obtained from the associated :class:`PPSCurveController`.  A vertical
        dashed line marks the current slice position on the x-axis.
        """
        if self.plotCanvas is None or self.curve_controller is None:
            return

        curves = self.curve_controller.compute_curves()

        fig = self.plotCanvas.figure
        ax = fig.axes[0] if fig.axes else fig.add_subplot(111)

        ax.clear()
        axis_label = "Time delay (ps)"
        if self.pps is not None:
            axis_label = f"{self.pps.get_axis_label()} ({self.pps.get_axis_unit()})"
        ax.set_xlabel(axis_label)
        if self.curve_controller.normalize_curves:
            ax.set_ylabel("Normalized signal")
        else:
            ax.set_ylabel("Average signal (arb. u.)")
        ax.grid(True, alpha=0.3)

        # 1) Draw all ROI curves
        for x, y, label, color in curves:
            ax.plot(x, y, color=color, label=label)

        # 2) Draw vertical dashed line for the current slice
        if self.pps is not None:
            axis_values = self.pps.get_axis_values()
            if 0 <= self.current_slice < len(axis_values):
                slice_x = axis_values[self.current_slice]
                ax.axvline(
                    slice_x,
                    color="gray",
                    linestyle="--",
                    linewidth=1.2,
                    alpha=0.8,
                )

        if curves:
            ax.legend(fontsize=8, loc="best")
        ax.relim()
        ax.autoscale_view(tight=True)
        self.plotCanvas.draw_idle()

    # ------------------------------------------------------------------
    # Rendering Image
    # ------------------------------------------------------------------
    def render_image(self, image_data: np.ndarray, vmin=None, vmax=None, colormap=None):
        # ... unchanged ...
        if image_data is None:
            return

        if colormap is None:
            colormap = self.colormap
        if vmin is None:
            vmin = self.vmin
        if vmax is None:
            vmax = self.vmax

        rgb, vmin_used, vmax_used = apply_colormap(
            image_data, vmin=vmin, vmax=vmax, cmap=colormap
        )

        if self.pps is not None:
            mask = np.asarray(self.pps.mask, dtype=bool)
            rgb[~mask] = [200, 200, 200]

        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
        h, w = rgb.shape[:2]
        bytes_per_line = rgb.strides[0]

        qimage = QImage(rgb.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimage)

        if self.pixmap_item is None:
            self.pixmap_item = self.scene.addPixmap(pixmap)
        else:
            self.pixmap_item.setPixmap(pixmap)

        self.pixmapRectChanged.emit(self.pixmap_item.boundingRect())

        size = (pixmap.width(), pixmap.height())
        if size != self._last_pixmap_size:
            self._last_pixmap_size = size
            self.ppsGraphicsView.fitInView(
                self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio
            )

        if self.colorbar is not None:
            self.update_colorbar(vmin_used, vmax_used)

    # ------------------------------------------------------------------
    # Colormap / Color scale
    # ------------------------------------------------------------------
    def set_colormap(self, name: str):
        """Set current colormap and recalculate vmin and vmax."""
        self.colormap = name
        if self.pps is not None:
            self.display_slice(self.current_slice)

    def set_colorbar_scale_mode(self, mode: str):
        """Set colorscale mode and recalculate vmin and vmax."""
        self.color_scale_mode = mode
        self._recalculate_color_scale()

        if self.pps is not None:
            self.display_slice(self.current_slice)

    def set_colorbar_range(self, vmin: float, vmax: float):
        """Set up custom colorbar range."""
        self.custom_vmin = float(vmin)
        self.custom_vmax = float(vmax)

        if self.color_scale_mode == self.MODE_CUSTOM:
            self._recalculate_color_scale()
            if self.pps is not None:
                self.display_slice(self.current_slice)

    def get_reference_ranges(self) -> dict:
        """Compute and return reference color ranges."""
        if self.pps is None:
            return {"std_min": None, "std_max": None, "full_min": None, "full_max": None}

        stats = self.pps.statistics(mask_on=False)

        full_min = stats['min']
        full_max = stats['max']

        mean = stats['mean']
        std = stats['std']
        abs_max = max(abs(mean - 4 * std), abs(mean + 4 * std))
        std_min = -abs_max
        std_max = abs_max

        return {
            "std_min": std_min,
            "std_max": std_max,
            "full_min": full_min,
            "full_max": full_max,
        }

    def _recalculate_color_scale(self):
        """Recalculate vmin/vmax based on the current color scale mode."""
        if self.pps is None:
            return

        ref = self.get_reference_ranges()

        if self.color_scale_mode == self.MODE_FULL_RANGE:
            self.vmin = ref["full_min"]
            self.vmax = ref["full_max"]

        elif self.color_scale_mode == self.MODE_CUSTOM:
            if self.custom_vmin is not None and self.custom_vmax is not None:
                self.vmin = self.custom_vmin
                self.vmax = self.custom_vmax
            else:
                self.vmin = ref["std_min"]
                self.vmax = ref["std_max"]

        else:  # MODE_STD_DEV
            self.vmin = ref["std_min"]
            self.vmax = ref["std_max"]

    # ------------------------------------------------------------------
    # Colorbar
    # ------------------------------------------------------------------
    def update_colorbar(self, vmin=None, vmax=None):
        # ... unchanged ...
        if self.colorbar is None:
            return

        if vmin is None:
            vmin = self.vmin
        if vmax is None:
            vmax = self.vmax
        if vmin is None or vmax is None:
            return

        gradient = np.linspace(vmin, vmax, 256).reshape(1, -1)
        rgb_gradient, vmin_used, vmax_used = apply_colormap(
            gradient, vmin=vmin, vmax=vmax, cmap=self.colormap
        )
        rgb_gradient = rgb_gradient.reshape(1, 256, 3)

        if self.colorbar.figure.axes:
            ax = self.colorbar.figure.axes[0]
        else:
            ax = self.colorbar.figure.add_subplot(111)

        ax.clear()
        ax.imshow(
            rgb_gradient,
            aspect='auto',
            origin='lower',
            extent=[vmin_used, vmax_used, 0, 1],
        )

        ax.set_yticks([])

        ticks = [vmin_used]
        if vmin_used < 0 < vmax_used:
            ticks.append(0.0)
        ticks.append(vmax_used)

        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{t:.2g}" for t in ticks], fontsize=8)
        ax.tick_params(axis='x', labelsize=10, pad=4)

        ax.set_xlim(vmin_used, vmax_used)
        ax.set_ylim(0, 1)

        self.colorbar.figure.subplots_adjust(left=0.1, right=0.9, bottom=0.45, top=0.9)
        self.colorbar.draw_idle()