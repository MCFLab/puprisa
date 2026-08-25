# puprisa/controllers/mask_controller.py
"""Qt controller for mask user actions.

Handles dialogs and orchestrates calls to :class:`MaskManager`.
Does not touch list widgets or any persistent view state — those belong to :class:`MaskViewModel`.
"""
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QFileDialog, QInputDialog, QMessageBox, QWidget

import numpy as np

from puprisa.model.mask_manager import MaskManager
from puprisa.model.stack_manager import StackManager
from puprisa.ui.dialogs.intensity_threshold import IntensityThresholdDialog


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
            threshold, sigma, mask_on = dialog.get_params()
            self.create_threshold_mask(threshold=threshold, sigma=sigma, mask_on=mask_on)

    def create_threshold_mask(self, threshold="Li", sigma=5.0, mask_on=True, label=None) -> str | None:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return None

        try:
            mask_id = self._mask_manager.create_threshold_mask(stack_id=stack_id, threshold=threshold, sigma=sigma, mask_on=mask_on, label=label)
            QMessageBox.information(self._parent, "Mask", f"Mask {mask_id} created.")
            return mask_id
        except (ValueError, KeyError) as exc:
            QMessageBox.warning(self._parent, "Mask", str(exc))
            return None

    # ------------------------------------------------------------------
    # Selected mask actions
    # ------------------------------------------------------------------
    def rename_mask(self, mask_id: str) -> bool:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return False

        entry = self._mask_manager.get_mask(stack_id, mask_id)
        if entry is None:
            QMessageBox.warning(self._parent, "Rename Mask", "Mask not found.")
            return False

        current = entry.get("label") or mask_id
        text, ok = QInputDialog.getText(self._parent, "Rename Mask", "Label:", text=current)
        if ok and text.strip():
            try:
                self._mask_manager.set_mask_label(stack_id, mask_id, text.strip())
                return True
            except KeyError as exc:
                QMessageBox.warning(self._parent, "Rename Mask", str(exc))
                return False
        return False

    def delete_mask(self, mask_id: str) -> bool:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return False

        try:
            self._mask_manager.remove_mask(stack_id, mask_id)
            return True
        except KeyError as exc:
            QMessageBox.warning(self._parent, "Delete Mask", str(exc))
            return False

    def reverse_mask(self, mask_id: str) -> bool:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return False

        try:
            self._mask_manager.reverse_mask(stack_id, mask_id)
            return True
        except KeyError as exc:
            QMessageBox.warning(self._parent, "Reverse Mask", str(exc))
            return False

    def clear_all_masks(self) -> bool:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return False

        try:
            self._mask_manager.clear_all_masks(stack_id)
            return True
        except KeyError as exc:
            QMessageBox.warning(self._parent, "Clear Masks", str(exc))
            return False

    # ------------------------------------------------------------------
    # Export / import
    # ------------------------------------------------------------------
    def export_selected_mask(self, mask_id: str) -> bool:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return False

        entry = self._mask_manager.get_mask(stack_id, mask_id)
        if entry is None:
            QMessageBox.warning(self._parent, "Export Mask", "Mask not found.")
            return False

        default_name = f"mask_{mask_id}.npz"
        path, _ = QFileDialog.getSaveFileName(self._parent, "Export Mask", default_name, "NPZ (*.npz);;All Files (*)")
        if not path:
            return False

        try:
            np.savez(path, mask=entry["mask"], shape=np.array(entry["mask"].shape), label=np.array(entry.get("label", "")), mask_id=np.array(mask_id))
            QMessageBox.information(self._parent, "Export Mask", f"Saved to {path}.")
            return True
        except Exception as exc:
            QMessageBox.critical(self._parent, "Export Mask", f"Export failed:\n{exc}")
            return False

    def export_all_masks(self) -> bool:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return False

        path, _ = QFileDialog.getSaveFileName(self._parent, "Export All Masks", "masks.json", "JSON (*.json)")
        if not path:
            return False

        try:
            self._mask_manager.save_masks_to_json(stack_id, path)
            QMessageBox.information(self._parent, "Export Masks", f"Saved to {path}.")
            return True
        except Exception as exc:
            QMessageBox.critical(self._parent, "Export Masks", f"Export failed:\n{exc}")
            return False

    def import_masks_from_json(self) -> bool:
        stack_id = self._current_stack_id()
        if stack_id is None:
            return False

        path, _ = QFileDialog.getOpenFileName(self._parent, "Import Masks", "", "JSON (*.json)")
        if not path:
            return False

        try:
            self._mask_manager.load_masks_from_json(stack_id, path)
            return True
        except Exception as exc:
            QMessageBox.critical(self._parent, "Import Masks", f"Import failed:\n{exc}")
            return False