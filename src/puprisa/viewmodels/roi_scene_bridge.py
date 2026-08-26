# puprisa/viewmodels/roi_scene_bridge.py
"""Space-specific scene bridges for ROI graphics items.

Each bridge owns the mapping between an :class:`RoiItem`'s data-space
parameters and the geometry of a :class:`QGraphicsItem` inside a
:class:`QGraphicsScene`.

The ViewModel never performs coordinate arithmetic itself; it delegates
to the bridge instance injected at construction time.
"""
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPolygonF
from PySide6.QtWidgets import QGraphicsItem

from puprisa.model.entities import RoiItem
from puprisa.model.stack_manager import StackManager
from puprisa.ui.widgets.draggable_roi import DraggableROI, DraggablePolygonROI


# ----------------------------------------------------------------------
# Protocol
# ----------------------------------------------------------------------

class RoiSceneBridge():
    """Interface every coordinate-space bridge must implement."""

    def create_item(self, roi: RoiItem) -> QGraphicsItem:
        """Create and return a new QGraphicsItem for ``roi``."""
        raise NotImplementedError()

    def sync_item_from_params(self, roi: RoiItem) -> None:
        """Update an existing item's geometry from ``roi.params``."""
        raise NotImplementedError()

    def extract_params_from_item(self, roi: RoiItem) -> dict:
        """Return fresh params read from the item's current scene geometry."""
        raise NotImplementedError()

    def movement_bounds(self, roi: RoiItem) -> QRectF:
        """Return the scene-space rectangle item movement is restricted to."""
        raise NotImplementedError()

    def set_item_color(self, roi: RoiItem, color: str) -> None:
        """Recolor an existing item."""
        item = roi.graphics_item
        if item is not None:
            item.set_roi_color(color)

    @staticmethod
    def _scene_polygon_to_local(scene_polygon: QPolygonF) -> tuple[QPolygonF, QPointF]:
        """Split scene-space polygon geometry into local points and item position."""
        origin = scene_polygon.boundingRect().topLeft()
        local_polygon = QPolygonF([
            QPointF(point.x() - origin.x(), point.y() - origin.y())
            for point in scene_polygon
        ])
        return local_polygon, origin

    def _create_polygon_item(self, scene_polygon: QPolygonF, color: str) -> DraggablePolygonROI:
        """Create a polygon item with local vertices and a scene-space position."""
        local_polygon, origin = self._scene_polygon_to_local(scene_polygon)
        item = DraggablePolygonROI(local_polygon, color=color)
        item.setPos(origin)
        return item

    def _sync_polygon_item(self, item: DraggablePolygonROI, scene_polygon: QPolygonF) -> None:
        """Update a polygon item while preserving the local-geometry convention."""
        local_polygon, origin = self._scene_polygon_to_local(scene_polygon)
        item.setPolygon(local_polygon)
        item.setPos(origin)


# ----------------------------------------------------------------------
# Phasor space
# ----------------------------------------------------------------------

