#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
puprisa_channel_view.py
Simple Channel View Window with ROI functionality

A window for viewing a single channel with slice navigation via slider.
Shows one image at a time from the stack and allows navigation through time points.
Includes draggable/resizable ROI and plot showing ROI signal vs time delay.

2D slices and masks use the same row order as ``PPS`` storage and as the main
PUPRISA window projections (matplotlib ``origin='upper'``: row 0 at the top).

Created: 2025
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QScrollArea,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem,
    QSplitter, QPushButton, QListWidget, QListWidgetItem, QInputDialog, QDialog,
    QDialogButtonBox, QLineEdit, QMenuBar, QMenu, QDoubleSpinBox, QSpinBox,
    QFormLayout, QCheckBox, QComboBox, QFileDialog, QMessageBox, QApplication,
)
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QImage, QPixmap, QPen, QBrush, QColor, QPainter, QWheelEvent, QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from pump_probe_analysis.phasor_analysis_window import PhasorAnalysisWindow
from pump_probe_analysis.pps import PPS

# Import ROI utilities from shared pump_probe_analysis PPS module
try:
    from pump_probe_analysis.pps import (
        roi_shape_to_mask,
        roi_entry_to_dict,
        roi_dict_to_entry,
    )
except ImportError:
    roi_shape_to_mask = roi_entry_to_dict = roi_dict_to_entry = None

# Default matplotlib color palette for ROI color-matching
ROI_COLOR_PALETTE = plt.rcParams['axes.prop_cycle'].by_key()['color']


def _guess_pps_data_type(path: Path):
    """Infer ``PPS`` ``dataType`` from file extension. Return None if user must choose."""
    suf = path.suffix.lower()
    if suf in (".pkl", ".pickle"):
        return "pickle"
    if suf in (".tif", ".tiff"):
        return "DukeScan"
    return None


# Mask NPZ: one file per mask; keys: mask, shape, label, comment, date (strings as 0-d arrays)
def _mask_npz_save(path, mask, image_dimensions, label="", comment="", date=""):
    """Save a single mask to an NPZ file with metadata."""
    if date is None or date == "":
        date = datetime.now().isoformat()
    np.savez(
        path,
        mask=np.asarray(mask, dtype=bool),
        shape=np.array(image_dimensions),
        label=np.array(str(label)),
        comment=np.array(str(comment)),
        date=np.array(str(date)),
    )

class IntensityThresholdDialog(QDialog):
    """Dialog for intensity threshold: Li or manual value, sigma, projection_use_mask."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Intensity threshold")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.thresholdTypeCombo = QComboBox()
        self.thresholdTypeCombo.addItems(["Li", "Manual value"])
        self.thresholdTypeCombo.currentTextChanged.connect(self._onThresholdTypeChanged)
        form.addRow("Threshold type:", self.thresholdTypeCombo)
        self.sigmaSpin = QDoubleSpinBox()
        self.sigmaSpin.setRange(0.1, 100)
        self.sigmaSpin.setValue(5)
        self.sigmaSpin.setDecimals(1)
        form.addRow("Sigma (Gaussian smoothing):", self.sigmaSpin)
        self.manualValueSpin = QDoubleSpinBox()
        self.manualValueSpin.setRange(-1e9, 1e9)
        self.manualValueSpin.setValue(0.05)
        self.manualValueSpin.setDecimals(4)
        form.addRow("Manual threshold value:", self.manualValueSpin)
        self.manualValueSpin.setEnabled(False)
        self.projectionUseMaskCheck = QCheckBox("Use current mask for projection")
        self.projectionUseMaskCheck.setChecked(True)
        form.addRow("", self.projectionUseMaskCheck)
        layout.addLayout(form)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _onThresholdTypeChanged(self, text):
        self.manualValueSpin.setEnabled(text == "Manual value")

    def getParams(self):
        """Return (threshold, sigma, projection_use_mask). threshold is 'Li' or float."""
        if self.thresholdTypeCombo.currentText() == "Li":
            threshold = "Li"
        else:
            threshold = self.manualValueSpin.value()
        return threshold, self.sigmaSpin.value(), self.projectionUseMaskCheck.isChecked()


def _mask_npz_load(path, expected_shape):
    """
    Load a single mask from NPZ. Returns dict with mask, label, comment, date or None if shape mismatch.
    expected_shape is (height, width).
    """
    try:
        data = np.load(path, allow_pickle=True)
    except Exception:
        return None
    if "mask" not in data or "shape" not in data:
        if "mask" not in data or "image_dimensions" not in data:
            return None
        shape = tuple(data["image_dimensions"].tolist())
    else:
        shape = tuple(data["shape"].tolist())
    if shape != expected_shape:
        return None
    mask = np.asarray(data["mask"], dtype=bool)
    def get_str(key, default=""):
        if key not in data:
            return default
        arr = data[key]
        if hasattr(arr, "item"):
            return str(arr.item())
        return str(arr) if arr.size else default
    return {
        "mask": mask,
        "label": get_str("label"),
        "comment": get_str("comment"),
        "date": get_str("date"),
    }


def apply_diverging_colormap(data, vmin=None, vmax=None):
    """
    Apply diverging colormap: blue (negative) -> black (zero) -> red (positive).
    
    Parameters
    ----------
    data : np.ndarray
        Input image data (can be any range)
    vmin : float, optional
        Minimum value for colormap scaling. If None, uses data minimum.
    vmax : float, optional
        Maximum value for colormap scaling. If None, uses data maximum.
    
    Returns
    -------
    rgb_image : np.ndarray
        RGB image array of shape (height, width, 3) with values 0-255
    vmin : float
        Actual minimum value used
    vmax : float
        Actual maximum value used
    """
    data = np.asarray(data, dtype=np.float64)
    
    # Determine scaling range
    if vmin is None:
        vmin = np.nanmin(data)
    if vmax is None:
        vmax = np.nanmax(data)
    
    # Handle edge case
    if vmax <= vmin:
        vmax = vmin + 1.0
    
    # Find the maximum absolute value for symmetric scaling
    abs_max = max(abs(vmin), abs(vmax))
    
    # Normalize data to [-1, 1] range (symmetric around zero)
    normalized = np.clip(data / abs_max, -1.0, 1.0)
    
    # Create RGB image
    height, width = data.shape
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Negative values: blue (0, 0, 255) -> black (0, 0, 0)
    negative_mask = normalized < 0
    negative_values = -normalized[negative_mask]  # Make positive for interpolation
    rgb_image[negative_mask, 2] = (negative_values * 255).astype(np.uint8)  # Blue channel
    
    # Positive values: black (0, 0, 0) -> red (255, 0, 0)
    positive_mask = normalized > 0
    positive_values = normalized[positive_mask]
    rgb_image[positive_mask, 0] = (positive_values * 255).astype(np.uint8)  # Red channel
    
    # Zero values remain black (already 0)
    
    return rgb_image, -abs_max, abs_max


def _matplotlib_color_to_qt(color_spec):
    """Convert matplotlib color (hex string or tuple) to QColor."""
    if isinstance(color_spec, QColor):
        return color_spec
    if isinstance(color_spec, str) and color_spec.startswith('#'):
        return QColor(color_spec)
    try:
        hex_color = mcolors.to_hex(color_spec)
        return QColor(hex_color)
    except (ValueError, TypeError):
        return QColor('#1f77b4')  # Fallback blue


class DraggableROI(QGraphicsRectItem):
    """Base draggable ROI: rectangle by default; subclasses override for circle/square/ellipse."""
    SHAPE_TYPE = "rectangle"

    def __init__(self, rect, parent=None, color=None, shape_type=None):
        super().__init__(rect, parent)
        self._shape_type = shape_type if shape_type is not None else self.SHAPE_TYPE
        self._roi_color = QColor(255, 0, 0) if color is None else _matplotlib_color_to_qt(color)
        self.setPen(QPen(self._roi_color, 2))
        self.setBrush(QBrush(QColor(self._roi_color.red(), self._roi_color.green(), self._roi_color.blue(), 50)))
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
        self._resizing = False
        self._resizeHandle = None
        self._roiChangedCallback = None
        
    def setRoiChangedCallback(self, callback):
        """Set callback function to be called when ROI changes."""
        self._roiChangedCallback = callback

    def getShapeType(self):
        """Return ROI shape type: rectangle, square, circle, or ellipse."""
        return self._shape_type

    def getSceneRect(self):
        """Return the ROI rect in scene coordinates."""
        return self.rect().translated(self.pos())

    def paint(self, painter, option, widget=None):
        """Draw the ROI shape (rect for rectangle/square, ellipse for circle/ellipse)."""
        r = self.rect()
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        if self._shape_type in ("circle", "ellipse"):
            painter.drawEllipse(r)
            # Draw dotted bounding rect so users can drag corners to resize
            dotted_pen = QPen(self._roi_color, 1)
            dotted_pen.setStyle(Qt.PenStyle.DotLine)
            painter.setPen(dotted_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(r)
        else:
            painter.drawRect(r)

    def _notifyChanged(self):
        """Notify that ROI has changed."""
        if self._roiChangedCallback:
            self._roiChangedCallback()
    
    def itemChange(self, change, value):
        """Handle item changes and emit signal."""
        result = super().itemChange(change, value)
        # Emit signal when position changes
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            self._notifyChanged()
        return result
    
    def setRect(self, rect):
        """Override setRect to emit signal when rect changes."""
        super().setRect(rect)
        self._notifyChanged()
    
    def mousePressEvent(self, event):
        """Handle mouse press for resizing."""
        # Check if click is near corner/edge for resizing
        rect = self.rect()
        pos = event.pos()
        
        # Define resize handle size
        handle_size = 10
        
        # Check corners and edges
        if abs(pos.x() - rect.left()) < handle_size and abs(pos.y() - rect.top()) < handle_size:
            self._resizing = True
            self._resizeHandle = 'top-left'
        elif abs(pos.x() - rect.right()) < handle_size and abs(pos.y() - rect.top()) < handle_size:
            self._resizing = True
            self._resizeHandle = 'top-right'
        elif abs(pos.x() - rect.left()) < handle_size and abs(pos.y() - rect.bottom()) < handle_size:
            self._resizing = True
            self._resizeHandle = 'bottom-left'
        elif abs(pos.x() - rect.right()) < handle_size and abs(pos.y() - rect.bottom()) < handle_size:
            self._resizing = True
            self._resizeHandle = 'bottom-right'
        elif abs(pos.x() - rect.left()) < handle_size:
            self._resizing = True
            self._resizeHandle = 'left'
        elif abs(pos.x() - rect.right()) < handle_size:
            self._resizing = True
            self._resizeHandle = 'right'
        elif abs(pos.y() - rect.top()) < handle_size:
            self._resizing = True
            self._resizeHandle = 'top'
        elif abs(pos.y() - rect.bottom()) < handle_size:
            self._resizing = True
            self._resizeHandle = 'bottom'
        else:
            self._resizing = False
            self._resizeHandle = None
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for resizing."""
        if self._resizing and self._resizeHandle:
            rect = self.rect()
            pos = event.pos()
            
            # Update rect based on resize handle
            if self._resizeHandle == 'top-left':
                new_rect = QRectF(pos.x(), pos.y(), 
                                 rect.right() - pos.x(), 
                                 rect.bottom() - pos.y())
            elif self._resizeHandle == 'top-right':
                new_rect = QRectF(rect.left(), pos.y(),
                                 pos.x() - rect.left(),
                                 rect.bottom() - pos.y())
            elif self._resizeHandle == 'bottom-left':
                new_rect = QRectF(pos.x(), rect.top(),
                                 rect.right() - pos.x(),
                                 pos.y() - rect.top())
            elif self._resizeHandle == 'bottom-right':
                new_rect = QRectF(rect.left(), rect.top(),
                                 pos.x() - rect.left(),
                                 pos.y() - rect.top())
            elif self._resizeHandle == 'left':
                new_rect = QRectF(pos.x(), rect.top(),
                                 rect.right() - pos.x(),
                                 rect.height())
            elif self._resizeHandle == 'right':
                new_rect = QRectF(rect.left(), rect.top(),
                                 pos.x() - rect.left(),
                                 rect.height())
            elif self._resizeHandle == 'top':
                new_rect = QRectF(rect.left(), pos.y(),
                                 rect.width(),
                                 rect.bottom() - pos.y())
            elif self._resizeHandle == 'bottom':
                new_rect = QRectF(rect.left(), rect.top(),
                                 rect.width(),
                                 pos.y() - rect.top())
            
            # Circle and square: keep equal width/height and keep center fixed
            if self._shape_type in ("circle", "square"):
                s = min(new_rect.width(), new_rect.height())
                if s > 5:
                    # Keep scene center fixed: center = pos() + rect().center()
                    scene_center = self.pos() + self.rect().center()
                    self.setRect(QRectF(0, 0, s, s))
                    self.setPos(scene_center.x() - s / 2, scene_center.y() - s / 2)
                    return
            if new_rect.width() > 5 and new_rect.height() > 5:
                self.setRect(new_rect)
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self._resizing = False
        self._resizeHandle = None
        super().mouseReleaseEvent(event)
        # Notify change after resize is complete
        self._notifyChanged()


