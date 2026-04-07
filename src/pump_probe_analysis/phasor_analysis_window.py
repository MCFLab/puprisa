#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phasor_analysis_window.py

Phasor Analysis window for PUPRISA.
Plots pixels in phasor (g,s) space with ROIs; average signal vs time per ROI;
grayscale spatial image with time slider and ROI-colored overlay.

Spatial projection uses the same row order as ``PPS`` storage and the main
window (row 0 at top); ROI overlays use the same indexing.
"""

import json
from datetime import datetime
from pathlib import Path
import numpy as np
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QSplitter, QWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsLineItem, QGraphicsTextItem,
    QDoubleSpinBox, QComboBox, QColorDialog, QInputDialog, QLineEdit,
    QMessageBox, QFileDialog, QMenuBar, QMenu,
)
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer
from PySide6.QtGui import QImage, QPixmap, QPen, QBrush, QColor, QPainter, QFont, QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Optional: get PPS from parent (channel view)
# No import from puprisa_channel_view to avoid circular import.


def phasor_shape_to_mask(shape_type, params, g_array, s_array):
    """
    Return a boolean mask over phasor points (same length as g_array, s_array).
    True where (g,s) is inside the shape. Params are in (g,s) space.
    shape_type: rectangle, square, circle, ellipse.
    """
    g = np.asarray(g_array, dtype=np.float64)
    s = np.asarray(s_array, dtype=np.float64)
    if g.shape != s.shape or g.size != s.size:
        return None
    g = g.ravel()
    s = s.ravel()

    if shape_type == "rectangle":
        x = params["x"]
        y = params["y"]
        w = params["width"]
        h = params["height"]
        mask = (g >= x) & (g < x + w) & (s >= y) & (s < y + h)
        return mask
    if shape_type == "square":
        cx = params["center_g"]
        cy = params["center_s"]
        sz = params["size"]
        half = sz / 2.0
        mask = (g >= cx - half) & (g < cx + half) & (s >= cy - half) & (s < cy + half)
        return mask
    if shape_type == "circle":
        cg = params["center_g"]
        cs = params["center_s"]
        r = params["radius"]
        mask = (g - cg) ** 2 + (s - cs) ** 2 <= r * r
        return mask
    if shape_type == "ellipse":
        cg = params["center_g"]
        cs = params["center_s"]
        rg = float(params["radius_g"])
        rs = float(params["radius_s"])
        angle_deg = params.get("angle_deg", 0.0)
        angle_rad = np.deg2rad(angle_deg)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        dg = g - cg
        ds = s - cs
        gr = (dg * cos_a + ds * sin_a) / (rg + 1e-10)
        sr = (-dg * sin_a + ds * cos_a) / (rs + 1e-10)
        mask = (gr * gr + sr * sr) <= 1.0
        return mask
    return None


def _matplotlib_color_to_qt(color_spec):
    """Convert matplotlib color to QColor."""
    if isinstance(color_spec, QColor):
        return color_spec
    if isinstance(color_spec, str) and color_spec.startswith('#'):
        return QColor(color_spec)
    try:
        hex_color = mcolors.to_hex(color_spec)
        return QColor(hex_color)
    except (ValueError, TypeError):
        return QColor('#1f77b4')


# Default ROI colors (matplotlib palette)
PHASOR_ROI_COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']


def _phasor_to_json_serializable_params(params):
    """Convert params dict to JSON-serializable (no numpy scalar types)."""
    out = {}
    for k, v in (params or {}).items():
        if isinstance(v, (np.floating, np.integer)):
            out[k] = float(v)
        else:
            out[k] = v
    return out


# Base font size for phasor axis labels and tick labels
PHASOR_AXIS_FONT_SIZE = 8


class PhasorDraggableROI(QGraphicsRectItem):
    """Draggable ROI for phasor (g,s) plot; same interaction as channel view ROIs."""
    SHAPE_TYPE = "rectangle"

    def __init__(self, rect, parent=None, color=None, shape_type=None):
        super().__init__(rect, parent)
        self._shape_type = shape_type if shape_type is not None else self.SHAPE_TYPE
        self._roi_color = QColor(255, 0, 0) if color is None else _matplotlib_color_to_qt(color)
        self.setPen(QPen(self._roi_color, 2))
        self.setBrush(QBrush(QColor(self._roi_color.red(), self._roi_color.green(), self._roi_color.blue(), 50)))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self._resizing = False
        self._resizeHandle = None
        self._roiChangedCallback = None

    def setRoiChangedCallback(self, callback):
        self._roiChangedCallback = callback

    def getShapeType(self):
        return self._shape_type

    def getSceneRect(self):
        return self.rect().translated(self.pos())

    def paint(self, painter, option, widget=None):
        r = self.rect()
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        if self._shape_type in ("circle", "ellipse"):
            painter.drawEllipse(r)
            dotted_pen = QPen(self._roi_color, 1)
            dotted_pen.setStyle(Qt.PenStyle.DotLine)
            painter.setPen(dotted_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(r)
        else:
            painter.drawRect(r)

    def _notifyChanged(self):
        if self._roiChangedCallback:
            self._roiChangedCallback()

    def itemChange(self, change, value):
        result = super().itemChange(change, value)
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionHasChanged:
            self._notifyChanged()
        return result

    def setRect(self, rect):
        super().setRect(rect)
        self._notifyChanged()

    def mousePressEvent(self, event):
        rect = self.rect()
        pos = event.pos()
        handle_size = 10
        self._resizing = False
        self._resizeHandle = None
        if abs(pos.x() - rect.left()) < handle_size and abs(pos.y() - rect.top()) < handle_size:
            self._resizing, self._resizeHandle = True, 'top-left'
        elif abs(pos.x() - rect.right()) < handle_size and abs(pos.y() - rect.top()) < handle_size:
            self._resizing, self._resizeHandle = True, 'top-right'
        elif abs(pos.x() - rect.left()) < handle_size and abs(pos.y() - rect.bottom()) < handle_size:
            self._resizing, self._resizeHandle = True, 'bottom-left'
        elif abs(pos.x() - rect.right()) < handle_size and abs(pos.y() - rect.bottom()) < handle_size:
            self._resizing, self._resizeHandle = True, 'bottom-right'
        elif abs(pos.x() - rect.left()) < handle_size:
            self._resizing, self._resizeHandle = True, 'left'
        elif abs(pos.x() - rect.right()) < handle_size:
            self._resizing, self._resizeHandle = True, 'right'
        elif abs(pos.y() - rect.top()) < handle_size:
            self._resizing, self._resizeHandle = True, 'top'
        elif abs(pos.y() - rect.bottom()) < handle_size:
            self._resizing, self._resizeHandle = True, 'bottom'
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._resizeHandle:
            rect = self.rect()
            pos = event.pos()
            if self._resizeHandle == 'top-left':
                new_rect = QRectF(pos.x(), pos.y(), rect.right() - pos.x(), rect.bottom() - pos.y())
            elif self._resizeHandle == 'top-right':
                new_rect = QRectF(rect.left(), pos.y(), pos.x() - rect.left(), rect.bottom() - pos.y())
            elif self._resizeHandle == 'bottom-left':
                new_rect = QRectF(pos.x(), rect.top(), rect.right() - pos.x(), pos.y() - rect.top())
            elif self._resizeHandle == 'bottom-right':
                new_rect = QRectF(rect.left(), rect.top(), pos.x() - rect.left(), pos.y() - rect.top())
            elif self._resizeHandle == 'left':
                new_rect = QRectF(pos.x(), rect.top(), rect.right() - pos.x(), rect.height())
            elif self._resizeHandle == 'right':
                new_rect = QRectF(rect.left(), rect.top(), pos.x() - rect.left(), rect.height())
            elif self._resizeHandle == 'top':
                new_rect = QRectF(rect.left(), pos.y(), rect.width(), rect.bottom() - pos.y())
            elif self._resizeHandle == 'bottom':
                new_rect = QRectF(rect.left(), rect.top(), rect.width(), pos.y() - rect.top())
            else:
                new_rect = rect
            if self._shape_type in ("circle", "square"):
                s = min(new_rect.width(), new_rect.height())
                if s > 5:
                    scene_center = self.pos() + self.rect().center()
                    self.setRect(QRectF(0, 0, s, s))
                    self.setPos(scene_center.x() - s / 2, scene_center.y() - s / 2)
                    return
            if new_rect.width() > 5 and new_rect.height() > 5:
                self.setRect(new_rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resizeHandle = None
        super().mouseReleaseEvent(event)
        self._notifyChanged()


class PhasorAnalysisWindow(QDialog):
    """Phasor Analysis: (g,s) plot with ROIs, signal vs time, spatial image with ROI overlay."""

    def __init__(self, parent=None, apply_effective_mask=False):
        super().__init__(parent)
        self.setWindowTitle("Phasor Analysis")
        self.setModal(False)
        self.setMinimumSize(1200, 700)
        self.resize(1200, 750)

        # Resolve PPS from parent (channel view has .pps)
        self.pps = getattr(parent, "pps", None)
        # Whether to respect the current effective mask from the channel view
        self._apply_effective_mask = bool(apply_effective_mask)
        self._effective_mask_1d = None
        self._phasor_coor = None   # (n_pixels, 2) g,s
        self._roiColorIndex = 0
        self.currentSlice = 0
        self.nSlices = 0
        self.header = getattr(parent, "header", {})

        # Phasor ROIs: list of {id, label, shape_type, params (g,s), color, rect_item}
        self.phasorRoiItems = []
        self._phasorRoiCounter = 0
        self._phasor_roi_autoload_done = False
        self.phasorSceneRect = None
        # Phasor axis limits and pixmap rect for scene ↔ (g,s) mapping
        self.phasorGLim = None
        self.phasorSLim = None
        self.phasorPixmapRect = None

        # Debounce
        self._roiUpdateTimer = QTimer()
        self._roiUpdateTimer.setSingleShot(True)
        self._roiUpdateTimer.timeout.connect(self._refreshFromPhasorRois)

        if self.pps is None:
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("No PPS data available. Open a channel view with a loaded stack first."))
            return

        # Cache the current effective mask (flattened) if requested
        if self._apply_effective_mask:
            try:
                mask2d = np.asarray(self.pps.mask, dtype=bool)
                self._effective_mask_1d = mask2d.ravel()
            except Exception:
                self._effective_mask_1d = None

        self.nSlices = len(self.pps.images)
        self.currentSlice = max(0, min(self.currentSlice, self.nSlices - 1))
        self._computePhasorData()
        self._buildUI()
        # Autoload default phasor ROI JSON once UI and phasor scene exist (after mask prompt / init)
        QTimer.singleShot(0, self._tryAutoloadPhasorRoisJson)

    def _getFreq(self):
        return self.freqSpin.value()

    def _computePhasorData(self):
        """Recompute phasor coordinates; always remove_zero=False so row index matches pixels."""
        freq = self._getFreq() if hasattr(self, "freqSpin") else 0.25
        self._phasor_coor = self.pps.phasor(freq=freq, remove_zero=False)
        # _phasor_coor shape (n_pixels, 2); row i = pixel i in row-major
        return self._phasor_coor

    def _buildUI(self):
        layout = QVBoxLayout(self)
        menu_bar = QMenuBar(self)
        roi_menu = menu_bar.addMenu("ROI")
        roi_menu.addAction("Import ROIs…", self._importPhasorRoisFromFile)
        roi_menu.addAction("Export ROIs…", self._exportPhasorRois)
        layout.addWidget(menu_bar)
        # Top: controls
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Frequency (THz):"))
        self.freqSpin = QDoubleSpinBox()
        self.freqSpin.setRange(0.01, 10.0)
        self.freqSpin.setValue(0.25)
        self.freqSpin.setDecimals(3)
        self.freqSpin.valueChanged.connect(self._onPhasorParamsChanged)
        ctrl.addWidget(self.freqSpin)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        splitter = QSplitter(Qt.Horizontal)
        # Left: phasor plot (QGraphicsView with histogram pixmap, axes overlay, and ROIs)
        phasorWidget = QWidget()
        phasorLayout = QVBoxLayout(phasorWidget)
        phasorLayout.addWidget(QLabel("Phasor (g, s)"))
        self.phasorView = QGraphicsView()
        self.phasorView.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.phasorView.setMinimumSize(380, 380)
        self.phasorScene = QGraphicsScene()
        self.phasorView.setScene(self.phasorScene)
        phasorLayout.addWidget(self.phasorView)
        # ROI controls for phasor
        roiCtrl = QHBoxLayout()
        roiCtrl.addWidget(QLabel("Shape:"))
        self.phasorRoiShapeCombo = QComboBox()
        self.phasorRoiShapeCombo.addItems(["Rectangle", "Square", "Circle", "Ellipse"])
        roiCtrl.addWidget(self.phasorRoiShapeCombo)
        addRoiBtn = QPushButton("Add ROI")
        addRoiBtn.clicked.connect(self._addPhasorROI)
        roiCtrl.addWidget(addRoiBtn)
        delRoiBtn = QPushButton("Delete")
        delRoiBtn.clicked.connect(self._deleteSelectedPhasorROI)
        roiCtrl.addWidget(delRoiBtn)
        renameRoiBtn = QPushButton("Rename")
        renameRoiBtn.clicked.connect(self._renameSelectedPhasorROI)
        roiCtrl.addWidget(renameRoiBtn)
        colorRoiBtn = QPushButton("Color…")
        colorRoiBtn.clicked.connect(self._colorSelectedPhasorROI)
        roiCtrl.addWidget(colorRoiBtn)
        roiCtrl.addStretch()
        phasorLayout.addLayout(roiCtrl)
        self.phasorRoiList = QListWidget()
        self.phasorRoiList.setMaximumHeight(80)
        phasorLayout.addWidget(self.phasorRoiList)
        splitter.addWidget(phasorWidget)

        # Right: signal plot + spatial image
        rightWidget = QWidget()
        rightLayout = QVBoxLayout(rightWidget)
        rightLayout.addWidget(QLabel("ROI average signal vs time"))
        self.signalFigure = Figure(figsize=(4, 3))
        self.signalFigure.subplots_adjust(left=0.15, bottom=0.18, right=0.95, top=0.95)
        self.signalCanvas = FigureCanvas(self.signalFigure)
        self.signalAxes = self.signalFigure.add_subplot(111)
        self.signalAxes.set_xlabel("Time delay (ps)")
        self.signalAxes.set_ylabel("Average signal (arb. u.)")
        self.signalAxes.grid(True, alpha=0.3)
        rightLayout.addWidget(self.signalCanvas)
        spatialHdr = QHBoxLayout()
        spatialHdr.addWidget(QLabel("Projection with ROI overlay"))
        self.spatialOverlaySchemeCombo = QComboBox()
        self.spatialOverlaySchemeCombo.addItems(
            [
                "Intensity-scaled opacity",
                "Solid ROI colors",
            ]
        )
        self.spatialOverlaySchemeCombo.setToolTip(
            "Intensity-scaled: ROI tint strength follows projection intensity.\n"
            "Solid: ROI pixels use the assigned color at full opacity."
        )
        self.spatialOverlaySchemeCombo.currentIndexChanged.connect(
            lambda _i: self._updateSpatialImage()
        )
        spatialHdr.addWidget(self.spatialOverlaySchemeCombo)
        spatialHdr.addStretch()
        rightLayout.addLayout(spatialHdr)
        self.spatialView = QGraphicsView()
        self.spatialScene = QGraphicsScene()
        self.spatialView.setScene(self.spatialScene)
        self.spatialView.setMinimumSize(350, 350)
        self.spatialView.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.spatialView.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rightLayout.addWidget(self.spatialView)
        splitter.addWidget(rightWidget)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

        self._refreshPhasorPlot()
        self._refreshFromPhasorRois()
        self._updateSpatialImage()

    def _onPhasorParamsChanged(self):
        self._computePhasorData()
        self._refreshPhasorPlot()
        self._refreshFromPhasorRois()

    def _phasorRoiShapeFromCombo(self):
        m = {"Rectangle": "rectangle", "Square": "square", "Circle": "circle", "Ellipse": "ellipse"}
        return m.get(self.phasorRoiShapeCombo.currentText(), "rectangle")

    def _phasorSceneToGS(self, scene_rect, shape_type=None):
        """Convert scene QRectF (pixmap coords) to (g,s) params. Scene: (0,0)=top-left=(g_lo,s_hi), (W,H)=bottom-right=(g_hi,s_lo)."""
        if self.phasorPixmapRect is None or self.phasorGLim is None or self.phasorSLim is None:
            return None
        W = self.phasorPixmapRect.width()
        H = self.phasorPixmapRect.height()
        if W <= 0 or H <= 0:
            return None
        g_lo, g_hi = self.phasorGLim
        s_lo, s_hi = self.phasorSLim
        r = scene_rect
        g_left = g_lo + (r.left() / W) * (g_hi - g_lo)
        g_right = g_lo + (r.right() / W) * (g_hi - g_lo)
        s_top = s_hi - (r.top() / H) * (s_hi - s_lo)
        s_bottom = s_hi - (r.bottom() / H) * (s_hi - s_lo)
        shape = shape_type if shape_type is not None else self._phasorRoiShapeFromCombo()
        if shape == "rectangle":
            return {"x": g_left, "y": s_bottom, "width": g_right - g_left, "height": s_top - s_bottom}
        if shape == "square":
            w, h = g_right - g_left, s_top - s_bottom
            sz = min(w, h)
            return {"center_g": (g_left + g_right) / 2.0, "center_s": (s_top + s_bottom) / 2.0, "size": sz}
        if shape == "circle":
            return {"center_g": (g_left + g_right) / 2.0, "center_s": (s_top + s_bottom) / 2.0, "radius": min(g_right - g_left, s_top - s_bottom) / 2.0}
        if shape == "ellipse":
            return {"center_g": (g_left + g_right) / 2.0, "center_s": (s_top + s_bottom) / 2.0, "radius_g": (g_right - g_left) / 2.0, "radius_s": (s_top - s_bottom) / 2.0, "angle_deg": 0.0}
        return None

    def _phasorParamsToSceneRect(self, shape_type, params):
        """Convert (g,s) params to scene QRectF (pixmap coords)."""
        if self.phasorPixmapRect is None or self.phasorGLim is None or self.phasorSLim is None:
            return None
        W = self.phasorPixmapRect.width()
        H = self.phasorPixmapRect.height()
        if W <= 0 or H <= 0:
            return None
        g_lo, g_hi = self.phasorGLim
        s_lo, s_hi = self.phasorSLim
        if shape_type == "rectangle":
            g_left, s_bottom = params["x"], params["y"]
            g_right = g_left + params["width"]
            s_top = s_bottom + params["height"]
        elif shape_type == "square":
            cx, cy, sz = params["center_g"], params["center_s"], params["size"]
            g_left, g_right = cx - sz / 2, cx + sz / 2
            s_bottom, s_top = cy - sz / 2, cy + sz / 2
        elif shape_type == "circle":
            cx, cy, r = params["center_g"], params["center_s"], params["radius"]
            g_left, g_right = cx - r, cx + r
            s_bottom, s_top = cy - r, cy + r
        elif shape_type == "ellipse":
            cx, cy = params["center_g"], params["center_s"]
            rg = params["radius_g"]
            rs = params.get("radius_s", params.get("radius_y", rg))
            g_left, g_right = cx - rg, cx + rg
            s_bottom, s_top = cy - rs, cy + rs
        else:
            return None
        x1 = (g_left - g_lo) / (g_hi - g_lo) * W
        x2 = (g_right - g_lo) / (g_hi - g_lo) * W
        y1 = (s_hi - s_top) / (s_hi - s_lo) * H
        y2 = (s_hi - s_bottom) / (s_hi - s_lo) * H
        return QRectF(x1, y1, x2 - x1, y2 - y1)

    def _refreshPhasorPlot(self):
        """Redraw phasor histogram with fixed [-1,1] axes as pixmap, preserve ROI items."""
        if self._phasor_coor is None or self._phasor_coor.size == 0:
            return
        g_all = self._phasor_coor[:, 0]
        s_all = self._phasor_coor[:, 1]
        # If requested, only visualize pixels that are inside the current effective mask
        if self._apply_effective_mask and self._effective_mask_1d is not None and self._effective_mask_1d.size == g_all.size:
            valid = self._effective_mask_1d
            g = g_all[valid]
            s = s_all[valid]
        else:
            g = g_all
            s = s_all
        # Fixed phasor axes in both dimensions: [-1, 1]
        g_lo, g_hi = -1.0, 1.0
        s_lo, s_hi = -1.0, 1.0
        self.phasorGLim = (g_lo, g_hi)
        self.phasorSLim = (s_lo, s_hi)

        size = 200
        bins_g = np.linspace(g_lo, g_hi, size + 1)
        bins_s = np.linspace(s_lo, s_hi, size + 1)
        H, _, _ = np.histogram2d(g, s, bins=(bins_g, bins_s))
        H = H.T
        H = H[::-1, :]
        H = np.clip(H, 0, np.percentile(H[H > 0], 99) if np.any(H > 0) else 1)
        if np.any(H > 0):
            H_norm = H / H.max()
        else:
            H_norm = H
        # Universal phasor semicircle: radius 0.5, center at (0.5, 0), theta in [0, π]
        theta = np.linspace(0.0, np.pi, 400)
        g_circle = 0.5 * (1.0 + np.cos(theta))
        s_circle_top = 0.5 * np.sin(theta)
        s_circle_bottom = -0.5 * np.sin(theta)
        # Upper semicircle (standard universal circle)
        for i in range(len(g_circle)):
            if g_lo <= g_circle[i] <= g_hi and s_lo <= s_circle_top[i] <= s_hi:
                xi = int((g_circle[i] - g_lo) / (g_hi - g_lo) * (size - 1) + 0.5)
                yi = int((s_hi - s_circle_top[i]) / (s_hi - s_lo) * (size - 1) + 0.5)
                if 0 <= xi < size and 0 <= yi < size:
                    H_norm[yi, xi] = 1.0
        # Lower, upside-down semicircle mirrored across s = 0 and then across the y-axis
        for i in range(len(g_circle)):
            g_mirrored = -g_circle[i]
            if g_lo <= g_mirrored <= g_hi and s_lo <= s_circle_bottom[i] <= s_hi:
                xi = int((g_mirrored - g_lo) / (g_hi - g_lo) * (size - 1) + 0.5)
                yi = int((s_hi - s_circle_bottom[i]) / (s_hi - s_lo) * (size - 1) + 0.5)
                if 0 <= xi < size and 0 <= yi < size:
                    H_norm[yi, xi] = 1.0
        cmap = plt.get_cmap("viridis")
        rgba = cmap(H_norm)
        rgb = np.ascontiguousarray((rgba[..., :3] * 255).astype(np.uint8), dtype=np.uint8)
        h, w = rgb.shape[:2]
        qimg = QImage(rgb.data, w, h, w * 3, QImage.Format.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimg)

        backups = []
        for item in self.phasorRoiItems:
            entry = item.get("params")
            if entry is None:
                scene_rect = item["rect_item"].getSceneRect()
                entry = self._phasorSceneToGS(scene_rect, shape_type=item["shape_type"])
                if entry is None:
                    continue
            backups.append({
                "id": item["id"],
                "shape_type": item["shape_type"],
                "params": dict(entry),
                "label": item["label"],
                "color": item["color"],
            })

        self.phasorScene.clear()
        self.phasorRoiItems.clear()
        pix_item = self.phasorScene.addPixmap(pixmap)
        self.phasorPixmapRect = pix_item.boundingRect()
        W = self.phasorPixmapRect.width()
        H_rect = self.phasorPixmapRect.height()

        axis_pen = QPen(QColor(0, 0, 0), 1)
        axis_pen.setStyle(Qt.PenStyle.SolidLine)
        y_axis_pen = QPen(QColor(0, 0, 0), 2)
        y_axis_pen.setStyle(Qt.PenStyle.SolidLine)
        left_axis = QGraphicsLineItem(0, 0, 0, H_rect)
        left_axis.setPen(y_axis_pen)
        left_axis.setZValue(5)
        self.phasorScene.addItem(left_axis)
        right_axis = QGraphicsLineItem(W, 0, W, H_rect)
        right_axis.setPen(y_axis_pen)
        right_axis.setZValue(5)
        self.phasorScene.addItem(right_axis)
        bottom_axis = QGraphicsLineItem(0, H_rect, W, H_rect)
        bottom_axis.setPen(axis_pen)
        bottom_axis.setZValue(5)
        self.phasorScene.addItem(bottom_axis)
        top_axis = QGraphicsLineItem(0, 0, W, 0)
        top_axis.setPen(axis_pen)
        top_axis.setZValue(5)
        self.phasorScene.addItem(top_axis)
        left_margin = 38
        g_label = QGraphicsTextItem("g")
        g_label.setFont(QFont("Sans Serif", PHASOR_AXIS_FONT_SIZE))
        g_label.setPos(W / 2 - 5, H_rect + 2)
        g_label.setZValue(5)
        self.phasorScene.addItem(g_label)
        s_label = QGraphicsTextItem("s")
        s_label.setFont(QFont("Sans Serif", PHASOR_AXIS_FONT_SIZE))
        s_label.setPos(-left_margin - 10, H_rect / 2 - 8)
        s_label.setZValue(5)
        self.phasorScene.addItem(s_label)
        g_lo_text = QGraphicsTextItem(f"{g_lo:.2f}")
        g_lo_text.setFont(QFont("Sans Serif", PHASOR_AXIS_FONT_SIZE - 2))
        g_lo_text.setPos(0, H_rect + 2)
        g_lo_text.setZValue(5)
        self.phasorScene.addItem(g_lo_text)
        g_hi_text = QGraphicsTextItem(f"{g_hi:.2f}")
        g_hi_text.setFont(QFont("Sans Serif", PHASOR_AXIS_FONT_SIZE - 2))
        g_hi_text.setPos(W - 28, H_rect + 2)
        g_hi_text.setZValue(5)
        self.phasorScene.addItem(g_hi_text)
        s_hi_text = QGraphicsTextItem(f"{s_hi:.2f}")
        s_hi_text.setFont(QFont("Sans Serif", PHASOR_AXIS_FONT_SIZE - 2))
        s_hi_text.setPos(-left_margin + 4, 2)
        s_hi_text.setZValue(5)
        self.phasorScene.addItem(s_hi_text)
        s_mid = (s_lo + s_hi) / 2.0
        s_mid_text = QGraphicsTextItem(f"{s_mid:.2f}")
        s_mid_text.setFont(QFont("Sans Serif", PHASOR_AXIS_FONT_SIZE - 2))
        s_mid_text.setPos(-left_margin + 4, H_rect / 2 - 4)
        s_mid_text.setZValue(5)
        self.phasorScene.addItem(s_mid_text)
        s_lo_text = QGraphicsTextItem(f"{s_lo:.2f}")
        s_lo_text.setFont(QFont("Sans Serif", PHASOR_AXIS_FONT_SIZE - 2))
        s_lo_text.setPos(-left_margin + 4, H_rect - 12)
        s_lo_text.setZValue(5)
        self.phasorScene.addItem(s_lo_text)

        for b in backups:
            scene_rect = self._phasorParamsToSceneRect(b["shape_type"], b["params"])
            if scene_rect is None:
                continue
            roi_id = b["id"]
            item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
            rect_item = PhasorDraggableROI(item_rect, color=b["color"], shape_type=b["shape_type"])
            rect_item.setPos(scene_rect.topLeft())
            rect_item.setRoiChangedCallback(self._onPhasorRoiChanged)
            rect_item.setZValue(10)
            self.phasorScene.addItem(rect_item)
            self.phasorRoiItems.append({
                "id": roi_id,
                "label": b["label"],
                "shape_type": b["shape_type"],
                "params": b["params"],
                "color": b["color"],
                "rect_item": rect_item,
            })
        self._refreshPhasorRoiList()
        scene_rect = self.phasorScene.itemsBoundingRect()
        if scene_rect.width() > 0 and scene_rect.height() > 0:
            margin = 4
            scene_rect = scene_rect.adjusted(-left_margin, -margin, margin, margin)
            self.phasorScene.setSceneRect(scene_rect)
            self.phasorView.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)

    def _onPhasorRoiChanged(self):
        self._roiUpdateTimer.start(50)

    def _refreshPhasorRoiList(self):
        self.phasorRoiList.clear()
        for item in self.phasorRoiItems:
            li = QListWidgetItem(item["label"] or item["id"])
            li.setData(Qt.ItemDataRole.UserRole, item["id"])
            qcol = _matplotlib_color_to_qt(item.get("color", "#1f77b4"))
            pm = QPixmap(12, 12)
            pm.fill(qcol)
            li.setIcon(QIcon(pm))
            self.phasorRoiList.addItem(li)

    def _refreshFromPhasorRois(self):
        """Update ROI params from scene rects, then refresh signal plot and spatial image."""
        if not self.phasorPixmapRect or not self.phasorRoiItems:
            self._drawSignalPlot()
            self._updateSpatialImage()
            return
        for item in self.phasorRoiItems:
            scene_rect = item["rect_item"].getSceneRect()
            params = self._phasorSceneToGS(scene_rect, shape_type=item["shape_type"])
            if params is not None:
                item["params"] = params
        self._drawSignalPlot()
        self._updateSpatialImage()
        self._refreshPhasorRoiList()

    def _getPhasorRoiPixelMask(self, item):
        """Boolean mask over image pixels (1D, size = n_pixels) for this phasor ROI."""
        if self._phasor_coor is None or self.pps is None:
            return None
        g = self._phasor_coor[:, 0]
        s = self._phasor_coor[:, 1]
        params = item.get("params")
        if params is None:
            return None
        base_mask = phasor_shape_to_mask(item["shape_type"], params, g, s)
        if base_mask is None:
            return None
        # If we're honoring the effective mask, ensure masked-out pixels are never included
        if self._apply_effective_mask and self._effective_mask_1d is not None and self._effective_mask_1d.size == base_mask.size:
            return base_mask & self._effective_mask_1d
        return base_mask

    def _signalForPhasorRoi(self, item):
        """Average TA curve for pixels in this phasor ROI (and inside pps.mask)."""
        mask = self._getPhasorRoiPixelMask(item)
        if mask is None:
            return None
        # Phasor mask is 1D (n_pixels); pps.mask is 2D — flatten for same-index combine
        pps_mask_1d = np.asarray(self.pps.mask, dtype=bool).ravel()
        combined = mask & pps_mask_1d
        n = np.sum(combined)
        if n == 0:
            return np.zeros(len(self.pps.images))
        signals = [np.mean(img.ravel()[combined]) for img in self.pps.images]
        return np.array(signals)

    def _drawSignalPlot(self):
        self.signalAxes.clear()
        self.signalAxes.set_xlabel("Time delay (ps)")
        self.signalAxes.set_ylabel("Average signal (arb. u.)")
        self.signalAxes.grid(True, alpha=0.3)
        times = np.asarray(self.pps.times, dtype=np.float64)
        for item in self.phasorRoiItems:
            sig = self._signalForPhasorRoi(item)
            if sig is None:
                continue
            color = item["color"]
            if isinstance(color, str) and not color.startswith('#'):
                try:
                    color = mcolors.to_hex(color)
                except Exception:
                    pass
            n = min(len(times), len(sig))
            self.signalAxes.plot(times[:n], sig[:n], color=color, marker='o', markersize=3, label=item["label"] or item["id"])
        if self.phasorRoiItems:
            self.signalAxes.legend(fontsize=8, loc="best")
        if self.signalAxes.lines:
            self.signalAxes.relim()
            self.signalAxes.autoscale_view(tight=True)
        self.signalCanvas.draw()

    def _addPhasorROI(self):
        if not self.phasorPixmapRect or self._phasor_coor is None:
            return
        shape = self._phasorRoiShapeFromCombo()
        color = PHASOR_ROI_COLORS[self._roiColorIndex % len(PHASOR_ROI_COLORS)]
        self._roiColorIndex += 1
        self._phasorRoiCounter += 1
        roi_id = f"phasor_roi_{self._phasorRoiCounter}"
        W = self.phasorPixmapRect.width()
        H = self.phasorPixmapRect.height()
        cx = W / 2
        cy = H / 2
        sz = min(W, H) * 0.15
        scene_rect = QRectF(cx - sz / 2, cy - sz / 2, sz, sz)
        item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
        rect_item = PhasorDraggableROI(item_rect, color=color, shape_type=shape)
        rect_item.setPos(scene_rect.topLeft())
        rect_item.setRoiChangedCallback(self._onPhasorRoiChanged)
        rect_item.setZValue(10)
        self.phasorScene.addItem(rect_item)
        params = self._phasorSceneToGS(scene_rect, shape_type=shape)
        if params is None:
            params = {"center_g": 0, "center_s": 0, "size": 0.2}
        label = f"ROI {len(self.phasorRoiItems) + 1}"
        self.phasorRoiItems.append({"id": roi_id, "label": label, "shape_type": shape, "params": params, "color": color, "rect_item": rect_item})
        self._refreshPhasorRoiList()
        self._refreshFromPhasorRois()

    def _deleteSelectedPhasorROI(self):
        li = self.phasorRoiList.currentItem()
        if not li:
            return
        roi_id = li.data(Qt.ItemDataRole.UserRole)
        for item in self.phasorRoiItems[:]:
            if item["id"] == roi_id:
                self.phasorScene.removeItem(item["rect_item"])
                self.phasorRoiItems.remove(item)
                break
        self._refreshPhasorRoiList()
        self._refreshFromPhasorRois()

    def _renameSelectedPhasorROI(self):
        li = self.phasorRoiList.currentItem()
        if not li:
            return
        roi_id = li.data(Qt.ItemDataRole.UserRole)
        item = next((x for x in self.phasorRoiItems if x["id"] == roi_id), None)
        if not item:
            return
        label, ok = QInputDialog.getText(self, "Rename ROI", "Label:", QLineEdit.EchoMode.Normal, item["label"] or roi_id)
        if ok and label is not None:
            item["label"] = label.strip() or item["id"]
            self._refreshPhasorRoiList()
            self._drawSignalPlot()

    def _colorSelectedPhasorROI(self):
        li = self.phasorRoiList.currentItem()
        if not li:
            QMessageBox.information(self, "Color", "Select an ROI first.")
            return
        roi_id = li.data(Qt.ItemDataRole.UserRole)
        item = next((x for x in self.phasorRoiItems if x["id"] == roi_id), None)
        if not item:
            return
        current = item["color"]
        if isinstance(current, str):
            qcolor = QColor(current) if current.startswith('#') else QColor(100, 100, 100)
        else:
            qcolor = _matplotlib_color_to_qt(current)
        color = QColorDialog.getColor(qcolor, self, "ROI color")
        if color.isValid():
            item["color"] = color.name()
            item["rect_item"]._roi_color = color
            item["rect_item"].setPen(QPen(color, 2))
            item["rect_item"].setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 50)))
            self._drawSignalPlot()
            self._updateSpatialImage()

    def _getDefaultPhasorRoisJsonPath(self):
        """Default path for phasor ROI JSON next to the stack file (same as export default)."""
        if self.pps is None or not getattr(self.pps, "filename", None):
            return None
        p = Path(self.pps.filename)
        return p.parent / f"{p.stem}_phasor_rois.json"

    def _tryAutoloadPhasorRoisJson(self):
        """If default JSON exists, load it once at startup (silent; no NPZ)."""
        if self._phasor_roi_autoload_done:
            return
        self._phasor_roi_autoload_done = True
        path = self._getDefaultPhasorRoisJsonPath()
        if path is None or not path.exists():
            return
        self._loadPhasorRoisFromJsonPath(path, silent=True)

    def _importPhasorRoisFromFile(self):
        """Manual import: user picks a phasor ROI JSON file (replaces current ROIs)."""
        if self.pps is None:
            return
        default_dir = str(Path(self.pps.filename).parent) if getattr(self.pps, "filename", None) else "."
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Import phasor ROIs",
            default_dir,
            "JSON (*.json);;All files (*)",
        )
        if not path_str:
            return
        self._loadPhasorRoisFromJsonPath(Path(path_str), silent=False)

    def _updatePhasorRoiCounterFromLoadedIds(self):
        """Set _phasorRoiCounter to max N seen in ids like phasor_roi_N."""
        max_n = self._phasorRoiCounter
        for item in self.phasorRoiItems:
            rid = str(item.get("id", ""))
            if rid.startswith("phasor_roi_"):
                try:
                    n = int(rid.split("_")[-1])
                    max_n = max(max_n, n)
                except ValueError:
                    pass
        self._phasorRoiCounter = max_n

    def _loadPhasorRoisFromJsonPath(self, path: Path, silent=False):
        """
        Replace all phasor ROIs from an export-format JSON file.

        Validates image_dimensions against the current stack; on mismatch, shows an error
        unless silent (autoload). Frequency from JSON is applied before recomputing phasors.
        """
        if self.pps is None or not hasattr(self.pps, "image_dimensions"):
            if not silent:
                QMessageBox.warning(self, "Import phasor ROIs", "No PPS data available.")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "Import phasor ROIs", f"Could not read JSON:\n{e}")
            return

        if not isinstance(data, dict):
            if not silent:
                QMessageBox.warning(self, "Import phasor ROIs", "Invalid file: root must be a JSON object.")
            return

        file_dims = data.get("image_dimensions")
        if file_dims is None:
            if not silent:
                QMessageBox.warning(self, "Import phasor ROIs", "Invalid file: missing image_dimensions.")
            return
        try:
            file_dims_t = tuple(int(x) for x in file_dims)
        except (TypeError, ValueError):
            if not silent:
                QMessageBox.warning(self, "Import phasor ROIs", "Invalid image_dimensions in file.")
            return
        stack_dims = tuple(int(x) for x in self.pps.image_dimensions)
        if file_dims_t != stack_dims:
            msg = (
                f"Image dimensions in file {file_dims_t} do not match current stack {stack_dims}.\n"
                "ROIs were not loaded."
            )
            if not silent:
                QMessageBox.warning(self, "Import phasor ROIs", msg)
            return

        rois = data.get("rois")
        if rois is None:
            if not silent:
                QMessageBox.warning(self, "Import phasor ROIs", "Invalid file: missing rois array.")
            return
        if not isinstance(rois, list):
            if not silent:
                QMessageBox.warning(self, "Import phasor ROIs", "Invalid file: rois must be a list.")
            return

        phasor_meta = data.get("phasor") or {}
        freq = phasor_meta.get("frequency_THz")
        if freq is not None:
            try:
                fv = float(freq)
                self.freqSpin.blockSignals(True)
                self.freqSpin.setValue(fv)
                self.freqSpin.blockSignals(False)
            except (TypeError, ValueError):
                pass

        self._computePhasorData()
        self._refreshPhasorPlot()

        allowed_shapes = {"rectangle", "square", "circle", "ellipse"}
        for roi in rois:
            if not isinstance(roi, dict):
                continue
            shape_type = roi.get("shape", "rectangle")
            if shape_type not in allowed_shapes:
                continue
            params = _phasor_to_json_serializable_params(roi.get("params") or {})
            label = roi.get("label") or roi.get("id") or "ROI"
            rid = roi.get("id")
            if not rid:
                self._phasorRoiCounter += 1
                roi_id = f"phasor_roi_{self._phasorRoiCounter}"
            else:
                roi_id = str(rid)
            color = roi.get("color", "#1f77b4")
            scene_rect = self._phasorParamsToSceneRect(shape_type, params)
            if scene_rect is None or scene_rect.width() <= 0 or scene_rect.height() <= 0:
                continue
            item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
            rect_item = PhasorDraggableROI(item_rect, color=color, shape_type=shape_type)
            rect_item.setPos(scene_rect.topLeft())
            rect_item.setRoiChangedCallback(self._onPhasorRoiChanged)
            rect_item.setZValue(10)
            self.phasorScene.addItem(rect_item)
            self.phasorRoiItems.append({
                "id": roi_id,
                "label": label,
                "shape_type": shape_type,
                "params": dict(params),
                "color": color,
                "rect_item": rect_item,
            })

        self._updatePhasorRoiCounterFromLoadedIds()
        self._roiColorIndex = len(self.phasorRoiItems)
        self._refreshPhasorRoiList()
        self._refreshFromPhasorRois()

        if not silent:
            QMessageBox.information(
                self,
                "Import phasor ROIs",
                f"Loaded {len(self.phasorRoiItems)} ROI(s) from:\n{path}",
            )

    def _exportPhasorRois(self):
        """Export all phasor ROIs to a JSON (phasor-space) and NPZ (image-space masks)."""
        if not self.phasorRoiItems:
            QMessageBox.information(self, "Export phasor ROIs", "No phasor ROIs to export.")
            return
        if self.pps is None or not hasattr(self.pps, "image_dimensions"):
            QMessageBox.warning(self, "Export phasor ROIs", "PPS image dimensions are not available.")
            return

        # Optional comment
        comment, ok = QInputDialog.getText(
            self,
            "Export phasor ROIs",
            "Comment (optional):",
            QLineEdit.EchoMode.Normal,
            "",
        )
        if not ok:
            return

        # Default export path based on PPS filename
        default_dir = Path.cwd()
        default_name = "phasor_rois.json"
        if hasattr(self.pps, "filename") and self.pps.filename:
            p = Path(self.pps.filename)
            default_dir = p.parent
            default_name = f"{p.stem}_phasor_rois.json"
        default_path = default_dir / default_name

        json_path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Export phasor ROIs",
            str(default_path),
            "JSON (*.json)",
        )
        if not json_path_str:
            return
        json_path = Path(json_path_str)

        # Ensure ROI params are up to date with scene rectangles
        self._refreshFromPhasorRois()

        # Build JSON structure
        freq = float(self._getFreq()) if hasattr(self, "_getFreq") else 0.0
        image_dims = tuple(self.pps.image_dimensions)
        rois_json = {
            "image_dimensions": list(image_dims),
            "phasor": {
                "frequency_THz": freq,
                "remove_zero": False,
            },
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "comment": comment,
            "rois": [],
        }

        masks = []
        labels = []
        shape_types = []
        roi_ids = []
        colors = []

        h, w = image_dims
        n_pixels = h * w

        for item in self.phasorRoiItems:
            params = item.get("params") or {}
            shape_type = item.get("shape_type", "rectangle")
            label = item.get("label") or item.get("id")
            roi_id = item.get("id")
            color = item.get("color")
            # Normalize color to hex string if possible
            if isinstance(color, str) and color.startswith("#"):
                color_hex = color
            else:
                try:
                    color_hex = mcolors.to_hex(color)
                except Exception:
                    color_hex = "#ff0000"

            rois_json["rois"].append(
                {
                    "id": roi_id,
                    "label": label,
                    "shape": shape_type,
                    "params": _phasor_to_json_serializable_params(params),
                    "color": color_hex,
                }
            )

            # Image-domain boolean mask for this ROI (1D → 2D)
            mask_1d = self._getPhasorRoiPixelMask(item)
            if mask_1d is None:
                continue
            mask_1d = np.asarray(mask_1d, dtype=bool).ravel()
            if mask_1d.size != n_pixels:
                continue
            mask_2d = mask_1d.reshape(h, w)
            masks.append(mask_2d)
            labels.append(str(label))
            shape_types.append(str(shape_type))
            roi_ids.append(str(roi_id))
            colors.append(color_hex)

        # Write JSON file
        try:
            with open(json_path, "w") as f:
                json.dump(rois_json, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Export phasor ROIs", f"Failed to write JSON:\n{e}")
            return

        # If no valid masks were generated, skip NPZ but keep JSON
        if not masks:
            QMessageBox.information(
                self,
                "Export phasor ROIs",
                f"Exported {len(rois_json['rois'])} ROI definitions to:\n{json_path}\n\n"
                "No valid image-domain masks could be generated, so no NPZ file was written.",
            )
            return

        masks_arr = np.stack(masks, axis=0).astype(bool)
        npz_stem = json_path.with_suffix("").name
        npz_path = json_path.parent / f"{npz_stem}_phasor_masks.npz"

        try:
            np.savez(
                npz_path,
                masks=masks_arr,
                image_dimensions=np.array(image_dims),
                labels=np.array(labels, dtype=object),
                shapes=np.array(shape_types, dtype=object),
                roi_ids=np.array(roi_ids, dtype=object),
                colors=np.array(colors, dtype=object),
                comment=np.array(str(comment)),
                phasor_frequency_THz=np.array(freq),
                phasor_remove_zero=np.array(False),
                date=np.array(datetime.now().isoformat()),
            )
        except Exception as e:
            QMessageBox.critical(self, "Export phasor ROIs", f"Failed to write NPZ mask file:\n{e}")
            return

        QMessageBox.information(
            self,
            "Export phasor ROIs",
            f"Exported {len(rois_json['rois'])} phasor ROI definitions to:\n{json_path}\n\n"
            f"and corresponding image-domain masks to:\n{npz_path}",
        )

    def _updateSpatialImage(self):
        """Draw static projection as grayscale; overlay ROI colors (intensity-scaled or solid)."""
        if self.pps is None:
            return
        proj = self.pps.project(maskOn=False)
        if proj.ndim != 2:
            return
        proj = np.nan_to_num(proj, nan=0.0, posinf=0.0, neginf=0.0)
        h, w = proj.shape
        effective_mask = np.asarray(self.pps.mask, dtype=bool)
        proj_valid = proj[effective_mask]
        proj_min = float(np.min(proj_valid)) if np.any(effective_mask) else 0.0
        proj_max = float(np.max(proj_valid)) if np.any(effective_mask) else 1.0
        if proj_max <= proj_min:
            proj_max = proj_min + 1.0
        proj_norm = np.clip((proj - proj_min) / (proj_max - proj_min), 0.0, 1.0).astype(np.float64)
        gray_u8 = (proj_norm * 255).astype(np.uint8)
        rgb = np.stack([gray_u8, gray_u8, gray_u8], axis=-1).astype(np.float64)
        rgb[~effective_mask, :] = 200.0
        n_pixels = h * w
        roi_assignment = np.full(n_pixels, -1)
        for idx, item in enumerate(self.phasorRoiItems):
            mask_1d = self._getPhasorRoiPixelMask(item)
            if mask_1d is None:
                continue
            roi_assignment[(roi_assignment == -1) & mask_1d] = idx
        roi_assignment_display = roi_assignment.reshape(h, w)
        for idx in range(len(self.phasorRoiItems)):
            item = self.phasorRoiItems[idx]
            color = item["color"]
            if isinstance(color, str) and color.startswith("#"):
                qc = QColor(color)
            else:
                try:
                    qc = QColor(mcolors.to_hex(color))
                except Exception:
                    qc = QColor(255, 0, 0)
            r, g, b = float(qc.red()), float(qc.green()), float(qc.blue())
            sel = roi_assignment_display == idx
            solid = (
                hasattr(self, "spatialOverlaySchemeCombo")
                and self.spatialOverlaySchemeCombo.currentIndex() == 1
            )
            if solid:
                rgb[sel, 0] = r
                rgb[sel, 1] = g
                rgb[sel, 2] = b
            else:
                alpha = proj_norm[sel]
                rgb[sel, 0] = (1.0 - alpha) * rgb[sel, 0] + alpha * r + 1
                rgb[sel, 1] = (1.0 - alpha) * rgb[sel, 1] + alpha * g + 1
                rgb[sel, 2] = (1.0 - alpha) * rgb[sel, 2] + alpha * b + 1
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        rgb[~effective_mask, :] = [200, 200, 200]
        rgb = np.ascontiguousarray(rgb)
        qimg = QImage(rgb.data, w, h, w * 3, QImage.Format.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimg)
        self.spatialScene.clear()
        self.spatialScene.addPixmap(pixmap)
        self._fitSpatialView()
        QTimer.singleShot(0, self._fitSpatialView)

    def _fitSpatialView(self):
        """Fit the projection image to the spatial graphics view viewport."""
        if not hasattr(self, "spatialView") or not hasattr(self, "spatialScene"):
            return
        r = self.spatialScene.itemsBoundingRect()
        if r.width() <= 0 or r.height() <= 0:
            return
        self.spatialView.fitInView(r, Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "phasorView") and hasattr(self, "phasorScene") and self.phasorPixmapRect is not None:
            scene_rect = self.phasorScene.sceneRect()
            if scene_rect.width() > 0 and scene_rect.height() > 0:
                self.phasorView.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)
        QTimer.singleShot(0, self._fitSpatialView)

    def showEvent(self, event):
        super().showEvent(event)
        if self.pps is not None:
            QTimer.singleShot(0, self._updateSpatialImage)
        if hasattr(self, "phasorView") and hasattr(self, "phasorScene") and self.phasorPixmapRect is not None:
            QTimer.singleShot(0, lambda: self._fitPhasorView())
        QTimer.singleShot(0, self._fitSpatialView)

    def _fitPhasorView(self):
        """Fit the phasor scene in the view (call after show or when scene content changes)."""
        if not hasattr(self, "phasorView") or not hasattr(self, "phasorScene"):
            return
        scene_rect = self.phasorScene.sceneRect()
        if scene_rect.width() > 0 and scene_rect.height() > 0:
            self.phasorView.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)
