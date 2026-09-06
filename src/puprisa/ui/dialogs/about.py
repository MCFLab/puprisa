# src/puprisa/ui/dialogs/about_dialog.py
from pathlib import Path
from PySide6.QtWidgets import QDialog
from PySide6.QtGui import QIcon, QPixmap

from puprisa.ui.generated.dialog_about import Ui_AboutDialog


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)

        icon_path = Path(__file__).resolve().parent.parent / "resources" / "icon.svg"
        pixmap = QPixmap(str(icon_path))
        if not pixmap.isNull():
            self.ui.label.setPixmap(pixmap)
            self.ui.label.setFixedSize(55, 55)
        else:
            self.ui.label.setText("Icon")

        self.setWindowIcon(QIcon(str(icon_path)))