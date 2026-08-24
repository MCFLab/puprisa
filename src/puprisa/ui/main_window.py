# puprisa/ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QMessageBox, QDialog
import numpy as np

from puprisa.controllers.pps_process_controller import PPSProcessingController
from puprisa.ui.generated.ui_main_window import Ui_MainWindow
from puprisa.controllers.pps_curve_controller import PPSCurveController
from puprisa.controllers.pps_plot_controller import PPSPlotController
from puprisa.controllers.pps_slider_controller import PPSSliderController
from puprisa.controllers.pps_roi_controller import PPSRoiController
from puprisa.controllers.pps_mask_controller import PPSMaskController
from puprisa.controllers.stack_controller import StackViewModel
from puprisa.model.stack_manager import StackManager
from puprisa.ui.dialogs.colorbar_customrange import ColorbarCustomRangeDialog

from puprisa.utils.color_utils import apply_colormap
from puprisa.utils.geometry_utils import shape_to_patch


class MainWindow(QMainWindow):
    """Main pump-probe analysis window."""

    def __init__(self, stack_manager: StackManager):
        super().__init__()
        self.stack_manager = stack_manager

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- Controllers ---
        self.stack_controller = StackViewModel(
            self.stack_manager, self.ui.stackListWidget
        )

        # Image / colorbar controller (owns plotCanvas for curves)
        self.plot_controller = PPSPlotController(
            self.ui.ppsGraphicsView,
            self.ui.colorbar,
            self.ui.plotCanvas,
            None,  # curve_controller assigned after creation
        )

        self.roi_controller = PPSRoiController(
            self.stack_manager,
            self.plot_controller.scene,
            self.ui.roiListWidget,
            self.ui.roiShapeComboBox
        )

        # Curve controller: data computation, export, standalone view
        self.curve_controller = PPSCurveController(
            self.stack_manager,
            self.roi_controller
        )
        self.plot_controller.curve_controller = self.curve_controller

        self.slider_controller = PPSSliderController(
            self.ui.sliceSlider, self.ui.sliceNumberLabel, self.ui.axisLabel,
            self.plot_controller
        )
        self.mask_controller = PPSMaskController(self.ui.maskListWidget)
        self.processing_controller = PPSProcessingController(self.plot_controller)

        # --- Menu connections ---
        self._connect_FileMenu_actions()
        self._connect_ViewMenu_actions()
        self._connect_ProcessMenu_actions()
        self._connect_MaskMenu_actions()
        self._connect_CurveMenu_actions() 
        self._connect_PhasorMenu_actions()

        # --- Button connections ---
        self._connect_buttons()
        self._connect_stack_signals()
        self._connect_slice_signals()
        self._connect_roi_signals()
        self._connect_mask_signals()
        self._connect_processing_signals()

    def _connect_FileMenu_actions(self):
        self.ui.actionOpenStack.triggered.connect(self.stack_controller.add_stack_from_file)

    def _connect_ViewMenu_actions(self):
        self.ui.actionStandardDeviation.triggered.connect(lambda: self.plot_controller.set_colorbar_scale_mode(PPSPlotController.MODE_STD_DEV))
        self.ui.actionFullRange.triggered.connect(lambda: self.plot_controller.set_colorbar_scale_mode(PPSPlotController.MODE_FULL_RANGE))
        self.ui.actionCustomRange.triggered.connect(self._show_custom_range_dialog)
        self.ui.actionDefault.triggered.connect(lambda: self.plot_controller.set_colormap('pumpprobe'))
        self.ui.actionRdBuR.triggered.connect(lambda: self.plot_controller.set_colormap('RdBu_r'))
        self.ui.actionViridis.triggered.connect(lambda: self.plot_controller.set_colormap('viridis'))
        self.ui.actionGray.triggered.connect(lambda: self.plot_controller.set_colormap('gray'))
        self.ui.actionSaveView.triggered.connect(self._save_view)

    def _connect_ProcessMenu_actions(self):
        self.ui.actionNegativeTimeDelaysPixelWise.triggered.connect(lambda: self.processing_controller.apply_background_subtraction_negative_delays(pixelwise=True))
        self.ui.actionNegativeTimeDelaysWholeImage.triggered.connect(lambda: self.processing_controller.apply_background_subtraction_negative_delays(pixelwise=False))
        self.ui.actionFirstLastNImages.triggered.connect(self.processing_controller.show_background_subtraction_dialog)
        self.ui.actionResetBackgroundSubtraction.triggered.connect(self.processing_controller.reset_background_subtraction)
        self.ui.actionIntensityThreshold.triggered.connect(self.mask_controller.show_intensity_threshold_dialog)

    def _connect_CurveMenu_actions(self):
        """Connect curve-related menu actions to the curve controller."""
        self.ui.actionNormalizeCurve.toggled.connect(self._on_normalize_curve_toggled)
        self.ui.actionExportCurve.triggered.connect(self.curve_controller.export_to_csv)
        self.ui.actionViewCurve.triggered.connect(self.curve_controller.view_standalone)

    def _connect_MaskMenu_actions(self):
        self.ui.actionImportMask.triggered.connect(self.mask_controller.import_masks_from_json)
        self.ui.actionExportMask.triggered.connect(self.mask_controller.export_all_masks)
        self.ui.actionClearAllMasks.triggered.connect(self.mask_controller.clear_all_masks)

    def _connect_PhasorMenu_actions(self):
        self.ui.actionPhasor.triggered.connect(self._open_phasor_window)

    # ------------------------------------------------------------------
    # BUTTON CONNECTIONS
    # ------------------------------------------------------------------
    def _connect_buttons(self):
        # Stack buttons
        self.ui.stackAddButton.clicked.connect(self.stack_controller.add_stack_from_file)
        self.ui.stackDeleteButton.clicked.connect(self.stack_controller.delete_selected_stack)
        self.ui.stackRenameButton.clicked.connect(self.stack_controller.rename_selected_stack)

        # ROI buttons
        self.ui.roiAddButton.clicked.connect(self.roi_controller.add_roi)
        self.ui.roiDeleteButton.clicked.connect(self.roi_controller.delete_selected_roi)
        self.ui.roiRenameButton.clicked.connect(self.roi_controller.rename_selected_roi)
        self.ui.roiConvertToMaskButton.clicked.connect(self.roi_controller.convert_selected_roi_to_mask)

        # Mask buttons
        self.ui.maskRenameButton.clicked.connect(self.mask_controller.rename_selected_mask)
        self.ui.maskDeleteButton.clicked.connect(self.mask_controller.delete_selected_mask)
        self.ui.maskReverseButton.clicked.connect(self.mask_controller.reverse_selected_mask)

    # ------------------------------------------------------------------
    # STACK SIGNALS
    # ------------------------------------------------------------------
    def _connect_stack_signals(self):
        self.stack_manager.stackChanged.connect(self._on_stack_changed)
        self.stack_manager.stackVisibilityChanged.connect(self.roi_controller.update_visibility_by_stack)
        self.stack_manager.stackDeleted.connect(self.roi_controller.remove_rois_for_stack)
        self.stack_manager.stackItemsChanged.connect(self._on_stack_items_changed)

    def _on_stack_changed(self, stack_item):
        """Update dependent controllers when the current stack changes."""
        pps = stack_item["pps"] if stack_item else None
        self.plot_controller.set_pps(pps)
        self.slider_controller.set_pps(pps, reset_slice=True)
        self.mask_controller.set_pps(pps)
        self.processing_controller.set_pps(pps)
        self.roi_controller.set_current_stack(stack_item)
        self._refresh_roi_plot()

    def _on_stack_items_changed(self):
        """Refresh ROI-dependent views after stack metadata changes."""
        self.roi_controller.refresh_list_widget()
        self._refresh_roi_plot()

    # ------------------------------------------------------------------
    # SLICE SIGNALS
    # ------------------------------------------------------------------
    def _connect_slice_signals(self):
        self.slider_controller.sliceChanged.connect(self.plot_controller.display_slice)
        self.slider_controller.sliceChanged.connect(self._refresh_roi_plot)
        self.ui.ppsGraphicsView.wheelSliceChanged.connect(self.slider_controller.change_slice_by_delta)

    # ------------------------------------------------------------------
    # ROI SIGNALS
    # ------------------------------------------------------------------
    def _on_normalize_curve_toggled(self, checked: bool):
        """Toggle curve normalization and refresh the embedded plot."""
        self.curve_controller.normalize_curves = checked
        self.plot_controller.update_roi_plot()

    def _connect_roi_signals(self):
        self.plot_controller.pixmapRectChanged.connect(self.roi_controller.set_pixmap_rect)
        self.roi_controller.roiChanged.connect(self._refresh_roi_plot)
        self.roi_controller.roiConvertToMaskRequested.connect(
            self._on_roi_convert_to_mask
        )

    def _refresh_roi_plot(self):
        """Ask the plot controller to redraw the ROI signal curves."""
        self.plot_controller.update_roi_plot()

    def _on_roi_convert_to_mask(self, roi_id, stack_id, exclude_mask):
        """Handle a request to convert an ROI into an exclude mask."""
        stack_item = self.stack_manager.get_item_by_id(stack_id)
        if stack_item is None:
            return

        pps = stack_item["pps"]
        roi = self.roi_controller._find_roi(roi_id)
        label = f"From ROI {roi['label']}" if roi else "From ROI"
        pps.add_mask(exclude_mask, label=label, enabled=True)
        self.mask_controller._refresh_after_change()

    # ------------------------------------------------------------------
    # MASK SIGNALS
    # ------------------------------------------------------------------
    def _connect_mask_signals(self):
        self.mask_controller.maskChanged.connect(self.plot_controller.on_mask_changed)
        self.mask_controller.maskChanged.connect(self._refresh_roi_plot)

    # ------------------------------------------------------------------
    # PROCESSING SIGNALS
    # ------------------------------------------------------------------
    def _connect_processing_signals(self):
        self.processing_controller.dataChanged.connect(
            lambda: self.plot_controller.set_colorbar_scale_mode(
                self.plot_controller.color_scale_mode
            )
        )
        self.processing_controller.dataChanged.connect(self._refresh_roi_plot)
        self.processing_controller.stackCreated.connect(
            self.stack_manager.add_existing_stack
        )

    # ------------------------------------------------------------------
    # OTHER WINDOW METHODS
    # ------------------------------------------------------------------
    def _open_phasor_window(self):
        """Open (or bring to front) the shared phasor window."""
        from puprisa.ui.phasor_window import PhasorWindow

        if not hasattr(self, "phasor_window"):
            self.phasor_window = PhasorWindow(self.stack_manager)
        self.phasor_window.show()

    def _show_custom_range_dialog(self):
        """Open the custom colorbar range dialog."""
        if self.plot_controller.pps is None:
            QMessageBox.information(self, "Custom Range", "Please open a stack first.")
            return

        dialog = ColorbarCustomRangeDialog(self)
        init_min = self.plot_controller.custom_vmin if self.plot_controller.custom_vmin is not None else self.plot_controller.vmin
        init_max = self.plot_controller.custom_vmax if self.plot_controller.custom_vmax is not None else self.plot_controller.vmax
        dialog.set_range(init_min, init_max)

        ref = self.plot_controller.get_reference_ranges()
        dialog.set_reference_ranges(ref)

        if dialog.exec() == QDialog.Accepted:
            vmin, vmax = dialog.get_range()
            self.plot_controller.set_colorbar_range(vmin, vmax)
            self.plot_controller.set_colorbar_scale_mode(PPSPlotController.MODE_CUSTOM)

    def _save_view(self):
        """Open a standalone matplotlib figure showing the current slice and ROI curves.

        Left panel: current image slice with mask, ROI outlines, and colorbar.
        Right panel: current ROI average curves with a marker for the current slice.
        """
        if self.plot_controller.pps is None:
            QMessageBox.information(self, "Save View", "Please open a stack first.")
            return

        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle, Circle, Ellipse, Polygon
        from matplotlib.colors import Normalize
        from matplotlib.cm import ScalarMappable

        pps = self.plot_controller.pps
        current_slice = self.plot_controller.current_slice
        vmin = self.plot_controller.vmin
        vmax = self.plot_controller.vmax
        cmap = self.plot_controller.colormap

        fig, (ax_img, ax_curve) = plt.subplots(
            1, 2,
            figsize=(13, 5.5),
            gridspec_kw={'width_ratios': [1, 1.4]},
            layout='constrained'
        )

        # ---------- Image panel ----------
        image_data = pps.images[current_slice]
        rgb, _, _ = apply_colormap(image_data, vmin=vmin, vmax=vmax, cmap=cmap)
        mask = np.asarray(pps.mask, dtype=bool)
        rgb[~mask] = [200, 200, 200]
        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)

        ax_img.imshow(rgb)
        stack_name = self.stack_manager.get_current_item()["name"] if self.stack_manager.get_current_item() else None
        ax_img.set_title(stack_name or pps.filename or "Current Slice")
        ax_img.axis('off')

        # Draw visible ROI outlines
        for roi in self.roi_controller.get_all_rois():
            item = roi.get("graphics_item")
            if item is None or not item.isVisible():
                continue
            patch = shape_to_patch(
                roi["shape"],
                roi["params"],
                fill=False,
                edgecolor=roi["color"],
                linewidth=1.5,
            )
            if patch is not None:
                ax_img.add_patch(patch)

        # Colorbar
        norm = Normalize(vmin=vmin, vmax=vmax)
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        fig.colorbar(sm, ax=ax_img, fraction=0.046, pad=0.04)

        # ---------- Curve panel ----------
        curves = self.curve_controller.compute_curves()
        normalize = self.curve_controller.normalize_curves

        for x, y, label, color in curves:
            ax_curve.plot(x, y, color=color, label=label)

        axis_values = pps.get_axis_values()
        if 0 <= current_slice < len(axis_values):
            ax_curve.axvline(
                axis_values[current_slice],
                color="gray", linestyle="--", linewidth=1.2, alpha=0.8,
            )

        ax_curve.set_xlabel("Time delay (ps)")
        ax_curve.set_ylabel(
            "Normalized signal" if normalize else "Average signal (arb. u.)"
        )
        ax_curve.grid(True, alpha=0.3)
        if curves:
            ax_curve.legend(fontsize=8, loc="best")

        fig.show()