# puprisa/ui/widgets/draggable_roi.py
from contextlib import contextmanager

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPolygonItem, QGraphicsRectItem

from puprisa.utils.color_utils import _matplotlib_color_to_qt


class ROIItemMixin:
    """Shared interaction, notification, and boundary behavior for ROI items."""

    def _init_roi_interaction(self) -> None:
        self._silent = False
        self._roi_changed_callback = None
        self._movement_bounds = None
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def set_roi_changed_callback(self, callback) -> None:
        self._roi_changed_callback = callback

    def set_movement_bounds(self, bounds_rect) -> None:
        """Restrict the item's scene-space bounding rectangle to the given bounds."""
        self._movement_bounds = QRectF(bounds_rect) if bounds_rect is not None else None

    @contextmanager
    def silent_geometry_change(self):
        """Suppress callbacks while geometry is being updated from the model."""
        previous = self._silent
        self._silent = True
        try:
            yield
        finally:
            self._silent = previous

    def _notify_changed(self) -> None:
        if not self._silent and self._roi_changed_callback:
            self._roi_changed_callback()

    def _bounded_position(self, value) -> QPointF:
        """Clamp a proposed item position so the full item remains in bounds."""
        new_pos = QPointF(value)
        if self._movement_bounds is None:
            return new_pos
        item_bounds = self.boundingRect()
        bounds = self._movement_bounds
        min_x = bounds.left() - item_bounds.left()
        min_y = bounds.top() - item_bounds.top()
        max_x = bounds.right() - item_bounds.right()
        max_y = bounds.bottom() - item_bounds.bottom()
        if max_x < min_x:
            max_x = min_x
        if max_y < min_y:
            max_y = min_y
        new_pos.setX(max(min_x, min(new_pos.x(), max_x)))
        new_pos.setY(max(min_y, min(new_pos.y(), max_y)))
        return new_pos

    def _bounded_local_point(self, local_point: QPointF) -> QPointF:
        """Clamp a local point to movement bounds and return it in local coordinates."""
        if self._movement_bounds is None:
            return QPointF(local_point)
        scene_point = self.mapToScene(local_point)
        bounds = self._movement_bounds
        scene_point.setX(max(bounds.left(), min(scene_point.x(), bounds.right())))
        scene_point.setY(max(bounds.top(), min(scene_point.y(), bounds.bottom())))
        return self.mapFromScene(scene_point)

    def _set_roi_color(self, color) -> None:
        qcolor = _matplotlib_color_to_qt(color) if isinstance(color, str) else QColor(color)
        self._roi_color = qcolor
        self.setPen(QPen(qcolor, 2))
        self.setBrush(QBrush(QColor(qcolor.red(), qcolor.green(), qcolor.blue(), 50)))
        self.update()


class DraggableROI(ROIItemMixin, QGraphicsRectItem):
    """Draggable rectangular, circular, or elliptical ROI."""

    SHAPE_TYPE = "rectangle"

    def __init__(self, rect, parent=None, color=None, shape_type=None):
        super().__init__(rect, parent)
        self._shape_type = shape_type if shape_type is not None else self.SHAPE_TYPE
        self._roi_color = QColor(255, 0, 0) if color is None else _matplotlib_color_to_qt(color)
        self._set_roi_color(self._roi_color)
        self._resizing = False
        self._resize_handle = None
        self._init_roi_interaction()

    def get_shape_type(self):
        return self._shape_type

    def get_scene_rect(self):
        """Return the ROI geometry (not pen width) in scene coordinates."""
        return self.mapToScene(self.rect()).boundingRect()

    def paint(self, painter: QPainter, option, widget=None):
        rect = self.rect()
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        if self._shape_type in ("circle", "ellipse"):
            painter.drawEllipse(rect)
            dotted_pen = QPen(self._roi_color, 1)
            dotted_pen.setStyle(Qt.PenStyle.DotLine)
            painter.setPen(dotted_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)
        else:
            painter.drawRect(rect)

    def set_roi_color(self, color):
        self._set_roi_color(color)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and not self._silent:
            return self._bounded_position(value)
        result = super().itemChange(change, value)
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._notify_changed()
        return result

    def setRect(self, rect):
        super().setRect(rect)
        self._notify_changed()

    def _hit_handle(self, pos):
        rect, handle_size = self.rect(), 10
        left_near = abs(pos.x() - rect.left()) < handle_size
        right_near = abs(pos.x() - rect.right()) < handle_size
        top_near = abs(pos.y() - rect.top()) < handle_size
        bottom_near = abs(pos.y() - rect.bottom()) < handle_size
        if left_near and top_near:
            return "top-left"
        if right_near and top_near:
            return "top-right"
        if left_near and bottom_near:
            return "bottom-left"
        if right_near and bottom_near:
            return "bottom-right"
        if left_near:
            return "left"
        if right_near:
            return "right"
        if top_near:
            return "top"
        if bottom_near:
            return "bottom"
        return None

    def _bounded_circle_side(self, requested_side: float, scene_center: QPointF) -> float:
        """Limit a center-anchored circle so its geometry remains in bounds."""
        if self._movement_bounds is None:
            return requested_side
        bounds = self._movement_bounds
        max_radius = min(
            scene_center.x() - bounds.left(),
            bounds.right() - scene_center.x(),
            scene_center.y() - bounds.top(),
            bounds.bottom() - scene_center.y(),
        )
        return min(requested_side, max(0.0, 2.0 * max_radius))

    def mousePressEvent(self, event):
        self._resize_handle = self._hit_handle(event.pos())
        self._resizing = self._resize_handle is not None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (self._resizing and self._resize_handle):
            super().mouseMoveEvent(event)
            return
        rect = self.rect()
        # A resize handle follows the mouse only as far as the scene bounds.
        pos = self._bounded_local_point(event.pos())
        handle = self._resize_handle
        if handle == "top-left":
            new_rect = QRectF(pos.x(), pos.y(), rect.right() - pos.x(), rect.bottom() - pos.y())
        elif handle == "top-right":
            new_rect = QRectF(rect.left(), pos.y(), pos.x() - rect.left(), rect.bottom() - pos.y())
        elif handle == "bottom-left":
            new_rect = QRectF(pos.x(), rect.top(), rect.right() - pos.x(), pos.y() - rect.top())
        elif handle == "bottom-right":
            new_rect = QRectF(rect.left(), rect.top(), pos.x() - rect.left(), pos.y() - rect.top())
        elif handle == "left":
            new_rect = QRectF(pos.x(), rect.top(), rect.right() - pos.x(), rect.height())
        elif handle == "right":
            new_rect = QRectF(rect.left(), rect.top(), pos.x() - rect.left(), rect.height())
        elif handle == "top":
            new_rect = QRectF(rect.left(), pos.y(), rect.width(), rect.bottom() - pos.y())
        else:
            new_rect = QRectF(rect.left(), rect.top(), rect.width(), pos.y() - rect.top())
        if self._shape_type == "circle":
            side = min(new_rect.width(), new_rect.height())
            scene_center = self.mapToScene(self.rect().center())
            side = self._bounded_circle_side(side, scene_center)
            if side > 5:
                self.setRect(QRectF(0, 0, side, side))
                self.setPos(scene_center.x() - side / 2, scene_center.y() - side / 2)
        elif new_rect.width() > 5 and new_rect.height() > 5:
            self.setRect(new_rect)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resize_handle = None
        super().mouseReleaseEvent(event)
        self._notify_changed()


