# puprisa/ui/phasor_window.py
"""Phasor analysis window.

Thin assembly shell: creates viewmodels and controllers from the
ApplicationContext and wires UI widgets to them.  No business logic here.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow

from puprisa.app_context import ApplicationContext
from puprisa.controllers.curve_controller import CurveController
from puprisa.controllers.mask_controller import MaskController
from puprisa.controllers.phasor_freq_controller import PhasorFrequencyController
from puprisa.controllers.roi_controller import RoiController
from puprisa.controllers.stack_controller import StackController
from puprisa.ui.generated.ui_phasor_window import Ui_PhasorWindow
from puprisa.viewmodels.curve_view_model import CurveViewModel
from puprisa.viewmodels.mask_view_model import MaskViewModel
from puprisa.viewmodels.phasor_plot_view_model import PhasorPlotViewModel
from puprisa.viewmodels.roi_scene_bridge import PhasorRoiSceneBridge
from puprisa.viewmodels.roi_view_model import RoiViewModel
from puprisa.viewmodels.stack_view_model import StackViewModel


class PhasorWindow(QMainWindow):
    """Phasor analysis window."""

    def __init__(self, ctx: ApplicationContext):
        super().__init__()
        self.ctx = ctx
        self.ui = Ui_PhasorWindow()
        self.ui.setupUi(self)

        # --------------------------------------------------------------
        # Stack list
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

        # --------------------------------------------------------------
        # Mask list
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

        # --------------------------------------------------------------
        # Phasor plot / spatial view
        # --------------------------------------------------------------
        self.phasor_plot_view_model = PhasorPlotViewModel(
            stack_manager=ctx.stack_manager,
            processing_manager=ctx.processing_manager,
            roi_manager=ctx.roi_manager,
            mask_manager=ctx.mask_manager,
            curve_manager=ctx.curve_manager,
            phasor_graphics_view=self.ui.phasorGraphicsView,
            spatial_graphics_view=self.ui.ppsGraphicsView,
            parent=self,
        )
        self.frequency_controller = PhasorFrequencyController(
            slider=self.ui.freqSlider,
            spinbox=self.ui.freqSpinBox,
            parent=self,
        )
        self.frequency_controller.frequencyChanged.connect(self.phasor_plot_view_model.set_frequency)
        self.phasor_plot_view_model.set_frequency(self.frequency_controller.frequency())
        self.ui.phasorGraphicsView.wheelSliceChanged.connect(self.frequency_controller.change_frequency_by_delta)

        # --------------------------------------------------------------
        # ROI list + scene
        # --------------------------------------------------------------
        self.phasor_bridge = PhasorRoiSceneBridge()
        self.roi_view_model = RoiViewModel(
            roi_manager=ctx.roi_manager,
            stack_manager=ctx.stack_manager,
            list_widget=self.ui.phasorRoiListWidget,
            scene=self.phasor_plot_view_model.phasor_scene,
            bridge=self.phasor_bridge,
            space="phasor",
            parent=self,
        )
        self.roi_controller = RoiController(
            roi_manager=ctx.roi_manager,
            stack_manager=ctx.stack_manager,
            parent_widget=self,
            space="phasor",
        )

        self.roi_view_model.colorChangeRequested.connect(self.roi_controller.change_roi_color)
        self.ui.actionEditROI.triggered.connect(lambda: self.roi_controller.edit_roi(self.roi_view_model.selected_roi_id()))
        self.ui.actionImportROI.triggered.connect(self.roi_controller.import_rois)
        self.ui.actionExportSelectedROI.triggered.connect(lambda: self.roi_controller.export_selected_roi(self.roi_view_model.selected_roi_id()))
        self.ui.actionExportROI.triggered.connect(self.roi_controller.export_all_rois)
        self.ui.phasorRoiAddButton.clicked.connect(lambda: self.roi_controller.add_roi(self.ui.phasorRoiShapeComboBox.currentText().lower()))
        self.ui.phasorRoiRenameButton.clicked.connect(lambda: self.roi_controller.rename_roi(self.roi_view_model.selected_roi_id()))
        self.ui.phasorRoiDeleteButton.clicked.connect(lambda: self.roi_controller.delete_roi(self.roi_view_model.selected_roi_id()))
        self.ui.phasorRoiConvertToMaskButton.clicked.connect(lambda: self.roi_controller.convert_roi_to_mask(self.roi_view_model.selected_roi_id()))

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
            space="phasor",
            parent=self,
        )
        self.curve_controller = CurveController(
            curve_manager=ctx.curve_manager,
            stack_manager=ctx.stack_manager,
            parent_widget=self,
        )

        self.ui.actionNormalizeCurve.toggled.connect(self.curve_view_model.set_normalize)
        self.ui.actionViewCurve.triggered.connect(lambda: self.curve_controller.view_standalone(space="phasor", normalize=self.curve_view_model.normalize))
        self.ui.actionExportCurve.triggered.connect(lambda: self.curve_controller.export_curve_dialog(space="phasor", normalize=self.curve_view_model.normalize))

        # --------------------------------------------------------------
        # View menu / fit on show and resize
        # --------------------------------------------------------------
        self.ui.actionSavePhasorView.triggered.connect(self.phasor_plot_view_model.view_phasor)
        self.ui.actionSaveView.triggered.connect(self.phasor_plot_view_model.view_standalone)

    # ------------------------------------------------------------------
    # Fit views on show / resize
    # ------------------------------------------------------------------
    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self.phasor_plot_view_model.fit_phasor_view)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        QTimer.singleShot(0, self.phasor_plot_view_model.fit_phasor_view)
        QTimer.singleShot(0, self.phasor_plot_view_model.fit_spatial_view)