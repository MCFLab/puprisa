# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bgsub_fixed_value_dialog.ui'
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
    QDialogButtonBox, QDoubleSpinBox, QHBoxLayout, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_FixedValueBgSubDialog(object):
    def setupUi(self, FixedValueBgSubDialog):
        if not FixedValueBgSubDialog.objectName():
            FixedValueBgSubDialog.setObjectName(u"FixedValueBgSubDialog")
        FixedValueBgSubDialog.resize(240, 120)
        self.verticalLayout = QVBoxLayout(FixedValueBgSubDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(FixedValueBgSubDialog)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.label)

        self.doubleSpinBox = QDoubleSpinBox(FixedValueBgSubDialog)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")

        self.horizontalLayout.addWidget(self.doubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.checkBox = QCheckBox(FixedValueBgSubDialog)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout.addWidget(self.checkBox)

        self.buttonBox = QDialogButtonBox(FixedValueBgSubDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(FixedValueBgSubDialog)
        self.buttonBox.accepted.connect(FixedValueBgSubDialog.accept)
        self.buttonBox.rejected.connect(FixedValueBgSubDialog.reject)

        QMetaObject.connectSlotsByName(FixedValueBgSubDialog)
    # setupUi

    def retranslateUi(self, FixedValueBgSubDialog):
        FixedValueBgSubDialog.setWindowTitle(QCoreApplication.translate("FixedValueBgSubDialog", u"Fixed Value", None))
        self.label.setText(QCoreApplication.translate("FixedValueBgSubDialog", u"Fixed Value:", None))
        self.checkBox.setText(QCoreApplication.translate("FixedValueBgSubDialog", u"Apply to all stacks", None))
    # retranslateUi

