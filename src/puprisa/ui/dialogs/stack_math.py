"""Behavior for the generated Stack Math Qt form."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem

from puprisa.model.entities import StackItem
from puprisa.ui.generated.dialog_stack_math import Ui_Dialog


class StackMathDialog(QDialog, Ui_Dialog):
    """Choose stacks for a linear combination or scalar multiplication."""

    _OPERATIONS = {
        "Add": "add",
        "Subtract": "subtract",
        "Multiply": "multiply",
        "Divide": "divide",
    }

    def __init__(
        self,
        stack_items: list[StackItem],
        current_stack_id: str | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)

        for stack_item in stack_items:
            self._add_stack_item(self.stack1ListWidget, stack_item)
            self._add_stack_item(self.stack2ListWidget, stack_item)
        self._select_defaults(current_stack_id)

        self._stack2_widgets = (
            self.stack2Label,
            self.stack2ListWidget,
            self.stack2CoeffLabel,
            self.stack2CoeffDoubleSpinBox,
        )
        self.opComboBox.currentTextChanged.connect(self._update_stack2_enabled)
        self._update_stack2_enabled(self.opComboBox.currentText())

    def get_parameters(self) -> dict:
        """Return the parameters expected by ``ProcessingManager``."""
        operation_label = self.opComboBox.currentText()
        try:
            operation = self._OPERATIONS[operation_label]
        except KeyError as exc:
            raise ValueError(f"Unsupported stack operation: {operation_label!r}") from exc

        parameters = {
            "first_stack_id": self._selected_stack_id(self.stack1ListWidget, "Stack 1"),
            "operation": operation,
            "first_coefficient": self.stack1CoeffDoubleSpinBox.value(),
        }
        if operation == "multiply":
            parameters.update(second_stack_id=None, second_coefficient=None)
        else:
            parameters.update(
                second_stack_id=self._selected_stack_id(self.stack2ListWidget, "Stack 2"),
                second_coefficient=self.stack2CoeffDoubleSpinBox.value(),
            )
        return parameters

    @staticmethod
    def _add_stack_item(widget: QListWidget, stack_item: StackItem) -> None:
        item = QListWidgetItem(stack_item.name)
        item.setData(Qt.ItemDataRole.UserRole, stack_item.id)
        widget.addItem(item)

    def _select_defaults(self, current_stack_id: str | None) -> None:
        if self.stack1ListWidget.count() == 0:
            return
        first_index = next(
            (
                index
                for index in range(self.stack1ListWidget.count())
                if self.stack1ListWidget.item(index).data(Qt.ItemDataRole.UserRole)
                == current_stack_id
            ),
            0,
        )
        self.stack1ListWidget.setCurrentRow(first_index)
        second_index = next(
            (index for index in range(self.stack2ListWidget.count()) if index != first_index),
            first_index,
        )
        self.stack2ListWidget.setCurrentRow(second_index)

    def _update_stack2_enabled(self, operation_label: str) -> None:
        enabled = operation_label != "Multiply"
        for widget in self._stack2_widgets:
            widget.setEnabled(enabled)

    @staticmethod
    def _selected_stack_id(widget: QListWidget, label: str) -> str:
        item = widget.currentItem()
        if item is None:
            raise ValueError(f"Select {label}")
        return item.data(Qt.ItemDataRole.UserRole)
