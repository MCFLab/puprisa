# puprisa/viewmodels/mask_view_model.py
"""Qt view model for the mask list widget.

Binds a MaskManager (model) to a QListWidget (view). Only masks of the
currently selected stack are displayed; switching stack rebuilds the list
automatically via StackManager events.
"""
from PySide6.QtCore import QObject, Qt, QSignalBlocker
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from puprisa.model.entities import MaskItem
from puprisa.model.mask_manager import MaskEvent, MaskManager
from puprisa.model.stack_manager import StackEvent, StackManager


class MaskViewModel(QObject):
    """Sync current stack's exclude masks with a QListWidget."""

    def __init__(self, mask_manager: MaskManager, stack_manager: StackManager, list_widget: QListWidget, parent: QObject | None = None):
        super().__init__(parent)
        self._mask_manager = mask_manager
        self._stack_manager = stack_manager
        self._list_widget = list_widget

        # Model -> View
        self._mask_manager.add_listener(self._on_mask_event)
        self._stack_manager.add_listener(self._on_stack_event)

        # View -> Model for checkbox toggles only
        self._list_widget.itemChanged.connect(self._on_item_changed)

        self._rebuild()

    # ------------------------------------------------------------------
    # Model -> View
    # ------------------------------------------------------------------
    def _current_stack_id(self) -> str | None:
        return self._stack_manager.get_current_stack_id()

    def _on_mask_event(self, event: MaskEvent) -> None:
        if event.stack_id != self._current_stack_id():
            return
        if event.event == "effective_changed":
            return
        self._rebuild()

    def _on_stack_event(self, event: StackEvent) -> None:
        if event.event == "current_changed":
            self._rebuild()

    # ------------------------------------------------------------------
    # View -> Model
    # ------------------------------------------------------------------
    def _on_item_changed(self, item: QListWidgetItem) -> None:
        mask_id = item.data(Qt.ItemDataRole.UserRole)
        enabled = item.checkState() == Qt.CheckState.Checked
        stack_id = self._current_stack_id()
        if stack_id is None:
            return
        mask_item = self._mask_manager.get_mask(stack_id, mask_id)
        if mask_item is not None and mask_item.enabled != enabled:
            self._mask_manager.set_mask_enabled(stack_id, mask_id, enabled)

    # ------------------------------------------------------------------
    # Widget rebuild
    # ------------------------------------------------------------------
    def _rebuild(self) -> None:
        with QSignalBlocker(self._list_widget):
            self._list_widget.clear()
            stack_id = self._current_stack_id()
            if stack_id is None:
                return
            for entry in self._mask_manager.get_all_masks(stack_id):
                self._list_widget.addItem(self._make_item(entry))

    @staticmethod
    def _make_item(mask_item: MaskItem) -> QListWidgetItem:
        mask_id = mask_item.id
        label = mask_item.label or mask_id
        item = QListWidgetItem(f"{label} [{mask_id}]")
        item.setData(Qt.ItemDataRole.UserRole, mask_id)
        item.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        item.setCheckState(
            Qt.CheckState.Checked if mask_item.enabled else Qt.CheckState.Unchecked
        )
        return item

    # ------------------------------------------------------------------
    # Widget query helpers
    # ------------------------------------------------------------------
    def selected_mask_id(self) -> str | None:
        item = self._list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None