# puprisa/viewmodels/stack_view_model.py
"""Qt controller for the stack list widget.

Binds a StackManager (model) to a QListWidget (view).  No business logic;
only event translation and widget synchronization.
"""
from PySide6.QtCore import QObject, Qt, Signal, QSignalBlocker
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from puprisa.model.entities import StackItem
from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.utils.color_utils import _matplotlib_color_to_qt

class StackViewModel(QObject):
    """Sync a StackManager with a QListWidget."""

    # Re-emitted for other controllers / windows
    currentStackChanged = Signal(object)        # StackItem | None
    stackVisibilityChanged = Signal(str, bool)
    colorChangeRequested = Signal(str)

    def __init__(
        self,
        manager: StackManager,
        list_widget: QListWidget,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._manager = manager
        self._list_widget = list_widget

        # Model -> View
        self._manager.add_listener(self._on_stack_event)

        # View -> Model
        self._list_widget.currentRowChanged.connect(self._on_row_changed)
        self._list_widget.itemChanged.connect(self._on_item_changed)
        self._list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._list_widget.model().rowsMoved.connect(self._on_rows_moved)
        
        # Initial population
        self._rebuild()

    # ------------------------------------------------------------------
    # Model -> View
    # ------------------------------------------------------------------
    def _on_stack_event(self, event: StackEvent) -> None:
        if event.event == "added":
            self._rebuild()
        elif event.event == "removed":
            self._rebuild()
        elif event.event == "renamed":
            self._rebuild()
        elif event.event == "reordered":
            self._rebuild()
        elif event.event == "color_changed":
            self._rebuild()
        elif event.event == "current_changed":
            self._select_current()
            self.currentStackChanged.emit(event.stack_item)
        elif event.event == "visibility_changed":
            self._update_checkbox(event.stack_id, event.stack_item.visible)
            self.stackVisibilityChanged.emit(event.stack_id, event.stack_item.visible)

    # ------------------------------------------------------------------
    # View -> Model
    # ------------------------------------------------------------------
    def _on_row_changed(self, row: int) -> None:
        """User clicked a row: tell the model to switch current stack."""
        if row >= 0:
            item = self._list_widget.item(row)
            stack_id = item.data(Qt.ItemDataRole.UserRole)
            self._manager.switch_stack(stack_id)

    def _on_rows_moved(self, parent, start, end, destination, row):
        stack_ids = [
            self._list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._list_widget.count())
        ]
        try:
            self._manager.reorder_stacks(stack_ids)
        except ValueError:
            self._rebuild()

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        """User toggled a checkbox: tell the model."""
        stack_id = item.data(Qt.ItemDataRole.UserRole)
        visible = item.checkState() == Qt.CheckState.Checked
        item_data = self._manager.get_item_by_id(stack_id)
        if item_data is not None and item_data.visible != visible:
            self._manager.set_stack_visible(stack_id, visible)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        stack_id = item.data(Qt.ItemDataRole.UserRole)
        if stack_id:
            self.colorChangeRequested.emit(stack_id)

    # ------------------------------------------------------------------
    # Widget rebuild helpers
    # ------------------------------------------------------------------
    def _rebuild(self) -> None:
        with QSignalBlocker(self._list_widget):
            self._list_widget.clear()
            for stack_item in self._manager.get_all_items():
                self._list_widget.addItem(self._make_item(stack_item))
        self._select_current()

    def _select_current(self) -> None:
        with QSignalBlocker(self._list_widget):
            current = self._manager.get_current_item()
            if current is None:
                self._list_widget.setCurrentRow(-1)
            else:
                for i in range(self._list_widget.count()):
                    item = self._list_widget.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == current.id:
                        self._list_widget.setCurrentRow(i)
                        return

    def _update_checkbox(self, stack_id: str, visible: bool) -> None:
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == stack_id:
                with QSignalBlocker(self._list_widget):
                    item.setCheckState(
                        Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
                    )
                return

    def _make_item(self, stack_item: StackItem) -> QListWidgetItem:
        item = QListWidgetItem(stack_item.name)
        item.setData(Qt.ItemDataRole.UserRole, stack_item.id)
        item.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsDragEnabled
        )
        item.setCheckState(Qt.CheckState.Checked if stack_item.visible else Qt.CheckState.Unchecked)

        qcolor = _matplotlib_color_to_qt(stack_item.color)
        pixmap = QPixmap(12, 12)
        pixmap.fill(qcolor)
        item.setIcon(QIcon(pixmap))

        return item

    # ------------------------------------------------------------------
    # Widget query helpers
    # ------------------------------------------------------------------
    def selected_stack_id(self) -> str | None:
        item = self._list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None