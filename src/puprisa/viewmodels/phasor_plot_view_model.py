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
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsPathItem

import numpy as np
import matplotlib.colors as mcolors

from puprisa.model.entities import RoiItem
from puprisa.model.processing_manager import ProcessingManager
from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.model.roi_manager import RoiManager


class PhasorPlotViewModel(QObject):
    """Render phasor density overlays and the spatial projection."""

    DENSITY_SIZE = 512
    G_LIM = (-1.0, 1.0)
    S_LIM = (-1.0, 1.0)

    def __init__(self, stack_manager: StackManager, processing_manager: ProcessingManager, roi_manager: RoiManager, phasor_graphics_view, spatial_graphics_view, parent: QObject | None = None):
        super().__init__(parent)
        self._stack_manager = stack_manager
        self._processing_manager = processing_manager
        self._roi_manager = roi_manager
        self._phasor_view = phasor_graphics_view
        self._spatial_view = spatial_graphics_view

        # Scenes
        self.phasor_scene = QGraphicsScene()
        self._phasor_view.setScene(self.phasor_scene)
        self._phasor_view.setBackgroundBrush(Qt.GlobalColor.white)

        self.spatial_scene = QGraphicsScene()
        self._spatial_view.setScene(self.spatial_scene)

        # Density items
        self._density_items: list[QGraphicsItem] = []
        self._axis_items: list[QGraphicsItem] = []

        # Runtime frequency and phasor cache
        self.frequency = 0.25
        self._build_axes()
        self.fit_phasor_view()

        # Model -> View
        self._stack_manager.add_listener(self._on_stack_event)
        self._processing_manager.add_listener(self._on_processing_event)
        self._roi_manager.add_listener(self._on_roi_event)

    # ------------------------------------------------------------------
    # Model event handlers
    # ------------------------------------------------------------------
    def _on_stack_event(self, event: StackEvent) -> None:
        if event.event in ("added", "removed", "visibility_changed", "current_changed"):
            if event.event == "current_changed":
                self.refresh_spatial_view()
            self.refresh_density()

    def _on_processing_event(self, event) -> None:
        if event.event == "data_changed":
            # Invalidate phasor cache and re-render both views.
            self._invalidate_all_phasor_coords()
            self.refresh_density()
            self.refresh_spatial_view()

    def _on_roi_event(self, event) -> None:
        if event.roi is None or event.roi.space != "phasor":
            return
        current_item = self._stack_manager.get_current_item()
        if current_item is not None and event.roi.stack_id == current_item.id:
            self.refresh_spatial_view()

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
        """Render the spatial projection for the current stack."""
        self.spatial_scene.clear()

        current_item = self._stack_manager.get_current_item()
        if current_item is None:
            return

        pps = current_item.pps
        projection = pps.project(mask_on=False)
        projection = np.nan_to_num(projection, nan=0.0, posinf=0.0, neginf=0.0)

        h, w = projection.shape
        mask_2d = np.asarray(pps.mask, dtype=bool)

        valid_proj = projection[mask_2d] if np.any(mask_2d) else projection
        vmin = float(valid_proj.min())
        vmax = float(valid_proj.max())
        if vmax <= vmin:
            vmax = vmin + 1.0

        gray = np.clip((projection - vmin) / (vmax - vmin), 0.0, 1.0)
        gray_u8 = (gray * 255).astype(np.uint8)
        rgb = np.stack([gray_u8] * 3, axis=-1).astype(np.float64)

        # ROI overlay on phasor-space ROIs
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

        rgb[~mask_2d] = [200, 200, 200]
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        rgb = np.ascontiguousarray(rgb)

        qimage = QImage(rgb.data, w, h, w * 3, QImage.Format.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimage)
        self.spatial_scene.addPixmap(pixmap)
        self.fit_spatial_view()

    def fit_phasor_view(self) -> None:
        rect = self.phasor_scene.itemsBoundingRect()
        if rect.width() > 0 and rect.height() > 0:
            rect = rect.adjusted(-10, -5, 10, 5)
            self.phasor_scene.setSceneRect(rect)
            self._phasor_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def fit_spatial_view(self) -> None:
        rect = self.spatial_scene.itemsBoundingRect()
        if rect.width() > 0 and rect.height() > 0:
            self._spatial_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    # ------------------------------------------------------------------
    # Phasor coordinate cache
    # ------------------------------------------------------------------
    def _invalidate_all_phasor_coords(self) -> None:
        for stack_item in self._stack_manager.get_all_items():
            stack_item.phasor_coords = None

    def _get_or_compute_phasor_coords(self, stack_item):
        if stack_item.phasor_coords is None:
            stack_item.phasor_coords = stack_item.pps.phasor(freq=self.frequency, remove_zero=False)
        return stack_item.phasor_coords

    # ------------------------------------------------------------------
    # Density pixmap construction
    # ------------------------------------------------------------------
    def _make_density_pixmap(self, coords: np.ndarray, color_hex: str) -> QPixmap:
        size = self.DENSITY_SIZE
        g = coords[:, 0]
        s = coords[:, 1]

        bins_g = np.linspace(self.G_LIM[0], self.G_LIM[1], size + 1)
        bins_s = np.linspace(self.S_LIM[0], self.S_LIM[1], size + 1)
        hist, _, _ = np.histogram2d(g, s, bins=[bins_g, bins_s])
        hist = hist.T[::-1, :]  # image rows = s (top high), cols = g

        if np.any(hist > 0):
            hist = hist / hist.max()

        rgb_color = np.array(mcolors.to_rgb(color_hex)) * 255.0
        rgba = np.zeros((size, size, 4), dtype=np.uint8)
        rgba[..., 0] = int(rgb_color[0])
        rgba[..., 1] = int(rgb_color[1])
        rgba[..., 2] = int(rgb_color[2])
        rgba[..., 3] = (hist * 180).astype(np.uint8)

        rgba = np.ascontiguousarray(rgba)
        qimage = QImage(rgba.data, size, size, size * 4, QImage.Format.Format_RGBA8888).copy()
        return QPixmap.fromImage(qimage)

    # ------------------------------------------------------------------
    # Axes / universal semicircle
    # ------------------------------------------------------------------
    def _build_axes(self) -> None:
        size = self.DENSITY_SIZE
        left_margin = 40
        border_pen = QPen(QColor(0, 0, 0), 1)

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

        # Labels
        g_label = QGraphicsTextItem("g")
        g_label.setFont(QFont("Sans Serif", 8))
        g_label.setPos(size / 2 - 5, size + 2)
        self.phasor_scene.addItem(g_label)
        self._axis_items.append(g_label)

        s_label = QGraphicsTextItem("s")
        s_label.setFont(QFont("Sans Serif", 8))
        s_label.setPos(-left_margin - 12, size / 2 - 8)
        self.phasor_scene.addItem(s_label)
        self._axis_items.append(s_label)

        # Tick labels
        for g_val in [self.G_LIM[0], 0.0, self.G_LIM[1]]:
            x = (g_val - self.G_LIM[0]) / (self.G_LIM[1] - self.G_LIM[0]) * size
            text = QGraphicsTextItem(f"{g_val:.1f}")
            text.setFont(QFont("Sans Serif", 6))
            text.setPos(x - 8, size + 3)
            self.phasor_scene.addItem(text)
            self._axis_items.append(text)

        for s_val in [self.S_LIM[0], 0.0, self.S_LIM[1]]:
            y = (self.S_LIM[1] - s_val) / (self.S_LIM[1] - self.S_LIM[0]) * size
            text = QGraphicsTextItem(f"{s_val:.1f}")
            text.setFont(QFont("Sans Serif", 6))
            text.setPos(-left_margin + 4, y - 6)
            self.phasor_scene.addItem(text)
            self._axis_items.append(text)

        # Universal semicircle
        theta = np.linspace(0.0, np.pi, 400)
        g_upper = 0.5 * (1.0 + np.cos(theta))
        s_upper = 0.5 * np.sin(theta)
        g_lower = -g_upper
        s_lower = -0.5 * np.sin(theta)

        path = QPainterPath()
        first_pt = self._gs_to_scene_point(g_upper[0], s_upper[0])
        path.moveTo(first_pt)
        for i in range(1, len(theta)):
            path.lineTo(self._gs_to_scene_point(g_upper[i], s_upper[i]))
        for i in range(len(theta)):
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
        x = (g - self.G_LIM[0]) / (self.G_LIM[1] - self.G_LIM[0]) * self.DENSITY_SIZE
        y = (self.S_LIM[1] - s) / (self.S_LIM[1] - self.S_LIM[0]) * self.DENSITY_SIZE
        return QPointF(x, y)