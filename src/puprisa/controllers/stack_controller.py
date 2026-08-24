# puprisa/controllers/stack_view_model.py
"""Controller that synchronises a :class:`StackManager` with a
:class:`QListWidget` and forwards user actions to the model.

This is the only object that touches the stack list widget.  It:

- rebuilds the list when the model changes,
- forwards checkbox/selection changes back to the model,
- exposes high-level action methods (open, delete, rename, colour pick)
  so windows can connect buttons directly without writing logic.
"""

from pathlib import Path

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QColorDialog,
)

from puprisa.core.pps import PPS
from puprisa.model.stack_manager import StackManager
from puprisa.utils.color_utils import _matplotlib_color_to_qt


class StackViewModel(QObject):
    """Bind a :class:`StackManager` to a :class:`QListWidget`.

    Parameters
    ----------
    manager : StackManager
        The model that holds the stack list.
    list_widget : QListWidget
        The widget to keep in sync.
    """

    def __init__(self, manager: StackManager, list_widget: QListWidget):
        super().__init__()
        self.manager = manager
        self.list_widget = list_widget

        # --- Model -> view ---
        manager.stackChanged.connect(self._on_stack_changed)
        manager.stackItemsChanged.connect(self._on_items_changed)
        manager.stackVisibilityChanged.connect(self._on_visibility_changed)

        # --- View -> model ---
        list_widget.currentRowChanged.connect(self._on_row_changed)
        list_widget.itemChanged.connect(self._on_item_changed)
        list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Initial population
        self._rebuild_list()

    # ------------------------------------------------------------------
    # Action methods (connected directly to buttons / menu actions)
    # ------------------------------------------------------------------
    def add_stack_from_file(self):
        """Open a file dialog and load the selected stack(s)."""
        paths, _ = QFileDialog.getOpenFileNames(
            self.list_widget,
            "Open Pump Probe Image Stack",
            "",
            "TIFF (*.tif *.tiff);;Pickle (*.pkl *.pickle)",
        )
        if not paths:
            return

        for path in paths:
            try:
                pps = PPS.load(path)
            except Exception as exc:
                QMessageBox.critical(
                    self.list_widget,
                    "Open Stack",
                    f"Failed to load {path}:\n{exc}",
                )
                continue

            self.manager.add_existing_stack(pps, name=Path(path).stem)

    def delete_selected_stack(self):
        """Delete the stack currently selected in the list widget."""
        row = self.list_widget.currentRow()
        if row >= 0:
            self.manager.delete_stack(row)

    def rename_selected_stack(self):
        """Prompt the user for a new name for the selected stack."""
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.manager.stack_items):
            return

        stack = self.manager.stack_items[row]
        text, ok = QInputDialog.getText(
            self.list_widget,
            "Rename Stack",
            "New name:",
            text=stack["name"],
        )
        if ok:
            self.manager.rename_stack(row, text)

    def change_stack_color(self, stack_id: str):
        """Open a colour picker and update the stack's colour."""
        stack = self.manager.get_item_by_id(stack_id)
        if stack is None:
            return

        current = _matplotlib_color_to_qt(stack["color"])
        new_color = QColorDialog.getColor(
            current, self.list_widget, "Choose Stack Color"
        )
        if new_color.isValid():
            self.manager.set_stack_color(stack_id, new_color.name())

    # ------------------------------------------------------------------
    # Model change handlers
    # ------------------------------------------------------------------
    def _on_stack_changed(self, stack_item):
        """Update the selected row when the model's current stack changes."""
        self._update_selection()

    def _on_items_changed(self):
        """Rebuild the list after structural or metadata changes."""
        self._rebuild_list()

    def _on_visibility_changed(self, stack_id: str, visible: bool):
        """Update the checkbox of a specific item without rebuilding."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == stack_id:
                item.setCheckState(
                    Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
                )
                return

    # ------------------------------------------------------------------
    # View change handlers
    # ------------------------------------------------------------------
    def _on_row_changed(self, row: int):
        """Forward selection change to the model."""
        self.manager.switch_stack(row)

    def _on_item_changed(self, item: QListWidgetItem):
        """Forward checkbox toggle to the model."""
        stack_id = item.data(Qt.ItemDataRole.UserRole)
        visible = item.checkState() == Qt.CheckState.Checked
        self.manager.set_stack_visible(stack_id, visible)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Open the colour picker on double-click."""
        self.change_stack_color(item.data(Qt.ItemDataRole.UserRole))

    # ------------------------------------------------------------------
    # List rebuilding
    # ------------------------------------------------------------------
    def _rebuild_list(self):
        """Recreate all list items from the model's stack list."""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        for stack in self.manager.get_all_items():
            self.list_widget.addItem(self._create_list_item(stack))

        self._update_selection()
        self.list_widget.blockSignals(False)

    def _update_selection(self):
        """Ensure the selected row matches the model's current stack."""
        current = self.manager.get_current_item()
        if current is None:
            self.list_widget.setCurrentRow(-1)
            return

        current_id = current["id"]
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) == current_id:
                self.list_widget.setCurrentRow(i)
                return

    @staticmethod
    def _create_list_item(stack: dict) -> QListWidgetItem:
        """Create a :class:`QListWidgetItem` for a stack item."""
        item = QListWidgetItem(stack["name"])
        item.setData(Qt.ItemDataRole.UserRole, stack["id"])
        item.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        item.setCheckState(
            Qt.CheckState.Checked if stack["visible"] else Qt.CheckState.Unchecked
        )

        color = stack.get("color")
        if color:
            item.setIcon(StackViewModel._color_icon(color))

        return item

    @staticmethod
    def _color_icon(color: str) -> QIcon:
        """Create a small square icon filled with the given colour."""
        qcolor = _matplotlib_color_to_qt(color)
        pixmap = QPixmap(12, 12)
        pixmap.fill(qcolor)
        return QIcon(pixmap)