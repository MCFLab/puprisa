# puprisa/ui/widgets/draggable_roi.py
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF

from contextlib import contextmanager
from puprisa.utils.color_utils import _matplotlib_color_to_qt

class DraggableROI(QGraphicsRectItem):
    """Base draggable ROI: rectangle by default; supports circle/ellipse."""

    SHAPE_TYPE = "rectangle"

    def __init__(self, rect, parent=None, color=None, shape_type=None):
        super().__init__(rect, parent)
        self._shape_type = shape_type if shape_type is not None else self.SHAPE_TYPE
        self._roi_color = QColor(255, 0, 0) if color is None else _matplotlib_color_to_qt(color)

        self.setPen(QPen(self._roi_color, 2))
        self.setBrush(QBrush(QColor(
            self._roi_color.red(),
            self._roi_color.green(),
            self._roi_color.blue(),
            50,
        )))

        self._resizing = False
        self._resize_handle = None
        self._roi_changed_callback = None
        self._silent = False
        self._movement_bounds = None

        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_roi_changed_callback(self, callback):
        """Set callback function to be called when ROI changes."""
        self._roi_changed_callback = callback

    def get_shape_type(self):
        """Return ROI shape type: rectangle, circle, or ellipse."""
        return self._shape_type

    def get_scene_rect(self):
        """Return the ROI rect in scene coordinates."""
        return self.rect().translated(self.pos())

    def set_movement_bounds(self, bounds_rect):
        """Restrict ROI movement to a scene-space bounds rectangle."""
        self._movement_bounds = QRectF(bounds_rect) if bounds_rect is not None else None

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paint(self, painter: QPainter, option, widget=None):
        """Draw the ROI shape (rect for rectangle, ellipse for circle/ellipse)."""
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

    def set_roi_color(self, color):
        """Set the ROI color (accepts matplotlib color string or QColor)."""
        if isinstance(color, str):
            qcolor = _matplotlib_color_to_qt(color)
        else:
            qcolor = QColor(color)

        self._roi_color = qcolor
        self.setPen(QPen(self._roi_color, 2))
        self.setBrush(QBrush(QColor(
            self._roi_color.red(),
            self._roi_color.green(),
            self._roi_color.blue(),
            50,
        )))
        self.update()

    # ------------------------------------------------------------------
    # Change notification
    # ------------------------------------------------------------------
    @contextmanager
    def silent_geometry_change(self):
        """Temporarily suppress change notifications.
        Use this when geometry is updated from the model side; user
        interactions must never run inside this context.
        """
        previous = self._silent
        self._silent = True
        try:
            yield
        finally:
            self._silent = previous

    def _notify_changed(self):
        if not self._silent and self._roi_changed_callback:
            self._roi_changed_callback()

    def itemChange(self, change, value):
        """Handle item changes: restrict movement and emit change signal."""
        if change == QGraphicsRectItem.ItemPositionChange and self._movement_bounds is not None:
            new_pos = QPointF(value)
            rect = self.rect()
            b = self._movement_bounds
            min_x = b.left()
            min_y = b.top()
            max_x = b.right() - rect.width()
            max_y = b.bottom() - rect.height()
            if max_x < min_x:
                max_x = min_x
            if max_y < min_y:
                max_y = min_y
            new_pos.setX(max(min_x, min(new_pos.x(), max_x)))
            new_pos.setY(max(min_y, min(new_pos.y(), max_y)))
            return new_pos

        result = super().itemChange(change, value)
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            self._notify_changed()
        return result

    def setRect(self, rect):
        """Override setRect to emit signal when rect changes."""
        super().setRect(rect)
        self._notify_changed()

    # ------------------------------------------------------------------
    # Mouse interaction / resizing
    # ------------------------------------------------------------------
    def _hit_handle(self, pos):
        """Return resize handle name at position, or None."""
        rect = self.rect()
        handle_size = 10

        left_near = abs(pos.x() - rect.left()) < handle_size
        right_near = abs(pos.x() - rect.right()) < handle_size
        top_near = abs(pos.y() - rect.top()) < handle_size
        bottom_near = abs(pos.y() - rect.bottom()) < handle_size

        if left_near and top_near:
            return 'top-left'
        if right_near and top_near:
            return 'top-right'
        if left_near and bottom_near:
            return 'bottom-left'
        if right_near and bottom_near:
            return 'bottom-right'
        if left_near:
            return 'left'
        if right_near:
            return 'right'
        if top_near:
            return 'top'
        if bottom_near:
            return 'bottom'
        return None

    def mousePressEvent(self, event):
        """Handle mouse press for resizing."""
        self._resize_handle = self._hit_handle(event.pos())
        self._resizing = self._resize_handle is not None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for resizing."""
        if self._resizing and self._resize_handle:
            rect = self.rect()
            pos = event.pos()

            handle = self._resize_handle
            if handle == 'top-left':
                new_rect = QRectF(pos.x(), pos.y(), rect.right() - pos.x(), rect.bottom() - pos.y())
            elif handle == 'top-right':
                new_rect = QRectF(rect.left(), pos.y(), pos.x() - rect.left(), rect.bottom() - pos.y())
            elif handle == 'bottom-left':
                new_rect = QRectF(pos.x(), rect.top(), rect.right() - pos.x(), pos.y() - rect.top())
            elif handle == 'bottom-right':
                new_rect = QRectF(rect.left(), rect.top(), pos.x() - rect.left(), pos.y() - rect.top())
            elif handle == 'left':
                new_rect = QRectF(pos.x(), rect.top(), rect.right() - pos.x(), rect.height())
            elif handle == 'right':
                new_rect = QRectF(rect.left(), rect.top(), pos.x() - rect.left(), rect.height())
            elif handle == 'top':
                new_rect = QRectF(rect.left(), pos.y(), rect.width(), rect.bottom() - pos.y())
            elif handle == 'bottom':
                new_rect = QRectF(rect.left(), rect.top(), rect.width(), pos.y() - rect.top())
            else:
                return

            # Circle: keep equal width/height and keep center fixed
            if self._shape_type in ("circle"):
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
        """Handle mouse release."""
        self._resizing = False
        self._resize_handle = None
        super().mouseReleaseEvent(event)
        self._notify_changed()


class DraggablePolygonROI(QGraphicsPolygonItem):
    """Draggable polygon ROI with vertex editing (add/remove via double-click)."""

    SHAPE_TYPE = "polygon"
    _vertexHitRadius = 8
    _vertexDrawSize = 4

    def __init__(self, polygon, parent=None, color=None):
        super().__init__(polygon, parent)
        self._shape_type = "polygon"
        self._roi_color = _matplotlib_color_to_qt(color) if color else QColor(255, 0, 0)

        self.setPen(QPen(self._roi_color, 2))
        self.setBrush(QBrush(QColor(
            self._roi_color.red(),
            self._roi_color.green(),
            self._roi_color.blue(),
            50,
        )))

        self._silent = False
        self._roi_changed_callback = None
        self._dragging_vertex_index = None
        self._movement_bounds = None

        self.setFlag(QGraphicsPolygonItem.ItemIsMovable, True)
        self.setFlag(QGraphicsPolygonItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPolygonItem.ItemSendsGeometryChanges, True)
        
        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.NoCache)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_roi_changed_callback(self, callback):
        self._roi_changed_callback = callback

    def get_shape_type(self):
        return self._shape_type

    def get_scene_polygon(self):
        return self.mapToScene(self.polygon())

    def set_movement_bounds(self, bounds_rect):
        self._movement_bounds = QRectF(bounds_rect) if bounds_rect is not None else None

    def set_roi_color(self, color):
        if isinstance(color, str):
            qcolor = _matplotlib_color_to_qt(color)
        else:
            qcolor = QColor(color)

        self._roi_color = qcolor
        self.setPen(QPen(self._roi_color, 2))
        self.setBrush(QBrush(QColor(
            self._roi_color.red(),
            self._roi_color.green(),
            self._roi_color.blue(),
            50,
        )))
        self.update()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPolygon(self.polygon())

        # Draw vertex handles
        painter.setBrush(QBrush(self._roi_color))
        painter.setPen(QPen(self._roi_color, 1))
        s = self._vertexDrawSize
        for pt in self.polygon():
            painter.drawRect(QRectF(pt.x() - s / 2, pt.y() - s / 2, s, s))

    # ------------------------------------------------------------------
    # Mouse interaction
    # ------------------------------------------------------------------
    def _find_nearest_vertex(self, pos):
        poly = self.polygon()
        min_dist = float('inf')
        closest_idx = -1
        for i, pt in enumerate(poly):
            dist = (pos - pt).manhattanLength()
            if dist < min_dist:
                min_dist = dist
                closest_idx = i
        return closest_idx, min_dist

    def mousePressEvent(self, event):
        pos = event.pos()
        closest_idx, min_dist = self._find_nearest_vertex(pos)

        if min_dist < self._vertexHitRadius:
            self._dragging_vertex_index = closest_idx
            event.accept()
            return

        self._dragging_vertex_index = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_vertex_index is not None:
            new_poly = QPolygonF(self.polygon())
            new_pt = event.pos()

            if self._movement_bounds is not None:
                scene_pt = self.mapToScene(new_pt)
                if not self._movement_bounds.contains(scene_pt):
                    return

            new_poly[self._dragging_vertex_index] = new_pt
            self.prepareGeometryChange()
            self.setPolygon(new_poly)
            self._notify_changed()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging_vertex_index is not None:
            self._dragging_vertex_index = None
            self._notify_changed()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to add or remove vertices."""
        pos = event.pos()
        poly = self.polygon()

        # Remove vertex if double-click on it
        closest_idx, min_dist = self._find_nearest_vertex(pos)
        if min_dist < self._vertexHitRadius:
            if poly.size() > 3:
                new_poly = QPolygonF(poly)
                new_poly.remove(closest_idx)
                self.prepareGeometryChange()
                self.setPolygon(new_poly)
                self._notify_changed()
                event.accept()
                return
            return

        # Add vertex on closest edge if within threshold
        if poly.size() >= 2:
            min_dist = float('inf')
            insert_after = -1
            for i in range(poly.size()):
                p1 = poly.at(i)
                p2 = poly.at((i + 1) % poly.size())
                line_vec = p2 - p1
                len_sq = line_vec.x() ** 2 + line_vec.y() ** 2
                if len_sq == 0:
                    dist = (pos - p1).manhattanLength()
                else:
                    t = QPointF.dotProduct(pos - p1, line_vec) / len_sq
                    t = max(0.0, min(1.0, t))
                    projection = p1 + t * line_vec
                    dist = (pos - projection).manhattanLength()
                if dist < min_dist:
                    min_dist = dist
                    insert_after = i

            if min_dist < 20 and insert_after >= 0:
                new_poly = QPolygonF(poly)
                new_poly.insert(insert_after + 1, pos)
                self.prepareGeometryChange()
                self.setPolygon(new_poly)
                self._notify_changed()
                event.accept()
                return

        super().mouseDoubleClickEvent(event)

    # ------------------------------------------------------------------
    # Change notification
    # ------------------------------------------------------------------
    def itemChange(self, change, value):
        if self._silent:
            return super().itemChange(change, value)
        if change == QGraphicsPolygonItem.ItemPositionChange and self._movement_bounds is not None:
            new_pos = QPointF(value)
            scene_rect = self.mapToScene(self.boundingRect()).boundingRect()
            b = self._movement_bounds
            if scene_rect.left() + new_pos.x() - self.pos().x() < b.left():
                new_pos.setX(b.left() - scene_rect.left() + self.pos().x())
            if scene_rect.right() + new_pos.x() - self.pos().x() > b.right():
                new_pos.setX(b.right() - scene_rect.right() + self.pos().x())
            if scene_rect.top() + new_pos.y() - self.pos().y() < b.top():
                new_pos.setY(b.top() - scene_rect.top() + self.pos().y())
            if scene_rect.bottom() + new_pos.y() - self.pos().y() > b.bottom():
                new_pos.setY(b.bottom() - scene_rect.bottom() + self.pos().y())
            return new_pos

        result = super().itemChange(change, value)
        if change == QGraphicsPolygonItem.ItemPositionHasChanged:
            self._notify_changed()
        return result

    @contextmanager
    def silent_geometry_change(self):
        """Temporarily suppress change notifications.
        Use this when geometry is updated from the model side; user
        interactions must never run inside this context.
        """
        previous = self._silent
        self._silent = True
        try:
            yield
        finally:
            self._silent = previous

    def _notify_changed(self):
        if not self._silent and self._roi_changed_callback:
            self._roi_changed_callback()