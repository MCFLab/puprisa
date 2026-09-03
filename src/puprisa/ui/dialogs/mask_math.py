"""Behavior for the generated Mask Math Qt form."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem, QStyle

from puprisa.model.entities import MaskItem
from puprisa.ui.generated.dialog_mask_math import Ui_Dialog


class MaskMathDialog(QDialog, Ui_Dialog):
    """Select one or two exclude masks and a boolean operation."""

    _OPERATIONS = {
        "AND": "and",
        "OR": "or",
        "NOT": "not",
        "XOR": "xor",
    }

    def __init__(self, masks: list[MaskItem], parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        info_icon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        self.infoLabel.setPixmap(info_icon.pixmap(16, 16))

        for mask in masks:
            self._add_mask_item(self.mask1ListWidget, mask)
            self._add_mask_item(self.mask2ListWidget, mask)
        self._select_defaults()

        self._mask2_widgets = (self.mask2Label, self.mask2ListWidget)
        self.opComboBox.currentTextChanged.connect(self._update_mask2_enabled)
        self._update_mask2_enabled(self.opComboBox.currentText())

    def get_parameters(self) -> dict:
        """Return the parameters expected by ``MaskManager.combine_masks``."""
        operation_label = self.opComboBox.currentText()
        try:
            operation = self._OPERATIONS[operation_label]
        except KeyError as exc:
            raise ValueError(f"Unsupported mask operation: {operation_label!r}") from exc

        parameters = {
            "first_mask_id": self._selected_mask_id(self.mask1ListWidget, "Mask 1"),
            "operation": operation,
        }
        parameters["second_mask_id"] = (
            None
            if operation == "not"
            else self._selected_mask_id(self.mask2ListWidget, "Mask 2")
        )
        return parameters

    @staticmethod
    def _add_mask_item(widget: QListWidget, mask_item: MaskItem) -> None:
        mask_id = mask_item.id
        label = mask_item.label or mask_id
        item = QListWidgetItem(f"{label} [{mask_id}]")
        item.setData(Qt.ItemDataRole.UserRole, mask_id)
        widget.addItem(item)

    def _select_defaults(self) -> None:
        if self.mask1ListWidget.count() == 0:
            return
        self.mask1ListWidget.setCurrentRow(0)
        self.mask2ListWidget.setCurrentRow(1 if self.mask2ListWidget.count() > 1 else 0)

    def _update_mask2_enabled(self, operation_label: str) -> None:
        enabled = operation_label != "NOT"
        for widget in self._mask2_widgets:
            widget.setEnabled(enabled)

    @staticmethod
    def _selected_mask_id(widget: QListWidget, label: str) -> str:
        item = widget.currentItem()
        if item is None:
            raise ValueError(f"Select {label}")
        return str(item.data(Qt.ItemDataRole.UserRole))
