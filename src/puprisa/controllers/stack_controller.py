# puprisa/controllers/stack_controller.py
from PySide6.QtCore import QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox, QWidget, QColorDialog
from pathlib import Path

from puprisa.model.entities import StackItem
from puprisa.model.stack_manager import StackManager
from puprisa.core.pps import PPS
from puprisa.utils.color_utils import MATLAB_COLORS

class StackController(QObject):
    def __init__(self, manager: StackManager, parent_widget: QWidget):
        super().__init__()
        self._manager = manager
        self._parent = parent_widget

    def open_stack_dialog(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self._parent, "Open Pump Probe Image Stack", "",
            "TIFF (*.tif *.tiff);;Pickle (*.pkl *.pickle)",
        )
        for path in paths:
            try:
                pps = PPS.load(path)
            except Exception as exc:
                QMessageBox.critical(self._parent, "Open Stack", str(exc))
                continue
            self._manager.add_stack(pps, name=Path(path).stem)

    def delete_selected_stack(self, stack_id: str | None) -> None:
        if not stack_id:
            QMessageBox.warning(self._parent, "Delete Stack", "No stack selected.")
            return
        try:
            self._manager.delete_stack(stack_id)
        except KeyError as exc:
            QMessageBox.warning(self._parent, "Delete Stack", str(exc))

    def rename_selected_stack(self, stack_id: str | None) -> None:
        if not stack_id:
            QMessageBox.warning(self._parent, "Rename Stack", "No stack selected.")
            return
        item = self._manager.get_item_by_id(stack_id)
        text, ok = QInputDialog.getText(self._parent, "Rename Stack", "Enter new name:", text=item.name)
        if ok:
            try:
                self._manager.rename_stack(stack_id, text)
            except (KeyError, ValueError) as exc:
                QMessageBox.warning(self._parent, "Rename Stack", str(exc))

    def change_stack_color(self, stack_id: str | None) -> None:
        """Prompt the user for a new color and apply it to the stack."""
        if not stack_id:
            QMessageBox.warning(self._parent, "Change Stack Color", "No stack selected.")
            return
        item = self._manager.get_item_by_id(stack_id)
        dlg = QColorDialog(QColor(item.color), self._parent)
        for i, hex_color in enumerate(MATLAB_COLORS):
            if i >= 16:
                break
            dlg.setCustomColor(i, QColor(hex_color))
        if dlg.exec() == QColorDialog.DialogCode.Accepted:
            new_color = dlg.selectedColor()
            if new_color.isValid():
                try:
                    self._manager.set_stack_color(stack_id, new_color.name())
                except KeyError:
                    QMessageBox.warning(self._parent, "Change Stack Color", "Stack no longer exists.")

    def save_selected_stack(self, stack_id: str | None, format: str) -> None:
        if format == "tiff":
            title = "Save Stack as TIFF"
            default_suffix = ".tiff"
            file_filter = "TIFF (*.tif *.tiff)"
            valid_suffixes = {".tif", ".tiff"}
        elif format == "pickle":
            title = "Save Stack as Pickle"
            default_suffix = ".pkl"
            file_filter = "Pickle (*.pkl *.pickle)"
            valid_suffixes = {".pkl", ".pickle"}
        else:
            raise ValueError(f"Unsupported format: {format}")

        if not stack_id:
            QMessageBox.warning(self._parent, "Save Stack", "No stack selected.")
            return
        item = self._manager.get_item_by_id(stack_id)
        if item is None:
            QMessageBox.warning(self._parent, "Save Stack", "Stack not found.")
            return

        path, _ = QFileDialog.getSaveFileName(self._parent, title, f"{item.name}{default_suffix}", file_filter)
        if not path:
            return

        output_path = Path(path)
        if output_path.suffix.lower() not in valid_suffixes:
            output_path = output_path.with_suffix(default_suffix)

        try:
            self._manager.save_stack(item.id, output_path, format=format)
            QMessageBox.information(self._parent, title, f"Saved to {output_path}.")
        except (OSError, ValueError, TypeError) as exc:
            QMessageBox.critical(self._parent, title, f"Save failed:\n{exc}")

    def clear_all_stacks(self) -> None:
        """Clear all stacks after user confirmation."""
        if not self._manager.get_all_items():
            QMessageBox.information(self._parent, "Clear All Stacks", "No stacks to clear.")
            return
        self._manager.clear_all_stacks()
