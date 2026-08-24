# puprisa/controllers/base_roi_controller.py
"""Common ROI management for image-space and phasor-space ROIs.

This controller maintains a global list of all ROIs across all stacks.
Each ROI dictionary has the following structure::

    {
        "id": str,              # unique ROI id
        "stack_id": str,        # id of the owning stack
        "label": str,           # user-visible label for the ROI
        "shape": str,           # "rectangle", "circle", "ellipse", "polygon"
        "params": dict,         # coordinate-space parameters (subclass-specific)
        "color": str,           # display colour
        "visible": bool,        # whether this ROI participates in plots
        "graphics_item": None,  # QGraphicsItem reference (runtime only)
    }

The controller distinguishes between:

- **list visibility** : all ROIs are always listed in the UI; the checkbox
  controls ``visible`` and therefore whether the ROI appears in plots.
- **scene visibility** : only ROIs belonging to the current stack and with
  ``visible == True`` are shown in the graphics scene.
- **stack link** : when a stack is hidden or deleted, its ROIs are
  automatically hidden or removed.

Subclasses must implement all methods prefixed with ``_space_*`` to handle
coordinate-space-specific geometry creation and parameter extraction.

The controller now receives a :class:`StackManager` for stack lookups and
a scene object.  It no longer depends on any plot controller.
"""

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QMessageBox,
    QInputDialog,
    QColorDialog,
)
import numpy as np

from puprisa.model.stack_manager import StackManager
from puprisa.utils.color_utils import MATLAB_COLORS

DEFAULT_COLOR_PALETTE = MATLAB_COLORS


