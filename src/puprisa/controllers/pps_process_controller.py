# puprisa/controllers/pps_process_controller.py
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox, QDialog

import numpy as np

from puprisa.controllers.pps_plot_controller import PPSPlotController
from puprisa.core.pps import PPS
from puprisa.ui.dialogs.background_subtraction import BackgroundSubtractionDialog


class PPSProcessingController(QObject):
    """Controller for data-processing operations on a PPS stack.

    Handles background subtraction, downsampling, normalization, and
    other data-modification operations.

    Signals
    -------
    dataChanged : Signal()
        Emitted when the current PPS object has been modified in-place
        (e.g., background subtraction, normalization).
    stackCreated : Signal(object)
        Emitted when a new PPS object has been created (e.g., downsampling).
        The receiver (typically the stack controller) is responsible for
        adding it to the stack list and switching to it.
    """

    dataChanged = Signal()
    stackCreated = Signal(object)

    def __init__(self, plot_controller: PPSPlotController):
        super().__init__()
        self.plot_controller = plot_controller
        self.pps: PPS | None = None

    def set_pps(self, pps: PPS | None):
        """Update the current PPS reference."""
        self.pps = pps

    # ------------------------------------------------------------------
    # Background subtraction
    # ------------------------------------------------------------------
    def apply_background_subtraction(self, indices, pixelwise=True):
        """Subtract background computed from the given frame indices.

        :param indices: Sequence of frame indices used for background estimation.
        :param pixelwise: If True, subtract a pixel-wise average; if False,
                          subtract a single scalar average across all pixels.
        """
        if not self._ensure_pps():
            return
        if not indices:
            QMessageBox.warning(None, "Background Subtraction", "No frames selected.")
            return

        self.pps.apply_background_subtraction(indices, pixelwise=pixelwise)
        self.dataChanged.emit()

    def apply_background_subtraction_negative_delays(self, pixelwise=True):
        """Use frames with negative time delays as background."""
        if not self._ensure_pps():
            return
        if self.pps.axis_type != 'time':
            QMessageBox.warning(None, "Background Subtraction", "Negative delays require a time-axis stack.")
            return
        times = self.pps.get_axis_values()
        indices = np.where(times < 0)[0].tolist()
        if not indices:
            QMessageBox.warning(None, "Background Subtraction", "No negative delays found.")
            return
        self.apply_background_subtraction(indices, pixelwise)

    def reset_background_subtraction(self):
        """Reset background subtraction to original images."""
        if not self._ensure_pps():
            return
        self.pps.reset_background_subtraction()
        self.dataChanged.emit()

    def show_background_subtraction_dialog(self):
        """Open dialog for first/last N frames background subtraction."""
        if not self._ensure_pps():
            return
        total_frames = len(self.pps.images)
        dialog = BackgroundSubtractionDialog(total_frames)
        if dialog.exec() == QDialog.Accepted:
            indices, pixelwise = dialog.get_parameters()
            self.apply_background_subtraction(indices, pixelwise)

    # ------------------------------------------------------------------
    # Downsampling
    # ------------------------------------------------------------------
    def show_downsample_dialog(self):
        # TODO: implement dialog and call self.downsample(factor)
        pass

    def downsample(self, factor):
        """Downsample the stack and emit stackCreated with the new PPS."""
        if not self._ensure_pps():
            return
        new_pps = self.pps.downsample(factor)
        self.pps = new_pps
        self.stackCreated.emit(new_pps)

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------
    def normalize(self, norm="minmax"):
        """Normalize the stack in-place."""
        if not self._ensure_pps():
            return
        self.pps.normalize(norm)
        self.dataChanged.emit()

    def show_normalize_dialog(self):
        # TODO: implement normalization dialog
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_pps(self) -> bool:
        """Return True if a PPS is loaded, else show a warning."""
        if self.pps is None:
            QMessageBox.information(None, "Processing", "Please open a stack first.")
            return False
        return True