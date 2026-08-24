# puprisa/controllers/pps_mask_controller.py
"""Qt controller for exclude masks stored in a :class:`PPS`.

Each item in the list widget represents one exclude mask.  The stored
mask array has ``True`` for pixels that are removed from analysis.

The controller subscribes to the underlying :class:`PPSMaskManager` so
that any change made elsewhere (e.g. in another window sharing the same
``PPS`` object) triggers an automatic refresh of the list widget.
"""

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QInputDialog,
    QFileDialog,
    QMessageBox,
    QDialog,
)

import numpy as np

from puprisa.core.pps import PPS
from puprisa.core.process import gaussian_threshold_mask
from puprisa.ui.dialogs.intensity_threshold import IntensityThresholdDialog


class PPSMaskController(QObject):
    """Qt controller for exclude masks in a :class:`PPS`.

    Parameters
    ----------
    mask_list_widget : QListWidget
        List widget that displays masks.  Each item has a checkbox
        reflecting the mask's ``enabled`` state and stores the mask ID in
        ``Qt.UserRole``.
    """

    maskChanged = Signal()

    def __init__(self, mask_list_widget: QListWidget):
        super().__init__()
        self.mask_list_widget = mask_list_widget
        self.pps: PPS | None = None
        self._listener_registered = False

        # Rebuild / update whenever the user toggles a checkbox.
        self.mask_list_widget.itemChanged.connect(self._on_item_changed)

    # ------------------------------------------------------------------
    # Stack management
    # ------------------------------------------------------------------
    def set_pps(self, pps: PPS | None):
        """Bind this controller to a new :class:`PPS` object.

        The controller subscribes to the new object's mask manager and
        unsubscribes from the previous one.  Passing ``None`` clears the
        list.
        """
        # Unsubscribe from the old mask manager.
        self._unsubscribe_from_mask_manager()

        self.pps = pps

        # Subscribe to the new mask manager, if any.
        if self.pps is not None:
            manager = self.pps.get_mask_manager()
            manager.add_change_listener(self._on_mask_manager_changed)
            self._listener_registered = True

        self._sync_from_pps()

    # ------------------------------------------------------------------
    # Model change handler
    # ------------------------------------------------------------------
    def _on_mask_manager_changed(self):
        """Called by the mask manager whenever any mask changes.

        Refreshes the list from the model and notifies listeners.
        """
        self._sync_from_pps()
        self.maskChanged.emit()

    def _unsubscribe_from_mask_manager(self):
        """Remove the change listener from the current mask manager."""
        if self.pps is not None and self._listener_registered:
            manager = self.pps.get_mask_manager()
            manager.remove_change_listener(self._on_mask_manager_changed)
            self._listener_registered = False

    def _sync_from_pps(self):
        """Rebuild the list widget from the current PPS object."""
        self.mask_list_widget.blockSignals(True)
        self.mask_list_widget.clear()

        if self.pps is not None:
            manager = self.pps.get_mask_manager()
            for mask_id in manager.get_all_mask_ids():
                entry = manager.get_mask(mask_id)
                if entry is None:
                    continue
                label = entry.get("label") or mask_id
                item = QListWidgetItem(f"{label} [{mask_id}]")
                item.setData(Qt.ItemDataRole.UserRole, mask_id)
                item.setCheckState(
                    Qt.CheckState.Checked
                    if entry.get("enabled", True)
                    else Qt.CheckState.Unchecked
                )
                self.mask_list_widget.addItem(item)

        self.mask_list_widget.blockSignals(False)

    # ------------------------------------------------------------------
    # UI -> model actions
    # ------------------------------------------------------------------
    def _on_item_changed(self, item: QListWidgetItem):
        """Handle checkbox toggles - update the enabled state in PPS."""
        if self.pps is None:
            return

        mask_id = item.data(Qt.ItemDataRole.UserRole)
        if mask_id is None:
            return

        enabled = item.checkState() == Qt.CheckState.Checked
        try:
            self.pps.set_mask_enabled(mask_id, enabled)
            # No manual refresh needed; the manager will notify us.
        except KeyError:
            self._sync_from_pps()

    # ------------------------------------------------------------------
    # Mask creation helpers
    # ------------------------------------------------------------------
    def create_mask_from_threshold(
        self,
        threshold="Li",
        sigma=5.0,
        mask_on=True,
        label=None,
    ):
        """Create an exclude mask from an intensity threshold.

        The threshold operation selects pixels *above* the cutoff (the
        region to keep).  Since this manager stores exclude masks, the
        complement is added so that those selected pixels remain included.

        Parameters
        ----------
        threshold : str or float
            ``"Li"`` or a numeric cutoff value.
        sigma : float
            Gaussian smoothing sigma.
        mask_on : bool
            If True, use the current effective mask for projection.
        label : str, optional
            Label for the new mask.

        Returns
        -------
        str or None
            New mask ID, or ``None`` if creation failed.
        """
        if self.pps is None:
            QMessageBox.information(self.mask_list_widget, "Intensity Threshold", "Please open a stack first.")
            return None

        projection = self.pps.project(mask_on=mask_on)
        effective_mask = (
            np.asarray(self.pps.mask, dtype=bool) if mask_on else None
        )

        try:
            keep_mask = gaussian_threshold_mask(
                projection,
                threshold=threshold,
                sigma=sigma,
                mask=effective_mask,
            )
        except Exception as exc:
            QMessageBox.critical(self.mask_list_widget, "Intensity Threshold", f"Thresholding failed:\n{exc}")
            return None

        if label is None:
            label = f"Intensity threshold ({threshold})"

        mask_id = self.pps.add_mask(~keep_mask, label=label, enabled=True)
        # Model notification will refresh the list; no explicit refresh needed.
        return mask_id

    def show_intensity_threshold_dialog(self):
        """Open the intensity threshold dialog and create a new mask layer."""
        if self.pps is None:
            QMessageBox.information(self.mask_list_widget, "Intensity Threshold", "Please open a stack first.")
            return

        dialog = IntensityThresholdDialog(self.mask_list_widget)
        if dialog.exec() == QDialog.Accepted:
            threshold, sigma, mask_on = dialog.get_params()
            self.create_mask_from_threshold(
                threshold=threshold,
                sigma=sigma,
                mask_on=mask_on,
            )

    # ------------------------------------------------------------------
    # Selected mask helpers
    # ------------------------------------------------------------------
    def get_selected_mask_id(self) -> str | None:
        """Return the mask ID of the currently selected item, or ``None``."""
        item = self.mask_list_widget.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def rename_selected_mask(self) -> bool:
        """Prompt for a new label for the selected mask."""
        mask_id = self.get_selected_mask_id()
        if mask_id is None:
            QMessageBox.warning(self.mask_list_widget, "Rename mask", "Select a mask first.")
            return False

        entry = self.pps.get_mask(mask_id) if self.pps else None
        current = (entry or {}).get("label") or mask_id
        label, ok = QInputDialog.getText(
            self.mask_list_widget,
            "Rename mask",
            "Label:",
            text=current,
        )
        if not ok:
            return False

        new_label = label.strip() or mask_id
        try:
            self.pps.set_mask_label(mask_id, new_label)
            # Model notification will refresh the list.
            return True
        except KeyError:
            self._sync_from_pps()
            return False

    def delete_selected_mask(self) -> bool:
        """Remove the selected mask."""
        mask_id = self.get_selected_mask_id()
        if mask_id is None:
            QMessageBox.warning(self.mask_list_widget, "Delete mask", "Select a mask first.")
            return False

        try:
            removed = self.pps.remove_mask(mask_id)
            # Model notification will refresh the list.
            return removed
        except KeyError:
            self._sync_from_pps()
            return False

    def reverse_selected_mask(self) -> bool:
        """Reverse the boolean values of the selected mask."""
        mask_id = self.get_selected_mask_id()
        if mask_id is None:
            QMessageBox.warning(self.mask_list_widget, "Reverse mask", "Select a mask first.")
            return False

        try:
            result = self.pps.reverse_mask(mask_id)
            # Model notification will refresh the list.
            return result
        except KeyError:
            self._sync_from_pps()
            return False

    def clear_all_masks(self) -> bool:
        """Remove every mask.  The effective mask returns to all-True."""
        if self.pps is None:
            return False

        self.pps.clear_all_masks()
        # Model notification will refresh the list.
        return True

    # ------------------------------------------------------------------
    # Export / import
    # ------------------------------------------------------------------
    def export_selected_mask(self) -> bool:
        """Export the selected mask to a NumPy NPZ file."""
        if self.pps is None:
            return False

        mask_id = self.get_selected_mask_id()
        if mask_id is None:
            QMessageBox.warning(self.mask_list_widget, "Export mask", "Select a mask first.")
            return False

        entry = self.pps.get_mask(mask_id)
        if entry is None:
            return False

        default_name = f"mask_{mask_id}.npz"
        path, _ = QFileDialog.getSaveFileName(
            self.mask_list_widget,
            "Export mask",
            default_name,
            "NPZ (*.npz);;All files (*)",
        )
        if not path:
            return False

        try:
            np.savez(
                path,
                mask=entry["mask"],
                shape=np.array(self.pps.image_dimensions),
                label=np.array(entry.get("label", "")),
                mask_id=np.array(mask_id),
            )
            QMessageBox.information(self.mask_list_widget, "Export mask", f"Saved to {path}.")
            return True
        except Exception as exc:
            QMessageBox.critical(self.mask_list_widget, "Export mask", f"Export failed:\n{exc}")
            return False

    def export_all_masks(self) -> bool:
        """Export all masks as a JSON file using :meth:`PPS.save_mask`."""
        if self.pps is None:
            return False

        path, _ = QFileDialog.getSaveFileName(
            self.mask_list_widget,
            "Export all masks",
            "masks.json",
            "JSON (*.json)",
        )
        if not path:
            return False

        try:
            self.pps.save_mask(path, format="json")
            QMessageBox.information(self.mask_list_widget, "Export masks", f"Saved to {path}.")
            return True
        except Exception as exc:
            QMessageBox.critical(self.mask_list_widget, "Export masks", f"Export failed:\n{exc}")
            return False

    def import_masks_from_json(self) -> bool:
        """Import masks from a JSON file produced by :meth:`PPS.save_mask`.

        The current mask manager state is replaced by the file contents.
        """
        if self.pps is None:
            QMessageBox.warning(self.mask_list_widget, "Import masks", "Load a stack first.")
            return False

        path, _ = QFileDialog.getOpenFileName(self.mask_list_widget, "Import masks", "", "JSON (*.json);;Pickle (*.pkl)")
        if not path:
            return False

        try:
            import json

            with open(path, "r") as f:
                data = json.load(f)

            self.pps.get_mask_manager().from_serializable(data)
            # Model notification will refresh the list.
            return True
        except Exception as exc:
            QMessageBox.critical(self.mask_list_widget, "Import masks", f"Import failed:\n{exc}")
            return False