class DraggablePolygonROI(ROIItemMixin, QGraphicsPolygonItem):
    """Draggable polygon ROI with editable vertices."""

    SHAPE_TYPE = "polygon"
    _vertexHitRadius = 8
    _vertexDrawSize = 4

    def __init__(self, polygon, parent=None, color=None):
        super().__init__(polygon, parent)
        self._shape_type = self.SHAPE_TYPE
        self._roi_color = _matplotlib_color_to_qt(color) if color else QColor(255, 0, 0)
        self._set_roi_color(self._roi_color)
        self._dragging_vertex_index = None
        self._init_roi_interaction()
        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.NoCache)

    def get_shape_type(self):
        return self._shape_type

    def get_scene_polygon(self):
        return self.mapToScene(self.polygon())

    def set_roi_color(self, color):
        self._set_roi_color(color)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPolygon(self.polygon())
        painter.setBrush(QBrush(self._roi_color))
        painter.setPen(QPen(self._roi_color, 1))
        size = self._vertexDrawSize
        for point in self.polygon():
            painter.drawRect(QRectF(point.x() - size / 2, point.y() - size / 2, size, size))

    def _find_nearest_vertex(self, pos):
        closest_index, min_distance = -1, float("inf")
        for index, point in enumerate(self.polygon()):
            distance = (pos - point).manhattanLength()
            if distance < min_distance:
                closest_index, min_distance = index, distance
        return closest_index, min_distance

    def mousePressEvent(self, event):
        closest_index, min_distance = self._find_nearest_vertex(event.pos())
        if min_distance < self._vertexHitRadius:
            self._dragging_vertex_index = closest_index
            event.accept()
            return
        self._dragging_vertex_index = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_vertex_index is None:
            super().mouseMoveEvent(event)
            return
        new_polygon = QPolygonF(self.polygon())
        new_polygon[self._dragging_vertex_index] = self._bounded_local_point(event.pos())
        self.setPolygon(new_polygon)
        self._notify_changed()
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._dragging_vertex_index is not None:
            self._dragging_vertex_index = None
            self._notify_changed()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Remove a vertex, or insert one on the nearest polygon edge."""
        pos, polygon = event.pos(), self.polygon()
        closest_index, min_distance = self._find_nearest_vertex(pos)
        if min_distance < self._vertexHitRadius:
            if polygon.size() > 3:
                new_polygon = QPolygonF(polygon)
                new_polygon.remove(closest_index)
                self.setPolygon(new_polygon)
                self._notify_changed()
                event.accept()
            return
        if polygon.size() >= 2:
            min_distance, insert_after = float("inf"), -1
            for index in range(polygon.size()):
                p1 = polygon.at(index)
                p2 = polygon.at((index + 1) % polygon.size())
                line_vector = p2 - p1
                length_squared = line_vector.x() ** 2 + line_vector.y() ** 2
                if length_squared == 0:
                    distance = (pos - p1).manhattanLength()
                else:
                    t = QPointF.dotProduct(pos - p1, line_vector) / length_squared
                    projection = p1 + max(0.0, min(1.0, t)) * line_vector
                    distance = (pos - projection).manhattanLength()
                if distance < min_distance:
                    min_distance, insert_after = distance, index
            if min_distance < 20:
                new_polygon = QPolygonF(polygon)
                new_polygon.insert(insert_after + 1, self._bounded_local_point(pos))
                self.setPolygon(new_polygon)
                self._notify_changed()
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and not self._silent:
            return self._bounded_position(value)
        result = super().itemChange(change, value)
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._notify_changed()
        return result
