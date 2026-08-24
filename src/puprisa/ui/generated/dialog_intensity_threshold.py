# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'intensity_threshold_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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

class Ui_intensityThresholdDialog(object):
    def setupUi(self, intensityThresholdDialog):
        if not intensityThresholdDialog.objectName():
            intensityThresholdDialog.setObjectName(u"intensityThresholdDialog")
        intensityThresholdDialog.resize(360, 180)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        intensityThresholdDialog.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(intensityThresholdDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelType = QLabel(intensityThresholdDialog)
        self.labelType.setObjectName(u"labelType")

        self.horizontalLayout.addWidget(self.labelType)

        self.thresholdTypeComboBox = QComboBox(intensityThresholdDialog)
        self.thresholdTypeComboBox.addItem("")
        self.thresholdTypeComboBox.addItem("")
        self.thresholdTypeComboBox.setObjectName(u"thresholdTypeComboBox")

        self.horizontalLayout.addWidget(self.thresholdTypeComboBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelSigma = QLabel(intensityThresholdDialog)
        self.labelSigma.setObjectName(u"labelSigma")

        self.horizontalLayout_2.addWidget(self.labelSigma)

        self.sigmaDoubleSpinBox = QDoubleSpinBox(intensityThresholdDialog)
        self.sigmaDoubleSpinBox.setObjectName(u"sigmaDoubleSpinBox")

        self.horizontalLayout_2.addWidget(self.sigmaDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelManual = QLabel(intensityThresholdDialog)
        self.labelManual.setObjectName(u"labelManual")
        self.labelManual.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.labelManual)

        self.manualValueDoubleSpinBox = QDoubleSpinBox(intensityThresholdDialog)
        self.manualValueDoubleSpinBox.setObjectName(u"manualValueDoubleSpinBox")
        self.manualValueDoubleSpinBox.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.manualValueDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.maskCheckBox = QCheckBox(intensityThresholdDialog)
        self.maskCheckBox.setObjectName(u"maskCheckBox")

        self.verticalLayout.addWidget(self.maskCheckBox)

        self.buttonBox = QDialogButtonBox(intensityThresholdDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(intensityThresholdDialog)
        self.buttonBox.accepted.connect(intensityThresholdDialog.accept)
        self.buttonBox.rejected.connect(intensityThresholdDialog.reject)

        QMetaObject.connectSlotsByName(intensityThresholdDialog)
    # setupUi

    def retranslateUi(self, intensityThresholdDialog):
        intensityThresholdDialog.setWindowTitle(QCoreApplication.translate("intensityThresholdDialog", u"Intensity Threshold", None))
        self.labelType.setText(QCoreApplication.translate("intensityThresholdDialog", u"Threshold Type:", None))
        self.thresholdTypeComboBox.setItemText(0, QCoreApplication.translate("intensityThresholdDialog", u"Li", None))
        self.thresholdTypeComboBox.setItemText(1, QCoreApplication.translate("intensityThresholdDialog", u"Manual", None))

        self.labelSigma.setText(QCoreApplication.translate("intensityThresholdDialog", u"Sigma (Gaussian smoothing):", None))
        self.labelManual.setText(QCoreApplication.translate("intensityThresholdDialog", u"Manual Threshold Value:", None))
        self.maskCheckBox.setText(QCoreApplication.translate("intensityThresholdDialog", u"Calculate with current effective mask on", None))
    # retranslateUi