class SliceScrollGraphicsView(QGraphicsView):
    """Custom QGraphicsView that handles mouse wheel scrolling to change slices."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.channelViewWindow = None  # Will be set by parent window
    
    def setChannelViewWindow(self, channel_view):
        """Set reference to the parent channel view window."""
        self.channelViewWindow = channel_view
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events to change the displayed slice."""
        if self.channelViewWindow is None:
            super().wheelEvent(event)
            return
        
        # Get wheel delta (positive = scroll up, negative = scroll down)
        delta = event.angleDelta().y()
        
        # Only handle vertical scrolling
        if delta == 0:
            super().wheelEvent(event)
            return
        
        # Determine direction: scroll up = next slice, scroll down = previous slice
        # (or reverse, depending on user preference - using standard: scroll up = increase)
        if delta > 0:
            # Scroll up - go to next slice (higher index)
            new_slice = min(self.channelViewWindow.currentSlice + 1, 
                          self.channelViewWindow.nSlices - 1)
        else:
            # Scroll down - go to previous slice (lower index)
            new_slice = max(self.channelViewWindow.currentSlice - 1, 0)
        
        # Only update if slice actually changed
        if new_slice != self.channelViewWindow.currentSlice:
            self.channelViewWindow.currentSlice = new_slice
            
            # Update slider position
            self.channelViewWindow.sliceSlider.setValue(new_slice)
            
            # Update labels immediately
            self.channelViewWindow.sliceLabel.setText(f'Slice: {new_slice + 1}/{self.channelViewWindow.nSlices}')
            if new_slice < len(self.channelViewWindow.pps.times):
                time_delay = self.channelViewWindow.pps.times[new_slice]
                self.channelViewWindow.timeLabel.setText(f'Time: {time_delay:.2f} ps')
            else:
                self.channelViewWindow.timeLabel.setText('')
            
            # Update image (use debounced update like slider)
            self.channelViewWindow._updateTimer.stop()
            self.channelViewWindow._updateTimer.start(10)
            
            # Update plot marker if ROIs exist
            if self.channelViewWindow.roiItems:
                self.channelViewWindow._updateRoiPlot()
        
        # Accept the event to prevent default scrolling behavior
        event.accept()


