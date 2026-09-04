# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mask_from_intensity_threshold_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QDoubleSpinBox, QHBoxLayout,
    QLabel, QSizePolicy, QVBoxLayout, QWidget)

class Ui_MaskFromIntensityThresholdDialog(object):
    def setupUi(self, MaskFromIntensityThresholdDialog):
        if not MaskFromIntensityThresholdDialog.objectName():
            MaskFromIntensityThresholdDialog.setObjectName(u"MaskFromIntensityThresholdDialog")
        MaskFromIntensityThresholdDialog.resize(360, 220)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        MaskFromIntensityThresholdDialog.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(MaskFromIntensityThresholdDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelType = QLabel(MaskFromIntensityThresholdDialog)
        self.labelType.setObjectName(u"labelType")

        self.horizontalLayout.addWidget(self.labelType)

        self.thresholdTypeComboBox = QComboBox(MaskFromIntensityThresholdDialog)
        self.thresholdTypeComboBox.addItem("")
        self.thresholdTypeComboBox.addItem("")
        self.thresholdTypeComboBox.setObjectName(u"thresholdTypeComboBox")

        self.horizontalLayout.addWidget(self.thresholdTypeComboBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelSigma = QLabel(MaskFromIntensityThresholdDialog)
        self.labelSigma.setObjectName(u"labelSigma")

        self.horizontalLayout_2.addWidget(self.labelSigma)

        self.sigmaDoubleSpinBox = QDoubleSpinBox(MaskFromIntensityThresholdDialog)
        self.sigmaDoubleSpinBox.setObjectName(u"sigmaDoubleSpinBox")

        self.horizontalLayout_2.addWidget(self.sigmaDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelManual = QLabel(MaskFromIntensityThresholdDialog)
        self.labelManual.setObjectName(u"labelManual")
        self.labelManual.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.labelManual)

        self.manualValueDoubleSpinBox = QDoubleSpinBox(MaskFromIntensityThresholdDialog)
        self.manualValueDoubleSpinBox.setObjectName(u"manualValueDoubleSpinBox")
        self.manualValueDoubleSpinBox.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.manualValueDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.maskCheckBox = QCheckBox(MaskFromIntensityThresholdDialog)
        self.maskCheckBox.setObjectName(u"maskCheckBox")

        self.verticalLayout.addWidget(self.maskCheckBox)

        self.applyAllCheckBox = QCheckBox(MaskFromIntensityThresholdDialog)
        self.applyAllCheckBox.setObjectName(u"applyAllCheckBox")

        self.verticalLayout.addWidget(self.applyAllCheckBox)

        self.buttonBox = QDialogButtonBox(MaskFromIntensityThresholdDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(MaskFromIntensityThresholdDialog)
        self.buttonBox.accepted.connect(MaskFromIntensityThresholdDialog.accept)
        self.buttonBox.rejected.connect(MaskFromIntensityThresholdDialog.reject)

        QMetaObject.connectSlotsByName(MaskFromIntensityThresholdDialog)
    # setupUi

    def retranslateUi(self, MaskFromIntensityThresholdDialog):
        MaskFromIntensityThresholdDialog.setWindowTitle(QCoreApplication.translate("MaskFromIntensityThresholdDialog", u"Mask from Intensity Threshold", None))
        self.labelType.setText(QCoreApplication.translate("MaskFromIntensityThresholdDialog", u"Threshold Type:", None))
        self.thresholdTypeComboBox.setItemText(0, QCoreApplication.translate("MaskFromIntensityThresholdDialog", u"Li", None))
        self.thresholdTypeComboBox.setItemText(1, QCoreApplication.translate("MaskFromIntensityThresholdDialog", u"Manual", None))

        self.labelSigma.setText(QCoreApplication.translate("MaskFromIntensityThresholdDialog", u"Sigma (Gaussian smoothing):", None))
        self.labelManual.setText(QCoreApplication.translate("MaskFromIntensityThresholdDialog", u"Manual Threshold Value:", None))
        self.maskCheckBox.setText(QCoreApplication.translate("MaskFromIntensityThresholdDialog", u"Calculate with current effective mask on", None))
        self.applyAllCheckBox.setText(QCoreApplication.translate("MaskFromIntensityThresholdDialog", u"Apply to all stacks", None))
    # retranslateUi