class PhasorRoiSceneBridge(RoiSceneBridge):
    """Map fixed (g, s) ∈ [-1, 1]^2 to a DENSITY_SIZE^2 scene square."""

    G_LIM = (-1.0, 1.0)
    S_LIM = (-1.0, 1.0)
    DENSITY_SIZE = 512

    def __init__(self) -> None:
        self.scene_rect = QRectF(0, 0, self.DENSITY_SIZE, self.DENSITY_SIZE)

    # ------------------------------ 1. Coordinate Mapping ------------------------------

    def _scene_point_to_gs(self, pt: QPointF) -> tuple[float, float]:
        g = self.G_LIM[0] + (pt.x() / self.DENSITY_SIZE) * (self.G_LIM[1] - self.G_LIM[0])
        s = self.S_LIM[1] - (pt.y() / self.DENSITY_SIZE) * (self.S_LIM[1] - self.S_LIM[0])
        return g, s

    def _gs_to_scene_point(self, g: float, s: float) -> QPointF:
        x = ((g - self.G_LIM[0]) / (self.G_LIM[1] - self.G_LIM[0]) * self.DENSITY_SIZE)
        y = ((self.S_LIM[1] - s) / (self.S_LIM[1] - self.S_LIM[0]) * self.DENSITY_SIZE)
        return QPointF(x, y)

    # ------------------------------ 2. Geometry Conversion ------------------------------
    def _params_to_scene_rect(self, shape: str, params: dict) -> QRectF | None:
        """Convert ROI params to a bounding box in scene coordinates."""
        if shape == "rectangle":
            g_left = params["x"]
            g_right = g_left + params["width"]
            s_bottom = params["y"]
            s_top = s_bottom + params["height"]
        elif shape == "circle":
            cg, cs, r = params["center_x"], params["center_y"], params["radius"]
            g_left, g_right = cg - r, cg + r
            s_bottom, s_top = cs - r, cs + r
        elif shape == "ellipse":
            cg, cs = params["center_x"], params["center_y"]
            rg, rs = params["radius_x"], params["radius_y"]
            g_left, g_right = cg - rg, cg + rg
            s_bottom, s_top = cs - rs, cs + rs
        else:
            return None

        p1 = self._gs_to_scene_point(g_left, s_top)
        p2 = self._gs_to_scene_point(g_right, s_bottom)
        return QRectF(p1, p2)

    def _scene_rect_to_params(self, shape: str, scene_rect: QRectF) -> dict | None:
        """Convert a scene bounding box to ROI params."""
        p1 = self._scene_point_to_gs(scene_rect.topLeft())
        p2 = self._scene_point_to_gs(scene_rect.bottomRight())
        g_left, s_top = p1[0], p1[1]
        g_right, s_bottom = p2[0], p2[1]

        w = g_right - g_left
        h = s_top - s_bottom
        cg = (g_left + g_right) / 2.0
        cs = (s_top + s_bottom) / 2.0

        if shape == "rectangle":
            return {"x": g_left, "y": s_bottom, "width": w, "height": h}
        if shape == "circle":
            return {"center_x": cg, "center_y": cs, "radius": min(w, h) / 2.0}
        if shape == "ellipse":
            return {"center_x": cg, "center_y": cs, "radius_x": w / 2.0, "radius_y": h / 2.0}
        return None

    def _vertices_to_scene_polygon(self, vertices: list[list[float]]) -> QPolygonF:
        """Convert a list of (g, s) vertices to a QPolygonF in scene coordinates."""
        pts = [self._gs_to_scene_point(v[0], v[1]) for v in vertices]
        return QPolygonF(pts)

    def _scene_polygon_to_vertices(self, polygon_item) -> list[list[float]]:
        """Convert a QPolygonF in scene coordinates to a list of (g, s) vertices."""
        scene_poly = polygon_item.get_scene_polygon()
        result = []
        for pt in scene_poly:
            g, s = self._scene_point_to_gs(pt)
            result.append([g, s])
        return result

    # ------------------------------ 3. Bridge scene and ROI params ------------------------------

    def create_item(self, roi: RoiItem) -> QGraphicsItem:
        if roi.shape == "polygon":
            scene_poly = self._vertices_to_scene_polygon(roi.params.get("vertices", []))
            return self._create_polygon_item(scene_poly, roi.color)

        scene_rect = self._params_to_scene_rect(roi.shape, roi.params)
        if scene_rect is None:
            raise ValueError(f"Unsupported shape: {roi.shape!r}")

        item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
        item = DraggableROI(item_rect, color=roi.color, shape_type=roi.shape)
        item.setPos(scene_rect.topLeft())
        return item

    def sync_item_from_params(self, roi: RoiItem) -> None:
        item = roi.graphics_item
        if item is None:
            return
        with item.silent_geometry_change():
            if roi.shape == "polygon":
                scene_poly = self._vertices_to_scene_polygon(roi.params.get("vertices", []))
                self._sync_polygon_item(item, scene_poly)
            else:
                scene_rect = self._params_to_scene_rect(roi.shape, roi.params)
                if scene_rect is None:
                    return
                item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
                item.setRect(item_rect)
                item.setPos(scene_rect.topLeft())

    def extract_params_from_item(self, roi: RoiItem) -> dict:
        item = roi.graphics_item
        if item is None:
            return roi.params

        if roi.shape == "polygon":
            return {"vertices": self._scene_polygon_to_vertices(item)}

        scene_rect = item.get_scene_rect()
        params = self._scene_rect_to_params(roi.shape, scene_rect)
        return params if params is not None else roi.params

    def movement_bounds(self, roi: RoiItem) -> QRectF:
        return QRectF(self.scene_rect)


# ----------------------------------------------------------------------
# Pixel space
# ----------------------------------------------------------------------

