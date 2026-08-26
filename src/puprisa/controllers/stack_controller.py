# puprisa/controllers/stack_controller.py
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox, QWidget
from pathlib import Path

from puprisa.model.entities import StackItem
from puprisa.model.stack_manager import StackManager
from puprisa.core.pps import PPS

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

    def delete_selected_stack(self, index: int):
        if index < 0:
            QMessageBox.warning(self._parent, "Delete Stack", "No stack selected.")
            return
        try:
            self._manager.delete_stack(index)
        except IndexError as exc:
            QMessageBox.warning(self._parent, "Delete Stack", str(exc))

    def rename_selected_stack(self, index: int):
        if index < 0:
            QMessageBox.warning(self._parent, "Rename Stack", "No stack selected.")
            return
        item = self._manager.get_all_items()[index]
        text, ok = QInputDialog.getText(self._parent, "Rename Stack", "Enter new name:", text=item.name)
        if ok:
            self._manager.rename_stack(index, text)

    def save_selected_stack(self, index: int, format: str) -> None:
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

        if index < 0:
            QMessageBox.warning(self._parent, "Save Stack", "No stack selected.")
            return
        item = self._manager.get_all_items()[index]

        path, _ = QFileDialog.getSaveFileName(
            self._parent,
            title,
            f"{item.name}{default_suffix}",
            file_filter,
        )
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
