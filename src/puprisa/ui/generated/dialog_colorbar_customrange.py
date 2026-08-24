# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'colorbar_customrange_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_colorbarCustomRangeDialog(object):
    def setupUi(self, colorbarCustomRangeDialog):
        if not colorbarCustomRangeDialog.objectName():
            colorbarCustomRangeDialog.setObjectName(u"colorbarCustomRangeDialog")
        colorbarCustomRangeDialog.resize(300, 180)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        colorbarCustomRangeDialog.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(colorbarCustomRangeDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(colorbarCustomRangeDialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.minDoubleSpinBox = QDoubleSpinBox(colorbarCustomRangeDialog)
        self.minDoubleSpinBox.setObjectName(u"minDoubleSpinBox")

        self.horizontalLayout.addWidget(self.minDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(colorbarCustomRangeDialog)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.maxDoubleSpinBox = QDoubleSpinBox(colorbarCustomRangeDialog)
        self.maxDoubleSpinBox.setObjectName(u"maxDoubleSpinBox")

        self.horizontalLayout_2.addWidget(self.maxDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.labelStdDev = QLabel(colorbarCustomRangeDialog)
        self.labelStdDev.setObjectName(u"labelStdDev")

        self.verticalLayout.addWidget(self.labelStdDev)

        self.labelFullScale = QLabel(colorbarCustomRangeDialog)
        self.labelFullScale.setObjectName(u"labelFullScale")

        self.verticalLayout.addWidget(self.labelFullScale)

        self.buttonBox = QDialogButtonBox(colorbarCustomRangeDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(colorbarCustomRangeDialog)
        self.buttonBox.accepted.connect(colorbarCustomRangeDialog.accept)
        self.buttonBox.rejected.connect(colorbarCustomRangeDialog.reject)

        QMetaObject.connectSlotsByName(colorbarCustomRangeDialog)
    # setupUi

    def retranslateUi(self, colorbarCustomRangeDialog):
        colorbarCustomRangeDialog.setWindowTitle(QCoreApplication.translate("colorbarCustomRangeDialog", u"Colorbar Custom Range", None))
        self.label.setText(QCoreApplication.translate("colorbarCustomRangeDialog", u"Minimum:", None))
        self.label_2.setText(QCoreApplication.translate("colorbarCustomRangeDialog", u"Maximum:", None))
        self.labelStdDev.setText(QCoreApplication.translate("colorbarCustomRangeDialog", u"Std Dev Range: N/A", None))
        self.labelFullScale.setText(QCoreApplication.translate("colorbarCustomRangeDialog", u"Full Scale Range: N/A", None))
    # retranslateUi