class PixelRoiSceneBridge(RoiSceneBridge):
    """Map image-space pixel coordinates to scene coordinates.

    The main window renders each slice at native resolution, therefore
    pixel coordinates are identical to scene coordinates.  The bridge
    keeps the same interface as ``PhasorRoiSceneBridge`` but performs no
    scaling; it only exists so the ViewModel stays space-agnostic.
    """

    def __init__(self, stack_manager: StackManager) -> None:
        self._stack_manager = stack_manager

    # ------------------------------ 1. Coordinate Mapping ------------------------------

    def _scene_point_to_pixel(self, pt: QPointF) -> tuple[float, float]:
        return pt.x(), pt.y()

    def _pixel_point_to_scene(self, pixel_col: float, pixel_row: float) -> QPointF:
        return QPointF(pixel_col, pixel_row)

    # ------------------------------ 2. Geometry Conversion ------------------------------

    def _params_to_scene_rect(self, shape: str, params: dict) -> QRectF | None:
        """Convert ROI params to a bounding box in scene coordinates."""
        if shape == "rectangle":
            x, y = params["x"], params["y"]
            w, h = params["width"], params["height"]
        elif shape == "circle":
            cx, cy, r = params["center_x"], params["center_y"], params["radius"]
            x, y, w, h = cx - r, cy - r, 2 * r, 2 * r
        elif shape == "ellipse":
            cx, cy = params["center_x"], params["center_y"]
            rx, ry = params["radius_x"], params["radius_y"]
            x, y, w, h = cx - rx, cy - ry, 2 * rx, 2 * ry
        else:
            return None

        p1 = self._pixel_point_to_scene(x, y)
        p2 = self._pixel_point_to_scene(x + w, y + h)
        return QRectF(p1, p2)

    def _scene_rect_to_params(self, shape: str, scene_rect: QRectF) -> dict | None:
        """Convert a scene bounding box to ROI params."""
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
            return {"center_x": cx, "center_y": cy, "radius_x": w / 2.0, "radius_y": h / 2.0}
        return None

    def _vertices_to_scene_polygon(self, vertices: list[list[float]]) -> QPolygonF:
        """Convert a list of pixel vertices to a QPolygonF in scene coordinates."""
        pts = [self._pixel_point_to_scene(v[0], v[1]) for v in vertices]
        return QPolygonF(pts)

    def _scene_polygon_to_vertices(self, polygon_item) -> list[list[float]]:
        """Convert a QPolygonF in scene coordinates back to pixel vertices."""
        scene_poly = polygon_item.get_scene_polygon()
        result = []
        for pt in scene_poly:
            col, row = self._scene_point_to_pixel(pt)
            result.append([col, row])
        return result

    # ------------------------------ 3. Bridge scene and ROI params ------------------------------

    def create_item(self, roi: RoiItem) -> QGraphicsItem:
        if roi.shape == "polygon":
            scene_poly = self._vertices_to_scene_polygon(roi.params.get("vertices", []))
            return self._create_polygon_item(scene_poly, roi.color)

        scene_rect = self._params_to_scene_rect(roi.shape, roi.params)
        if scene_rect is None:
            raise ValueError(f"Unsupported shape: {roi.shape!r}")

        item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
        item = DraggableROI(item_rect, color=roi.color, shape_type=roi.shape)
        item.setPos(scene_rect.topLeft())
        return item

    def sync_item_from_params(self, roi: RoiItem) -> None:
        item = roi.graphics_item
        if item is None:
            return

        with item.silent_geometry_change():
            if roi.shape == "polygon":
                scene_poly = self._vertices_to_scene_polygon(roi.params.get("vertices", []))
                self._sync_polygon_item(item, scene_poly)
            else:
                scene_rect = self._params_to_scene_rect(roi.shape, roi.params)
                if scene_rect is None:
                    return
                item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
                item.setRect(item_rect)
                item.setPos(scene_rect.topLeft())

    def extract_params_from_item(self, roi: RoiItem) -> dict:
        item = roi.graphics_item
        if item is None:
            return roi.params

        if roi.shape == "polygon":
            return {"vertices": self._scene_polygon_to_vertices(item)}

        scene_rect = item.get_scene_rect()
        params = self._scene_rect_to_params(roi.shape, scene_rect)
        return params if params is not None else roi.params

    def movement_bounds(self, roi: RoiItem) -> QRectF:
        stack_item = self._stack_manager.get_item_by_id(roi.stack_id)
        if stack_item is None:
            return QRectF()
        h, w = stack_item.pps.image_dimensions
        return QRectF(0, 0, w, h)
