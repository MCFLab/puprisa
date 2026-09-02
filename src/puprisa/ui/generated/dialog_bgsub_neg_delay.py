# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bgsub_neg_delay_dialog.ui'
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
    QDialogButtonBox, QHBoxLayout, QLabel, QRadioButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_NegDelayBgSubDialog(object):
    def setupUi(self, NegDelayBgSubDialog):
        if not NegDelayBgSubDialog.objectName():
            NegDelayBgSubDialog.setObjectName(u"NegDelayBgSubDialog")
        NegDelayBgSubDialog.resize(349, 120)
        self.verticalLayout = QVBoxLayout(NegDelayBgSubDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(NegDelayBgSubDialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.radioButton = QRadioButton(NegDelayBgSubDialog)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setChecked(True)

        self.horizontalLayout.addWidget(self.radioButton)

        self.radioButton_2 = QRadioButton(NegDelayBgSubDialog)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.horizontalLayout.addWidget(self.radioButton_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.checkBox = QCheckBox(NegDelayBgSubDialog)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout.addWidget(self.checkBox)

        self.buttonBox = QDialogButtonBox(NegDelayBgSubDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(NegDelayBgSubDialog)
        self.buttonBox.accepted.connect(NegDelayBgSubDialog.accept)
        self.buttonBox.rejected.connect(NegDelayBgSubDialog.reject)

        QMetaObject.connectSlotsByName(NegDelayBgSubDialog)
    # setupUi

    def retranslateUi(self, NegDelayBgSubDialog):
        NegDelayBgSubDialog.setWindowTitle(QCoreApplication.translate("NegDelayBgSubDialog", u"Negetive Delays", None))
        self.label.setText(QCoreApplication.translate("NegDelayBgSubDialog", u"Subtraction Method:", None))
        self.radioButton.setText(QCoreApplication.translate("NegDelayBgSubDialog", u"Pixel-wise", None))
        self.radioButton_2.setText(QCoreApplication.translate("NegDelayBgSubDialog", u"Whole image", None))
        self.checkBox.setText(QCoreApplication.translate("NegDelayBgSubDialog", u"Apply to all stacks", None))
    # retranslateUi

