# puprisa/ui/main_window.py
"""Main pump-probe analysis window.

Thin assembly shell: creates viewmodels and controllers from the
ApplicationContext and wires UI widgets to them.  No business logic here.
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow

from puprisa.app_context import ApplicationContext
from puprisa.controllers.plot_controller import PlotController
from puprisa.controllers.curve_controller import CurveController
from puprisa.controllers.mask_controller import MaskController
from puprisa.controllers.pps_slice_controller import PPSSliceController
from puprisa.controllers.processing_controller import ProcessingController
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

        self.stack_view_model.colorChangeRequested.connect(self.stack_controller.change_stack_color)
        self.ui.stackAddButton.clicked.connect(self.stack_controller.open_stack_dialog)
        self.ui.stackRenameButton.clicked.connect(lambda: self.stack_controller.rename_selected_stack(self.stack_view_model._selected_stack_index()))
        self.ui.stackDeleteButton.clicked.connect(lambda: self.stack_controller.delete_selected_stack(self.stack_view_model._selected_stack_index()))
        self.ui.actionOpenStack.triggered.connect(self.stack_controller.open_stack_dialog)
        self.ui.actionSaveStackTIFF.triggered.connect(lambda: self.stack_controller.save_selected_stack(index=self.stack_view_model._selected_stack_index(), format="tiff"))
        self.ui.actionSaveStackPickle.triggered.connect(lambda: self.stack_controller.save_selected_stack(index=self.stack_view_model._selected_stack_index(), format="pickle"))
        self.ui.actionExit.triggered.connect(self.close)

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

        self.ui.maskReverseButton.clicked.connect(lambda: self.mask_controller.reverse_mask(self.mask_view_model.selected_mask_id()))
        self.ui.maskRenameButton.clicked.connect(lambda: self.mask_controller.rename_mask(self.mask_view_model.selected_mask_id()))
        self.ui.maskDeleteButton.clicked.connect(lambda: self.mask_controller.delete_mask(self.mask_view_model.selected_mask_id()))

        self.ui.actionImportMask.triggered.connect(self.mask_controller.import_masks_from_json)
        self.ui.actionExportMask.triggered.connect(self.mask_controller.export_all_masks)
        self.ui.actionClearAllMasks.triggered.connect(self.mask_controller.clear_all_masks)
        self.ui.actionExportSelectedMask.triggered.connect(lambda: self.mask_controller.export_selected_mask(self.mask_view_model.selected_mask_id()))
        self.ui.actionMaskIntensityThreshold.triggered.connect(self.mask_controller.show_intensity_threshold_dialog)
        self.ui.actionMaskMath.triggered.connect(self.mask_controller.show_mask_math_dialog)

        # --------------------------------------------------------------
        # Image plot / slice: ViewModel + Controller
        # --------------------------------------------------------------
        self.plot_view_model = PPSPlotViewModel(
            stack_manager=ctx.stack_manager,
            mask_manager=ctx.mask_manager,
            processing_manager=ctx.processing_manager,
            plot_manager=ctx.plot_manager,
            roi_manager=ctx.roi_manager,
            curve_manager=ctx.curve_manager,
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
        self.plot_controller = PlotController(
            plot_manager=ctx.plot_manager,
            parent_widget=self,
        )

        self.ui.actionStandardDeviation.triggered.connect(lambda: self.plot_controller.set_std_dev())
        self.ui.actionFullRange.triggered.connect(lambda: self.plot_controller.set_full_range())
        self.ui.actionCustomRange.triggered.connect(lambda: self.plot_controller.show_custom_range_dialog())
        self.ui.actionDefault.triggered.connect(lambda: self.plot_controller.set_colormap("pumpprobe"))
        self.ui.actionRdBuR.triggered.connect(lambda: self.plot_controller.set_colormap("RdBu_r"))
        self.ui.actionViridis.triggered.connect(lambda: self.plot_controller.set_colormap("viridis"))
        self.ui.actionGray.triggered.connect(lambda: self.plot_controller.set_colormap("gray"))
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

        self.roi_view_model.colorChangeRequested.connect(self.roi_controller.change_roi_color)
        self.ui.actionEditROI.triggered.connect(lambda: self.roi_controller.edit_roi(self.roi_view_model.selected_roi_id()))
        self.ui.roiAddButton.clicked.connect(lambda: self.roi_controller.add_roi(self.ui.roiShapeComboBox.currentText().lower()))
        self.ui.roiRenameButton.clicked.connect(lambda: self.roi_controller.rename_roi(self.roi_view_model.selected_roi_id()))
        self.ui.roiDeleteButton.clicked.connect(lambda: self.roi_controller.delete_roi(self.roi_view_model.selected_roi_id()))
        self.ui.roiConvertToMaskButton.clicked.connect(lambda: self.roi_controller.convert_roi_to_mask(self.roi_view_model.selected_roi_id()))

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
        self.ui.actionCurveFit.triggered.connect(lambda: self.curve_controller.open_fit_dialog(space="pixel", normalize=self.curve_view_model.normalize))
        self.ui.actionViewCurve.triggered.connect(lambda: self.curve_controller.view_standalone(space="pixel", normalize=self.curve_view_model.normalize))
        self.ui.actionExportCurve.triggered.connect(lambda: self.curve_controller.export_curve_dialog(space="pixel", normalize=self.curve_view_model.normalize))
        self.slice_controller.sliceChanged.connect(self.curve_view_model.set_current_slice)
        self.ui.actionSaveView.triggered.connect(lambda: self.plot_view_model.view_standalone(normalize=self.curve_view_model.normalize))
        # --------------------------------------------------------------
        # Processing: Controller only (no viewmodel, no UI widgets)
        # --------------------------------------------------------------
        self.processing_controller = ProcessingController(
            stack_manager=ctx.stack_manager,
            processing_manager=ctx.processing_manager,
            parent_widget=self,
        )
        self.ui.actionSubNegativeTime.triggered.connect(self.processing_controller.show_neg_delay_background_subtraction_dialog)
        self.ui.actionSubFixedValue.triggered.connect(self.processing_controller.show_fixed_value_background_subtraction_dialog)
        self.ui.actionSubFirstLastNFrames.triggered.connect(self.processing_controller.show_background_subtraction_dialog)
        self.ui.actionResetBackgroundSubtraction.triggered.connect(self.processing_controller.reset_background_subtraction)
        self.ui.actionSlice.triggered.connect(self.processing_controller.show_slice_dialog)
        self.ui.actionDownsample.triggered.connect(self.processing_controller.show_downsample_dialog)
        self.ui.actionSVDDenoise.triggered.connect(self.processing_controller.show_svd_denoise_dialog)
        self.ui.actionStackMath.triggered.connect(self.processing_controller.show_stack_math_dialog)

        # Phasor window
        self.ui.actionPhasor.triggered.connect(self._open_phasor_window)

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