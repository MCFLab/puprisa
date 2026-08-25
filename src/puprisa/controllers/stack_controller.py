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
        try:
            self._manager.delete_stack(index)
        except IndexError as exc:
            QMessageBox.warning(self._parent, "Delete Stack", str(exc))

    def rename_selected_stack(self, index: int):
        item = self._manager.get_all_items()[index]
        text, ok = QInputDialog.getText(self._parent, "Rename Stack", "Enter new name:", text=item.name)
        if ok:
            self._manager.rename_stack(index, text)
