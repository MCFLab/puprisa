from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget, QInputDialog

from puprisa.model.processing_manager import ProcessingManager
from puprisa.model.stack_manager import StackManager
from puprisa.ui.dialogs.background_subtraction import BgSubFirstLastDialog, BgSubFixedValueDialog, BgSubNegDelayDialog
from puprisa.ui.dialogs.stack_math import StackMathDialog
from puprisa.utils.range_parser_utils import parse_range_string

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

    # ------------------------------------------------------------------
    # Background Subtraction: First/Last N frames
    # ------------------------------------------------------------------
    def show_background_subtraction_dialog(self):
        current_stack_id = self._stack_manager.get_current_stack_id()
        dialog = BgSubFirstLastDialog(self._parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        n_frames, is_first, pixelwise, apply_all = dialog.get_parameters()
        if apply_all:
            targets = self._stack_manager.get_all_stack_ids()
            if not targets:
                QMessageBox.warning(self._parent, "Background Subtraction", "No stacks available.")
                return
        else:
            if current_stack_id is None:
                QMessageBox.warning(self._parent, "Background Subtraction", "Please select a stack first.")
                return
            targets = [current_stack_id]
        for stack_id in targets:
            stack_item = self._stack_manager.get_item_by_id(stack_id)
            if stack_item is None:
                continue
            total_frames = len(stack_item.pps.images)
            if n_frames > total_frames:
                QMessageBox.critical(self._parent, "Background Subtraction", f"Stack {stack_id}: requested {n_frames} frames, but only {total_frames} available.")
                continue
            if is_first:
                indices = list(range(n_frames))
            else:
                indices = list(range(total_frames - n_frames, total_frames))
            try:
                self._processing_manager.apply_background_subtraction(stack_id=stack_id, indices=indices, pixelwise=pixelwise)
            except (ValueError, IndexError, TypeError) as exc:
                QMessageBox.critical(self._parent, "Background Subtraction", str(exc))

    # ------------------------------------------------------------------
    # Background Subtraction: Fixed Value
    # ------------------------------------------------------------------
    def show_fixed_value_background_subtraction_dialog(self) -> None:
        dialog = BgSubFixedValueDialog(self._parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        value, apply_all = dialog.get_parameters()
        current_stack_id = self._stack_manager.get_current_stack_id()
        if apply_all:
            targets = self._stack_manager.get_all_stack_ids()
            if not targets:
                QMessageBox.warning(self._parent, "Background Subtraction", "No stacks available.")
                return
        else:
            if current_stack_id is None:
                QMessageBox.warning(self._parent, "Background Subtraction", "Please select a stack first.")
                return
            targets = [current_stack_id]
        for stack_id in targets:
            try:
                self._processing_manager.apply_background_subtraction_fixed_value(stack_id, value)
            except ValueError as exc:
                QMessageBox.critical(self._parent, "Background Subtraction", str(exc))

    # ------------------------------------------------------------------
    # Background Subtraction: Negative Delays
    # ------------------------------------------------------------------
    def show_neg_delay_background_subtraction_dialog(self) -> None:
        dialog = BgSubNegDelayDialog(self._parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        pixelwise, apply_all = dialog.get_parameters()
        current_stack_id = self._stack_manager.get_current_stack_id()
        if apply_all:
            targets = self._stack_manager.get_all_stack_ids()
            if not targets:
                QMessageBox.warning(self._parent, "Background Subtraction", "No stacks available.")
                return
        else:
            if current_stack_id is None:
                QMessageBox.warning(self._parent, "Background Subtraction", "Please select a stack first.")
                return
            targets = [current_stack_id]
        for stack_id in targets:
            try:
                self._processing_manager.apply_background_subtraction_negative_delays(
                    stack_id, pixelwise=pixelwise
                )
            except ValueError as exc:
                QMessageBox.critical(self._parent, "Background Subtraction", str(exc))

    # ------------------------------------------------------------------
    # Background Subtraction: Reset
    # ------------------------------------------------------------------
    def reset_background_subtraction(self) -> None:
        """Reset the background subtraction for the current stack."""
        current_stack_id = self._stack_manager.get_current_stack_id()
        if current_stack_id is None:
            QMessageBox.warning(self._parent, "Background Subtraction", "Please select a stack first.")
            return
        all_stack_ids = self._stack_manager.get_all_stack_ids()
        if len(all_stack_ids) <= 1:
            targets = [current_stack_id]
        else:
            answer = QMessageBox.question(
                self._parent,
                "Background Subtraction",
                "Reset background subtraction for all stacks?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            )
            if answer == QMessageBox.StandardButton.Yes:
                targets = all_stack_ids
            elif answer == QMessageBox.StandardButton.No:
                targets = [current_stack_id]
            else:
                return
        for stack_id in targets:
            try:
                self._processing_manager.reset_background_subtraction(stack_id)
            except ValueError as exc:
                QMessageBox.critical(self._parent, "Background Subtraction", str(exc))
                return

    # ------------------------------------------------------------------
    # SVD Denoising
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Slice Stack
    # ------------------------------------------------------------------
    def show_slice_dialog(self) -> None:
        stack_id = self._stack_manager.get_current_stack_id()
        if stack_id is None:
            QMessageBox.warning(self._parent, "Slice Stack", "Please select a stack first.")
            return

        stack_item = self._stack_manager.get_item_by_id(stack_id)
        n_frames = len(stack_item.pps.images)
        text, ok = QInputDialog.getText(
            self._parent,
            "Slice Stack",
            f"Enter frame numbers (1-based, e.g., 1,3-5) [1-{n_frames}]:"
        )
        if not ok or not text.strip():
            return
        try:
            # User inputs 1-based frame numbers, we convert to 0-based indices for internal processing
            indices = parse_range_string(text, offset=-1)
        except ValueError as exc:
            QMessageBox.critical(self._parent, "Slice Stack", f"Invalid input: {exc}")
            return

        if not indices:
            QMessageBox.critical(self._parent, "Slice Stack", "No valid frames provided.")
            return
        if any(i < 0 or i >= n_frames for i in indices):
            QMessageBox.critical(self._parent, "Slice Stack", f"Frame numbers must be between 1 and {n_frames}.")
            return
        try:
            pps_sliced = stack_item.pps.slice(indices)
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self._parent, "Slice Stack", f"Slice failed: {exc}")
            return
        try:
            new_id = self._stack_manager.add_stack(pps=pps_sliced, name=f"{stack_item.name} (sliced)")
            QMessageBox.information(self._parent, "Slice Stack", f"Created new stack: {new_id}")
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self._parent, "Slice Stack", f"Failed to add stack: {exc}")

    # ------------------------------------------------------------------
    # Stack Math
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Downsample Stack
    # ------------------------------------------------------------------
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