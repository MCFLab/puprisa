# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mask_math_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 400)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.mask1Label = QLabel(Dialog)
        self.mask1Label.setObjectName(u"mask1Label")

        self.verticalLayout.addWidget(self.mask1Label)

        self.mask1ListWidget = QListWidget(Dialog)
        self.mask1ListWidget.setObjectName(u"mask1ListWidget")

        self.verticalLayout.addWidget(self.mask1ListWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.opLabel = QLabel(Dialog)
        self.opLabel.setObjectName(u"opLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.opLabel.sizePolicy().hasHeightForWidth())
        self.opLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.opLabel)

        self.infoLabel = QLabel(Dialog)
        self.infoLabel.setObjectName(u"infoLabel")

        self.horizontalLayout.addWidget(self.infoLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.opComboBox = QComboBox(Dialog)
        self.opComboBox.addItem("")
        self.opComboBox.addItem("")
        self.opComboBox.addItem("")
        self.opComboBox.addItem("")
        self.opComboBox.setObjectName(u"opComboBox")

        self.horizontalLayout.addWidget(self.opComboBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.mask2Label = QLabel(Dialog)
        self.mask2Label.setObjectName(u"mask2Label")

        self.verticalLayout.addWidget(self.mask2Label)

        self.mask2ListWidget = QListWidget(Dialog)
        self.mask2ListWidget.setObjectName(u"mask2ListWidget")

        self.verticalLayout.addWidget(self.mask2ListWidget)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Mask Math", None))
        self.mask1Label.setText(QCoreApplication.translate("Dialog", u"Mask 1", None))
        self.opLabel.setText(QCoreApplication.translate("Dialog", u"Operation", None))
#if QT_CONFIG(tooltip)
        self.infoLabel.setToolTip(QCoreApplication.translate("Dialog", u"The masked area is where bool = True.", None))
#endif // QT_CONFIG(tooltip)
        self.infoLabel.setText(QCoreApplication.translate("Dialog", u"Info", None))
        self.opComboBox.setItemText(0, QCoreApplication.translate("Dialog", u"AND", None))
        self.opComboBox.setItemText(1, QCoreApplication.translate("Dialog", u"OR", None))
        self.opComboBox.setItemText(2, QCoreApplication.translate("Dialog", u"NOT", None))
        self.opComboBox.setItemText(3, QCoreApplication.translate("Dialog", u"XOR", None))

        self.mask2Label.setText(QCoreApplication.translate("Dialog", u"Mask 2", None))
    # retranslateUi

