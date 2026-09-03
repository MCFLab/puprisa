# puprisa/viewmodels/pps_plot_view_model.py
"""Qt view model for pump-probe image display and colorbar.

Subscribes to StackManager / MaskManager / PlotManager events and
automatically renders the current slice.  Rendering uses the centralized
plot state from PlotManager; this class does not own or modify that state.
"""

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QGraphicsScene

import numpy as np

from puprisa.core.visualize import render_slice_rgb
from puprisa.model.mask_manager import MaskEvent, MaskManager
from puprisa.model.plot_manager import PlotEvent, PlotManager
from puprisa.model.processing_manager import ProcessingManager
from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.model.roi_manager import RoiManager
from puprisa.model.curve_manager import CurveManager
from puprisa.ui.widgets.mpl_canvas import MatplotlibFigureCanvas
from puprisa.ui.widgets.scrollable_graphics_view import ScrollableGraphicsView
from puprisa.utils.color_utils import apply_colormap
from puprisa.utils.curve_plot_utils import draw_roi_curves
from puprisa.utils.geometry_utils import shape_to_patch


class PPSPlotViewModel(QObject):
    """Render the current stack slice into a graphics scene and manage colorbar."""

    def __init__(
        self,
        stack_manager: StackManager,
        mask_manager: MaskManager,
        processing_manager: ProcessingManager,
        plot_manager: PlotManager,
        roi_manager: RoiManager,
        curve_manager: CurveManager,
        graphics_view: ScrollableGraphicsView,
        colorbar: MatplotlibFigureCanvas | None = None,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._stack_manager = stack_manager
        self._mask_manager = mask_manager
        self._processing_manager = processing_manager
        self._plot_manager = plot_manager
        self._roi_manager = roi_manager
        self._curve_manager = curve_manager
        self._graphics_view = graphics_view
        self._colorbar = colorbar

        self._scene = graphics_view.scene() or QGraphicsScene()
        self._graphics_view.setScene(self._scene)

        self._pixmap_item = None
        self._current_slice = 0
        self._last_pixmap_size = None

        # Model -> View
        self._stack_manager.add_listener(self._on_stack_event)
        self._mask_manager.add_listener(self._on_mask_event)
        self._processing_manager.add_listener(self._on_processing_event)

        if self._plot_manager is not None:
            self._plot_manager.add_listener(self._on_plot_event)

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
        self.display_slice(0)

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
            self.display_slice(self._current_slice)

    def _on_plot_event(self, event: PlotEvent) -> None:
        if self._current_pps() is not None:
            self.display_slice(self._current_slice)

    # ------------------------------------------------------------------
    # Public rendering API
    # ------------------------------------------------------------------
    def display_slice(self, index: int) -> None:
        pps = self._current_pps()
        if pps is None:
            return
        self._current_slice = max(0, min(index, len(pps.images) - 1))
        self._render_image()

    def fit_view(self) -> None:
        if self._pixmap_item is None:
            return

        # After each stack switch, make the scene's bounds exactly equal to
        # the current image; otherwise sceneRect only grows and never shrinks
        # automatically, causing small stacks to be offset to the left/up.
        image_rect = self._pixmap_item.sceneBoundingRect()
        self._scene.setSceneRect(image_rect)

        # Clear the pan/zoom left over from the previous image, then center
        # the current image.
        self._graphics_view.resetTransform()
        self._graphics_view.fitInView(
            image_rect,
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self._graphics_view.centerOn(image_rect.center())

    # ------------------------------------------------------------------
    # Internal rendering
    # ------------------------------------------------------------------
    def _render_image(self) -> None:
        pps = self._current_pps()
        if pps is None:
            return
        if self._plot_manager is not None:
            colormap = self._plot_manager.colormap
            vmin, vmax = self._plot_manager.vmin, self._plot_manager.vmax
        else:
            colormap = "pumpprobe"
            vmin, vmax = None, None

        rgb, vmin_used, vmax_used = render_slice_rgb(
            pps,
            slice_index=self._current_slice,
            colormap=colormap,
            vmin=vmin,
            vmax=vmax,
            mask_color=(200, 200, 200),
        )
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
            self._update_colorbar(vmin_used, vmax_used, colormap)

    def _update_colorbar(self, vmin_used: float, vmax_used: float, colormap: str) -> None:
        if self._colorbar is None:
            return

        gradient = np.linspace(vmin_used, vmax_used, 256).reshape(1, -1)
        rgb_gradient, vmin_used, vmax_used = apply_colormap(
            gradient, vmin=vmin_used, vmax=vmax_used, cmap=colormap
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

    def _clear(self) -> None:
        self._current_slice = 0
        if self._pixmap_item is not None:
            self._scene.removeItem(self._pixmap_item)
            self._pixmap_item = None

    # ------------------------------------------------------------------
    # Standalone view
    # ------------------------------------------------------------------
    def view_standalone(self, normalize: bool) -> None:
        """Open a standalone Matplotlib figure for the current view.

        Parameters
        ----------
        normalize : bool, optional
            Whether to normalize the ROI average curves in the right panel.
            The default is False.
        """
        from puprisa.core.visualize import plot_slice
        import matplotlib.pyplot as plt
        from matplotlib.colors import Normalize
        from matplotlib.cm import ScalarMappable
        
        pps = self._current_pps()
        if pps is None:
            return

        if self._plot_manager is not None:
            colormap = self._plot_manager.colormap
            vmin, vmax = self._plot_manager.vmin, self._plot_manager.vmax
            if vmin is None or vmax is None:
                ref = self._plot_manager.get_reference_ranges()
                vmin, vmax = ref["std_min"], ref["std_max"]
        else:
            colormap = "pumpprobe"
            vmin, vmax = None, None

        current_slice = self._current_slice
        fig, (ax_img, ax_curve) = plt.subplots(
            1, 2,
            figsize=(9, 4),
            gridspec_kw={'width_ratios': [1, 1]},
            layout='constrained'
        )

        # --------- 1. Image panel ---------
        # Stack slice image
        ax_img = plot_slice(
            pps,
            slice_index=current_slice,
            ax=ax_img,
            colormap=colormap,
            vmin=vmin,
            vmax=vmax,
            colorbar=False,
        )
        stack_item = self._stack_manager.get_current_item()
        ax_img.set_title(stack_item.name if stack_item else pps.filename)
        ax_img.axis('off')

        # ROI outlines
        if self._roi_manager is not None:
            for roi in self._roi_manager.get_scene_visible_rois():
                patch = shape_to_patch(
                    roi.shape,
                    roi.params,
                    fill=False,
                    edgecolor=roi.color,
                    linewidth=1.5,
                )
                if patch is not None:
                    ax_img.add_patch(patch)

        # Colorbar
        if vmin is not None and vmax is not None:
            norm = Normalize(vmin=vmin, vmax=vmax)
            sm = ScalarMappable(cmap=colormap, norm=norm)
            sm.set_array([])
            fig.colorbar(sm, ax=ax_img, fraction=0.046, pad=0.04)

        # --------- 2. ROI average curves panel ---------
        curves = []
        if self._curve_manager is not None:
            curves = self._curve_manager.compute_curves(
                space="pixel", normalize=normalize
            )
        axis_values = pps.get_axis_values()
        slice_x = None
        if 0 <= current_slice < len(axis_values):
            slice_x = axis_values[current_slice]
        xlabel = f"{pps.get_axis_label()} ({pps.get_axis_unit()})"
        ylabel = "Normalized signal (a.u.)" if normalize else "Average signal (a.u.)"
        title = "ROI Average Curves"

        draw_roi_curves(ax_curve, curves, xlabel=xlabel, ylabel=ylabel, title=title, current_slice_x=slice_x)

        fig.show()