class PuprisaChannelViewWindow(QMainWindow):
    """
    Window for viewing a single channel with slice navigation and ROI functionality.
    Shows one image at a time with a slider to navigate through time points.
    Includes draggable/resizable ROI and plot showing ROI signal vs time delay.
    """
    
    def __init__(self, pps_obj=None, channel_num=1, fileName=None, header=None):
        super().__init__()
        
        # Single-channel window; ``pps`` may be None until File → Open Stack…
        self.pps = pps_obj
        self.channelNum = 1
        if pps_obj is not None:
            self.fileName = fileName or getattr(pps_obj, "filename", None)
            self.nSlices = len(pps_obj.images)
        else:
            self.fileName = fileName
            self.nSlices = 0
        self.header = header or {}
        self._phasorWindow = None
        
        # Current slice (0-based for indexing)
        self.currentSlice = 0
        
        # Flag to prevent concurrent updates
        self._updating = False
        
        # Timer for debouncing rapid slider updates
        self._updateTimer = QTimer()
        self._updateTimer.setSingleShot(True)
        self._updateTimer.timeout.connect(self._doUpdateImage)
        
        # ROI management - support multiple ROIs
        self.roiItems = []  # List of {"roi_id": str, "rect_item": DraggableROI, "color": str} — active ROIs only
        self.imagePixmap = None  # Store the current pixmap for coordinate conversion
        self.pixmapRect = None  # Store actual pixmap rect in scene coordinates
        self._roiColorIndex = 0  # Index into ROI_COLOR_PALETTE for next ROI
        
        # Timer for debouncing ROI updates
        self._roiUpdateTimer = QTimer()
        self._roiUpdateTimer.setSingleShot(True)
        self._roiUpdateTimer.timeout.connect(self._updateRoiPlot)
        
        # Colormap settings
        self.colormap_vmin = None  # Store min for colormap scaling
        self.colormap_vmax = None  # Store max for colormap scaling
        self.use_colormap = True  # Flag to enable/disable colormap
        self.colormap_mode = 'std_dev'  # Scale mode: 'std_dev', 'full_range', 'custom'
        self.custom_vmin = None  # Custom min value
        self.custom_vmax = None  # Custom max value
        
        # Set window properties
        if self.pps is not None:
            title = Path(str(self.fileName)).name if self.fileName else "Channel"
            self.setWindowTitle(f"{title} — puprisa")
        else:
            self.setWindowTitle("puprisa — File → Open Stack…")
        self.setMinimumSize(1000, 600)
        
        # Set window flags to ensure it's a top-level window
        self.setWindowFlags(Qt.Window)
        
        print(
            f"PuprisaChannelViewWindow: init (stack loaded={self.pps is not None}, n_slices={self.nSlices})"
        )
        
        # Initialize UI
        self.initUI()
        
        # Create menu bar
        self.createMenuBar()

        if self.pps is not None:
            self.refreshMaskList()
            self._mask_autoload_done = False
        else:
            self._mask_autoload_done = True

        self._set_stack_menus_enabled(self.pps is not None)
        
        print("PuprisaChannelViewWindow: Window initialized successfully")
    
    def initUI(self):
        """Initialize the user interface."""
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        mainLayout = QVBoxLayout(centralWidget)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setSpacing(10)
        
        # Create title label
        if self.nSlices == 0:
            self.titleLabel = QLabel("No stack loaded — use File → Open Stack…")
        else:
            self.titleLabel = QLabel(
                f"Channel {self.channelNum} — Slice {self.currentSlice + 1}/{self.nSlices}"
            )
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        mainLayout.addWidget(self.titleLabel)
        
        # Create splitter for image and plot
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Image with ROI
        imageWidget = QWidget()
        imageLayout = QVBoxLayout(imageWidget)
        imageLayout.setContentsMargins(0, 0, 0, 0)
        
        # Create graphics view for interactive ROI with mouse wheel scrolling
        self.graphicsView = SliceScrollGraphicsView()
        self.graphicsView.setChannelViewWindow(self)
        self.graphicsScene = QGraphicsScene()
        self.graphicsView.setScene(self.graphicsScene)
        self.graphicsView.setMinimumSize(400, 400)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.graphicsView.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        imageLayout.addWidget(self.graphicsView)
        
        # Add colorbar scale below the image (moved from right side)
        colorbarWidget = QWidget()
        colorbarLayout = QVBoxLayout(colorbarWidget)
        colorbarLayout.setContentsMargins(0, 5, 0, 0)
        
        colorbarTitle = QLabel("Signal Scale")
        colorbarTitle.setAlignment(Qt.AlignCenter)
        colorbarTitle.setStyleSheet("font-weight: bold; font-size: 10px;")
        colorbarLayout.addWidget(colorbarTitle)
        
        # Create matplotlib figure for colorbar
        self.colorbarFigure = Figure(figsize=(4, 1.0))
        self.colorbarFigure.subplots_adjust(bottom=0.4, top=0.9, left=0.1, right=0.95)
        self.colorbarCanvas = FigureCanvas(self.colorbarFigure)
        self.colorbarCanvas.setMinimumHeight(80)  # Ensure enough space for labels
        self.colorbarAxes = self.colorbarFigure.add_subplot(111)
        colorbarLayout.addWidget(self.colorbarCanvas)
        
        imageLayout.addWidget(colorbarWidget)
        
        splitter.addWidget(imageWidget)
        
        # Right side: Plot
        plotWidget = QWidget()
        plotLayout = QVBoxLayout(plotWidget)
        plotLayout.setContentsMargins(0, 0, 0, 0)
        
        plotTitle = QLabel("ROI Signal vs Time Delay")
        plotTitle.setAlignment(Qt.AlignCenter)
        plotTitle.setStyleSheet("font-weight: bold; font-size: 12px;")
        plotLayout.addWidget(plotTitle)
        
        # Create matplotlib figure for ROI signal plot
        self.plotFigure = Figure(figsize=(4, 4))
        self.plotFigure.subplots_adjust(left=0.15, bottom=0.18, right=0.95, top=0.95)
        self.plotCanvas = FigureCanvas(self.plotFigure)
        self.plotAxes = self.plotFigure.add_subplot(111)
        self.plotAxes.set_xlabel('Time Delay (ps)')
        self.plotAxes.set_ylabel('Average Signal (arb. u.)')
        self.plotAxes.grid(True, alpha=0.3)
        plotLayout.addWidget(self.plotCanvas)
        
        # ROI list (saved ROIs with labels) - moved from left side
        roiListLabel = QLabel("Active ROIs:")
        roiListLabel.setStyleSheet("font-weight: bold; font-size: 10px;")
        plotLayout.addWidget(roiListLabel)
        self.roiListWidget = QListWidget()
        self.roiListWidget.setMaximumHeight(120)
        self.roiListWidget.itemSelectionChanged.connect(self.onRoiListSelectionChanged)
        self.roiListWidget.itemDoubleClicked.connect(self._onRoiListItemDoubleClicked)
        plotLayout.addWidget(self.roiListWidget)

        # ROI controls grouped with ROI list (bottom-right)
        roiControlsLayout = QHBoxLayout()
        shapeLabel = QLabel("Shape:")
        roiControlsLayout.addWidget(shapeLabel)
        self.roiShapeCombo = QComboBox()
        self.roiShapeCombo.addItems(["Rectangle", "Square", "Circle", "Ellipse"])
        roiControlsLayout.addWidget(self.roiShapeCombo)
        createRoiButton = QPushButton("Create")
        createRoiButton.clicked.connect(self.createROI)
        deleteRoiButton = QPushButton("Delete")
        deleteRoiButton.clicked.connect(self.deleteSelectedROI)
        renameRoiButton = QPushButton("Rename")
        renameRoiButton.clicked.connect(self.renameSelectedROI)
        roiControlsLayout.addWidget(createRoiButton)
        roiControlsLayout.addWidget(deleteRoiButton)
        roiControlsLayout.addWidget(renameRoiButton)
        roiControlsLayout.addStretch()
        plotLayout.addLayout(roiControlsLayout)

        # Mask layers panel
        maskListLabel = QLabel("Mask layers:")
        maskListLabel.setStyleSheet("font-weight: bold; font-size: 10px;")
        plotLayout.addWidget(maskListLabel)
        self.maskListWidget = QListWidget()
        self.maskListWidget.setMaximumHeight(100)
        self.maskListWidget.itemSelectionChanged.connect(self.onMaskListSelectionChanged)
        self.maskListWidget.itemChanged.connect(self.onMaskListItemChanged)
        plotLayout.addWidget(self.maskListWidget)
        maskControlsLayout = QHBoxLayout()
        renameMaskButton = QPushButton("Rename")
        renameMaskButton.clicked.connect(self.renameSelectedMaskLayer)
        commentMaskButton = QPushButton("Edit comment…")
        commentMaskButton.clicked.connect(self.editSelectedMaskComment)
        removeMaskButton = QPushButton("Remove")
        removeMaskButton.clicked.connect(self.removeSelectedMaskLayer)
        maskControlsLayout.addWidget(renameMaskButton)
        maskControlsLayout.addWidget(commentMaskButton)
        maskControlsLayout.addWidget(removeMaskButton)
        maskControlsLayout.addStretch()
        plotLayout.addLayout(maskControlsLayout)
        
        splitter.addWidget(plotWidget)
        
        # Set splitter proportions (60% image, 40% plot)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        
        mainLayout.addWidget(splitter)
        
        # Create slider and controls
        controlsLayout = QHBoxLayout()
        
        # Slider label
        self.sliceLabel = QLabel(f'Slice: {self.currentSlice + 1}/{self.nSlices}')
        self.sliceLabel.setMinimumWidth(100)
        controlsLayout.addWidget(self.sliceLabel)
        
        # Slider
        self.sliceSlider = QSlider(Qt.Horizontal)
        self.sliceSlider.setMinimum(0)
        self.sliceSlider.setMaximum(max(0, self.nSlices - 1))
        self.sliceSlider.setValue(0)
        self.sliceSlider.valueChanged.connect(self.onSliderChanged)
        self.sliceSlider.sliderReleased.connect(self.onSliderReleased)
        controlsLayout.addWidget(self.sliceSlider)
        
        # Time delay label (if available)
        self.timeLabel = QLabel('')
        self.timeLabel.setMinimumWidth(120)
        controlsLayout.addWidget(self.timeLabel)
        
        mainLayout.addLayout(controlsLayout)
        
        # Set focus for keyboard events
        self.setFocusPolicy(Qt.StrongFocus)
    
    def createMenuBar(self):
        """Create the menu bar with color scale options."""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        open_action = file_menu.addAction("Open Stack…")
        open_action.triggered.connect(self.mnuOpenStack)
        file_menu.addSeparator()
        about_action = file_menu.addAction("About puprisa")
        about_action.triggered.connect(self.mnuAbout)
        file_menu.addSeparator()
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(lambda: QApplication.instance().quit())
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Color Scale submenu
        color_scale_menu = view_menu.addMenu('Color Scale')
        
        # Standard deviation option (default)
        std_dev_action = color_scale_menu.addAction('± Standard Deviation')
        std_dev_action.setCheckable(True)
        std_dev_action.setChecked(True)  # Default
        std_dev_action.triggered.connect(lambda: self.setColorScaleMode('std_dev'))
        self.std_dev_action = std_dev_action
        
        # Full range option
        full_range_action = color_scale_menu.addAction('Full Range (Min to Max)')
        full_range_action.setCheckable(True)
        full_range_action.triggered.connect(lambda: self.setColorScaleMode('full_range'))
        self.full_range_action = full_range_action
        
        # Custom range option
        custom_action = color_scale_menu.addAction('Custom Range...')
        custom_action.setCheckable(True)
        custom_action.triggered.connect(lambda: self.setColorScaleMode('custom'))
        self.custom_action = custom_action
        
        # Processing menu
        processing_menu = menubar.addMenu('Processing')
        
        # Background Subtraction submenu
        bg_subtract_menu = processing_menu.addMenu('Background Subtraction')
        
        # Negative delays option (default)
        bg_neg_delays_action = bg_subtract_menu.addAction('Negative Time Delays (Pixel-wise)')
        bg_neg_delays_action.triggered.connect(lambda: self.applyBackgroundSubtraction('negative_delays', pixelwise=True))
        
        bg_neg_delays_scalar_action = bg_subtract_menu.addAction('Negative Time Delays (Whole Image)')
        bg_neg_delays_scalar_action.triggered.connect(lambda: self.applyBackgroundSubtraction('negative_delays', pixelwise=False))
        
        bg_subtract_menu.addSeparator()
        
        # First n images option
        bg_first_n_action = bg_subtract_menu.addAction('First N Images...')
        bg_first_n_action.triggered.connect(self.showBackgroundSubtractionDialog)
        
        bg_subtract_menu.addSeparator()
        
        # Reset background subtraction option
        bg_reset_action = bg_subtract_menu.addAction('Reset Background Subtraction')
        bg_reset_action.triggered.connect(self.resetBackgroundSubtraction)
        
        processing_menu.addSeparator()
        intensity_threshold_action = processing_menu.addAction('Intensity threshold…')
        intensity_threshold_action.triggered.connect(self.runIntensityThreshold)
        
        # ROI menu
        roi_menu = menubar.addMenu('ROI')
        export_rois_action = roi_menu.addAction('Export ROIs...')
        export_rois_action.triggered.connect(self.exportRoisToJson)
        load_rois_action = roi_menu.addAction('Load ROIs from file...')
        load_rois_action.triggered.connect(self.loadRoisFromFile)
        roi_menu.addSeparator()
        clear_rois_action = roi_menu.addAction('Clear All ROIs')
        clear_rois_action.triggered.connect(self.clearAllROIs)

        # Mask menu
        mask_menu = menubar.addMenu('Mask')
        mask_add_action = mask_menu.addAction('Add mask from file…')
        mask_add_action.triggered.connect(self.addMaskFromFile)
        mask_export_all_action = mask_menu.addAction('Export all masks…')
        mask_export_all_action.triggered.connect(self.exportAllMasks)
        mask_export_selected_action = mask_menu.addAction('Export selected mask…')
        mask_export_selected_action.triggered.connect(self.exportSelectedMask)
        mask_load_masks_action = mask_menu.addAction('Load masks from directory…')
        mask_load_masks_action.triggered.connect(self.autoloadMasksFromImageDir)

        # Analysis menu
        analysis_menu = menubar.addMenu('Analysis')
        phasor_action = analysis_menu.addAction('Phasor Analysis...')
        phasor_action.triggered.connect(self.openPhasorAnalysis)

        self._menus_require_stack = [
            view_menu,
            processing_menu,
            roi_menu,
            mask_menu,
            analysis_menu,
        ]

    def mnuAbout(self):
        """About dialog."""
        QMessageBox.about(
            self,
            "About PUPRISA",
            "PUPRISA: PUmp PRobe Image Stack Analysis.\n"
            "Warren Lab: Duke University.\n"
            "Created 2011 by J. W. Wilson.\n"
            "Contributions by P. Samineni, M.J. Simpson, M.C. Fischer\n\n"
            "Python port — single stack / channel view.",
        )

    def mnuOpenStack(self):
        """File dialog to open one stack (DukeScan, pickle, or Mathematica)."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open pump-probe stack",
            str(Path.cwd()),
            "Stacks (*.tif *.TIF *.tiff *.pkl *.pickle);;"
            "TIFF (*.tif *.TIF *.tiff);;"
            "Pickle (*.pkl *.pickle);;"
            "All files (*)",
        )
        if path:
            self.load_stack_from_path(path)

    def load_stack_from_path(self, path_str, data_type=None):
        """
        Load one ``PPS`` stack from disk. Replaces current stack and resets the UI.

        Parameters
        ----------
        path_str : str
            File path.
        data_type : str, optional
            ``\"DukeScan\"``, ``\"pickle\"``, or ``\"mathematica\"``. If None, guess from extension
            or prompt.
        """
        path = Path(path_str)
        if not path.is_file():
            QMessageBox.warning(self, "Open", f"File not found:\n{path_str}")
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if data_type is None:
                guessed = _guess_pps_data_type(path)
                if guessed is None:
                    choice, ok = QInputDialog.getItem(
                        self,
                        "Stack format",
                        "Choose format for this file:",
                        ["DukeScan (TIFF)", "pickle", "mathematica"],
                        0,
                        False,
                    )
                    if not ok:
                        return
                    key = choice.lower()
                    if "pickle" in key:
                        data_type = "pickle"
                    elif "mathematica" in key:
                        data_type = "mathematica"
                    else:
                        data_type = "DukeScan"
                else:
                    data_type = guessed

            new_pps = PPS(str(path), dataType=data_type)
        except Exception as e:
            QMessageBox.critical(self, "Open", f"Failed to load stack:\n{e}")
            return
        finally:
            QApplication.restoreOverrideCursor()

        self.reset_ui_for_new_stack(new_pps, str(path))

    def reset_ui_for_new_stack(self, new_pps, file_name=None):
        """Replace ``self.pps`` and clear scene/UI state so a new stack has a clean session."""
        self._updateTimer.stop()
        self._roiUpdateTimer.stop()

        if getattr(self, "_phasorWindow", None) is not None:
            try:
                self._phasorWindow.close()
            except Exception:
                pass
            self._phasorWindow = None

        for roi_info in self.roiItems[:]:
            try:
                self.graphicsScene.removeItem(roi_info["rect_item"])
            except Exception:
                pass
        self.roiItems.clear()
        self.roiListWidget.clear()

        self.graphicsScene.clear()
        self.pixmapRect = None
        self.imagePixmap = None
        self._lastPixmapRect = None

        self.pps = new_pps
        self.fileName = file_name or getattr(new_pps, "filename", None)
        self.channelNum = 1
        self.nSlices = len(new_pps.images)
        self.currentSlice = 0
        self.colormap_vmin = None
        self.colormap_vmax = None
        self.custom_vmin = None
        self.custom_vmax = None
        self._roiColorIndex = 0
        self._mask_autoload_done = False

        h0, w0 = new_pps.image_dimensions[0], new_pps.image_dimensions[1]
        self.header = {
            "fullHeaderText": (
                f"File: {Path(str(self.fileName)).name}\n"
                f"Slices: {self.nSlices}\n"
                f"Dimensions: {h0} x {w0}"
            ),
            "nSlices": self.nSlices,
            "numofchannels": 1,
        }

        self.sliceSlider.setMaximum(max(0, self.nSlices - 1))
        self.sliceSlider.setValue(0)
        self.sliceSlider.setEnabled(self.nSlices > 0)

        if self.pps is not None:
            self.setWindowTitle(f"{Path(str(self.fileName)).name} — puprisa")
        else:
            self.setWindowTitle("puprisa")

        self.titleLabel.setText(
            f"Channel {self.channelNum} — Slice {self.currentSlice + 1}/{max(1, self.nSlices)}"
        )
        self.sliceLabel.setText(f"Slice: {self.currentSlice + 1}/{max(1, self.nSlices)}")
        self.timeLabel.setText("")

        self.plotAxes.clear()
        self.plotAxes.set_xlabel("Time Delay (ps)")
        self.plotAxes.set_ylabel("Average Signal (arb. u.)")
        self.plotAxes.grid(True, alpha=0.3)
        self.plotCanvas.draw()

        try:
            self.colorbarAxes.clear()
            self.colorbarCanvas.draw()
        except Exception:
            pass

        self.refreshMaskList()
        self._set_stack_menus_enabled(True)
        # Restore default color scale (± standard deviation) and menu state; replaces a plain updateImage().
        self.setColorScaleMode("std_dev")

    def _set_stack_menus_enabled(self, enabled):
        for m in getattr(self, "_menus_require_stack", []):
            m.setEnabled(enabled)
    
    def setColorScaleMode(self, mode):
        """Set the color scale mode and update the display."""
        # If custom mode, prompt for values first
        if mode == 'custom':
            # Store previous mode in case user cancels
            previous_mode = self.colormap_mode
            if self.showCustomScaleDialog():
                # User confirmed - set mode to custom
                self.colormap_mode = mode
                self._recalculateColorScale()
                self.updateImage()
            else:
                # User cancelled - restore previous mode
                self.colormap_mode = previous_mode
        else:
            # Set mode immediately for non-custom modes
            self.colormap_mode = mode
            # Reset custom values when switching away from custom mode
            self.custom_vmin = None
            self.custom_vmax = None
            # Recalculate scale and update image
            self._recalculateColorScale()
            self.updateImage()
        
        # Update action check states based on current mode
        self.std_dev_action.setChecked(self.colormap_mode == 'std_dev')
        self.full_range_action.setChecked(self.colormap_mode == 'full_range')
        self.custom_action.setChecked(self.colormap_mode == 'custom')
    
    def showCustomScaleDialog(self):
        """Show dialog to input custom color scale values. Returns True if accepted, False if cancelled."""
        if self.pps is None:
            return False
        # Get current data range for reference
        all_data = np.concatenate([img.flatten() for img in self.pps.images])
        data_min = float(np.nanmin(all_data))
        data_max = float(np.nanmax(all_data))
        
        # Use existing custom values or current scale values as defaults
        if self.custom_vmin is None:
            default_min = self.colormap_vmin if self.colormap_vmin is not None else data_min
        else:
            default_min = self.custom_vmin
        
        if self.custom_vmax is None:
            default_max = self.colormap_vmax if self.colormap_vmax is not None else data_max
        else:
            default_max = self.custom_vmax
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Custom Color Scale')
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        # Min value input
        min_spinbox = QDoubleSpinBox()
        min_spinbox.setRange(-1e10, 1e10)
        min_spinbox.setValue(default_min)
        min_spinbox.setDecimals(6)
        min_spinbox.setSingleStep((data_max - data_min) / 100)
        layout.addRow('Minimum:', min_spinbox)
        
        # Max value input
        max_spinbox = QDoubleSpinBox()
        max_spinbox.setRange(-1e10, 1e10)
        max_spinbox.setValue(default_max)
        max_spinbox.setDecimals(6)
        max_spinbox.setSingleStep((data_max - data_min) / 100)
        layout.addRow('Maximum:', max_spinbox)
        
        # Info label
        info_label = QLabel(f'Data range: [{data_min:.4e}, {data_max:.4e}]')
        info_label.setStyleSheet('color: gray; font-size: 9px;')
        layout.addRow('', info_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            self.custom_vmin = min_spinbox.value()
            self.custom_vmax = max_spinbox.value()
            
            # Ensure min < max
            if self.custom_vmin >= self.custom_vmax:
                self.custom_vmax = self.custom_vmin + 1.0
            
            return True
        else:
            return False
    
    def _recalculateColorScale(self):
        """Recalculate color scale based on current mode."""
        if self.pps is None:
            return
        all_data = np.concatenate([img.flatten() for img in self.pps.images])
        
        if self.colormap_mode == 'std_dev':
            # ± standard deviation
            std = np.nanstd(all_data)
            mean = np.nanmean(all_data)
            abs_max = max(abs(mean - std), abs(mean + std))
            # Use symmetric scaling around zero
            self.colormap_vmin = -abs_max
            self.colormap_vmax = abs_max
        
        elif self.colormap_mode == 'full_range':
            # Full min to max range (actual data range)
            self.colormap_vmin = float(np.nanmin(all_data))
            self.colormap_vmax = float(np.nanmax(all_data))
        
        elif self.colormap_mode == 'custom':
            # Use custom values
            if self.custom_vmin is not None and self.custom_vmax is not None:
                self.colormap_vmin = self.custom_vmin
                self.colormap_vmax = self.custom_vmax
            else:
                # Fallback to std_dev if custom values not set
                std = np.nanstd(all_data)
                mean = np.nanmean(all_data)
                abs_max = max(abs(mean - std), abs(mean + std))
                self.colormap_vmin = -abs_max
                self.colormap_vmax = abs_max
    
    def applyBackgroundSubtraction(self, method="negative_delays", n=None, pixelwise=True):
        """Apply background subtraction to the PPS object and update display."""
        if self.pps is None:
            return
        try:
            # Apply background subtraction
            self.pps.subtractFirst(method=method, n=n, pixelwise=pixelwise, inplace=True)
            
            # Recalculate color scale since data has changed
            self._recalculateColorScale()
            
            # Update image display
            self.updateImage()
            
            # Update ROI plot if ROIs exist
            if self.roiItems:
                self._updateRoiPlot()
            
            # Show confirmation
            method_str = "negative time delays" if method == "negative_delays" else f"first {n} images"
            pixelwise_str = "pixel-wise" if pixelwise else "whole image"
            print(f"Background subtraction applied: {method_str} ({pixelwise_str})")
        except Exception as e:
            print(f"Error applying background subtraction: {e}")
            import traceback
            traceback.print_exc()
    
    def resetBackgroundSubtraction(self):
        """Reset background subtraction to restore original images."""
        if self.pps is None:
            return
        try:
            # Reset background subtraction in PPS object
            self.pps.resetBackgroundSubtraction()
            
            # Recalculate color scale since data has changed
            self._recalculateColorScale()
            
            # Update image display
            self.updateImage()
            
            # Update ROI plot if ROIs exist
            if self.roiItems:
                self._updateRoiPlot()
            
            print("Background subtraction reset - original images restored.")
        except Exception as e:
            print(f"Error resetting background subtraction: {e}")
            import traceback
            traceback.print_exc()
    
    def showBackgroundSubtractionDialog(self):
        """Show dialog to configure first N images background subtraction."""
        if self.pps is None:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle('Background Subtraction - First N Images')
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        # Number of images input
        n_spinbox = QSpinBox()
        n_spinbox.setRange(1, len(self.pps.images))
        n_spinbox.setValue(1)
        n_spinbox.setSingleStep(1)
        layout.addRow('Number of images (N):', n_spinbox)
        
        # Pixel-wise vs whole image option (radio buttons)
        pixelwise_checkbox = QCheckBox('Pixel-wise subtraction')
        pixelwise_checkbox.setChecked(True)
        wholeimage_checkbox = QCheckBox('Whole image subtraction')
        wholeimage_checkbox.setChecked(False)
        
        # Make them mutually exclusive
        def toggle_pixelwise(checked):
            if checked:
                wholeimage_checkbox.setChecked(False)
        
        def toggle_wholeimage(checked):
            if checked:
                pixelwise_checkbox.setChecked(False)
        
        pixelwise_checkbox.toggled.connect(toggle_pixelwise)
        wholeimage_checkbox.toggled.connect(toggle_wholeimage)
        
        method_layout = QVBoxLayout()
        method_layout.addWidget(pixelwise_checkbox)
        method_layout.addWidget(wholeimage_checkbox)
        method_widget = QWidget()
        method_widget.setLayout(method_layout)
        layout.addRow('Subtraction method:', method_widget)
        
        # Info label
        info_label = QLabel(f'Total images in stack: {len(self.pps.images)}')
        info_label.setStyleSheet('color: gray; font-size: 9px;')
        layout.addRow('', info_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            n = n_spinbox.value()
            pixelwise = pixelwise_checkbox.isChecked()
            self.applyBackgroundSubtraction(method='first_n', n=n, pixelwise=pixelwise)
    
    def createROI(self):
        """Create a new ROI with the selected shape and add it to the stack (active immediately)."""
        if not self.pixmapRect:
            self.updateImage()
            QTimer.singleShot(100, self.createROI)
            return
        shape_map = {"Rectangle": "rectangle", "Square": "square", "Circle": "circle", "Ellipse": "ellipse"}
        shape_type = shape_map.get(self.roiShapeCombo.currentText(), "rectangle")
        color = ROI_COLOR_PALETTE[self._roiColorIndex % len(ROI_COLOR_PALETTE)]
        self._roiColorIndex += 1
        center_x = self.pixmapRect.center().x()
        center_y = self.pixmapRect.center().y()
        roi_size = min(self.pixmapRect.width(), self.pixmapRect.height()) * 0.1
        # Standardize ROI geometry: local rect at (0,0,w,h), scene position = top-left.
        item_rect = QRectF(0, 0, roi_size, roi_size)
        rect_item = DraggableROI(item_rect, color=color, shape_type=shape_type)
        rect_item.setPos(QPointF(center_x - roi_size / 2, center_y - roi_size / 2))
        rect_item.setRoiChangedCallback(self.onROIChanged)
        rect_item.setZValue(10)
        self.graphicsScene.addItem(rect_item)
        params = self._sceneRectToRoiParams(shape_type, rect_item.getSceneRect())
        if params is None:
            self.graphicsScene.removeItem(rect_item)
            return
        default_label = f"ROI {len(self.pps.rois) + 1}"
        roi_id = self.pps.add_roi(shape=shape_type, params=params, label=default_label)
        self.roiItems.append({"roi_id": roi_id, "rect_item": rect_item, "color": color})
        self.refreshRoiList()
        self._updateRoiPlot()
    
    def deleteSelectedROI(self):
        """Delete the currently selected ROI from PPS and scene."""
        item = self.roiListWidget.currentItem()
        if not item:
            return
        roi_id = item.data(Qt.UserRole)
        if roi_id is None:
            return
        if self.pps.remove_roi(roi_id):
            for roi_info in self.roiItems[:]:
                if roi_info["roi_id"] == roi_id:
                    self.graphicsScene.removeItem(roi_info["rect_item"])
                    self.roiItems.remove(roi_info)
                    break
            self.refreshRoiList()
            self._updateRoiPlot()

    def renameSelectedROI(self):
        """Rename the currently selected ROI (same as double-click)."""
        self._onRoiListItemDoubleClicked(self.roiListWidget.currentItem())

    def _onRoiListItemDoubleClicked(self, list_item):
        """Edit ROI label on double-click."""
        if not list_item:
            return
        roi_id = list_item.data(Qt.UserRole)
        if roi_id is None:
            return
        current = self.pps.get_roi_label(roi_id) or roi_id
        label, ok = QInputDialog.getText(self, "Rename ROI", "New name:", QLineEdit.Normal, current)
        if ok and label.strip():
            self.pps.set_roi_label(roi_id, label.strip())
            self.refreshRoiList()
            self._updateRoiPlot()
    
    def _getRoisJsonPath(self):
        """Path to rois.json in the image directory (deterministic for autoload)."""
        if not self.fileName:
            return None
        p = Path(self.fileName)
        return p.parent / f"{p.stem}_ROIs.json"

    def exportRoisToJson(self):
        """Export all active ROIs to rois.json in the image directory."""
        if roi_entry_to_dict is None:
            print("ROI export: pps.roi_entry_to_dict not available")
            return
        path = self._getRoisJsonPath()
        if path is None:
            print("ROI export: no image path")
            return
        # If the default ROI JSON already exists, ask the user whether to overwrite or choose a new filename.
        if path.exists():
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Export ROIs")
            msg_box.setText(f"An ROI file already exists:\n{path}\n\nDo you want to overwrite it?")
            msg_box.setInformativeText("Choose 'Overwrite' to replace the existing file, "
                                       "'Save As…' to export to a different filename, or 'Cancel' to abort.")
            overwrite_button = msg_box.addButton("Overwrite", QMessageBox.AcceptRole)
            save_as_button = msg_box.addButton("Save As…", QMessageBox.ActionRole)
            cancel_button = msg_box.addButton(QMessageBox.Cancel)
            msg_box.setDefaultButton(overwrite_button)
            msg_box.exec()
            clicked = msg_box.clickedButton()
            if clicked == cancel_button:
                # User cancelled the export
                return
            if clicked == save_as_button:
                # Let user pick a different filename (JSON only)
                new_path_str, _ = QFileDialog.getSaveFileName(
                    self,
                    "Export ROIs As",
                    str(path),
                    "JSON (*.json)"
                )
                if not new_path_str:
                    # User cancelled out of Save As dialog
                    return
                path = Path(new_path_str)
        # Build list of ROI dicts from active roiItems (sync with PPS)
        self.updateROIMask()
        rois_data = {
            "image_dimensions": list(self.pps.image_dimensions),
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "rois": [],
        }
        for roi_info in self.roiItems:
            roi_id = roi_info["roi_id"]
            entry = next((r for r in self.pps.rois if r["id"] == roi_id), None)
            if entry is not None:
                rois_data["rois"].append(roi_entry_to_dict(entry, include_id=True))
        try:
            with open(path, "w") as f:
                json.dump(rois_data, f, indent=2)
            print(f"Exported {len(rois_data['rois'])} ROIs to {path}")

        except Exception as e:
            print(f"Export ROIs failed: {e}")
    
    def _clearAllRoisInternal(self):
        """Remove all active ROIs from PPS and scene without prompting."""
        if not self.roiItems:
            return
        for roi_info in self.roiItems:
            roi_id = roi_info["roi_id"]
            # Remove from PPS (ignore return, we want to best-effort clear)
            self.pps.remove_roi(roi_id)
            # Remove the graphics item from the scene
            self.graphicsScene.removeItem(roi_info["rect_item"])
        self.roiItems.clear()
        # Reset color index so new ROIs start from the beginning of the palette
        self._roiColorIndex = 0
        self.refreshRoiList()
        self._updateRoiPlot()
        self.updateROIMask()

    def clearAllROIs(self):
        """Ask for confirmation, then delete all active ROIs."""
        if not self.roiItems:
            return
        reply = QMessageBox.question(
            self,
            "Clear All ROIs",
            "This will delete all active ROIs for this channel.\n\nAre you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self._clearAllRoisInternal()

    # ---- Mask layer UI ----
    def refreshMaskList(self):
        """Rebuild the mask list widget from PPS mask layers (checkbox = enabled)."""
        self.maskListWidget.blockSignals(True)
        self.maskListWidget.clear()
        if self.pps is None:
            self.maskListWidget.blockSignals(False)
            return
        for layer_id in self.pps.get_all_mask_layer_ids():
            layer = self.pps.get_mask_layer(layer_id)
            if layer is None:
                continue
            label = layer.get("label") or layer_id
            item = QListWidgetItem(f"{label} [{layer_id}]")
            item.setData(Qt.ItemDataRole.UserRole, layer_id)
            item.setCheckState(Qt.CheckState.Checked if layer.get("enabled", True) else Qt.CheckState.Unchecked)
            self.maskListWidget.addItem(item)
        self.maskListWidget.blockSignals(False)

    def onMaskListSelectionChanged(self):
        """Handle mask list selection change."""
        pass

    def onMaskListItemChanged(self, item):
        """Checkbox toggled: set layer enabled/disabled."""
        layer_id = item.data(Qt.ItemDataRole.UserRole)
        if layer_id is None:
            return
        enabled = item.checkState() == Qt.CheckState.Checked
        try:
            self.pps.set_mask_layer_enabled(layer_id, enabled)
            self.updateImage()
            self._updateRoiPlot()
        except KeyError:
            pass

    def _maskChangeRefresh(self):
        """After any mask add/remove/rename: refresh list, image, and ROI plot."""
        self.refreshMaskList()
        self.updateImage()
        self._updateRoiPlot()

    def _getImageDirectory(self):
        """Image directory for mask NPZ autoload/export."""
        if not self.fileName:
            return None
        return Path(self.fileName).parent

    def addMaskFromFile(self):
        """Load one or more mask NPZ files and add as layers."""
        img_dir = self._getImageDirectory()
        path, _ = QFileDialog.getOpenFileName(
            self, "Add mask from file",
            str(img_dir) if img_dir else ".",
            "NPZ (*.npz);;All files (*)"
        )
        if not path:
            return
        self._loadMaskNpzAndAdd(Path(path))

    def _loadMaskNpzAndAdd(self, path, silent=False):
        """Load a single NPZ and add as mask layer. Returns True if added."""
        expected = self.pps.image_dimensions

        # First, try to interpret as a phasor ROI mask export (multiple masks in one NPZ)
        try:
            data = np.load(path, allow_pickle=True)
        except Exception:
            data = None

        if data is not None and "masks" in data:
            try:
                masks = np.asarray(data["masks"], dtype=bool)
                if masks.ndim == 3:
                    n_masks, h, w = masks.shape
                    if (h, w) == tuple(expected):
                        # Optional metadata
                        def _get_str(arr, default=""):
                            if arr is None:
                                return default
                            try:
                                # 0-d or object arrays
                                if hasattr(arr, "item"):
                                    return str(arr.item())
                            except Exception:
                                pass
                            try:
                                return str(arr)
                            except Exception:
                                return default

                        labels_arr = data["labels"] if "labels" in data else None
                        shapes_arr = data["shapes"] if "shapes" in data else None
                        colors_arr = data["colors"] if "colors" in data else None
                        global_comment = _get_str(data["comment"], "") if "comment" in data else ""
                        date_str = _get_str(data["date"], "") if "date" in data else ""

                        for idx in range(n_masks):
                            label = (
                                _get_str(labels_arr[idx])
                                if labels_arr is not None and len(labels_arr) > idx
                                else f"Phasor ROI {idx + 1}"
                            )
                            comment = global_comment
                            mask_layer = masks[idx]
                            self.pps.add_mask_layer(
                                mask_layer,
                                label=label,
                                comment=comment,
                                date=date_str,
                                enabled=True,
                                restrict_to_effective=False,
                            )
                        self._maskChangeRefresh()
                        return True
            except Exception as e:
                if not silent:
                    QMessageBox.warning(
                        self,
                        "Load mask",
                        f"Error interpreting {path.name} as phasor ROI masks:\n{e}",
                    )
                # Fall through to standard single-mask loader

        # Fallback: standard single-mask NPZ format
        loaded = _mask_npz_load(path, expected)
        if loaded is None:
            if not silent:
                QMessageBox.warning(
                    self, "Load mask",
                    f"Could not load mask from {path.name}\n(shape mismatch or invalid file)."
                )
            return False
        try:
            self.pps.add_mask_layer(
                loaded["mask"],
                label=loaded["label"],
                comment=loaded["comment"],
                date=loaded["date"],
                enabled=True,
                restrict_to_effective=False,
            )
            self._maskChangeRefresh()
            return True
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "Load mask", str(e))
            return False

    def exportAllMasks(self):
        """Export each mask layer to its own NPZ in the image directory."""
        img_dir = self._getImageDirectory()
        if img_dir is None:
            QMessageBox.warning(self, "Export masks", "No image path set.")
            return
        img_dir = Path(img_dir)
        def sanitize(s):
            return re.sub(r'[^\w\-.]', '_', str(s))[:50]
        for layer_id in self.pps.get_all_mask_layer_ids():
            layer = self.pps.get_mask_layer(layer_id)
            if layer is None:
                continue
            label = sanitize(layer.get("label") or layer_id)
            date = layer.get("date", "")[:19].replace(":", "-")
            fname = f"mask_{label}_{date}.npz" if date else f"mask_{layer_id}.npz"
            path = img_dir / fname
            _mask_npz_save(
                path,
                layer["mask"],
                self.pps.image_dimensions,
                label=layer.get("label", ""),
                comment=layer.get("comment", ""),
                date=layer.get("date", ""),
            )
        QMessageBox.information(
            self, "Export masks",
            f"Exported {len(self.pps.get_all_mask_layer_ids())} mask(s) to {img_dir}."
        )

    def exportSelectedMask(self):
        """Export the selected mask layer to one NPZ file."""
        item = self.maskListWidget.currentItem()
        if item is None:
            QMessageBox.warning(self, "Export mask", "Select a mask layer first.")
            return
        layer_id = item.data(Qt.ItemDataRole.UserRole)
        layer = self.pps.get_mask_layer(layer_id)
        if layer is None:
            return
        img_dir = self._getImageDirectory()
        default_dir = str(img_dir) if img_dir else "."
        label = (layer.get("label") or layer_id).replace(" ", "_")[:30]
        date = (layer.get("date", "")[:19]).replace(":", "-")
        default_name = f"mask_{label}_{date}.npz" if date else f"mask_{layer_id}.npz"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export selected mask",
            str(Path(default_dir) / default_name),
            "NPZ (*.npz);;All files (*)"
        )
        if not path:
            return
        _mask_npz_save(
            path,
            layer["mask"],
            self.pps.image_dimensions,
            label=layer.get("label", ""),
            comment=layer.get("comment", ""),
            date=layer.get("date", ""),
        )
        QMessageBox.information(self, "Export mask", f"Saved to {path}.")

    def renameSelectedMaskLayer(self):
        """Rename the selected mask layer."""
        item = self.maskListWidget.currentItem()
        if item is None:
            QMessageBox.warning(self, "Rename mask", "Select a mask layer first.")
            return
        layer_id = item.data(Qt.ItemDataRole.UserRole)
        layer = self.pps.get_mask_layer(layer_id)
        current = (layer or {}).get("label") or layer_id
        label, ok = QInputDialog.getText(self, "Rename mask layer", "Label:", QLineEdit.Normal, current)
        if ok and label is not None:
            try:
                self.pps.set_mask_layer_label(layer_id, label.strip() or layer_id)
                self._maskChangeRefresh()
            except KeyError:
                pass

    def editSelectedMaskComment(self):
        """Edit the comment of the selected mask layer."""
        item = self.maskListWidget.currentItem()
        if item is None:
            QMessageBox.warning(self, "Edit comment", "Select a mask layer first.")
            return
        layer_id = item.data(Qt.ItemDataRole.UserRole)
        layer = self.pps.get_mask_layer(layer_id)
        current = (layer or {}).get("comment", "")
        comment, ok = QInputDialog.getText(self, "Edit mask comment", "Comment:", QLineEdit.Normal, current)
        if ok and comment is not None:
            try:
                self.pps.set_mask_layer_comment(layer_id, comment)
                self._maskChangeRefresh()
            except KeyError:
                pass

    def removeSelectedMaskLayer(self):
        """Remove the selected mask layer."""
        item = self.maskListWidget.currentItem()
        if item is None:
            QMessageBox.warning(self, "Remove mask", "Select a mask layer first.")
            return
        layer_id = item.data(Qt.ItemDataRole.UserRole)
        try:
            self.pps.remove_mask_layer(layer_id)
            self._maskChangeRefresh()
        except KeyError:
            pass

    def runIntensityThreshold(self):
        """Run intensity threshold and add the result as a new mask layer (exportable from Mask panel)."""
        if self.pps is None:
            return
        dlg = IntensityThresholdDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        threshold, sigma, projection_use_mask = dlg.getParams()
        try:
            new_mask = self.pps.intensity_threshold(
                threshold=threshold,
                sigma=sigma,
                projection_use_mask=projection_use_mask,
                inplace=False,
            )
            label = "Intensity threshold (Li)" if threshold == "Li" else f"Intensity threshold ({threshold})"
            self.pps.add_mask_layer(new_mask, label=label, enabled=True)
            self._maskChangeRefresh()
            QMessageBox.information(
                self,
                "Intensity threshold",
                "New mask layer added. You can enable/disable, rename, or export it from the Mask layers panel below.",
            )
        except Exception as e:
            QMessageBox.critical(self, "Intensity threshold", f"Error applying intensity threshold:\n{str(e)}")

    def autoloadMasksFromImageDir(self, silent=False):
        """Scan image directory for mask_*.npz (or NPZ with mask+shape) and add matching layers."""
        if self.pps is None:
            return
        img_dir = self._getImageDirectory()
        if img_dir is None:
            if not silent:
                QMessageBox.warning(self, "Load masks", "No image path set.")
            return
        img_dir = Path(img_dir)
        expected = self.pps.image_dimensions
        # Prefer mask_*.npz then any .npz with mask and shape
        added = 0
        for path in sorted(img_dir.glob("mask_*.npz")):
            if self._loadMaskNpzAndAdd(path, silent=True):
                added += 1
        for path in sorted(img_dir.glob("*.npz")):
            if path.name.startswith("mask_"):
                continue
            if self._loadMaskNpzAndAdd(path, silent=True):
                added += 1
        if not silent and added > 0:
            QMessageBox.information(self, "Load masks", f"Loaded {added} mask(s) from {img_dir}.")

    def loadRoisFromFile(self):
        """Load ROIs from a JSON file (manual override; path from dialog)."""
        if roi_dict_to_entry is None or roi_shape_to_mask is None:
            print("ROI load: pps helpers not available")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Load ROIs", str(Path(self.fileName).parent if self.fileName else "."), "JSON (*.json)")
        if not path:
            return
        # After the user has selected a file, optionally clear existing ROIs before loading.
        if self.roiItems:
            reply = QMessageBox.question(
                self,
                "Load ROIs",
                "There are existing ROIs in this channel.\n\n"
                "Do you want to clear all existing ROIs before importing from file?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._clearAllRoisInternal()
        self._loadRoisFromJsonPath(Path(path))

    def _loadRoisFromJsonPath(self, path):
        """Load ROIs from a JSON file at path; add to PPS and create items."""
        if roi_dict_to_entry is None or roi_shape_to_mask is None:
            return
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception as e:
            print(f"Load ROIs failed: {e}")
            return
        rois_list = data.get("rois", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        if not rois_list:
            return
        dims = data.get("image_dimensions")
        if dims is not None and list(dims) != list(self.pps.image_dimensions):
            QMessageBox.warning(self, "Load ROIs", f"JSON image_dimensions {dims} differ from current {list(self.pps.image_dimensions)}. ROIs may be scaled/clipped.")
        for i, d in enumerate(rois_list):
            entry = roi_dict_to_entry(d, self.pps.image_dimensions)
            roi_id = self.pps.add_roi(shape=entry["shape"], params=entry["params"], label=entry["label"])
            if not self.pixmapRect:
                continue
            scene_rect = self._roiParamsToSceneRect(entry["shape"], entry["params"])
            if scene_rect is None:
                continue
            item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
            color = ROI_COLOR_PALETTE[(len(self.roiItems) + i) % len(ROI_COLOR_PALETTE)]
            rect_item = DraggableROI(item_rect, color=color, shape_type=entry["shape"])
            rect_item.setPos(scene_rect.topLeft())
            rect_item.setRoiChangedCallback(self.onROIChanged)
            rect_item.setZValue(10)
            self.graphicsScene.addItem(rect_item)
            self.roiItems.append({"roi_id": roi_id, "rect_item": rect_item, "color": color})
        # Advance color index so newly created ROIs continue from the end of the current list
        self._roiColorIndex = len(self.roiItems)
        self.refreshRoiList()
        self._updateRoiPlot()
        print(f"Loaded {len(rois_list)} ROIs from {path}")

    def _autoloadRoisFromJson(self):
        """Load ROIs from rois.json in the image directory if present (called when channel view is shown).

        This is invoked every time the channel view window is shown. If an ROI JSON file with the
        appropriate filename exists, the current ROIs are cleared and the JSON ROIs are imported so
        that the GUI always reflects the contents of that file.
        """
        path = self._getRoisJsonPath()
        if path is None or not path.exists():
            return
        # Clear any existing ROIs so the GUI matches the JSON on each open.
        if self.roiItems:
            self._clearAllRoisInternal()
        self._loadRoisFromJsonPath(path)
        print(f"Autoloaded ROIs from {path}")
    
    def onRoiListSelectionChanged(self):
        """Handle ROI list selection change."""
        pass
    
    def refreshRoiList(self):
        """Populate ROI list from active roiItems (sync with scene)."""
        self.roiListWidget.clear()
        for roi_info in self.roiItems:
            roi_id = roi_info["roi_id"]
            label = self.pps.get_roi_label(roi_id) or roi_id
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, roi_id)
            # Color indicator icon
            qcol = _matplotlib_color_to_qt(roi_info.get("color", "#1f77b4"))
            pm = QPixmap(12, 12)
            pm.fill(qcol)
            item.setIcon(QIcon(pm))
            self.roiListWidget.addItem(item)
    
    def onROIChanged(self):
        """Handle ROI rectangle changes."""
        self.updateROIMask()
        self._roiUpdateTimer.stop()
        self._roiUpdateTimer.start(50)

    def _loadPpsRoisToDisplay(self):
        """Create ROI items for PPS ROIs that don't have display items yet (from shape + params)."""
        if not self.pixmapRect:
            return
        existing_ids = {r["roi_id"] for r in self.roiItems}
        for i, roi_entry in enumerate(self.pps.rois):
            roi_id = roi_entry["id"]
            if roi_id in existing_ids:
                continue
            shape_type = roi_entry.get("shape", "rectangle")
            params = roi_entry.get("params", {})
            scene_rect = self._roiParamsToSceneRect(shape_type, params)
            if scene_rect is None:
                continue
            item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
            color = ROI_COLOR_PALETTE[i % len(ROI_COLOR_PALETTE)]
            rect_item = DraggableROI(item_rect, color=color, shape_type=shape_type)
            rect_item.setPos(scene_rect.topLeft())
            rect_item.setRoiChangedCallback(self.onROIChanged)
            rect_item.setZValue(10)
            self.graphicsScene.addItem(rect_item)
            self.roiItems.append({"roi_id": roi_id, "rect_item": rect_item, "color": color})
        # Ensure the next ROI color starts after all currently active ROIs
        self._roiColorIndex = len(self.roiItems)
        self.refreshRoiList()
    
    def _itemToMask(self, roi_item):
        """Convert any draggable ROI item to boolean mask using shape + params."""
        if not roi_item or not self.pixmapRect or roi_shape_to_mask is None:
            return None
        shape_type = roi_item.getShapeType()
        scene_rect = roi_item.getSceneRect()
        params = self._sceneRectToRoiParams(shape_type, scene_rect)
        if params is None:
            return None
        return roi_shape_to_mask(shape_type, params, self.pps.image_dimensions)
    
    def _signalForMask(self, roi_mask, mask_on=True):
        """Compute average signal vs time for an arbitrary boolean mask (same logic as PPS.get_roi_signal)."""
        if roi_mask is None or roi_mask.shape != self.pps.image_dimensions:
            return None
        combined = (roi_mask & self.pps.mask) if mask_on else roi_mask
        n_pixels = np.sum(combined)
        if n_pixels == 0:
            return np.zeros(len(self.pps.images))
        signals = [np.mean(img[combined]) for img in self.pps.images]
        return np.array(signals)
    
    def _updateRoiPlot(self):
        """Update the ROI plot - show all visible ROIs (saved and unsaved) with color-matched lines."""
        if not self.roiItems:
            self.plotAxes.clear()
            self.plotAxes.set_xlabel('Time Delay (ps)')
            self.plotAxes.set_ylabel('Average Signal (arb. u.)')
            self.plotAxes.grid(True, alpha=0.3)
            self.plotCanvas.draw()
            return
        
        times = np.asarray(self.pps.times, dtype=np.float64)
        self.plotAxes.clear()
        
        for i, roi_info in enumerate(self.roiItems):
            roi_id = roi_info["roi_id"]
            color = roi_info["color"]
            roi_mask = self.pps.get_roi_mask(roi_id)
            label = self.pps.get_roi_label(roi_id) or roi_id
            if roi_mask is None:
                continue
            signal = self._signalForMask(roi_mask)
            if signal is None:
                continue
            
            n_pts = min(len(times), len(signal))
            self.plotAxes.plot(times[:n_pts], np.asarray(signal)[:n_pts], color=color,
                              marker='o', markersize=3, label=label)
        
        self.plotAxes.set_xlabel('Time Delay (ps)')
        self.plotAxes.set_ylabel('Average Signal (arb. u.)')
        self.plotAxes.grid(True, alpha=0.3)
        if self.roiItems:
            self.plotAxes.legend(fontsize=8, loc="best")

        # Fit axis limits to plotted TA data
        if self.plotAxes.lines:
            self.plotAxes.relim()
            self.plotAxes.autoscale_view(tight=True)

        # Mark current slice
        if self.currentSlice < len(times):
            current_time = times[self.currentSlice]
            ylim = self.plotAxes.get_ylim()
            self.plotAxes.axvline(x=current_time, color='green', linestyle='--', linewidth=2)
            self.plotAxes.set_ylim(ylim)
        
        self.plotCanvas.draw()
    
    def _updateColorbar(self, vmin, vmax):
        """Update the colorbar scale display."""
        self.colorbarAxes.clear()
        
        # Use the actual colormap scale values (which reflect the selected mode)
        # These are the values that will be used for symmetric scaling
        actual_vmin = self.colormap_vmin if self.colormap_vmin is not None else vmin
        actual_vmax = self.colormap_vmax if self.colormap_vmax is not None else vmax
        
        # Create a gradient from actual_vmin to actual_vmax
        n_colors = 256
        gradient = np.linspace(actual_vmin, actual_vmax, n_colors).reshape(1, -1)
        
        # Apply colormap to gradient - this will return symmetric values
        rgb_gradient, vmin_used, vmax_used = apply_diverging_colormap(gradient, vmin=actual_vmin, vmax=actual_vmax)
        # Reshape for imshow: (1, n_colors, 3) -> (n_colors, 3) then reshape to (1, n_colors, 3)
        rgb_gradient = rgb_gradient[0, :, :].reshape(1, n_colors, 3)
        
        # Display gradient using the symmetric values that are actually used
        self.colorbarAxes.imshow(rgb_gradient, aspect='auto', extent=[vmin_used, vmax_used, 0, 1])
        self.colorbarAxes.set_xlabel('Signal Value', fontsize=9)
        self.colorbarAxes.set_yticks([])
        
        # Show actual values at the ends (and zero if it's within range)
        tick_positions = []
        tick_labels = []
        
        # Always show min and max at the ends (these are the symmetric values actually used)
        tick_positions.append(vmin_used)
        tick_labels.append(f'{vmin_used:.3e}')
        
        # Show zero if it's within the range
        if vmin_used < 0 < vmax_used:
            tick_positions.append(0)
            tick_labels.append('0')
        
        tick_positions.append(vmax_used)
        tick_labels.append(f'{vmax_used:.3e}')
        
        self.colorbarAxes.set_xticks(tick_positions)
        self.colorbarAxes.set_xticklabels(tick_labels, fontsize=8)
        
        self.colorbarCanvas.draw()
    
    def updateROIMask(self):
        """Update PPS ROI params from current ROI items (shape + params)."""
        if not self.pixmapRect:
            return
        for roi_info in self.roiItems:
            roi_id = roi_info["roi_id"]
            item = roi_info["rect_item"]
            shape_type = item.getShapeType()
            params = self._sceneRectToRoiParams(shape_type, item.getSceneRect())
            if params is not None:
                self.pps.update_roi(roi_id, shape=shape_type, params=params)
        self._updateRoiPlot()
    
    def _sceneToPixelCoords(self, scene_rect):
        """Convert scene coordinates to image pixel coordinates."""
        if not self.pixmapRect:
            print("_sceneToPixelCoords: pixmapRect is None")
            return None
        
        # Get ROI rect relative to pixmap
        roi_in_pixmap = scene_rect.intersected(self.pixmapRect)
        if roi_in_pixmap.isEmpty():
            return None
        
        # Calculate scale factors
        pixmap_width = self.pixmapRect.width()
        pixmap_height = self.pixmapRect.height()
        image_width, image_height = self.pps.image_dimensions[1], self.pps.image_dimensions[0]
        
        if pixmap_width <= 0 or pixmap_height <= 0:
            print(f"_sceneToPixelCoords: Invalid pixmap size: {pixmap_width}x{pixmap_height}")
            return None
        
        scale_x = image_width / pixmap_width
        scale_y = image_height / pixmap_height
        
        # Convert coordinates (relative to pixmap top-left)
        x1 = (roi_in_pixmap.left() - self.pixmapRect.left()) * scale_x
        y1 = (roi_in_pixmap.top() - self.pixmapRect.top()) * scale_y
        x2 = (roi_in_pixmap.right() - self.pixmapRect.left()) * scale_x
        y2 = (roi_in_pixmap.bottom() - self.pixmapRect.top()) * scale_y
        
        return QRectF(x1, y1, x2 - x1, y2 - y1)

    def _sceneRectToRoiParams(self, shape_type, scene_rect):
        """Convert scene rect to ROI params dict (image pixel coords) for backend/JSON."""
        pixel_rect = self._sceneToPixelCoords(scene_rect)
        if pixel_rect is None:
            return None
        h, w = self.pps.image_dimensions[0], self.pps.image_dimensions[1]
        x1, y1 = pixel_rect.left(), pixel_rect.top()
        pw, ph = pixel_rect.width(), pixel_rect.height()
        # Scene origin is top-left; image row 0 is top (same as main window projection)
        im_y1 = max(0, min(y1, h - 1e-9))
        im_h = min(ph, h - im_y1)
        cx = x1 + pw / 2.0
        cy_im = im_y1 + im_h / 2.0
        if shape_type == "rectangle":
            return {"x": x1, "y": im_y1, "width": pw, "height": im_h}
        if shape_type == "square":
            s = min(pw, im_h)
            return {"center_x": cx, "center_y": cy_im, "size": s}
        if shape_type == "circle":
            r = min(pw, ph) / 2.0
            return {"center_x": cx, "center_y": cy_im, "radius": r}
        if shape_type == "ellipse":
            return {"center_x": cx, "center_y": cy_im, "radius_x": pw / 2.0, "radius_y": im_h / 2.0, "angle_deg": 0.0}
        return None

    def _roiParamsToSceneRect(self, shape_type, params):
        """Convert ROI params (image pixel coords) to scene QRectF for placing item."""
        if not self.pixmapRect:
            return None
        h, w = self.pps.image_dimensions
        pix_w, pix_h = self.pixmapRect.width(), self.pixmapRect.height()
        if pix_w <= 0 or pix_h <= 0:
            return None

        # Convert ROI params -> bounding box in image pixel coords (x,y,width,height)
        if shape_type == "rectangle":
            x = float(params["x"])
            y = float(params["y"])
            bw = float(params["width"])
            bh = float(params["height"])
        elif shape_type == "square":
            cx = float(params["center_x"])
            cy = float(params["center_y"])
            s = float(params["size"])
            x, y, bw, bh = cx - s / 2.0, cy - s / 2.0, s, s
        elif shape_type == "circle":
            cx = float(params["center_x"])
            cy = float(params["center_y"])
            r = float(params["radius"])
            x, y, bw, bh = cx - r, cy - r, 2 * r, 2 * r
        elif shape_type == "ellipse":
            cx = float(params["center_x"])
            cy = float(params["center_y"])
            rx = float(params["radius_x"])
            ry = float(params["radius_y"])
            x, y, bw, bh = cx - rx, cy - ry, 2 * rx, 2 * ry
        else:
            return None

        # Image pixel bbox (row y at top) -> scene bbox (pixmap top = row 0)
        sx = self.pixmapRect.left() + (x / w) * pix_w
        sy = self.pixmapRect.top() + (y / h) * pix_h
        sw = (bw / w) * pix_w
        sh = (bh / h) * pix_h
        return QRectF(sx, sy, sw, sh)

    def resizeEvent(self, event):
        """Refit the image to the view when the window is resized (no full re-render)."""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._fitChannelImageView)

    def _fitChannelImageView(self):
        """Scale the scene so the full image fits in the graphics view viewport."""
        if not getattr(self, "graphicsView", None) or not getattr(self, "graphicsScene", None):
            return
        r = self.graphicsScene.itemsBoundingRect()
        if r.width() <= 0 or r.height() <= 0:
            return
        self.graphicsView.fitInView(r, Qt.AspectRatioMode.KeepAspectRatio)
    
    def showEvent(self, event):
        """Override showEvent to update image, autoload ROIs, and autoload masks after window is shown."""
        super().showEvent(event)
        if self.pps is None:
            return
        self._updateTimer.stop()
        QTimer.singleShot(0, self.updateImage)
        # Autoload ROIs from JSON file (e.g., *_ROIs.json)
        QTimer.singleShot(200, self._autoloadRoisFromJson)
        # Autoload masks from NPZ files (mask_*.npz) - only once per window instance
        if not getattr(self, "_mask_autoload_done", True):
            self._mask_autoload_done = True
            QTimer.singleShot(250, lambda: self.autoloadMasksFromImageDir(silent=True))

    def openPhasorAnalysis(self):
        """Open the Phasor Analysis window, optionally applying current active masks."""
        if self.pps is None:
            QMessageBox.information(self, "Phasor Analysis", "Load a stack first (File → Open Stack…).")
            return
        reply = QMessageBox.question(
            self,
            "Phasor Analysis",
            "Apply current active masks to phasor analysis?\n\n"
            "If you choose Yes, pixels that are masked out in the Channel View\n"
            "will be excluded from the phasor plot and from any phasor ROI masks.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        apply_masks = reply == QMessageBox.StandardButton.Yes

        # Always create a fresh window so the choice applies for this launch
        self._phasorWindow = PhasorAnalysisWindow(self, apply_effective_mask=apply_masks)
        self._phasorWindow.show()
        self._phasorWindow.raise_()
        self._phasorWindow.activateWindow()
    
    def onSliderChanged(self, value):
        """Handle slider value change (called continuously during dragging)."""
        # Update the slice index
        self.currentSlice = value
        
        # Update labels immediately for responsive UI
        self.sliceLabel.setText(f'Slice: {self.currentSlice + 1}/{self.nSlices}')
        # Update time label if available
        if self.currentSlice < len(self.pps.times):
            time_delay = self.pps.times[self.currentSlice]
            self.timeLabel.setText(f'Time: {time_delay:.2f} ps')
        else:
            self.timeLabel.setText('')
        
        # Debounce image updates
        self._updateTimer.stop()
        self._updateTimer.start(10)
        
        # Update plot marker if ROIs exist
        if self.pps.get_all_roi_ids():
            self._updateRoiPlot()
    
    def onSliderReleased(self):
        """Handle slider release - update image immediately when user stops dragging."""
        # Cancel any pending timer and update immediately
        self._updateTimer.stop()
        self.updateImage()
    
    def _doUpdateImage(self):
        """Internal method called by timer to update image."""
        self.updateImage()
    
    def updateImage(self):
        """Update the image display with current slice."""
        # Prevent concurrent updates
        if self._updating:
            return

        if self.pps is None:
            return
        
        if self.nSlices == 0:
            print("PuprisaChannelViewWindow: No slices available")
            return
        
        # Check if window/widget is still valid
        if not self.isVisible() or not self.graphicsView:
            return
        
        # Ensure currentSlice is within bounds
        self.currentSlice = max(0, min(self.currentSlice, self.nSlices - 1))
        
        self._updating = True
        try:
            # Get image slice from PPS object
            imageSlice = self.pps.images[self.currentSlice]
            
            # Validate image data
            if imageSlice is None:
                raise ValueError("Image slice is None")
            if not isinstance(imageSlice, np.ndarray):
                raise ValueError(f"Image slice is not a numpy array: {type(imageSlice)}")
            if imageSlice.ndim != 2:
                raise ValueError(f"Image slice must be 2D, got {imageSlice.ndim}D with shape {imageSlice.shape}")
            if imageSlice.size == 0:
                raise ValueError("Image slice is empty")
            
            # Check for invalid values
            if np.any(np.isnan(imageSlice)) or np.any(np.isinf(imageSlice)):
                print(f"Warning: Image slice contains NaN or Inf values, replacing with 0")
                imageSlice = np.nan_to_num(imageSlice, nan=0.0, posinf=0.0, neginf=0.0)
            
            effective_mask = np.asarray(self.pps.mask, dtype=bool)

            # Apply colormap: blue (negative) -> black (zero) -> red (positive)
            if self.use_colormap:
                # Initialize scale on first image if not set
                if self.colormap_vmin is None or self.colormap_vmax is None:
                    self._recalculateColorScale()
                
                # Apply colormap
                rgb_image, vmin_used, vmax_used = apply_diverging_colormap(
                    imageSlice, 
                    vmin=self.colormap_vmin, 
                    vmax=self.colormap_vmax
                )
                # Overlay masked-out pixels (excluded from analysis) as light gray
                rgb_image[~effective_mask] = [200, 200, 200]
                
                # Update colorbar
                self._updateColorbar(vmin_used, vmax_used)
                
                # Convert RGB numpy array to QImage
                height, width = rgb_image.shape[:2]
                # QImage expects bytes in RGB format
                rgb_bytes = rgb_image.tobytes()
                q_image = QImage(rgb_bytes, width, height, width * 3, QImage.Format_RGB888)
            else:
                # Grayscale fallback
                if imageSlice.dtype != np.uint8:
                    img_min = np.nanmin(imageSlice)
                    img_max = np.nanmax(imageSlice)
                    if img_max > img_min:
                        imageSlice = ((imageSlice - img_min) / (img_max - img_min) * 255).astype(np.uint8)
                    else:
                        imageSlice = np.zeros_like(imageSlice, dtype=np.uint8)
                else:
                    imageSlice = imageSlice.astype(np.uint8)
                # Overlay masked-out pixels as light gray (grayscale 200)
                imageSlice = imageSlice.astype(np.uint8)
                imageSlice[~effective_mask] = 200
                # Convert numpy array to QImage (grayscale)
                height, width = imageSlice.shape
                image_bytes = imageSlice.tobytes()
                q_image = QImage(image_bytes, width, height, width, QImage.Format_Grayscale8)
            
            # Convert QImage to QPixmap for display
            pixmap = QPixmap.fromImage(q_image)
            self.imagePixmap = pixmap
            
            # Store ROI shape+params before clearing (use PPS as source of truth)
            roi_backups = []
            for roi_info in self.roiItems:
                roi_id = roi_info["roi_id"]
                entry = next((r for r in self.pps.rois if r["id"] == roi_id), None)
                if entry is None:
                    continue
                roi_backups.append({
                    "roi_id": roi_id,
                    "color": roi_info["color"],
                    "shape_type": entry.get("shape", "rectangle"),
                    "params": entry.get("params", {}),
                })
            
            # Clear scene and add full-resolution pixmap; view transform fits it to the window
            self.graphicsScene.clear()
            self.roiItems = []
            pixmap_item = self.graphicsScene.addPixmap(pixmap)
            self.pixmapRect = pixmap_item.boundingRect()
            
            # Re-add ROI items from shape+params
            for backup in roi_backups:
                scene_rect = self._roiParamsToSceneRect(backup["shape_type"], backup["params"])
                if scene_rect is None:
                    continue
                item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
                rect_item = DraggableROI(item_rect, color=backup["color"], shape_type=backup["shape_type"])
                rect_item.setPos(scene_rect.topLeft())
                rect_item.setRoiChangedCallback(self.onROIChanged)
                rect_item.setZValue(10)
                self.graphicsScene.addItem(rect_item)
                self.roiItems.append({"roi_id": backup["roi_id"], "rect_item": rect_item, "color": backup["color"]})
            
            # Load any PPS ROIs that don't have rect_items yet (e.g., from pickle)
            self._loadPpsRoisToDisplay()
            
            # Store pixmap rect for next update
            self._lastPixmapRect = self.pixmapRect
            # Fit full image in view after layout has correct viewport size
            self._fitChannelImageView()
            QTimer.singleShot(0, self._fitChannelImageView)
            
            # Update title
            self.titleLabel.setText(f'Channel {self.channelNum} - Slice {self.currentSlice + 1}/{self.nSlices}')
            
            # Update labels
            self.sliceLabel.setText(f'Slice: {self.currentSlice + 1}/{self.nSlices}')
            
            # Update time delay label if available
            if self.currentSlice < len(self.pps.times):
                time_delay = self.pps.times[self.currentSlice]
                self.timeLabel.setText(f'Time: {time_delay:.2f} ps')
            else:
                self.timeLabel.setText('')
            
            print(f"PuprisaChannelViewWindow: Image updated for slice {self.currentSlice + 1}")
        except Exception as e:
            print(f"PuprisaChannelViewWindow: Error updating image: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._updating = False
