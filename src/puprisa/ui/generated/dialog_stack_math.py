# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'stack_math.ui'
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
    QDialogButtonBox, QDoubleSpinBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 400)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.stack1Label = QLabel(Dialog)
        self.stack1Label.setObjectName(u"stack1Label")

        self.verticalLayout.addWidget(self.stack1Label)

        self.stack1ListWidget = QListWidget(Dialog)
        self.stack1ListWidget.setObjectName(u"stack1ListWidget")

        self.verticalLayout.addWidget(self.stack1ListWidget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.stack1CoeffLabel = QLabel(Dialog)
        self.stack1CoeffLabel.setObjectName(u"stack1CoeffLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stack1CoeffLabel.sizePolicy().hasHeightForWidth())
        self.stack1CoeffLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.stack1CoeffLabel)

        self.stack1CoeffDoubleSpinBox = QDoubleSpinBox(Dialog)
        self.stack1CoeffDoubleSpinBox.setObjectName(u"stack1CoeffDoubleSpinBox")
        self.stack1CoeffDoubleSpinBox.setMinimum(-100000.000000000000000)
        self.stack1CoeffDoubleSpinBox.setMaximum(100000.000000000000000)
        self.stack1CoeffDoubleSpinBox.setSingleStep(0.100000000000000)
        self.stack1CoeffDoubleSpinBox.setValue(1.000000000000000)

        self.horizontalLayout_2.addWidget(self.stack1CoeffDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.stack2Label = QLabel(Dialog)
        self.stack2Label.setObjectName(u"stack2Label")

        self.verticalLayout.addWidget(self.stack2Label)

        self.stack2ListWidget = QListWidget(Dialog)
        self.stack2ListWidget.setObjectName(u"stack2ListWidget")

        self.verticalLayout.addWidget(self.stack2ListWidget)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.stack2CoeffLabel = QLabel(Dialog)
        self.stack2CoeffLabel.setObjectName(u"stack2CoeffLabel")
        sizePolicy.setHeightForWidth(self.stack2CoeffLabel.sizePolicy().hasHeightForWidth())
        self.stack2CoeffLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.stack2CoeffLabel)

        self.stack2CoeffDoubleSpinBox = QDoubleSpinBox(Dialog)
        self.stack2CoeffDoubleSpinBox.setObjectName(u"stack2CoeffDoubleSpinBox")
        self.stack2CoeffDoubleSpinBox.setMinimum(-100000.000000000000000)
        self.stack2CoeffDoubleSpinBox.setMaximum(100000.000000000000000)
        self.stack2CoeffDoubleSpinBox.setSingleStep(0.100000000000000)
        self.stack2CoeffDoubleSpinBox.setValue(1.000000000000000)

        self.horizontalLayout_3.addWidget(self.stack2CoeffDoubleSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.opLabel = QLabel(Dialog)
        self.opLabel.setObjectName(u"opLabel")
        sizePolicy.setHeightForWidth(self.opLabel.sizePolicy().hasHeightForWidth())
        self.opLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.opLabel)

        self.opComboBox = QComboBox(Dialog)
        self.opComboBox.addItem("")
        self.opComboBox.addItem("")
        self.opComboBox.addItem("")
        self.opComboBox.addItem("")
        self.opComboBox.setObjectName(u"opComboBox")

        self.horizontalLayout.addWidget(self.opComboBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

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
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Stack Math", None))
        self.stack1Label.setText(QCoreApplication.translate("Dialog", u"Stack 1", None))
        self.stack1CoeffLabel.setText(QCoreApplication.translate("Dialog", u"Stack 1 Coefficient:", None))
        self.stack2Label.setText(QCoreApplication.translate("Dialog", u"Stack 2", None))
        self.stack2CoeffLabel.setText(QCoreApplication.translate("Dialog", u"Stack 2 Coefficient:", None))
        self.opLabel.setText(QCoreApplication.translate("Dialog", u"Operation:", None))
        self.opComboBox.setItemText(0, QCoreApplication.translate("Dialog", u"Add", None))
        self.opComboBox.setItemText(1, QCoreApplication.translate("Dialog", u"Subtract", None))
        self.opComboBox.setItemText(2, QCoreApplication.translate("Dialog", u"Multiply", None))
        self.opComboBox.setItemText(3, QCoreApplication.translate("Dialog", u"Divide", None))

    # retranslateUi

