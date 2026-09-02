# puprisa/ui/dialogs/edit_roi.py
"""Dialog for editing an existing ROI's geometry and creating copies."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QTableWidgetItem, QMessageBox

from puprisa.model.entities import RoiItem
from puprisa.ui.generated.dialog_edit_roi import Ui_EditRoiDialog


class EditRoiDialog(QDialog):
    """Edit ROI parameters, with options to copy geometry.

    Signals:
        okClicked(dict)           - OK button pressed, carries new params.
        copyClicked(dict)         - Copy button pressed, carries new params.
        copyAllClicked(dict)      - Copy for All Stacks pressed, carries new params.
    """

    okClicked = Signal(dict)
    copyClicked = Signal(dict)
    copyAllClicked = Signal(dict)

    def __init__(self, roi: RoiItem, parent=None):
        super().__init__(parent)
        self.ui = Ui_EditRoiDialog()
        self.ui.setupUi(self)

        self._roi = roi
        self._space = roi.space
        self._shape = roi.shape

        # Space display (read-only)
        if self._space == "pixel":
            self.ui.spaceComboBox.setCurrentIndex(0)
        else:  # phasor
            self.ui.spaceComboBox.setCurrentIndex(1)
        self.ui.spaceComboBox.setEnabled(False)

        geometry_boxes = [
            self.ui.rectLeftXBox,
            self.ui.rectTopYBox,
            self.ui.rectWidthBox,
            self.ui.rectHeightBox,
            self.ui.circCenterXBox,
            self.ui.circCenterYBox,
            self.ui.circRBox,
            self.ui.ellipseCenterXBox,
            self.ui.ellipseCenterYBox,
            self.ui.ellipseRadiusXBox,
            self.ui.ellipseRadiusYBox,
        ]
        for box in geometry_boxes:
            box.setRange(-1e6, 1e6)
            box.setDecimals(2)

        self._populate_geometry()
        self._update_controls_enabled()

        self.ui.okButton.clicked.connect(self._on_ok)
        self.ui.copyButton.clicked.connect(self._on_copy)
        self.ui.copyForAllButton.clicked.connect(self._on_copy_all)
        self.ui.cancelButton.clicked.connect(self.reject)

    # ------------------------------------------------------------------
    # Population helpers
    # ------------------------------------------------------------------
    def _populate_geometry(self):
        """Fill geometry controls from roi.params."""
        params = self._roi.params

        if self._shape == "rectangle":
            self.ui.rectLeftXBox.setValue(float(params.get("x", 0)))
            self.ui.rectTopYBox.setValue(float(params.get("y", 0)))
            self.ui.rectWidthBox.setValue(float(params.get("width", 0)))
            self.ui.rectHeightBox.setValue(float(params.get("height", 0)))

        elif self._shape == "circle":
            self.ui.circCenterXBox.setValue(float(params.get("center_x", 0)))
            self.ui.circCenterYBox.setValue(float(params.get("center_y", 0)))
            self.ui.circRBox.setValue(float(params.get("radius", 0)))

        elif self._shape == "ellipse":
            self.ui.ellipseCenterXBox.setValue(float(params.get("center_x", 0)))
            self.ui.ellipseCenterYBox.setValue(float(params.get("center_y", 0)))
            self.ui.ellipseRadiusXBox.setValue(float(params.get("radius_x", 0)))
            self.ui.ellipseRadiusYBox.setValue(float(params.get("radius_y", 0)))

        elif self._shape == "polygon":
            vertices = params.get("vertices", [])
            table = self.ui.polygonTableWidget

            if self._space == "phasor":
                headers = ["g", "s"]
            else:
                headers = ["x", "y"]
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(headers)
            table.verticalHeader().setVisible(False)

            table.setRowCount(len(vertices))

            for row, vertex in enumerate(vertices):
                x_item = QTableWidgetItem(str(vertex[0]))
                y_item = QTableWidgetItem(str(vertex[1]))
                table.setItem(row, 0, x_item)
                table.setItem(row, 1, y_item)
        else:
            raise KeyError(f"Unknown shape: {self._shape}")

    def _update_controls_enabled(self):
        """Disable geometry controls unrelated to the current shape."""
        rect_widgets = [
            self.ui.rectLabel,
            self.ui.rectLeftXLabel, self.ui.rectLeftXBox,
            self.ui.rectTopYLabel, self.ui.rectTopYBox,
            self.ui.rectWidthLabel, self.ui.rectWidthBox,
            self.ui.rectHeightLabel, self.ui.rectHeightBox,
        ]
        circ_widgets = [
            self.ui.circLabel,
            self.ui.circCenterXLabel, self.ui.circCenterXBox,
            self.ui.circCenterYLabel, self.ui.circCenterYBox,
            self.ui.circRLabel, self.ui.circRBox,
        ]
        ellipse_widgets = [
            self.ui.ellipseLabel,
            self.ui.ellipseCenterXLabel, self.ui.ellipseCenterXBox,
            self.ui.ellipseCenterYLabel, self.ui.ellipseCenterYBox,
            self.ui.ellipseRadiusXLabel, self.ui.ellipseRadiusXBox,
            self.ui.ellipseRadiusYLabel, self.ui.ellipseRadiusYBox,
        ]
        polygon_widgets = [
            self.ui.polygonLabel,
            self.ui.polygonTableWidget,
        ]

        all_widgets = rect_widgets + circ_widgets + ellipse_widgets + polygon_widgets

        for w in all_widgets:
            w.setEnabled(False)

        if self._shape == "rectangle":
            for w in rect_widgets:
                w.setEnabled(True)
        elif self._shape == "circle":
            for w in circ_widgets:
                w.setEnabled(True)
        elif self._shape == "ellipse":
            for w in ellipse_widgets:
                w.setEnabled(True)
        elif self._shape == "polygon":
            for w in polygon_widgets:
                w.setEnabled(True)

    # ------------------------------------------------------------------
    # Parameter extraction from UI
    # ------------------------------------------------------------------
    def get_parameters(self) -> dict:
        """Read geometry parameters from the UI and return a params dict."""
        if self._shape == "rectangle":
            return {
                "x": self.ui.rectLeftXBox.value(),
                "y": self.ui.rectTopYBox.value(),
                "width": self.ui.rectWidthBox.value(),
                "height": self.ui.rectHeightBox.value(),
            }

        elif self._shape == "circle":
            return {
                "center_x": self.ui.circCenterXBox.value(),
                "center_y": self.ui.circCenterYBox.value(),
                "radius": self.ui.circRBox.value(),
            }

        elif self._shape == "ellipse":
            return {
                "center_x": self.ui.ellipseCenterXBox.value(),
                "center_y": self.ui.ellipseCenterYBox.value(),
                "radius_x": self.ui.ellipseRadiusXBox.value(),
                "radius_y": self.ui.ellipseRadiusYBox.value(),
            }

        elif self._shape == "polygon":
            vertices = []
            table = self.ui.polygonTableWidget
            for row in range(table.rowCount()):
                x_item = table.item(row, 0)
                y_item = table.item(row, 1)
                if x_item is None or y_item is None:
                    QMessageBox.warning(self, "Edit ROI", f"Missing vertex data at row {row + 1}.")
                    return {}
                try:
                    x = float(x_item.text())
                    y = float(y_item.text())
                except ValueError:
                    QMessageBox.warning(self, "Edit ROI", f"Invalid vertex value at row {row + 1}.")
                    return {}
                vertices.append([x, y])
            if len(vertices) < 3:
                QMessageBox.warning(self, "Edit ROI", "Polygon requires at least 3 vertices.")
                return {}

            return {"vertices": vertices}

        return {}

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------
    def _on_ok(self):
        params = self.get_parameters()
        if params:
            self.okClicked.emit(params)
            self.accept()

    def _on_copy(self):
        params = self.get_parameters()
        if params:
            self.copyClicked.emit(params)
            self.accept()

    def _on_copy_all(self):
        params = self.get_parameters()
        if params:
            self.copyAllClicked.emit(params)
            self.accept()