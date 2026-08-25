# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'background_subtraction_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QButtonGroup, QComboBox,
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QRadioButton, QSizePolicy, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_backgroundSubtractionDialog(object):
    def setupUi(self, backgroundSubtractionDialog):
        if not backgroundSubtractionDialog.objectName():
            backgroundSubtractionDialog.setObjectName(u"backgroundSubtractionDialog")
        backgroundSubtractionDialog.resize(320, 180)
        self.verticalLayout_2 = QVBoxLayout(backgroundSubtractionDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(backgroundSubtractionDialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.imgNumberSpinBox = QSpinBox(backgroundSubtractionDialog)
        self.imgNumberSpinBox.setObjectName(u"imgNumberSpinBox")

        self.horizontalLayout_3.addWidget(self.imgNumberSpinBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(backgroundSubtractionDialog)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.subTypeComboBox = QComboBox(backgroundSubtractionDialog)
        self.subTypeComboBox.addItem("")
        self.subTypeComboBox.addItem("")
        self.subTypeComboBox.setObjectName(u"subTypeComboBox")

        self.horizontalLayout_2.addWidget(self.subTypeComboBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_3 = QLabel(backgroundSubtractionDialog)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pixelwiseRadioButton = QRadioButton(backgroundSubtractionDialog)
        self.buttonGroup = QButtonGroup(backgroundSubtractionDialog)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.pixelwiseRadioButton)
        self.pixelwiseRadioButton.setObjectName(u"pixelwiseRadioButton")

        self.verticalLayout.addWidget(self.pixelwiseRadioButton)

        self.wholeimgRadioButton = QRadioButton(backgroundSubtractionDialog)
        self.buttonGroup.addButton(self.wholeimgRadioButton)
        self.wholeimgRadioButton.setObjectName(u"wholeimgRadioButton")

        self.verticalLayout.addWidget(self.wholeimgRadioButton)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(backgroundSubtractionDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(backgroundSubtractionDialog)
        self.buttonBox.accepted.connect(backgroundSubtractionDialog.accept)
        self.buttonBox.rejected.connect(backgroundSubtractionDialog.reject)

        QMetaObject.connectSlotsByName(backgroundSubtractionDialog)
    # setupUi

    def retranslateUi(self, backgroundSubtractionDialog):
        backgroundSubtractionDialog.setWindowTitle(QCoreApplication.translate("backgroundSubtractionDialog", u"First/Last N Images", None))
        self.label.setText(QCoreApplication.translate("backgroundSubtractionDialog", u"# of Images (N):", None))
        self.label_2.setText(QCoreApplication.translate("backgroundSubtractionDialog", u"Subtraction Images:", None))
        self.subTypeComboBox.setItemText(0, QCoreApplication.translate("backgroundSubtractionDialog", u"First", None))
        self.subTypeComboBox.setItemText(1, QCoreApplication.translate("backgroundSubtractionDialog", u"Last", None))

        self.label_3.setText(QCoreApplication.translate("backgroundSubtractionDialog", u"Subtraction Method:", None))
        self.pixelwiseRadioButton.setText(QCoreApplication.translate("backgroundSubtractionDialog", u"Pixel-wise", None))
        self.wholeimgRadioButton.setText(QCoreApplication.translate("backgroundSubtractionDialog", u"Whole image", None))
    # retranslateUi

