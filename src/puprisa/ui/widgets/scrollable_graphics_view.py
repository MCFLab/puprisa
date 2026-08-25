# puprisa/ui/widgets/scrollable_graphics_view.py
from PySide6.QtCore import Signal
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QGraphicsView

class ScrollableGraphicsView(QGraphicsView):
    """QGraphicsView that emits wheelSliceChanged when the user scrolls vertically."""

    # Request slice change: delta > 0 means scrolling up, delta < 0 means scrolling down
    wheelSliceChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events to change the displayed slice."""
        delta = event.angleDelta().y()
        if delta == 0:
            super().wheelEvent(event)
            return

        # Emit slice changed signal, and let slider controller determine which slice to show
        self.wheelSliceChanged.emit(-1 if delta > 0 else 1)

        event.accept()