class BaseRoiController(QObject):
    """Abstract controller for ROI lists bound to multiple stacks.

    Concrete subclasses must implement:

    - ``_space_default_params(shape)``
    - ``_space_create_graphics_item(roi)``
    - ``_space_update_params_from_item(roi)``
    - ``_space_build_mask(roi, pps)``

    The base class handles list management, visibility rules, colour,
    renaming, deletion, conversion to mask, and stack-related notifications.
    """

    # Emitted whenever the ROI list changes or any ROI is modified.
    roiChanged = Signal()

    # Emitted when the user requests to convert an ROI into an exclude mask.
    # Arguments: roi_id (str), stack_id (str), exclude_mask (2D bool array)
    roiConvertToMaskRequested = Signal(str, str, np.ndarray)

    def __init__(
        self,
        roi_list_widget: QListWidget,
        shape_combo: QComboBox,
        scene,
        stack_manager: StackManager,
    ):
        super().__init__()
        self.roi_list_widget = roi_list_widget
        self.shape_combo = shape_combo
        self.scene = scene
        self.stack_manager = stack_manager

        # Global list of all ROIs, regardless of stack.
        self.rois: list[dict] = []

        # Currently selected stack id and name
        self._current_stack_id: str | None = None
        self._current_stack_name: str = ""

        # Colour cycling for new ROIs
        self._roi_color_index = 0

        # Generator counter for ROI ids
        self._roi_id_counter = 0

        # Connect UI signals
        self.roi_list_widget.itemChanged.connect(self._on_item_changed)
        self.roi_list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_current_stack(self, stack_item: dict | None):
        """Update the current stack context.

        Used to determine which ROIs are visible/interactive in the scene.
        The ROIs themselves are not cleared; only scene visibility changes.
        """
        if stack_item is None:
            self._current_stack_id = None
            self._current_stack_name = ""
        else:
            self._current_stack_id = stack_item["id"]
            self._current_stack_name = stack_item.get("name", "")

        self._sync_visibility_in_scene()
        self.refresh_list_widget()
        self.roiChanged.emit()

    def update_visibility_by_stack(self, stack_id: str, visible: bool):
        """Force all ROIs belonging to ``stack_id`` to be visible/hidden.

        This is connected to the stack manager's visibility signal.
        When a stack is hidden, its ROIs are automatically disabled.
        """
        for roi in self.rois:
            if roi["stack_id"] == stack_id:
                roi["visible"] = visible
                self._update_graphics_item_visibility(roi)

        self.refresh_list_widget()
        self.roiChanged.emit()

    def remove_rois_for_stack(self, stack_id: str):
        """Remove all ROIs belonging to the given stack."""
        rois_to_remove = [r for r in self.rois if r["stack_id"] == stack_id]
        for roi in rois_to_remove:
            if roi["graphics_item"] is not None:
                self.scene.removeItem(roi["graphics_item"])
            self.rois.remove(roi)

        self.refresh_list_widget()
        self.roiChanged.emit()

    def add_roi(self):
        """Create a new ROI for the current stack and add it to the global list."""
        if self._current_stack_id is None:
            QMessageBox.warning(None, "Add ROI", "Please select a stack first.")
            return None

        shape = self._current_shape()
        if shape not in ("rectangle", "circle", "ellipse", "polygon"):
            QMessageBox.warning(None, "Add ROI", f"Unsupported shape: {shape}")
            return None

        params = self._space_default_params(shape)
        color = self._next_color()
        roi_id = self._generate_roi_id()
        label = self._default_label(roi_id, shape)

        roi = {
            "id": roi_id,
            "stack_id": self._current_stack_id,
            "label": label,
            "shape": shape,
            "params": params,
            "color": color,
            "visible": True,
            "graphics_item": None,
        }

        self._space_create_graphics_item(roi)
        self.rois.append(roi)

        self._sync_visibility_in_scene()
        self.refresh_list_widget()
        self.roiChanged.emit()
        return roi_id

    def delete_selected_roi(self):
        """Delete the ROI currently selected in the list widget."""
        item = self.roi_list_widget.currentItem()
        if item is None:
            QMessageBox.warning(None, "Delete ROI", "Select an ROI first.")
            return False

        roi_id = item.data(Qt.ItemDataRole.UserRole)
        roi = self._find_roi(roi_id)
        if roi is None:
            return False

        if roi["graphics_item"] is not None:
            self.scene.removeItem(roi["graphics_item"])
        self.rois.remove(roi)

        self.refresh_list_widget()
        self.roiChanged.emit()
        return True

    def rename_selected_roi(self):
        """Rename the selected ROI."""
        item = self.roi_list_widget.currentItem()
        if item is None:
            QMessageBox.warning(None, "Rename ROI", "Select an ROI first.")
            return False

        roi_id = item.data(Qt.ItemDataRole.UserRole)
        roi = self._find_roi(roi_id)
        if roi is None:
            return False

        text, ok = QInputDialog.getText(
            None, "Rename ROI", "New label:", text=roi["label"]
        )
        if ok and text.strip():
            roi["label"] = text.strip()
            self.refresh_list_widget()
            self.roiChanged.emit()
            return True
        return False

    def get_all_rois(self) -> list[dict]:
        """Return a shallow copy of the global ROI list."""
        return list(self.rois)

    def get_visible_rois(self) -> list[dict]:
        """Return only ROIs with ``visible == True``."""
        return [r for r in self.rois if r["visible"]]

    def convert_selected_roi_to_mask(self):
        """Convert the currently selected ROI into an exclude mask.

        The mask is built in pixel space by the subclass (``_space_build_mask``)
        and emitted via :attr:`roiConvertToMaskRequested` together with the
        owning stack's id.
        """
        item = self.roi_list_widget.currentItem()
        if item is None:
            QMessageBox.warning(None, "Convert to Mask", "Select an ROI first.")
            return

        roi_id = item.data(Qt.ItemDataRole.UserRole)
        roi = self._find_roi(roi_id)
        if roi is None:
            return

        stack_item = self.stack_manager.get_item_by_id(roi["stack_id"])
        if stack_item is None:
            QMessageBox.warning(None, "Convert to Mask", "Stack not found.")
            return

        pps = stack_item["pps"]
        keep_mask = self._space_build_mask(roi, pps)
        if keep_mask is None or not np.any(keep_mask):
            QMessageBox.warning(None, "Convert to Mask", "ROI is empty.")
            return

        # Emit the exclude mask (complement of the keep region).
        self.roiConvertToMaskRequested.emit(roi_id, roi["stack_id"], ~keep_mask)

    def refresh_list_widget(self):
        """Rebuild the QListWidget from the global ROI list."""
        self.roi_list_widget.blockSignals(True)
        selected_id = self._current_selected_id()

        self.roi_list_widget.clear()
        for roi in self.rois:
            item = QListWidgetItem(roi["label"])
            item.setData(Qt.ItemDataRole.UserRole, roi["id"])
            item.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
            )
            item.setCheckState(
                Qt.CheckState.Checked if roi["visible"] else Qt.CheckState.Unchecked
            )

            pm = QPixmap(12, 12)
            pm.fill(QColor(roi["color"]))
            item.setIcon(QIcon(pm))

            self.roi_list_widget.addItem(item)

            if roi["id"] == selected_id:
                self.roi_list_widget.setCurrentItem(item)

        self.roi_list_widget.blockSignals(False)

    # ------------------------------------------------------------------
    # Protected helpers (shared by subclasses)
    # ------------------------------------------------------------------
    def _find_roi(self, roi_id: str) -> dict | None:
        """Return the ROI dict with the given id, or None."""
        return next((r for r in self.rois if r["id"] == roi_id), None)

    def _current_shape(self) -> str:
        """Return the currently selected shape from the combo box."""
        return self.shape_combo.currentText().lower()

    def _current_pps(self):
        """Return the :class:`PPS` object of the current stack, or None."""
        item = self.stack_manager.get_current_item()
        return item["pps"] if item else None

    def _next_color(self) -> str:
        """Return the next colour from the shared palette."""
        color = DEFAULT_COLOR_PALETTE[self._roi_color_index % len(DEFAULT_COLOR_PALETTE)]
        self._roi_color_index += 1
        return color

    def _generate_roi_id(self) -> str:
        """Generate a unique ROI id."""
        existing_ids = {r["id"] for r in self.rois}
        while True:
            self._roi_id_counter += 1
            candidate = f"roi_{self._roi_id_counter}"
            if candidate not in existing_ids:
                return candidate

    def _default_label(self, roi_id: str, shape: str) -> str:
        """Create a default label for a new ROI."""
        if self._current_stack_name:
            return f"{roi_id} of {self._current_stack_name}"
        return f"{roi_id} ({shape})"

    def _current_selected_id(self) -> str | None:
        """Return the id of the currently selected list item, or None."""
        item = self.roi_list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _sync_visibility_in_scene(self):
        """Ensure only ROIs of the current stack are visible in the scene."""
        for roi in self.rois:
            self._update_graphics_item_visibility(roi)

    def _update_graphics_item_visibility(self, roi: dict):
        """Set the visibility of a single ROI's graphics item."""
        item = roi.get("graphics_item")
        if item is not None:
            show_in_scene = (
                roi["stack_id"] == self._current_stack_id
                and roi["visible"]
            )
            item.setVisible(show_in_scene)

    # ------------------------------------------------------------------
    # Abstract methods — coordinate-space-specific behaviour
    # ------------------------------------------------------------------
    def _space_default_params(self, shape: str) -> dict:
        """Return default geometry parameters in the coordinate space."""
        raise NotImplementedError

    def _space_create_graphics_item(self, roi: dict):
        """Create a QGraphicsItem in the scene for the given ROI."""
        raise NotImplementedError

    def _space_update_params_from_item(self, roi: dict):
        """Update ``roi["params"]`` from the graphics item's geometry."""
        raise NotImplementedError

    def _space_build_mask(self, roi: dict, pps) -> np.ndarray | None:
        """Build a 2D pixel-space keep-mask for the given ROI.

        Parameters
        ----------
        roi : dict
            The ROI dictionary.
        pps : PPS
            The owning stack.

        Returns
        -------
        np.ndarray or None
            Boolean mask of shape ``pps.image_dimensions`` where ``True``
            marks pixels inside the ROI.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # UI event handlers (common)
    # ------------------------------------------------------------------
    def _on_graphics_item_changed(self, roi_id: str):
        """Called when a graphics item is moved/resized; update ROI data."""
        roi = self._find_roi(roi_id)
        if roi is None:
            return
        self._space_update_params_from_item(roi)
        self.roiChanged.emit()

    def _on_item_changed(self, item: QListWidgetItem):
        """Handle checkbox toggles for ROI visibility."""
        roi_id = item.data(Qt.ItemDataRole.UserRole)
        roi = self._find_roi(roi_id)
        if roi is None:
            return

        roi["visible"] = item.checkState() == Qt.CheckState.Checked
        self._update_graphics_item_visibility(roi)
        self.roiChanged.emit()

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Open a colour picker to change the ROI colour."""
        roi_id = item.data(Qt.ItemDataRole.UserRole)
        roi = self._find_roi(roi_id)
        if roi is None:
            return

        current_color = QColor(roi["color"])
        new_color = QColorDialog.getColor(current_color, None, "Choose ROI Color")
        if new_color.isValid():
            roi["color"] = new_color.name()
            if roi["graphics_item"] is not None and hasattr(
                roi["graphics_item"], "set_roi_color"
            ):
                roi["graphics_item"].set_roi_color(new_color)
            self.refresh_list_widget()
            self.roiChanged.emit()