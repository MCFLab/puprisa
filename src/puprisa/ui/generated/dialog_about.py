# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(320, 160)
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label = QLabel(AboutDialog)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 0))
        self.label.setScaledContents(True)

        self.horizontalLayout.addWidget(self.label)

        self.label_2 = QLabel(AboutDialog)
        self.label_2.setObjectName(u"label_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(32)
        self.label_2.setFont(font)

        self.horizontalLayout.addWidget(self.label_2)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.label_3 = QLabel(AboutDialog)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.label_4 = QLabel(AboutDialog)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.label_5 = QLabel(AboutDialog)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout.addWidget(self.label_5)


        self.retranslateUi(AboutDialog)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About Puprisa", None))
        self.label.setText(QCoreApplication.translate("AboutDialog", u"Icon", None))
        self.label_2.setText(QCoreApplication.translate("AboutDialog", u"PUPRISA", None))
        self.label_3.setText(QCoreApplication.translate("AboutDialog", u"Pump Probe Image Stack Analysis (PUPRISA)", None))
        self.label_4.setText(QCoreApplication.translate("AboutDialog", u"Version 1.0.2 (Build 2026.09)", None))
        self.label_5.setText(QCoreApplication.translate("AboutDialog", u"Copyright \u00a9 Warren Lab, Duke University", None))
    # retranslateUi

