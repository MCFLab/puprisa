# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bgsub_first_last_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QButtonGroup, QCheckBox,
    QComboBox, QDialog, QDialogButtonBox, QHBoxLayout,
    QLabel, QRadioButton, QSizePolicy, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_FirstLastBgSubDialog(object):
    def setupUi(self, FirstLastBgSubDialog):
        if not FirstLastBgSubDialog.objectName():
            FirstLastBgSubDialog.setObjectName(u"FirstLastBgSubDialog")
        FirstLastBgSubDialog.resize(320, 220)
        self.verticalLayout_2 = QVBoxLayout(FirstLastBgSubDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(FirstLastBgSubDialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.imgNumberSpinBox = QSpinBox(FirstLastBgSubDialog)
        self.imgNumberSpinBox.setObjectName(u"imgNumberSpinBox")
        self.imgNumberSpinBox.setMinimum(1)
        self.imgNumberSpinBox.setMaximum(65536)

        self.horizontalLayout_3.addWidget(self.imgNumberSpinBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(FirstLastBgSubDialog)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.subTypeComboBox = QComboBox(FirstLastBgSubDialog)
        self.subTypeComboBox.addItem("")
        self.subTypeComboBox.addItem("")
        self.subTypeComboBox.setObjectName(u"subTypeComboBox")

        self.horizontalLayout_2.addWidget(self.subTypeComboBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_3 = QLabel(FirstLastBgSubDialog)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pixelwiseRadioButton = QRadioButton(FirstLastBgSubDialog)
        self.buttonGroup = QButtonGroup(FirstLastBgSubDialog)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.pixelwiseRadioButton)
        self.pixelwiseRadioButton.setObjectName(u"pixelwiseRadioButton")

        self.verticalLayout.addWidget(self.pixelwiseRadioButton)

        self.wholeimgRadioButton = QRadioButton(FirstLastBgSubDialog)
        self.buttonGroup.addButton(self.wholeimgRadioButton)
        self.wholeimgRadioButton.setObjectName(u"wholeimgRadioButton")

        self.verticalLayout.addWidget(self.wholeimgRadioButton)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.applyAllCheckBox = QCheckBox(FirstLastBgSubDialog)
        self.applyAllCheckBox.setObjectName(u"applyAllCheckBox")

        self.verticalLayout_2.addWidget(self.applyAllCheckBox)

        self.buttonBox = QDialogButtonBox(FirstLastBgSubDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(FirstLastBgSubDialog)
        self.buttonBox.accepted.connect(FirstLastBgSubDialog.accept)
        self.buttonBox.rejected.connect(FirstLastBgSubDialog.reject)

        QMetaObject.connectSlotsByName(FirstLastBgSubDialog)
    # setupUi

    def retranslateUi(self, FirstLastBgSubDialog):
        FirstLastBgSubDialog.setWindowTitle(QCoreApplication.translate("FirstLastBgSubDialog", u"First/Last N Images", None))
        self.label.setText(QCoreApplication.translate("FirstLastBgSubDialog", u"# of Images (N):", None))
        self.label_2.setText(QCoreApplication.translate("FirstLastBgSubDialog", u"Subtraction Images:", None))
        self.subTypeComboBox.setItemText(0, QCoreApplication.translate("FirstLastBgSubDialog", u"First", None))
        self.subTypeComboBox.setItemText(1, QCoreApplication.translate("FirstLastBgSubDialog", u"Last", None))

        self.label_3.setText(QCoreApplication.translate("FirstLastBgSubDialog", u"Subtraction Method:", None))
        self.pixelwiseRadioButton.setText(QCoreApplication.translate("FirstLastBgSubDialog", u"Pixel-wise", None))
        self.wholeimgRadioButton.setText(QCoreApplication.translate("FirstLastBgSubDialog", u"Whole image", None))
        self.applyAllCheckBox.setText(QCoreApplication.translate("FirstLastBgSubDialog", u"Apply to all stacks", None))
    # retranslateUi

