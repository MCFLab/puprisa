# puprisa/ui/main_window.py
"""Main pump-probe analysis window.

Thin assembly shell: creates viewmodels and controllers from the
ApplicationContext and wires UI widgets to them.  No business logic here.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow

from puprisa.app_context import ApplicationContext
from puprisa.controllers.curve_controller import CurveController
from puprisa.controllers.mask_controller import MaskController
from puprisa.controllers.pps_slice_controller import PPSSliceController
from puprisa.controllers.roi_controller import RoiController
from puprisa.controllers.stack_controller import StackController
from puprisa.ui.generated.ui_main_window import Ui_MainWindow
from puprisa.viewmodels.curve_view_model import CurveViewModel
from puprisa.viewmodels.mask_view_model import MaskViewModel
from puprisa.viewmodels.pps_plot_view_model import PPSPlotViewModel
from puprisa.viewmodels.roi_scene_bridge import PixelRoiSceneBridge
from puprisa.viewmodels.roi_view_model import RoiViewModel
from puprisa.viewmodels.stack_view_model import StackViewModel


class MainWindow(QMainWindow):
    """Main pump-probe analysis window."""

    def __init__(self, ctx: ApplicationContext):
        super().__init__()
        self.ctx = ctx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --------------------------------------------------------------
        # Stack list: ViewModel + Controller
        # --------------------------------------------------------------
        self.stack_view_model = StackViewModel(
            manager=ctx.stack_manager,
            list_widget=self.ui.stackListWidget,
            parent=self,
        )
        self.stack_controller = StackController(
            manager=ctx.stack_manager,
            parent_widget=self,
        )

        self.ui.stackAddButton.clicked.connect(self.stack_controller.open_stack_dialog)
        self.ui.stackRenameButton.clicked.connect(self._rename_selected_stack)
        self.ui.stackDeleteButton.clicked.connect(self._delete_selected_stack)

        self.ui.actionOpenStack.triggered.connect(self.stack_controller.open_stack_dialog)

        # --------------------------------------------------------------
        # Mask list: ViewModel + Controller  (creates before ROI because
        # ROI controller needs mask manager through context, not the view)
        # --------------------------------------------------------------
        self.mask_view_model = MaskViewModel(
            mask_manager=ctx.mask_manager,
            stack_manager=ctx.stack_manager,
            list_widget=self.ui.maskListWidget,
            parent=self,
        )
        self.mask_controller = MaskController(
            mask_manager=ctx.mask_manager,
            stack_manager=ctx.stack_manager,
            parent_widget=self,
        )

        self.ui.maskReverseButton.clicked.connect(self._reverse_selected_mask)
        self.ui.maskRenameButton.clicked.connect(self._rename_selected_mask)
        self.ui.maskDeleteButton.clicked.connect(self._delete_selected_mask)

        self.ui.actionImportMask.triggered.connect(self.mask_controller.import_masks_from_json)
        self.ui.actionExportMask.triggered.connect(self.mask_controller.export_all_masks)
        self.ui.actionClearAllMasks.triggered.connect(self.mask_controller.clear_all_masks)
        self.ui.actionIntensityThreshold.triggered.connect(self.mask_controller.show_intensity_threshold_dialog)

        # --------------------------------------------------------------
        # Image plot / slice: ViewModel + Controller
        # --------------------------------------------------------------
        self.plot_view_model = PPSPlotViewModel(
            stack_manager=ctx.stack_manager,
            mask_manager=ctx.mask_manager,
            processing_manager=ctx.processing_manager,
            graphics_view=self.ui.ppsGraphicsView,
            colorbar=self.ui.colorbar,
            parent=self,
        )
        self.slice_controller = PPSSliceController(
            stack_manager=ctx.stack_manager,
            plot_viewmodel=self.plot_view_model,
            slider=self.ui.sliceSlider,
            slice_label=self.ui.sliceNumberLabel,
            axis_label=self.ui.axisLabel,
            parent=self,
        )

        self.ui.ppsGraphicsView.wheelSliceChanged.connect(self.slice_controller.change_slice_by_delta)

        # --------------------------------------------------------------
        # ROI list + scene: ViewModel + Controller
        # --------------------------------------------------------------
        self.pixel_bridge = PixelRoiSceneBridge(stack_manager=ctx.stack_manager)
        self.roi_view_model = RoiViewModel(
            roi_manager=ctx.roi_manager,
            stack_manager=ctx.stack_manager,
            list_widget=self.ui.roiListWidget,
            scene=self.plot_view_model._scene,
            bridge=self.pixel_bridge,
            space="pixel",
            parent=self,
        )
        self.roi_controller = RoiController(
            roi_manager=ctx.roi_manager,
            stack_manager=ctx.stack_manager,
            parent_widget=self,
            space="pixel",
        )

        self.ui.roiAddButton.clicked.connect(self._add_roi)
        self.ui.roiRenameButton.clicked.connect(self._rename_selected_roi)
        self.ui.roiDeleteButton.clicked.connect(self._delete_selected_roi)
        self.ui.roiConvertToMaskButton.clicked.connect(self._convert_selected_roi_to_mask)

        # --------------------------------------------------------------
        # Curve: ViewModel + Controller
        # --------------------------------------------------------------
        self.curve_view_model = CurveViewModel(
            curve_manager=ctx.curve_manager,
            roi_manager=ctx.roi_manager,
            stack_manager=ctx.stack_manager,
            mask_manager=ctx.mask_manager,
            processing_manager=ctx.processing_manager,
            canvas=self.ui.plotCanvas,
            space="pixel",
            parent=self,
        )
        self.curve_controller = CurveController(
            curve_manager=ctx.curve_manager,
            parent_widget=self,
        )

        self.ui.actionNormalizeCurve.toggled.connect(self.curve_view_model.set_normalize)
        self.ui.actionViewCurve.triggered.connect(lambda: self.curve_controller.view_standalone(space="pixel", normalize=self.curve_view_model.normalize))
        self.ui.actionExportCurve.triggered.connect(lambda: self.curve_controller.export_curve_dialog(space="pixel", normalize=self.curve_view_model.normalize))

        # --------------------------------------------------------------
        # View menu
        # --------------------------------------------------------------
        self.ui.actionStandardDeviation.triggered.connect(lambda: self.plot_view_model.set_color_scale_mode(PPSPlotViewModel.MODE_STD_DEV))
        self.ui.actionFullRange.triggered.connect(lambda: self.plot_view_model.set_color_scale_mode(PPSPlotViewModel.MODE_FULL_RANGE))
        self.ui.actionDefault.triggered.connect(lambda: self.plot_view_model.set_colormap("pumpprobe"))
        self.ui.actionRdBuR.triggered.connect(lambda: self.plot_view_model.set_colormap("RdBu_r"))
        self.ui.actionViridis.triggered.connect(lambda: self.plot_view_model.set_colormap("viridis"))
        self.ui.actionGray.triggered.connect(lambda: self.plot_view_model.set_colormap("gray"))

        # Phasor window
        self.ui.actionPhasor.triggered.connect(self._open_phasor_window)

    # ------------------------------------------------------------------
    # Stack action helpers
    # ------------------------------------------------------------------
    def _selected_stack_index(self) -> int:
        return self.ui.stackListWidget.currentRow()

    def _rename_selected_stack(self) -> None:
        index = self._selected_stack_index()
        if index < 0:
            return
        self.stack_controller.rename_selected_stack(index)

    def _delete_selected_stack(self) -> None:
        index = self._selected_stack_index()
        if index < 0:
            return
        self.stack_controller.delete_selected_stack(index)

    # ------------------------------------------------------------------
    # Mask action helpers
    # ------------------------------------------------------------------
    def _selected_mask_id(self) -> str | None:
        item = self.ui.maskListWidget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _reverse_selected_mask(self) -> None:
        mask_id = self._selected_mask_id()
        if mask_id:
            self.mask_controller.reverse_mask(mask_id)

    def _rename_selected_mask(self) -> None:
        mask_id = self._selected_mask_id()
        if mask_id:
            self.mask_controller.rename_mask(mask_id)

    def _delete_selected_mask(self) -> None:
        mask_id = self._selected_mask_id()
        if mask_id:
            self.mask_controller.delete_mask(mask_id)

    # ------------------------------------------------------------------
    # ROI action helpers
    # ------------------------------------------------------------------
    def _selected_roi_id(self) -> str | None:
        item = self.ui.roiListWidget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _add_roi(self) -> None:
        shape = self.ui.roiShapeComboBox.currentText().lower()
        self.roi_controller.add_roi(shape)

    def _rename_selected_roi(self) -> None:
        roi_id = self._selected_roi_id()
        if roi_id:
            self.roi_controller.rename_roi(roi_id)

    def _delete_selected_roi(self) -> None:
        roi_id = self._selected_roi_id()
        if roi_id:
            self.roi_controller.delete_roi(roi_id)

    def _convert_selected_roi_to_mask(self) -> None:
        roi_id = self._selected_roi_id()
        if roi_id:
            self.roi_controller.convert_roi_to_mask(roi_id)

    # ------------------------------------------------------------------
    # Phasor window
    # ------------------------------------------------------------------
    def _open_phasor_window(self) -> None:
        if not hasattr(self, "_phasor_window"):
            self._phasor_window = self.ctx.create_phasor_window()
        self._phasor_window.show()

    # ------------------------------------------------------------------
    # Fit image view on resize
    # ------------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        QTimer.singleShot(0, self.plot_view_model.fit_view)