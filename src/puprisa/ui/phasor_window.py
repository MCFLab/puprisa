from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QTimer
import matplotlib.pyplot as plt
import numpy as np
from puprisa.ui.generated.ui_phasor_window import Ui_MainWindow
from puprisa.controllers.phasor_plot_controller import PhasorPlotController
from puprisa.controllers.phasor_curve_controller import PhasorCurveController
from puprisa.controllers.phasor_roi_controller import PhasorRoiController
from puprisa.controllers.pps_mask_controller import PPSMaskController
from puprisa.controllers.phasor_slider_controller import PhasorFrequencyController
from puprisa.controllers.stack_controller import StackViewModel
from puprisa.model.stack_manager import StackManager

class PhasorWindow(QMainWindow):
    """Phasor analysis window."""
    def __init__(self, stack_manager: StackManager):
        super().__init__()
        self.stack_manager = stack_manager
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # --- Controllers ---
        self.stack_view_model = StackViewModel(
            self.stack_manager, self.ui.stackListWidget
        )
        # Create plot controller first (without curve controller)
        self.plot_controller = PhasorPlotController(
            self.ui.phasorGraphicsView,
            self.ui.ppsGraphicsView,
            self.ui.plotCanvas,
            None,  # curve controller will be set later
        )
        self.roi_controller = PhasorRoiController(
            self.stack_manager,
            self.plot_controller,
            self.ui.phasorRoiListWidget,
            self.ui.phasorRoiShapeComboBox,
        )
        # Create curve controller and attach to plot controller
        self.curve_controller = PhasorCurveController(
            self.stack_manager,
            self.roi_controller,
        )
        self.plot_controller.curve_controller = self.curve_controller
        self.mask_controller = PPSMaskController(self.ui.maskListWidget)
        self.frequency_controller = PhasorFrequencyController(
            self.ui.freqSlider, self.ui.freqSpinBox
        )
        # --- Connect menu and buttons ---
        self._connect_FileMenu_actions()
        self._connect_CurveMenu_actions()
        self._connect_buttons()
        self._connect_signals()

    # ------------------------------------------------------------------
    # Menu connections
    # ------------------------------------------------------------------
    def _connect_FileMenu_actions(self):
        self.ui.actionOpenStack.triggered.connect(
            self.stack_view_model.add_stack_from_file
        )
        self.ui.actionSavePhasorView.triggered.connect(self._save_phasor_view)
        self.ui.actionSaveView.triggered.connect(self._save_view)
    def _connect_CurveMenu_actions(self):
        self.ui.actionNormalizeCurve.toggled.connect(self._on_normalize_toggled)
        self.ui.actionViewCurve.triggered.connect(
            self.curve_controller.view_standalone
        )
        self.ui.actionExportCurve.triggered.connect(
            self.curve_controller.export_to_csv
        )

    # ------------------------------------------------------------------
    # BUTTON CONNECTIONS
    # ------------------------------------------------------------------
    def _connect_buttons(self):
        # Stack buttons
        self.ui.stackAddButton.clicked.connect(
            self.stack_view_model.add_stack_from_file
        )
        self.ui.stackDeleteButton.clicked.connect(
            self.stack_view_model.delete_selected_stack
        )
        self.ui.stackRenameButton.clicked.connect(
            self.stack_view_model.rename_selected_stack
        )

        # ROI buttons
        self.ui.phasorRoiAddButton.clicked.connect(self.roi_controller.add_roi)
        self.ui.phasorRoiDeleteButton.clicked.connect(self.roi_controller.delete_selected_roi)
        self.ui.phasorRoiRenameButton.clicked.connect(self.roi_controller.rename_selected_roi)
        if hasattr(self.ui, "phasorRoiConvertToMaskButton"):
            self.ui.phasorRoiConvertToMaskButton.clicked.connect(
                self.roi_controller.convert_selected_roi_to_mask
            )

        # Mask buttons
        self.ui.maskReverseButton.clicked.connect(self.mask_controller.reverse_selected_mask)
        self.ui.maskRenameButton.clicked.connect(self.mask_controller.rename_selected_mask)
        self.ui.maskDeleteButton.clicked.connect(self.mask_controller.delete_selected_mask)

    # ------------------------------------------------------------------
    # SIGNAL CONNECTIONS
    # ------------------------------------------------------------------
    def _connect_signals(self):
        # Frequency
        self.frequency_controller.frequencyChanged.connect(self._on_freq_changed)
        self.ui.phasorGraphicsView.wheelSliceChanged.connect(
            self.frequency_controller.change_frequency_by_delta
        )

        # Stack model
        self.stack_manager.stackChanged.connect(self._on_current_stack_changed)
        self.stack_manager.stackVisibilityChanged.connect(
            self.roi_controller.update_visibility_by_stack
        )
        self.stack_manager.stackDeleted.connect(
            self.roi_controller.remove_rois_for_stack
        )
        self.stack_manager.stackItemsChanged.connect(self._on_stacks_changed)

        # ROI and mask changes
        self.roi_controller.roiChanged.connect(self._on_rois_changed)
        self.roi_controller.roiConvertToMaskRequested.connect(
            self._on_roi_convert_to_mask
        )
        self.mask_controller.maskChanged.connect(self._on_rois_changed)

    # ------------------------------------------------------------------
    # SLOT IMPLEMENTATIONS
    # ------------------------------------------------------------------
    def _update_phasor_coords(self, freq):
        """Attach phasor coordinates to each stack item as a runtime cache."""
        for item in self.stack_manager.get_all_items():
            item["phasor_coords"] = item["pps"].phasor(freq=freq, remove_zero=False)

    def _on_freq_changed(self, freq):
        self._update_phasor_coords(freq)
        self.plot_controller.render_density(self.stack_manager.get_all_items())
        self._refresh_plots()

    def _on_stacks_changed(self):
        self._update_phasor_coords(self.frequency_controller.frequency())
        self.plot_controller.render_density(self.stack_manager.get_all_items())
        self.plot_controller.fit_phasor_view()
        self._refresh_plots()

    def _on_current_stack_changed(self, stack_item):
        self.roi_controller.set_current_stack(stack_item)
        pps = stack_item["pps"] if stack_item else None
        self.mask_controller.set_pps(pps)
        self._refresh_plots()

    def _on_rois_changed(self):
        self._refresh_plots()

    def _on_roi_convert_to_mask(self, roi_id, stack_id, exclude_mask):
        """Handle a request to convert a phasor ROI into an exclude mask."""
        stack_item = self.stack_manager.get_item_by_id(stack_id)
        if stack_item is None:
            return

        pps = stack_item["pps"]
        roi = self.roi_controller._find_roi(roi_id)
        label = f"From ROI {roi['label']}" if roi else "From ROI"
        pps.add_mask(exclude_mask, label=label, enabled=True)
        self.mask_controller._refresh_after_change()

    def _refresh_plots(self):
        """Update signal curves and spatial view."""
        all_items = self.stack_manager.get_all_items()
        current_item = self.stack_manager.get_current_item()
        visible_rois = self.roi_controller.get_visible_rois()
        all_rois = self.roi_controller.get_all_rois()

        self.plot_controller.update_signal_plot()
        self.plot_controller.update_spatial_view(current_item, all_rois)

    # ------------------------------------------------------------------
    # SHOW / RESIZE
    # ------------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.plot_controller.fit_phasor_view)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.plot_controller.fit_phasor_view)

    def _on_normalize_toggled(self, checked: bool):
        """Toggle curve normalization and refresh the embedded plot."""
        self.curve_controller.normalize_curves = checked
        self.plot_controller.update_signal_plot()

    def _save_phasor_view(self):
        """Open a standalone matplotlib figure showing the phasor plot."""
        # Render phasor scene to QImage, convert to numpy array and display
        image = self.plot_controller.get_phasor_scene_image()
        if image.isNull():
            QMessageBox.information(self, "Save Phasor View", "No phasor scene to save.")
            return

        # Convert QImage to numpy array for imshow
        from PySide6.QtCore import QBuffer
        import numpy as np

        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        image.save(buffer, "PNG")
        data = buffer.data().data()
        buffer.close()

        # Use matplotlib to read the PNG bytes
        import matplotlib.image as mpimg
        import io
        bio = io.BytesIO(data)
        img_array = mpimg.imread(bio)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(img_array)
        ax.axis('off')
        ax.set_title("Phasor Plot")
        fig.tight_layout()
        fig.show()

    def _save_view(self):
        """Open a standalone figure showing the full Phasor window layout."""
        # Get rendered images
        phasor_img = self.plot_controller.get_phasor_scene_image()
        spatial_img = self.plot_controller.get_spatial_scene_image()

        if phasor_img.isNull() or spatial_img.isNull():
            QMessageBox.information(self, "Save View", "No view to save.")
            return

        # Convert QImages to numpy arrays
        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        import io
        import matplotlib.image as mpimg
        from PySide6.QtCore import QBuffer

        def qimage_to_numpy(img):
            buffer = QBuffer()
            buffer.open(QBuffer.OpenModeFlag.ReadWrite)
            img.save(buffer, "PNG")
            data = buffer.data().data()
            buffer.close()
            bio = io.BytesIO(data)
            return mpimg.imread(bio)

        phasor_array = qimage_to_numpy(phasor_img)
        spatial_array = qimage_to_numpy(spatial_img)

        # Curves
        curves = self.curve_controller.compute_curves()
        normalize = self.curve_controller.normalize_curves

        fig = plt.figure(figsize=(16, 8), layout='constrained')
        gs = GridSpec(2, 2, figure=fig, width_ratios=[1, 1], height_ratios=[1, 1])

        # Phasor plot (top-left)
        ax_phasor = fig.add_subplot(gs[0, 0])
        ax_phasor.imshow(phasor_array)
        ax_phasor.axis('off')
        ax_phasor.set_title("Phasor Plot")

        # Spatial projection (top-right)
        ax_spatial = fig.add_subplot(gs[0, 1])
        ax_spatial.imshow(spatial_array)
        ax_spatial.axis('off')
        ax_spatial.set_title("Spatial Projection")

        # Curve plot (bottom spanning both columns)
        ax_curve = fig.add_subplot(gs[1, :])
        for x, y, label, color in curves:
            ax_curve.plot(x, y, color=color, label=label)
        ax_curve.set_xlabel("Time delay (ps)")
        ax_curve.set_ylabel(
            "Normalized signal" if normalize else "Average signal (arb. u.)"
        )
        ax_curve.grid(True, alpha=0.3)
        if curves:
            ax_curve.legend(fontsize=8, loc="best")

        fig.show()