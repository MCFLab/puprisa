from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget, QInputDialog

from puprisa.model.processing_manager import ProcessingManager
from puprisa.model.stack_manager import StackManager
from puprisa.ui.dialogs.background_subtraction import BackgroundSubtractionDialog
from puprisa.ui.dialogs.stack_math import StackMathDialog


class ProcessingController(QObject):
    def __init__(self, stack_manager: StackManager, processing_manager: ProcessingManager, parent_widget: QWidget):
        super().__init__()
        self._stack_manager = stack_manager
        self._processing_manager = processing_manager
        self._parent = parent_widget

    def _current_stack_id(self):
        stack_id = self._stack_manager.get_current_stack_id()
        if stack_id is None:
            QMessageBox.warning(self._parent, "Processing", "Please select a stack first.")
        return stack_id

    def show_background_subtraction_dialog(self):
        stack_id = self._current_stack_id()
        if stack_id is None:
            return

        stack_item = self._stack_manager.get_item_by_id(stack_id)
        frame_count = len(stack_item.pps.images)

        dialog = BackgroundSubtractionDialog(frame_count, parent=self._parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            indices, pixelwise = dialog.get_parameters()

            try:
                self._processing_manager.apply_background_subtraction(
                    stack_id=stack_id,
                    indices=indices,
                    pixelwise=pixelwise,
                )
            except (ValueError, IndexError, TypeError) as exc:
                QMessageBox.critical(self._parent, "Background Subtraction", str(exc))

    def show_fixed_value_background_subtraction_dialog(self) -> None:
        """Ask the user for a constant value and subtract it from the stack."""
        stack_id = self._stack_manager.get_current_stack_id()
        if stack_id is None:
            QMessageBox.warning(self._parent, "Background Subtraction", "Please select a stack first.")
            return
        value, ok = QInputDialog.getDouble(self._parent, "Subtract Fixed Value", "Value to subtract:", 0.0, -1e9, 1e9, 6)
        if not ok:
            return
        try:
            self._processing_manager.apply_background_subtraction_fixed_value(stack_id, value)
        except ValueError as exc:
            QMessageBox.critical(self._parent, "Background Subtraction", str(exc))

    def apply_background_subtraction_negative_delays(self) -> None:
        """Subtract the average of all negative-delay frames from the stack."""
        stack_id = self._stack_manager.get_current_stack_id()
        if stack_id is None:
            QMessageBox.warning(self._parent, "Background Subtraction", "Please select a stack first.")
            return
        try:
            self._processing_manager.apply_background_subtraction_negative_delays(stack_id)
        except ValueError as exc:
            QMessageBox.critical(self._parent, "Background Subtraction", str(exc))

    def reset_background_subtraction(self) -> None:
        """Reset the background subtraction for the current stack."""
        stack_id = self._stack_manager.get_current_stack_id()
        if stack_id is None:
            QMessageBox.warning(self._parent, "Background Subtraction", "Please select a stack first.")
            return
        try:
            self._processing_manager.reset_background_subtraction(stack_id)
        except ValueError as exc:
            QMessageBox.critical(self._parent, "Background Subtraction", str(exc))

    def show_svd_denoise_dialog(self) -> None:
        """Ask the user for the number of SVD components and apply SVD denoising."""
        stack_id = self._stack_manager.get_current_stack_id()
        if stack_id is None:
            QMessageBox.warning(self._parent, "SVD Denoising", "Please select a stack first.")
            return
        n_components, ok = QInputDialog.getInt(self._parent, "SVD Denoising", "Number of components:", 3, 1, 1000, 1)
        if not ok:
            return
        try:
            self._processing_manager.svd_reconstruct(stack_id, n_components)
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self._parent, "SVD Denoising", str(exc))

    def show_stack_math_dialog(self) -> None:
        """Combine two registered stacks and add the result as a new stack."""
        items = self._stack_manager.get_all_items()
        if not items:
            QMessageBox.warning(self._parent, "Stack Math", "Please open a stack first.")
            return

        dialog = StackMathDialog(
            items,
            current_stack_id=self._stack_manager.get_current_stack_id(),
            parent=self._parent,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            parameters = dialog.get_parameters()
            self._processing_manager.combine_stacks(**parameters)
        except (ValueError, TypeError, KeyError) as exc:
            QMessageBox.critical(self._parent, "Stack Math", str(exc))

    def show_downsample_dialog(self) -> None:
        """Ask the user for a downsampling factor and create a derived stack."""
        stack_id = self._stack_manager.get_current_stack_id()
        if stack_id is None:
            QMessageBox.warning(self._parent, "Downsample", "Please select a stack first.")
            return

        factor, ok = QInputDialog.getInt(self._parent, "Downsample Stack", "Downsampling factor:", 2, 1, 100, 1)
        if not ok:
            return
        stack_item = self._stack_manager.get_item_by_id(stack_id)
        h, w = stack_item.pps.image_dimensions
        if h % factor != 0 or w % factor != 0:
            answer = QMessageBox.warning(
                self._parent,
                "Downsample",
                f"Image size ({w}x{h}) is not divisible by {factor}.\n"
                "Edge pixels will be cropped.\nContinue?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Ok:
                return
        try:
            new_id = self._processing_manager.downsample(stack_id=stack_id, factor=factor, name=None)
            QMessageBox.information(self._parent, "Downsample", f"Created new stack: {new_id}")
        except (ValueError, TypeError, IndexError) as exc:
            QMessageBox.critical(self._parent, "Downsample", str(exc))