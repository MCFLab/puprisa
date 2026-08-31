# puprisa/controllers/roi_controller.py
"""Qt controller for ROI user actions.

Handles dialogs and orchestrates calls to :class:`RoiManager`.
Does not touch list widgets, graphics items, or any persistent view
state — those belong to :class:`RoiViewModel`.
"""
from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QInputDialog, QMessageBox, QWidget

from puprisa.model.entities import RoiItem
from puprisa.model.roi_manager import RoiManager
from puprisa.model.stack_manager import StackManager
from puprisa.utils.color_utils import MATLAB_COLORS


class RoiController(QObject):
    """Process user actions that modify ROI data through RoiManager."""

    def __init__(self, roi_manager: RoiManager, stack_manager: StackManager, parent_widget: QWidget | None, space: str) -> None:
        super().__init__()
        self._roi_manager = roi_manager
        self._stack_manager = stack_manager
        self._parent = parent_widget
        self._space = space

    def add_roi(self, shape: str) -> RoiItem | None:
        """Create a new ROI in the current stack with the given shape."""
        stack_id = self._stack_manager.get_current_stack_id()
        if stack_id is None:
            QMessageBox.warning(self._parent, "Add ROI", "Please select a stack first.")
            return None

        try:
            return self._roi_manager.add_roi(stack_id=stack_id, space=self._space, shape=shape)
        except (KeyError, ValueError) as exc:
            QMessageBox.warning(self._parent, "Add ROI", str(exc))
            return None

    def delete_roi(self, roi_id: str) -> bool:
        """Delete the ROI with the given id."""
        try:
            self._roi_manager.delete_roi(roi_id)
            return True
        except KeyError as exc:
            QMessageBox.warning(self._parent, "Delete ROI", "ROI not found.")
            return False

    def rename_roi(self, roi_id: str) -> bool:
        """Prompt for a new label and update the ROI."""
        roi = self._roi_manager.get_roi_by_id(roi_id)
        if roi is None:
            QMessageBox.warning(self._parent, "Rename ROI", "ROI not found.")
            return False

        text, ok = QInputDialog.getText(self._parent, "Rename ROI", "New label:", text=roi.label)
        if ok and text.strip():
            try:
                self._roi_manager.update_label(roi_id, text.strip())
                return True
            except KeyError as exc:
                QMessageBox.warning(self._parent, "Rename ROI", str(exc))
                return False
        return False

    def change_roi_color(self, roi_id: str) -> bool:
        """Open a color picker and update the ROI color."""
        roi = self._roi_manager.get_roi_by_id(roi_id)
        if roi is None:
            QMessageBox.warning(self._parent, "Change Color", "ROI not found.")
            return False
        dlg = QColorDialog(QColor(roi.color), self._parent)
        dlg.setWindowTitle("Choose Color")
        for i, hex_color in enumerate(MATLAB_COLORS):
            if i >= 16:
                break
            dlg.setCustomColor(i, QColor(hex_color))
        if dlg.exec() == QColorDialog.DialogCode.Accepted:
            new_color = dlg.selectedColor()
            if new_color.isValid():
                try:
                    self._roi_manager.update_color(roi_id, new_color.name())
                except KeyError:
                    QMessageBox.warning(self._parent, "Change Color", "ROI no longer exists.")

    def convert_roi_to_mask(self, roi_id: str) -> str | None:
        """Convert the ROI into an exclude mask on its owning stack."""
        try:
            mask_id = self._roi_manager.convert_roi_to_mask(roi_id)
            QMessageBox.information(self._parent, "Convert to Mask", f"Mask {mask_id} created.")
            return mask_id
        except (KeyError, ValueError) as exc:
            QMessageBox.warning(self._parent, "Convert to Mask", str(exc))
            return None