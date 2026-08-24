# puprisa/controllers/pps_roi_controller.py
"""Image-space ROI controller for the main window.

This subclass handles ROIs defined in pixel coordinates.  The graphics
scene is the main ``ppsGraphicsView``.  Coordinate conversion between
pixel coordinates and scene coordinates uses the current displayed image
rectangle (``pixmap_rect``).

The controller receives a :class:`StackManager` for pps lookups and a
``QGraphicsScene`` for graphics-item placement.  It has no dependency on
:class:`PPSPlotController`.
"""

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPolygonF
from PySide6.QtWidgets import QGraphicsScene

import numpy as np

from puprisa.controllers.base_roi_controller import BaseRoiController
from puprisa.ui.widgets.draggable_roi import DraggableROI, DraggablePolygonROI
from puprisa.model.stack_manager import StackManager
from puprisa.utils.geometry_utils import shape_to_mask


class PPSRoiController(BaseRoiController):
    """Manage ROI rectangles/circles/ellipses/polygons in image space.

    Parameters
    ----------
    stack_manager : StackManager
        Shared stack model used for pps lookups.
    scene : QGraphicsScene
        Scene in which ROI graphics items are placed.
    roi_list_widget : QListWidget
        List widget displaying all ROIs.
    shape_combo : QComboBox
        Combo box for choosing the shape of new ROIs.
    """

    def __init__(
        self,
        stack_manager: StackManager,
        scene: QGraphicsScene,
        roi_list_widget,
        shape_combo,
    ):
        super().__init__(
            roi_list_widget, shape_combo, scene, stack_manager
        )
        self._pixmap_rect: QRectF | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_pixmap_rect(self, rect: QRectF):
        """Update the displayed image rectangle used for coordinate mapping."""
        self._pixmap_rect = QRectF(rect)
        # Update movement bounds for all ROI items.
        for roi in self.rois:
            item = roi.get("graphics_item")
            if item is not None:
                item.set_movement_bounds(self._pixmap_rect)

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------
    def _space_default_params(self, shape: str) -> dict:
        """Generate default pixel parameters at the centre of the current image."""
        if self._pixmap_rect is None:
            return {"x": 0, "y": 0, "width": 10, "height": 10}

        pps = self._current_pps()
        if pps is None:
            h_px, w_px = 512, 512
        else:
            h_px, w_px = pps.image_dimensions

        scene_center = self._pixmap_rect.center()
        pixel_center = self._scene_point_to_pixel(scene_center)

        size_px = min(w_px, h_px) * 0.1

        if shape == "rectangle":
            return {
                "x": pixel_center[0] - size_px / 2,
                "y": pixel_center[1] - size_px / 2,
                "width": size_px,
                "height": size_px,
            }
        if shape == "circle":
            return {
                "center_x": pixel_center[0],
                "center_y": pixel_center[1],
                "radius": size_px / 2,
            }
        if shape == "ellipse":
            return {
                "center_x": pixel_center[0],
                "center_y": pixel_center[1],
                "radius_x": size_px / 2,
                "radius_y": size_px / 2,
            }
        if shape == "polygon":
            radius = size_px / 2
            vertices = []
            for i in range(3):
                angle = 2 * np.pi * i / 3 - np.pi / 2
                px = pixel_center[0] + radius * np.cos(angle)
                py = pixel_center[1] + radius * np.sin(angle)
                vertices.append([px, py])
            return {"vertices": vertices}
        raise ValueError(f"Unsupported shape: {shape}")

    def _space_create_graphics_item(self, roi: dict):
        """Create a DraggableROI or DraggablePolygonROI in the scene."""
        shape = roi["shape"]
        params = roi["params"]
        color = roi["color"]

        if shape == "polygon":
            scene_poly = self._roi_params_to_scene_polygon(params)
            item = DraggablePolygonROI(scene_poly, color=color)
        else:
            scene_rect = self._roi_params_to_scene_rect(shape, params)
            if scene_rect is None:
                roi["graphics_item"] = None
                return
            item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
            item = DraggableROI(item_rect, color=color, shape_type=shape)
            item.setPos(scene_rect.topLeft())

        item.set_roi_changed_callback(
            lambda: self._on_graphics_item_changed(roi["id"])
        )
        item.set_movement_bounds(self._pixmap_rect)
        item.setZValue(10)
        self.scene.addItem(item)

        roi["graphics_item"] = item
        self._update_graphics_item_visibility(roi)

    def _space_update_params_from_item(self, roi: dict):
        """Extract pixel parameters from the ROI's graphics item."""
        item = roi.get("graphics_item")
        if item is None:
            return

        shape = roi["shape"]
        if shape == "polygon":
            roi["params"] = self._scene_polygon_to_roi_params(item)
        else:
            scene_rect = item.get_scene_rect()
            params = self._scene_rect_to_roi_params(shape, scene_rect)
            if params is not None:
                roi["params"] = params

    def _space_build_mask(self, roi: dict, pps) -> np.ndarray | None:
        """Build a 2D pixel keep-mask from the ROI's image-space geometry."""
        h, w = pps.image_dimensions
        xx, yy = np.meshgrid(np.arange(w), np.arange(h))
        return shape_to_mask(roi["shape"], roi["params"], xx, yy)

    # ------------------------------------------------------------------
    # Coordinate conversions: pixel <-> scene
    # ------------------------------------------------------------------
    def _scene_point_to_pixel(self, scene_pt: QPointF):
        """Scene QPointF -> pixel coordinates (col, row)."""
        if self._pixmap_rect is None:
            return 0.0, 0.0
        pps = self._current_pps()
        if pps is None:
            return 0.0, 0.0
        scale_x = pps.image_dimensions[1] / self._pixmap_rect.width()
        scale_y = pps.image_dimensions[0] / self._pixmap_rect.height()
        x = (scene_pt.x() - self._pixmap_rect.left()) * scale_x
        y = (scene_pt.y() - self._pixmap_rect.top()) * scale_y
        return x, y

    def _pixel_point_to_scene(self, pixel_col: float, pixel_row: float) -> QPointF:
        """Pixel coordinates -> scene QPointF."""
        if self._pixmap_rect is None:
            return QPointF()
        pps = self._current_pps()
        if pps is None:
            return QPointF()
        scale_x = self._pixmap_rect.width() / pps.image_dimensions[1]
        scale_y = self._pixmap_rect.height() / pps.image_dimensions[0]
        sx = self._pixmap_rect.left() + pixel_col * scale_x
        sy = self._pixmap_rect.top() + pixel_row * scale_y
        return QPointF(sx, sy)

    def _scene_rect_to_roi_params(self, shape: str, scene_rect: QRectF) -> dict | None:
        """Scene QRectF -> ROI parameters (pixel coordinates)."""
        p1 = self._scene_point_to_pixel(scene_rect.topLeft())
        p2 = self._scene_point_to_pixel(scene_rect.bottomRight())
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        w = x2 - x1
        h = y2 - y1
        cx = x1 + w / 2.0
        cy = y1 + h / 2.0

        if shape == "rectangle":
            return {"x": x1, "y": y1, "width": w, "height": h}
        if shape == "circle":
            return {"center_x": cx, "center_y": cy, "radius": min(w, h) / 2.0}
        if shape == "ellipse":
            return {
                "center_x": cx,
                "center_y": cy,
                "radius_x": w / 2.0,
                "radius_y": h / 2.0,
            }
        return None

    def _roi_params_to_scene_rect(self, shape: str, params: dict) -> QRectF | None:
        """ROI parameters (pixel coordinates) -> scene QRectF."""
        if shape == "rectangle":
            x, y = params["x"], params["y"]
            w, h = params["width"], params["height"]
        elif shape == "circle":
            cx, cy = params["center_x"], params["center_y"]
            r = params["radius"]
            x, y, w, h = cx - r, cy - r, 2 * r, 2 * r
        elif shape == "ellipse":
            cx, cy = params["center_x"], params["center_y"]
            rx, ry = params["radius_x"], params["radius_y"]
            x, y, w, h = cx - rx, cy - ry, 2 * rx, 2 * ry
        else:
            return None

        top_left = self._pixel_point_to_scene(x, y)
        bottom_right = self._pixel_point_to_scene(x + w, y + h)
        return QRectF(top_left, bottom_right)

    def _scene_polygon_to_roi_params(self, polygon_item) -> dict:
        """Scene polygon -> pixel vertices."""
        scene_poly = polygon_item.get_scene_polygon()
        vertices = []
        for pt in scene_poly:
            col, row = self._scene_point_to_pixel(pt)
            vertices.append([col, row])
        return {"vertices": vertices}

    def _roi_params_to_scene_polygon(self, params: dict) -> QPolygonF:
        """Pixel vertices -> scene polygon."""
        vertices = params.get("vertices", [])
        pts = [self._pixel_point_to_scene(v[0], v[1]) for v in vertices]
        return QPolygonF(pts)