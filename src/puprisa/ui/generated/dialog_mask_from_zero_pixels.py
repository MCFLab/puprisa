# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mask_from_zero_pixels_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_MaskFromZeroPixelsDialog(object):
    def setupUi(self, MaskFromZeroPixelsDialog):
        if not MaskFromZeroPixelsDialog.objectName():
            MaskFromZeroPixelsDialog.setObjectName(u"MaskFromZeroPixelsDialog")
        MaskFromZeroPixelsDialog.resize(360, 126)
        self.verticalLayout = QVBoxLayout(MaskFromZeroPixelsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.maskCheckBox = QCheckBox(MaskFromZeroPixelsDialog)
        self.maskCheckBox.setObjectName(u"maskCheckBox")

        self.verticalLayout.addWidget(self.maskCheckBox)

        self.maskNoteLabel = QLabel(MaskFromZeroPixelsDialog)
        self.maskNoteLabel.setObjectName(u"maskNoteLabel")
        font = QFont()
        font.setItalic(True)
        self.maskNoteLabel.setFont(font)

        self.verticalLayout.addWidget(self.maskNoteLabel)

        self.applyAllCheckBox = QCheckBox(MaskFromZeroPixelsDialog)
        self.applyAllCheckBox.setObjectName(u"applyAllCheckBox")

        self.verticalLayout.addWidget(self.applyAllCheckBox)

        self.buttonBox = QDialogButtonBox(MaskFromZeroPixelsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(MaskFromZeroPixelsDialog)
        self.buttonBox.accepted.connect(MaskFromZeroPixelsDialog.accept)
        self.buttonBox.rejected.connect(MaskFromZeroPixelsDialog.reject)

        QMetaObject.connectSlotsByName(MaskFromZeroPixelsDialog)
    # setupUi

    def retranslateUi(self, MaskFromZeroPixelsDialog):
        MaskFromZeroPixelsDialog.setWindowTitle(QCoreApplication.translate("MaskFromZeroPixelsDialog", u"Mask from Zero Pixels", None))
        self.maskCheckBox.setText(QCoreApplication.translate("MaskFromZeroPixelsDialog", u"Calculate with current effective mask on", None))
        self.maskNoteLabel.setText(QCoreApplication.translate("MaskFromZeroPixelsDialog", u"Note: this will only remove zero-pixels inside current mask.", None))
        self.applyAllCheckBox.setText(QCoreApplication.translate("MaskFromZeroPixelsDialog", u"Apply to all stacks", None))
    # retranslateUi

