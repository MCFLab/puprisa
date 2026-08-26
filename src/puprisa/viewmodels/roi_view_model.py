# puprisa/viewmodels/roi_view_model.py
"""Qt view model for ROI list and graphics scene synchronization.

Binds a RoiManager (model) to a QListWidget and a QGraphicsScene.
Coordinate-space differences (pixel vs phasor) are delegated to a
:class:`RoiSceneBridge` instance, keeping this class space-agnostic.
"""
from PySide6.QtCore import QObject, Qt, Signal, QSignalBlocker
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QGraphicsScene

import numpy as np

from puprisa.model.entities import RoiItem
from puprisa.model.roi_manager import RoiEvent, RoiManager
from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.utils.color_utils import _matplotlib_color_to_qt
from puprisa.viewmodels.roi_scene_bridge import RoiSceneBridge

class RoiViewModel(QObject):
    """Synchronize RoiManager state with a list widget and scene."""

    roiSelectionChanged = Signal(str)          # roi_id | ""

    def __init__(
        self,
        roi_manager: RoiManager,
        stack_manager: StackManager,
        list_widget: QListWidget,
        scene: QGraphicsScene,
        bridge: RoiSceneBridge,
        space: str,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._roi_manager = roi_manager
        self._stack_manager = stack_manager
        self._list_widget = list_widget
        self._scene = scene
        self._bridge = bridge
        self._space = space

        # Model -> View
        self._roi_manager.add_listener(self._on_roi_event)
        self._stack_manager.add_listener(self._on_stack_event)

        # View -> Model for checkbox toggles only
        self._list_widget.itemChanged.connect(self._on_item_changed)

        self._rebuild()

    # ------------------------------------------------------------------
    # Model -> View
    # ------------------------------------------------------------------
    def _on_roi_event(self, event: RoiEvent) -> None:
        if event.roi is None:
            return
        if event.roi.space != self._space:
            return
        if event.event == "added":
            self._create_scene_item(event.roi)
            self._rebuild()
        elif event.event == "removed":
            self._remove_scene_item(event.roi)
            self._rebuild()
        elif event.event == "params_changed":
            self._sync_scene_item_geometry(event.roi)
        elif event.event == "label_changed":
            self._rebuild()
        elif event.event == "color_changed":
            self._bridge.set_item_color(event.roi, event.roi.color)
            self._rebuild()
        elif event.event == "visibility_changed":
            self._update_scene_visibility(event.roi)
            self._rebuild()
        
    def _on_stack_event(self, event: StackEvent) -> None:
        if event.event == "current_changed":
            self._update_all_scene_visibility()
            self._rebuild()

    # ------------------------------------------------------------------
    # View -> Model
    # ------------------------------------------------------------------
    def _on_item_changed(self, item: QListWidgetItem) -> None:
        roi_id = item.data(Qt.ItemDataRole.UserRole)
        visible = item.checkState() == Qt.CheckState.Checked
        roi = self._roi_manager.get_roi_by_id(roi_id)
        if roi is not None and roi.visible != visible:
            self._roi_manager.set_visible(roi_id, visible)

    # ------------------------------------------------------------------
    # Scene item management
    # ------------------------------------------------------------------
    def _create_scene_item(self, roi: RoiItem) -> None:
        item = self._bridge.create_item(roi)
        roi.graphics_item = item
        item.setZValue(10)
        item.set_roi_changed_callback(lambda: self._on_graphics_item_changed(roi.id))
        item.set_movement_bounds(self._bridge.movement_bounds(roi))
        self._scene.addItem(item)
        self._update_scene_visibility(roi)

    def _remove_scene_item(self, roi: RoiItem) -> None:
        item = roi.graphics_item
        if item is not None:
            self._scene.removeItem(item)
            roi.graphics_item = None

    def _sync_scene_item_geometry(self, roi: RoiItem) -> None:
        """Programmatic params change -> update the item geometry."""
        if roi.graphics_item is not None:
            self._bridge.sync_item_from_params(roi)
            self._update_scene_visibility(roi)

    def _update_scene_visibility(self, roi: RoiItem) -> None:
        item = roi.graphics_item
        if item is not None:
            current_stack_id = self._stack_manager.get_current_stack_id()
            show = roi.visible and roi.stack_id == current_stack_id
            item.setVisible(show)

    def _update_all_scene_visibility(self) -> None:
        for roi in self._roi_manager.get_all_rois():
            if roi.space != self._space:
                continue
            self._update_scene_visibility(roi)

    def _on_graphics_item_changed(self, roi_id: str) -> None:
        roi = self._roi_manager.get_roi_by_id(roi_id)
        if roi is None:
            return
        params = self._bridge.extract_params_from_item(roi)
        self._roi_manager.update_params(roi_id, params)

    # ------------------------------------------------------------------
    # List widget synchronization
    # ------------------------------------------------------------------
    def _rebuild(self) -> None:
        with QSignalBlocker(self._list_widget):
            selected_id = self.selected_roi_id()
            self._list_widget.clear()
            for roi in self._roi_manager.get_all_rois():
                if roi.space != self._space:
                    continue
                item = self._make_item(roi)
                self._list_widget.addItem(item)
                if roi.id == selected_id:
                    self._list_widget.setCurrentItem(item)
        self.roiSelectionChanged.emit(selected_id or "")

    @staticmethod
    def _make_item(roi: RoiItem) -> QListWidgetItem:
        item = QListWidgetItem(roi.label)
        item.setData(Qt.ItemDataRole.UserRole, roi.id)
        item.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        item.setCheckState(
            Qt.CheckState.Checked if roi.visible else Qt.CheckState.Unchecked
        )

        qcolor = _matplotlib_color_to_qt(roi.color)
        pixmap = QPixmap(12, 12)
        pixmap.fill(qcolor)
        item.setIcon(QIcon(pixmap))
        return item

    # ------------------------------------------------------------------
    # Widget query helpers
    # ------------------------------------------------------------------
    def selected_roi_id(self) -> str | None:
        item = self._list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None