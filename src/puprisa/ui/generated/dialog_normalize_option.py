# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'normalize_option_dialog.ui'
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
    QHBoxLayout, QLabel, QRadioButton, QSizePolicy,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_NormalizeOptionDialog(object):
    def setupUi(self, NormalizeOptionDialog):
        if not NormalizeOptionDialog.objectName():
            NormalizeOptionDialog.setObjectName(u"NormalizeOptionDialog")
        NormalizeOptionDialog.resize(360, 120)
        self.verticalLayout = QVBoxLayout(NormalizeOptionDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.maxAbsRadioButton = QRadioButton(NormalizeOptionDialog)
        self.maxAbsRadioButton.setObjectName(u"maxAbsRadioButton")

        self.verticalLayout.addWidget(self.maxAbsRadioButton)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.sliceRadioButton = QRadioButton(NormalizeOptionDialog)
        self.sliceRadioButton.setObjectName(u"sliceRadioButton")

        self.horizontalLayout.addWidget(self.sliceRadioButton)

        self.sliceSpinBox = QSpinBox(NormalizeOptionDialog)
        self.sliceSpinBox.setObjectName(u"sliceSpinBox")

        self.horizontalLayout.addWidget(self.sliceSpinBox)

        self.sliceLabel = QLabel(NormalizeOptionDialog)
        self.sliceLabel.setObjectName(u"sliceLabel")

        self.horizontalLayout.addWidget(self.sliceLabel)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(NormalizeOptionDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(NormalizeOptionDialog)
        self.buttonBox.accepted.connect(NormalizeOptionDialog.accept)
        self.buttonBox.rejected.connect(NormalizeOptionDialog.reject)

        QMetaObject.connectSlotsByName(NormalizeOptionDialog)
    # setupUi

    def retranslateUi(self, NormalizeOptionDialog):
        NormalizeOptionDialog.setWindowTitle(QCoreApplication.translate("NormalizeOptionDialog", u"Normalize Option", None))
        self.maxAbsRadioButton.setText(QCoreApplication.translate("NormalizeOptionDialog", u"Normalize by max absolute value of signal", None))
        self.sliceRadioButton.setText(QCoreApplication.translate("NormalizeOptionDialog", u"Normalize at slice", None))
        self.sliceLabel.setText(QCoreApplication.translate("NormalizeOptionDialog", u"t = 0 ps", None))
    # retranslateUi

