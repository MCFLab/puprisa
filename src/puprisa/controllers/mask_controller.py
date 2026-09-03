# puprisa/controllers/mask_controller.py
"""Qt controller for mask user actions.

Handles dialogs and orchestrates calls to :class:`MaskManager`.
Does not touch list widgets or any persistent view state — those belong to :class:`MaskViewModel`.
"""
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QFileDialog, QInputDialog, QMessageBox, QWidget

import json

from puprisa.model.mask_manager import MaskManager
from puprisa.model.stack_manager import StackManager
from puprisa.ui.dialogs.intensity_threshold import IntensityThresholdDialog
from puprisa.ui.dialogs.mask_math import MaskMathDialog


class MaskController(QObject):
    """Process user actions that modify masks through MaskManager."""

    def __init__(self, mask_manager: MaskManager, stack_manager: StackManager, parent_widget: QWidget | None) -> None:
        super().__init__()
        self._mask_manager = mask_manager
        self._stack_manager = stack_manager
        self._parent = parent_widget

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _current_stack_id(self) -> str | None:
        stack_id = self._stack_manager.get_current_stack_id()
        if stack_id is None:
            QMessageBox.warning(self._parent, "Mask", "Please select a stack first.")
        return stack_id

    # ------------------------------------------------------------------
    # Threshold mask actions
    # ------------------------------------------------------------------
    def show_intensity_threshold_dialog(self) -> None:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return
        dialog = IntensityThresholdDialog(self._parent)
        if dialog.exec() == QDialog.Accepted:
            threshold, sigma, mask_on, apply_all = dialog.get_params()
            if apply_all:
                success = 0
                for stack_id in self._stack_manager.get_all_stack_ids():
                    try:
                        self.add_mask_from_threshold(stack_id=stack_id, threshold=threshold, sigma=sigma, mask_on=mask_on, message=False)
                        success += 1
                    except (ValueError, KeyError) as exc:
                        QMessageBox.warning(self._parent, "Mask", str(exc))
                if success > 0:
                    QMessageBox.information(self._parent, "Mask", f"Created masks in {success} stacks.")
            else:
                self.add_mask_from_threshold(stack_id=stack_id, threshold=threshold, sigma=sigma, mask_on=mask_on, message=True)

    def add_mask_from_threshold(self, stack_id=None, threshold="Li", sigma=5.0, mask_on=True, label=None, message=True) -> None:
        if stack_id is None:
            stack_id = self._current_stack_id()
        if stack_id is None:
            return
        try:
            mask_id = self._mask_manager.add_mask_from_threshold(stack_id=stack_id, threshold=threshold, sigma=sigma, mask_on=mask_on, label=label)
            if message:
                QMessageBox.information(self._parent, "Mask", f"Mask {mask_id} created.")
        except (ValueError, KeyError) as exc:
            QMessageBox.warning(self._parent, "Mask", str(exc))

    # ------------------------------------------------------------------
    # Selected mask actions
    # ------------------------------------------------------------------
    def rename_mask(self, mask_id: str) -> None:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return
        mask_item = self._mask_manager.get_mask(stack_id, mask_id)
        if mask_item is None:
            QMessageBox.warning(self._parent, "Rename Mask", "Mask not found.")
            return
        current = mask_item.label or mask_id
        text, ok = QInputDialog.getText(self._parent, "Rename Mask", "Label:", text=current)
        if ok and text.strip():
            try:
                self._mask_manager.set_mask_label(stack_id, mask_id, text.strip())
            except KeyError as exc:
                QMessageBox.warning(self._parent, "Rename Mask", str(exc))
        return

    def delete_mask(self, mask_id: str) -> None:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return
        if mask_id is None:
            return
        try:
            self._mask_manager.remove_mask(stack_id, mask_id)
        except KeyError as exc:
            QMessageBox.warning(self._parent, "Delete Mask", str(exc))

    def reverse_mask(self, mask_id: str) -> None:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return
        if mask_id is None:
            return
        try:
            self._mask_manager.reverse_mask(stack_id, mask_id)
        except KeyError as exc:
            QMessageBox.warning(self._parent, "Reverse Mask", str(exc))

    def clear_all_masks(self) -> None:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return
        try:
            self._mask_manager.clear_all_masks(stack_id)
        except KeyError as exc:
            QMessageBox.warning(self._parent, "Clear Masks", str(exc))
    
    # ------------------------------------------------------------------
    # Mask Math
    # ------------------------------------------------------------------
    def show_mask_math_dialog(self) -> None:
        """Combine stored masks on the current stack into a new mask layer."""
        stack_id = self._current_stack_id()
        if stack_id is None:
            return
        masks = self._mask_manager.get_all_masks(stack_id)
        if not masks:
            QMessageBox.warning(self._parent, "Mask Math", "Create a mask first.")
            return

        dialog = MaskMathDialog(masks, parent=self._parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            mask_id = self._mask_manager.combine_masks(stack_id=stack_id, **dialog.get_parameters())
            QMessageBox.information(self._parent, "Mask Math", f"Mask {mask_id} created.")
        except (KeyError, TypeError, ValueError) as exc:
            QMessageBox.warning(self._parent, "Mask Math", str(exc))
            
    # ------------------------------------------------------------------
    # Export / Import
    # ------------------------------------------------------------------
    def export_selected_mask(self, mask_id: str) -> None:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return

        mask_item = self._mask_manager.get_mask(stack_id, mask_id)
        if mask_item is None:
            QMessageBox.warning(self._parent, "Export Mask", "Mask not found.")
            return

        default_name = f"mask_{mask_id}.json"
        path, _ = QFileDialog.getSaveFileName(
            self._parent,
            "Export Mask",
            default_name,
            "JSON (*.json);;All Files (*)",
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(
                    {
                        "masks": [mask_item.to_serializable()]
                    },
                    file,
                    indent=2,
                )
            QMessageBox.information(self._parent, "Export Mask", f"Saved to {path}.")
        except Exception as exc:
            QMessageBox.critical(self._parent, "Export Mask", f"Export failed:\n{exc}")

    def export_all_masks(self) -> None:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return

        path, _ = QFileDialog.getSaveFileName(self._parent, "Export All Masks", "masks.json", "JSON (*.json)")
        if not path:
            return

        try:
            self._mask_manager.save_masks_to_json(stack_id, path)
            QMessageBox.information(self._parent, "Export Masks", f"Saved to {path}.")
        except Exception as exc:
            QMessageBox.critical(self._parent, "Export Masks", f"Export failed:\n{exc}")

    def import_masks_from_json(self) -> None:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return

        path, _ = QFileDialog.getOpenFileName(self._parent, "Import Masks", "", "JSON (*.json)")
        if not path:
            return

        try:
            self._mask_manager.load_masks_from_json(stack_id, path)
        except Exception as exc:
            QMessageBox.critical(self._parent, "Import Masks", f"Import failed:\n{exc}")
