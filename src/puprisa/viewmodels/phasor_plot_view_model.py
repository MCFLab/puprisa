# puprisa/viewmodels/phasor_plot_view_model.py
"""Qt view model for phasor density and spatial projection views.

Subscribes to StackManager / ProcessingManager events and automatically
refreshes when stacks change, data changes, or the phasor frequency is
updated.  The ViewModel owns the ``phasor_coords`` cache semantics for
all stacks.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Qt, QRectF, QPointF
from PySide6.QtGui import QImage, QPixmap, QPen, QColor, QPainter, QPainterPath, QFont
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsPathItem, QGraphicsView

import numpy as np
import matplotlib.colors as mcolors
from matplotlib.axes import Axes

from puprisa.core.visualize import render_phasor_rgba, render_projection_rgb, universal_semicircle
from puprisa.model.entities import RoiItem, StackItem
from puprisa.model.mask_manager import MaskEvent, MaskManager
from puprisa.model.plot_manager import PlotEvent, PlotManager
from puprisa.model.processing_manager import ProcessingEvent, ProcessingManager
from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.model.roi_manager import RoiEvent, RoiManager
from puprisa.model.curve_manager import CurveManager
from puprisa.utils.curve_plot_utils import draw_roi_curves
from puprisa.utils.geometry_utils import shape_to_patch


class PhasorPlotViewModel(QObject):
    """Render phasor density overlays and the spatial projection."""

    G_LIM = (-1.0, 1.0)
    S_LIM = (-1.0, 1.0)

    def __init__(
        self,
        stack_manager: StackManager, 
        processing_manager: ProcessingManager,
        plot_manager: PlotManager,
        roi_manager: RoiManager, 
        mask_manager: MaskManager, 
        curve_manager: CurveManager,
        phasor_graphics_view: QGraphicsView, 
        spatial_graphics_view: QGraphicsView, 
        parent: QObject | None = None
    ):

        super().__init__(parent)
        self._stack_manager = stack_manager
        self._processing_manager = processing_manager
        self._plot_manager = plot_manager
        self._roi_manager = roi_manager
        self._mask_manager = mask_manager
        self._curve_manager = curve_manager
        self._phasor_view = phasor_graphics_view
        self._spatial_view = spatial_graphics_view

        # Scenes
        self.phasor_scene = QGraphicsScene()
        self._phasor_view.setScene(self.phasor_scene)
        self._phasor_view.setBackgroundBrush(Qt.GlobalColor.white)

        self.spatial_scene = QGraphicsScene()
        self._spatial_view.setScene(self.spatial_scene)
        self._spatial_pixmap_item = None

        # Density items
        self._density_items: list[QGraphicsItem] = []
        self._axis_items: list[QGraphicsItem] = []

        # Runtime frequency and phasor cache
        self.frequency = 0.25
        self._density_size = self._plot_manager.phasor_bins
        self._build_axes()
        self.fit_phasor_view()

        # Model -> View
        self._stack_manager.add_listener(self._on_stack_event)
        self._processing_manager.add_listener(self._on_processing_event)
        self._roi_manager.add_listener(self._on_roi_event)
        self._mask_manager.add_listener(self._on_mask_event)
        self._plot_manager.add_listener(self._on_plot_event)

    # ------------------------------------------------------------------
    # Model event handlers
    # ------------------------------------------------------------------
    def _on_stack_event(self, event: StackEvent) -> None:
        if event.event in ("added", "removed", "visibility_changed"):
            self.refresh_density()
        if event.event == "current_changed":
            self.refresh_spatial_view()

    def _on_processing_event(self, event: ProcessingEvent) -> None:
        if event.event == "data_changed":
            # Invalidate phasor cache and re-render both views.
            self._invalidate_all_phasor_coords()
            self.refresh_density()
            self.refresh_spatial_view()

    def _on_roi_event(self, event: RoiEvent) -> None:
        if event.roi is None or event.roi.space != "phasor":
            return
        current_item = self._stack_manager.get_current_item()
        if current_item is not None and event.roi.stack_id == current_item.id:
            self.refresh_spatial_view()

    def _on_mask_event(self, event: MaskEvent) -> None:
        if event.event == "effective_changed" and event.stack_id:
            # Invalidate phasor cache for the affected stack and re-render both views.
            stack_item = self._stack_manager.get_item_by_id(event.stack_id)
            if stack_item is not None:
                stack_item.phasor_coords = None
            self.refresh_density()
            self.refresh_spatial_view()

    def _on_plot_event(self, event: PlotEvent) -> None:
        if event.event == "phasor_changed":
            if event.phasor_bins != self._density_size:
                self._density_size = event.phasor_bins
                self._build_axes()
            self.refresh_density()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_frequency(self, freq: float) -> None:
        """Update the phasor frequency and recompute all density overlays."""
        self.frequency = float(freq)
        # Frequency changed → all cached coords are stale.
        self._invalidate_all_phasor_coords()
        self.refresh_density()
        self.refresh_spatial_view()

    def refresh_density(self) -> None:
        """Rebuild density overlays for all visible stacks."""
        # Remove old density items, keep axes.
        for item in self._density_items:
            self.phasor_scene.removeItem(item)
        self._density_items.clear()

        for stack_item in self._stack_manager.get_all_items():
            if not stack_item.visible:
                continue

            coords = self._get_or_compute_phasor_coords(stack_item)
            if coords is None:
                continue

            pixmap = self._make_density_pixmap(coords, stack_item.color)
            density_item = self.phasor_scene.addPixmap(pixmap)
            density_item.setZValue(1)
            self._density_items.append(density_item)

        self._bring_axes_to_front()
        self.fit_phasor_view()

    def refresh_spatial_view(self) -> None:
        self.spatial_scene.clear()

        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return

        pps = current_item.pps
        rgb, _, _ = render_projection_rgb(pps)

        h, w = rgb.shape[:2]
        coords = self._get_or_compute_phasor_coords(current_item)
        if coords is not None:
            current_stack_id = current_item.id
            phasor_rois = [
                roi for roi in self._roi_manager.get_rois_for_stack(current_stack_id)
                if roi.space == "phasor" and roi.visible
            ]
            for roi in phasor_rois:
                keep_mask = self._roi_manager.build_roi_mask(roi)
                if keep_mask is None:
                    continue
                color = np.array(mcolors.to_rgb(roi.color)) * 255.0
                rgb[keep_mask, 0] = color[0]
                rgb[keep_mask, 1] = color[1]
                rgb[keep_mask, 2] = color[2]

        qimage = QImage(rgb.tobytes(), w, h, rgb.strides[0],
                        QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimage)
        self._spatial_pixmap_item = self.spatial_scene.addPixmap(pixmap)
        self.fit_spatial_view()

    def fit_phasor_view(self) -> None:
        rect = self.phasor_scene.itemsBoundingRect()
        if rect.width() > 0 and rect.height() > 0:
            rect = rect.adjusted(-5, -5, 5, 5)
            self.phasor_scene.setSceneRect(rect)
            self._phasor_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def fit_spatial_view(self) -> None:
        if getattr(self, "_spatial_pixmap_item", None) is None:
            return
        image_rect = self._spatial_pixmap_item.sceneBoundingRect()
        self.spatial_scene.setSceneRect(image_rect)
        self._spatial_view.resetTransform()
        self._spatial_view.fitInView(
            image_rect,
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self._spatial_view.centerOn(image_rect.center())

    # ------------------------------------------------------------------
    # Phasor coordinate cache
    # ------------------------------------------------------------------
    def _invalidate_all_phasor_coords(self) -> None:
        for stack_item in self._stack_manager.get_all_items():
            stack_item.phasor_coords = None

    def _get_or_compute_phasor_coords(self, stack_item: StackItem) -> np.ndarray | None:
        if stack_item is None or stack_item.pps.axis_type != "time":
            return None
        if stack_item.phasor_coords is None:
            stack_item.phasor_coords = stack_item.pps.phasor(freq=self.frequency, use_mask=True)
        return stack_item.phasor_coords

    # ------------------------------------------------------------------
    # Density pixmap construction
    # ------------------------------------------------------------------
    def _make_density_pixmap(self, coords: np.ndarray, color_hex: str) -> QPixmap:
        rgba = render_phasor_rgba(
            coords,
            color_hex,
            g_lim=self.G_LIM,
            s_lim=self.S_LIM,
            size=self._density_size,
            alpha_min=self._plot_manager.phasor_alpha_min,
            alpha_max=self._plot_manager.phasor_alpha_max
        )
        size = self._density_size
        qimage = QImage(rgba.tobytes(), size, size,
                        size * 4, QImage.Format_RGBA8888).copy()
        return QPixmap.fromImage(qimage)

    # ------------------------------------------------------------------
    # Axes / universal semicircle
    # ------------------------------------------------------------------
    def _build_axes(self) -> None:
        size = self._density_size
        border_pen = QPen(QColor(0, 0, 0), 1)

        for item in self._axis_items:
            self.phasor_scene.removeItem(item)
        self._axis_items.clear()

        # Border
        for line in [
            QGraphicsLineItem(0, 0, 0, size),
            QGraphicsLineItem(size, 0, size, size),
            QGraphicsLineItem(0, size, size, size),
            QGraphicsLineItem(0, 0, size, 0),
        ]:
            line.setPen(border_pen)
            self.phasor_scene.addItem(line)
            self._axis_items.append(line)

        # Universal semicircle
        g_upper, s_upper, g_lower, s_lower = universal_semicircle()

        path = QPainterPath()
        first_pt = self._gs_to_scene_point(g_upper[0], s_upper[0])
        path.moveTo(first_pt)
        for i in range(1, len(g_upper)):
            path.lineTo(self._gs_to_scene_point(g_upper[i], s_upper[i]))
        for i in range(len(g_lower)):
            path.lineTo(self._gs_to_scene_point(g_lower[i], s_lower[i]))
        path.closeSubpath()

        semi_item = QGraphicsPathItem(path)
        semi_pen = QPen(QColor(100, 100, 100), 1)
        semi_pen.setStyle(Qt.PenStyle.DashLine)
        semi_item.setPen(semi_pen)
        self.phasor_scene.addItem(semi_item)
        self._axis_items.append(semi_item)

        self._bring_axes_to_front()

    def _bring_axes_to_front(self) -> None:
        for item in self._axis_items:
            item.setZValue(5)

    def _gs_to_scene_point(self, g: float, s: float) -> QPointF:
        x = (g - self.G_LIM[0]) / (self.G_LIM[1] - self.G_LIM[0]) * self._density_size
        y = (self.S_LIM[1] - s) / (self.S_LIM[1] - self.S_LIM[0]) * self._density_size
        return QPointF(x, y)

    # ------------------------------------------------------------------
    # Standalone view
    # ------------------------------------------------------------------
    def view_phasor(self) -> None:
        """Open a standalone Matplotlib figure containing only the phasor plot."""
        import matplotlib.pyplot as plt

        fig, ax_phasor = plt.subplots(
            1, 1,
            figsize=(5, 5),
            layout="constrained",
        )

        self._draw_phasor_plot(ax_phasor, draw_roi=False)
        fig.show()


    def view_standalone(self, normalize: bool = False) -> None:
        """Open a standalone Matplotlib figure with phasor, spatial, and ROI curves.

        Layout
        ------
        Top-left:
            Phasor density plot.
        Top-right:
            Spatial projection view.
        Bottom:
            ROI average curves for phasor-space ROIs.

        Parameters
        ----------
        normalize : bool, optional
            Whether to normalize the ROI average curves. The default is False.
        """
        import matplotlib.pyplot as plt

        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return

        fig = plt.figure(figsize=(10, 8), layout="constrained")
        gs = fig.add_gridspec(
            2, 2,
            height_ratios=[1.0, 1.0],
            width_ratios=[1.0, 1.0],
        )

        ax_phasor = fig.add_subplot(gs[0, 0])
        ax_spatial = fig.add_subplot(gs[0, 1])
        ax_curve = fig.add_subplot(gs[1, :])

        self._draw_phasor_plot(ax_phasor, draw_roi=True)
        self._draw_spatial_projection(ax_spatial)
        self._draw_roi_curves(ax_curve, normalize=normalize)

        fig.show()

    def _draw_phasor_plot(self, ax: Axes, draw_roi: bool) -> None:
        """Draw visible-stack phasor density overlays into a Matplotlib axis."""
        frequency = self.frequency
        ax.set_xlabel("g")
        ax.set_ylabel("s")
        ax.set_xlim(self.G_LIM)
        ax.set_ylim(self.S_LIM)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, alpha=0.25)

        # Universal circle/semicircle guide.
        g_upper, s_upper, g_lower, s_lower = universal_semicircle()
        ax.plot(g_upper, s_upper, color="gray", linestyle="--", linewidth=1.0)
        ax.plot(g_lower, s_lower, color="gray", linestyle="--", linewidth=1.0)

        # Density overlays for all visible stacks.
        visible_stacks = []
        for stack_item in self._stack_manager.get_all_items():
            if not stack_item.visible:
                continue
            visible_stacks.append(stack_item)
            coords = self._get_or_compute_phasor_coords(stack_item)
            if coords is None or len(coords) == 0:
                continue
            self._draw_density_overlay(ax, coords, stack_item.color)

        # ROI outlines for current stack's phasor-space ROIs.
        current_item = self._stack_manager.get_current_item()
        if current_item is not None:
            rois = [
                roi for roi in self._roi_manager.get_rois_for_stack(current_item.id)
                if roi.space == "phasor" and roi.visible
            ]

            for roi in rois:
                patch = shape_to_patch(
                    roi.shape,
                    roi.params,
                    fill=False,
                    edgecolor=roi.color,
                    linewidth=1.5,
                )
                if patch is not None and draw_roi:
                    ax.add_patch(patch)
        
        frequency_unit = current_item.pps.get_phasor_unit() if current_item is not None else "THz"
        ax.set_title(f"Phasor Plot @ {frequency:.2f} {frequency_unit}")
        
        if visible_stacks:
            from matplotlib.patches import Patch
            handles = [
                Patch(color=stack_item.color, label=stack_item.name or stack_item.id)
                for stack_item in visible_stacks
            ]
            ax.legend(handles=handles, fontsize=8, loc="best", framealpha=0.9)

    def _draw_spatial_projection(self, ax: Axes) -> None:
        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return

        pps = current_item.pps
        rgb = render_projection_rgb(pps)[0]

        coords = self._get_or_compute_phasor_coords(current_item)
        if coords is not None:
            phasor_rois = [
                roi for roi in self._roi_manager.get_rois_for_stack(current_item.id)
                if roi.space == "phasor" and roi.visible
            ]
            for roi in phasor_rois:
                keep_mask = self._roi_manager.build_roi_mask(roi)
                if keep_mask is None:
                    continue
                color = np.array(mcolors.to_rgb(roi.color)) * 255.0
                rgb[keep_mask, 0] = color[0]
                rgb[keep_mask, 1] = color[1]
                rgb[keep_mask, 2] = color[2]

        ax.imshow(rgb)
        ax.set_title("Spatial View")
        ax.axis("off")

    def _draw_density_overlay(self, ax, coords: np.ndarray, color_hex: str) -> None:
        """Draw a single phasor density overlay into a Matplotlib axis."""
        rgba = render_phasor_rgba(
            coords,
            color_hex,
            g_lim=self.G_LIM,
            s_lim=self.S_LIM,
            size=self._density_size,
            alpha_min=self._plot_manager.phasor_alpha_min,
            alpha_max=self._plot_manager.phasor_alpha_max
        )
        ax.imshow(
            rgba,
            extent=[self.G_LIM[0], self.G_LIM[1], self.S_LIM[0], self.S_LIM[1]],
            origin="upper",
            interpolation="nearest",
            aspect="equal",
        )


    def _draw_roi_curves(self, ax, normalize: bool = False) -> None:
        """Draw ROI average curves for phasor-space ROIs."""
        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return
        pps = current_item.pps
        curves = []
        if self._curve_manager is not None:
            curves = self._curve_manager.compute_curves(space="phasor", normalize=normalize)
        xlabel = f"{pps.get_axis_label()} ({pps.get_axis_unit()})"
        ylabel = "Normalized signal (a.u.)" if normalize else "Average signal (a.u.)"
        title = "ROI Average Curves"
        draw_roi_curves(ax, curves, xlabel=xlabel, ylabel=ylabel, title=title)


    def _single_color_cmap(self, color_hex: str):
        """Build a transparent-to-color colormap for phasor density plotting."""
        from matplotlib.colors import LinearSegmentedColormap

        rgb = mcolors.to_rgb(color_hex)
        return LinearSegmentedColormap.from_list(
            "phasor_density",
            [
                (rgb[0], rgb[1], rgb[2], 0.0),
                (rgb[0], rgb[1], rgb[2], 0.75),
            ],
        )