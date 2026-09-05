# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'phasor_alpha_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_PhasorAlphaDialog(object):
    def setupUi(self, PhasorAlphaDialog):
        if not PhasorAlphaDialog.objectName():
            PhasorAlphaDialog.setObjectName(u"PhasorAlphaDialog")
        PhasorAlphaDialog.resize(240, 120)
        self.verticalLayout = QVBoxLayout(PhasorAlphaDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.alphaMinLabel = QLabel(PhasorAlphaDialog)
        self.alphaMinLabel.setObjectName(u"alphaMinLabel")

        self.horizontalLayout.addWidget(self.alphaMinLabel)

        self.alphaMinDoubleSpinBox = QDoubleSpinBox(PhasorAlphaDialog)
        self.alphaMinDoubleSpinBox.setObjectName(u"alphaMinDoubleSpinBox")
        self.alphaMinDoubleSpinBox.setDecimals(1)
        self.alphaMinDoubleSpinBox.setMaximum(255.000000000000000)

        self.horizontalLayout.addWidget(self.alphaMinDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.alphaMaxLabel = QLabel(PhasorAlphaDialog)
        self.alphaMaxLabel.setObjectName(u"alphaMaxLabel")

        self.horizontalLayout_2.addWidget(self.alphaMaxLabel)

        self.alphaMaxDoubleSpinBox = QDoubleSpinBox(PhasorAlphaDialog)
        self.alphaMaxDoubleSpinBox.setObjectName(u"alphaMaxDoubleSpinBox")
        self.alphaMaxDoubleSpinBox.setDecimals(1)
        self.alphaMaxDoubleSpinBox.setMaximum(255.000000000000000)
        self.alphaMaxDoubleSpinBox.setValue(255.000000000000000)

        self.horizontalLayout_2.addWidget(self.alphaMaxDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.buttonBox = QDialogButtonBox(PhasorAlphaDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(PhasorAlphaDialog)
        self.buttonBox.accepted.connect(PhasorAlphaDialog.accept)
        self.buttonBox.rejected.connect(PhasorAlphaDialog.reject)

        QMetaObject.connectSlotsByName(PhasorAlphaDialog)
    # setupUi

    def retranslateUi(self, PhasorAlphaDialog):
        PhasorAlphaDialog.setWindowTitle(QCoreApplication.translate("PhasorAlphaDialog", u"Phasor Alpha Range", None))
        self.alphaMinLabel.setText(QCoreApplication.translate("PhasorAlphaDialog", u"Alpha Minimum:", None))
        self.alphaMaxLabel.setText(QCoreApplication.translate("PhasorAlphaDialog", u"Alpha Maximum:", None))
    # retranslateUi

