"""Plot controller for the Phasor analysis window."""
from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING, Optional
from PySide6.QtCore import QObject, Qt, QRectF, QPointF
from PySide6.QtGui import (
    QImage, QPixmap, QPen, QColor, QPainter, QPainterPath, QFont,
)
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsLineItem,
    QGraphicsTextItem, QGraphicsPathItem,
)
import matplotlib.colors as mcolors
from puprisa.core.pps import PPS
from puprisa.utils.geometry_utils import shape_to_mask
from puprisa.ui.widgets.mpl_canvas import MatplotlibFigureCanvas
if TYPE_CHECKING:
    from puprisa.controllers.phasor_curve_controller import PhasorCurveController

class PhasorPlotController(QObject):
    """Render phasor density, signal curves, and spatial false-color views."""
    DENSITY_SIZE = 512
    def __init__(
        self,
        phasorGraphicsView: QGraphicsView,
        ppsGraphicsView: QGraphicsView,
        plotCanvas: MatplotlibFigureCanvas,
        curve_controller: Optional[PhasorCurveController] = None,
    ):
        super().__init__()
        self.phasorGraphicsView = phasorGraphicsView
        self.ppsGraphicsView = ppsGraphicsView
        self.plotCanvas = plotCanvas
        self.curve_controller = curve_controller
        if self.plotCanvas is not None:
            self.plotCanvas.figure.set_constrained_layout(True)
        # Scenes
        self.phasorScene = QGraphicsScene()
        self.phasorGraphicsView.setScene(self.phasorScene)
        self.phasorGraphicsView.setBackgroundBrush(Qt.GlobalColor.white)
        self.ppsScene = QGraphicsScene()
        self.ppsGraphicsView.setScene(self.ppsScene)
        # Fixed phasor ranges
        self.g_lim = (-1.0, 1.0)
        self.s_lim = (-1.0, 1.0)
        self.phasor_pixmap_rect = QRectF(0, 0, self.DENSITY_SIZE, self.DENSITY_SIZE)
        self.densityMaps: list = []
        self.phasorAxes: list = []
        self._build_axes()
        self.fit_phasor_view()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def render_density(self, stack_items: list[dict]):
        """Render 2D density overlays for all visible stack items.

        Rebuilds the phasor-plot density display from scratch on every call:
        any previously added density pixmaps are removed first, then one
        density pixmap is generated and added for each visible stack entry
        that has a precomputed ``phasor_coords`` array.

        Parameters
        ----------
        stack_items : list of dict
            The stack items managed by ``PhasorStackController``. Each
            entry must expose at least the following keys:

            - ``visible`` : bool
                Whether the entry should be rendered. Hidden items are
                skipped.
            - ``color`` : QColor or str
                Base color used to tint the density pixmap.
            - ``phasor_coords`` : array-like of (g, s) tuples or None
                Precomputed phasor coordinates used to build the density
                map. items without coordinates (``None``) are skipped.

        Notes
        -----
        Only density items are removed/replaced; ROI items and the phasor
        axes are left untouched. Density pixmaps are placed on ``ZValue`` 1
        so they sit above the axes background, and the axes are brought to
        the front afterwards to keep them visible on top.
        """
        # Remove only density items; ROI items and axes stay untouched.
        for densityMap in self.densityMaps:
            self.phasorScene.removeItem(densityMap)
        self.densityMaps.clear()

        for stack in stack_items:
            if not stack["visible"]:
                continue
            coords = stack.get("phasor_coords")
            if coords is None:
                continue
            pixmap = self._make_density_pixmap(coords, stack["color"])
            densityMap = self.phasorScene.addPixmap(pixmap)
            densityMap.setZValue(1)
            self.densityMaps.append(densityMap)

        self._bring_axes_to_front()

    def update_signal_plot(self):
        """Redraw ROI signal curves using the curve controller.
        The curves are computed by :class:`PhasorCurveController` and
        drawn on the embedded matplotlib canvas.
        """
        if self.plotCanvas is None or self.curve_controller is None:
            return
        curves = self.curve_controller.compute_curves()
        fig = self.plotCanvas.figure
        ax = fig.axes[0] if fig.axes else fig.add_subplot(111)
        ax.clear()
        ax.set_xlabel("Time delay (ps)")
        if self.curve_controller.normalize_curves:
            ax.set_ylabel("Normalized signal")
        else:
            ax.set_ylabel("Average signal (arb. u.)")
        ax.grid(True, alpha=0.3)
        for x, y, label, color in curves:
            ax.plot(x, y, color=color, label=label)
        if curves:
            ax.legend(fontsize=8, loc="best")
        ax.relim()
        ax.autoscale_view(tight=True)
        self.plotCanvas.draw_idle()

    def update_spatial_view(self, stack_item: dict | None, rois: list[dict]):
        """Render the false-color spatial projection for the given stack item.

        Clears the spatial view, then, if a stack item is provided, computes
        its phasor projection, normalizes it to the ``[0, 1]`` range, and
        renders it as a grayscale image on the canvas. Optionally, the
        phasor coordinates of the stack item are used to draw colored
        overlays for each visible ROI whose ``stack_id`` matches the current
        stack.

        Parameters
        ----------
        stack_item : dict or None
            The currently selected stack item. Its ``"pps"`` key holds the
            phasor plot state and ``"phasor_coords"`` holds the per-pixel
            phasor coordinates used for ROI overlays. Pass ``None`` to clear
            the spatial view.
        rois : list of dict
            All ROI dicts. Only those whose ``stack_id`` matches the current
            stack item and whose visibility flag is set are used for overlay;
            each is drawn using its ``color`` and ``label``.

        Returns
        -------
        None
            The method updates the canvas in place; it returns nothing.
        """
        self.ppsScene.clear()
        if stack_item is None:
            return

        pps = stack_item["pps"]
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

        coords = stack_item.get("phasor_coords")
        if coords is not None:
            g = coords[:, 0]
            s = coords[:, 1]

            # Only colour ROIs belonging to the currently selected stack.
            for roi in rois:
                if roi.get("stack_id") != stack_item["id"] or not roi.get("visible", True):
                    continue

                mask_1d = shape_to_mask(roi["shape"], roi["params"], g, s)
                if mask_1d is None:
                    continue

                mask_roi = mask_1d.reshape(h, w)
                color = np.array(mcolors.to_rgb(roi["color"])) * 255.0
                rgb[mask_roi, 0] = color[0]
                rgb[mask_roi, 1] = color[1]
                rgb[mask_roi, 2] = color[2]

        rgb[~mask_2d] = [200, 200, 200]
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        rgb = np.ascontiguousarray(rgb)

        qimage = QImage(rgb.data, w, h, w * 3, QImage.Format.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimage)
        self.ppsScene.addPixmap(pixmap)
        self.fit_spatial_view()

    def render_scene_to_image(self, scene: QGraphicsScene, size=None) -> QImage:
        """Render a QGraphicsScene to a QImage for saving/exporting.
        Parameters
        ----------
        scene : QGraphicsScene
            Scene to render.
        size : tuple or None, optional
            Output size (width, height). If None, the scene's
            ``itemsBoundingRect`` is used.
        Returns
        -------
        QImage
            The rendered image in RGB32 format.
        """
        if size is None:
            rect = scene.itemsBoundingRect()
            if rect.width() <= 0 or rect.height() <= 0:
                return QImage(1, 1, QImage.Format.Format_RGB32)
            size = (int(rect.width()), int(rect.height()))
        else:
            size = (int(size[0]), int(size[1]))
        image = QImage(size[0], size[1], QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        scene.render(painter, QRectF(image.rect()), scene.itemsBoundingRect())
        painter.end()
        return image
    def get_phasor_scene_image(self) -> QImage:
        """Return a rendered image of the phasor scene."""
        return self.render_scene_to_image(self.phasorScene)
    def get_spatial_scene_image(self) -> QImage:
        """Return a rendered image of the spatial projection scene."""
        return self.render_scene_to_image(self.ppsScene)

    # ------------------------------------------------------------------
    # Coordinate conversion: scene <-> (g,s)
    # ------------------------------------------------------------------
    def scene_point_to_gs(self, pt: QPointF) -> tuple[float, float]:
        """Convert a scene point to (g, s) coordinates."""
        g = self.g_lim[0] + (pt.x() / self.DENSITY_SIZE) * (
            self.g_lim[1] - self.g_lim[0]
        )
        s = self.s_lim[1] - (pt.y() / self.DENSITY_SIZE) * (
            self.s_lim[1] - self.s_lim[0]
        )
        return g, s

    def gs_to_scene_point(self, g: float, s: float) -> QPointF:
        """Convert (g, s) coordinates to a scene point."""
        x = (g - self.g_lim[0]) / (self.g_lim[1] - self.g_lim[0]) * self.DENSITY_SIZE
        y = (self.s_lim[1] - s) / (self.s_lim[1] - self.s_lim[0]) * self.DENSITY_SIZE
        return QPointF(x, y)

    # ------------------------------------------------------------------
    # Internal rendering helpers
    # ------------------------------------------------------------------
    def _make_density_pixmap(self, coords: np.ndarray, color_hex: str) -> QPixmap:
        """
        Build a transparent density overlay pixmap from (g, s) coordinates.

        The coordinate pairs are binned onto a ``DENSITY_SIZE`` x
        ``DENSITY_SIZE`` histogram spanning the current ``g_lim`` and
        ``s_lim`` ranges, normalised so the densest cell maps to full
        opacity, and rasterised in the given color over a transparent
        background.  This produces a heat-map style overlay that can be
        composited on top of the phasor plot.

        Parameters
        ----------
        coords : np.ndarray
            Array of shape ``(N, 2)`` holding the (g, s) coordinates of
            the points to display, where ``coords[:, 0]`` is the g value
            and ``coords[:, 1]`` is the s value.
        color_hex : str
            Hex color string (e.g. ``"#ff0000"``) used to tint the
            density overlay; per-cell opacity is modulated by the
            normalised bin count.

        Returns
        -------
        QPixmap
            A ``DENSITY_SIZE`` x ``DENSITY_SIZE`` pixmap with
            transparent background and the density overlay drawn in
            ``color_hex``.  The returned pixmap is a copy and is safe
            to use after the underlying buffer is released.
        """
        size = self.DENSITY_SIZE
        g = coords[:, 0]
        s = coords[:, 1]

        bins_g = np.linspace(self.g_lim[0], self.g_lim[1], size + 1)
        bins_s = np.linspace(self.s_lim[0], self.s_lim[1], size + 1)
        hist, _, _ = np.histogram2d(g, s, bins=[bins_g, bins_s])
        hist = hist.T[::-1, :]  # image rows = s (top high), cols = g

        if np.any(hist > 0):
            hist = hist / hist.max()

        rgb_color = np.array(mcolors.to_rgb(color_hex)) * 255.0
        rgba = np.zeros((size, size, 4), dtype=np.uint8)
        rgba[..., 0] = int(rgb_color[0])
        rgba[..., 1] = int(rgb_color[1])
        rgba[..., 2] = int(rgb_color[2])
        rgba[..., 3] = (hist * 180).astype(np.uint8)  # max alpha 180

        rgba = np.ascontiguousarray(rgba)
        qimage = QImage(
            rgba.data, size, size, size * 4, QImage.Format.Format_RGBA8888
        ).copy()
        return QPixmap.fromImage(qimage)

    def _build_axes(self):
        """Draw coordinate axes, tick labels, and the universal semicircle."""
        size = self.DENSITY_SIZE
        left_margin = 40

        border_pen = QPen(QColor(0, 0, 0), 1)

        # Axis lines
        left_axis = QGraphicsLineItem(0, 0, 0, size)
        left_axis.setPen(border_pen)
        self.phasorScene.addItem(left_axis)
        self.phasorAxes.append(left_axis)

        right_axis = QGraphicsLineItem(size, 0, size, size)
        right_axis.setPen(border_pen)
        self.phasorScene.addItem(right_axis)
        self.phasorAxes.append(right_axis)

        bottom_axis = QGraphicsLineItem(0, size, size, size)
        bottom_axis.setPen(border_pen)
        self.phasorScene.addItem(bottom_axis)
        self.phasorAxes.append(bottom_axis)

        top_axis = QGraphicsLineItem(0, 0, size, 0)
        top_axis.setPen(border_pen)
        self.phasorScene.addItem(top_axis)
        self.phasorAxes.append(top_axis)

        # Axis labels
        g_label = QGraphicsTextItem("g")
        g_label.setFont(QFont("Sans Serif", 8))
        g_label.setPos(size / 2 - 5, size + 2)
        self.phasorScene.addItem(g_label)
        self.phasorAxes.append(g_label)

        s_label = QGraphicsTextItem("s")
        s_label.setFont(QFont("Sans Serif", 8))
        s_label.setPos(-left_margin - 12, size / 2 - 8)
        self.phasorScene.addItem(s_label)
        self.phasorAxes.append(s_label)

        # Tick labels
        for g_val in [self.g_lim[0], 0.0, self.g_lim[1]]:
            x = (g_val - self.g_lim[0]) / (self.g_lim[1] - self.g_lim[0]) * size
            text = QGraphicsTextItem(f"{g_val:.1f}")
            text.setFont(QFont("Sans Serif", 6))
            text.setPos(x - 8, size + 3)
            self.phasorScene.addItem(text)
            self.phasorAxes.append(text)

        for s_val in [self.s_lim[0], 0.0, self.s_lim[1]]:
            y = (self.s_lim[1] - s_val) / (self.s_lim[1] - self.s_lim[0]) * size
            text = QGraphicsTextItem(f"{s_val:.1f}")
            text.setFont(QFont("Sans Serif", 6))
            text.setPos(-left_margin + 4, y - 6)
            self.phasorScene.addItem(text)
            self.phasorAxes.append(text)

        # Universal semicircle (upper and mirrored lower half)
        theta = np.linspace(0.0, np.pi, 400)
        g_upper = 0.5 * (1.0 + np.cos(theta))
        s_upper = 0.5 * np.sin(theta)
        g_lower = -g_upper
        s_lower = -0.5 * np.sin(theta)

        path = QPainterPath()
        first_pt = self.gs_to_scene_point(g_upper[0], s_upper[0])
        path.moveTo(first_pt)
        for i in range(1, len(theta)):
            pt = self.gs_to_scene_point(g_upper[i], s_upper[i])
            path.lineTo(pt)
        for i in range(len(theta)):
            pt = self.gs_to_scene_point(g_lower[i], s_lower[i])
            path.lineTo(pt)
        path.closeSubpath()

        semi_item = QGraphicsPathItem(path)
        semi_pen = QPen(QColor(100, 100, 100), 1)
        semi_pen.setStyle(Qt.PenStyle.DashLine)
        semi_item.setPen(semi_pen)
        self.phasorScene.addItem(semi_item)
        self.phasorAxes.append(semi_item)

        self._bring_axes_to_front()

    def _bring_axes_to_front(self):
        """Ensure axes are above density items but below ROI items."""
        for item in self.phasorAxes:
            item.setZValue(5)

    def fit_phasor_view(self):
        """Fit the phasor scene to the viewport."""
        rect = self.phasorScene.itemsBoundingRect()
        if rect.width() <= 0 or rect.height() <= 0:
            return
        rect = rect.adjusted(-10, -5, 10, 5)
        self.phasorScene.setSceneRect(rect)
        self.phasorGraphicsView.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def fit_spatial_view(self):
        """Fit the spatial projection to the viewport."""
        rect = self.ppsScene.itemsBoundingRect()
        if rect.width() > 0 and rect.height() > 0:
            self.ppsGraphicsView.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)