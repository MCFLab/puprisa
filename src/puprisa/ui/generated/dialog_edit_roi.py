# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_roi_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QDoubleSpinBox,
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_EditRoiDialog(object):
    def setupUi(self, EditRoiDialog):
        if not EditRoiDialog.objectName():
            EditRoiDialog.setObjectName(u"EditRoiDialog")
        EditRoiDialog.resize(518, 420)
        self.verticalLayout_16 = QVBoxLayout(EditRoiDialog)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.spaceLabel = QLabel(EditRoiDialog)
        self.spaceLabel.setObjectName(u"spaceLabel")
        self.spaceLabel.setMinimumSize(QSize(70, 0))

        self.horizontalLayout_6.addWidget(self.spaceLabel)

        self.spaceComboBox = QComboBox(EditRoiDialog)
        self.spaceComboBox.addItem("")
        self.spaceComboBox.addItem("")
        self.spaceComboBox.setObjectName(u"spaceComboBox")
        self.spaceComboBox.setEnabled(False)

        self.horizontalLayout_6.addWidget(self.spaceComboBox)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_5)


        self.verticalLayout_16.addLayout(self.horizontalLayout_6)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer)

        self.rectLabel = QLabel(EditRoiDialog)
        self.rectLabel.setObjectName(u"rectLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rectLabel.sizePolicy().hasHeightForWidth())
        self.rectLabel.setSizePolicy(sizePolicy)
        self.rectLabel.setMinimumSize(QSize(70, 25))
        self.rectLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_12.addWidget(self.rectLabel)


        self.horizontalLayout.addLayout(self.verticalLayout_12)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_5)

        self.rectLeftXLabel = QLabel(EditRoiDialog)
        self.rectLeftXLabel.setObjectName(u"rectLeftXLabel")
        sizePolicy.setHeightForWidth(self.rectLeftXLabel.sizePolicy().hasHeightForWidth())
        self.rectLeftXLabel.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.rectLeftXLabel)

        self.rectLeftXBox = QDoubleSpinBox(EditRoiDialog)
        self.rectLeftXBox.setObjectName(u"rectLeftXBox")

        self.verticalLayout.addWidget(self.rectLeftXBox)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_6)

        self.rectTopYLabel = QLabel(EditRoiDialog)
        self.rectTopYLabel.setObjectName(u"rectTopYLabel")
        sizePolicy.setHeightForWidth(self.rectTopYLabel.sizePolicy().hasHeightForWidth())
        self.rectTopYLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.rectTopYLabel)

        self.rectTopYBox = QDoubleSpinBox(EditRoiDialog)
        self.rectTopYBox.setObjectName(u"rectTopYBox")

        self.verticalLayout_2.addWidget(self.rectTopYBox)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_7)

        self.rectWidthLabel = QLabel(EditRoiDialog)
        self.rectWidthLabel.setObjectName(u"rectWidthLabel")
        sizePolicy.setHeightForWidth(self.rectWidthLabel.sizePolicy().hasHeightForWidth())
        self.rectWidthLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.rectWidthLabel)

        self.rectWidthBox = QDoubleSpinBox(EditRoiDialog)
        self.rectWidthBox.setObjectName(u"rectWidthBox")

        self.verticalLayout_3.addWidget(self.rectWidthBox)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_8)

        self.rectHeightLabel = QLabel(EditRoiDialog)
        self.rectHeightLabel.setObjectName(u"rectHeightLabel")
        sizePolicy.setHeightForWidth(self.rectHeightLabel.sizePolicy().hasHeightForWidth())
        self.rectHeightLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_4.addWidget(self.rectHeightLabel)

        self.rectHeightBox = QDoubleSpinBox(EditRoiDialog)
        self.rectHeightBox.setObjectName(u"rectHeightBox")

        self.verticalLayout_4.addWidget(self.rectHeightBox)


        self.horizontalLayout.addLayout(self.verticalLayout_4)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout_16.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_13.addItem(self.verticalSpacer_2)

        self.circLabel = QLabel(EditRoiDialog)
        self.circLabel.setObjectName(u"circLabel")
        sizePolicy.setHeightForWidth(self.circLabel.sizePolicy().hasHeightForWidth())
        self.circLabel.setSizePolicy(sizePolicy)
        self.circLabel.setMinimumSize(QSize(70, 25))
        self.circLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_13.addWidget(self.circLabel)


        self.horizontalLayout_2.addLayout(self.verticalLayout_13)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_9)

        self.circCenterXLabel = QLabel(EditRoiDialog)
        self.circCenterXLabel.setObjectName(u"circCenterXLabel")
        sizePolicy.setHeightForWidth(self.circCenterXLabel.sizePolicy().hasHeightForWidth())
        self.circCenterXLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_5.addWidget(self.circCenterXLabel)

        self.circCenterXBox = QDoubleSpinBox(EditRoiDialog)
        self.circCenterXBox.setObjectName(u"circCenterXBox")

        self.verticalLayout_5.addWidget(self.circCenterXBox)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_10)

        self.circCenterYLabel = QLabel(EditRoiDialog)
        self.circCenterYLabel.setObjectName(u"circCenterYLabel")
        sizePolicy.setHeightForWidth(self.circCenterYLabel.sizePolicy().hasHeightForWidth())
        self.circCenterYLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_6.addWidget(self.circCenterYLabel)

        self.circCenterYBox = QDoubleSpinBox(EditRoiDialog)
        self.circCenterYBox.setObjectName(u"circCenterYBox")

        self.verticalLayout_6.addWidget(self.circCenterYBox)


        self.horizontalLayout_2.addLayout(self.verticalLayout_6)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_11)

        self.circRLabel = QLabel(EditRoiDialog)
        self.circRLabel.setObjectName(u"circRLabel")
        sizePolicy.setHeightForWidth(self.circRLabel.sizePolicy().hasHeightForWidth())
        self.circRLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_7.addWidget(self.circRLabel)

        self.circRBox = QDoubleSpinBox(EditRoiDialog)
        self.circRBox.setObjectName(u"circRBox")

        self.verticalLayout_7.addWidget(self.circRBox)


        self.horizontalLayout_2.addLayout(self.verticalLayout_7)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)


        self.verticalLayout_16.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_14.addItem(self.verticalSpacer_3)

        self.ellipseLabel = QLabel(EditRoiDialog)
        self.ellipseLabel.setObjectName(u"ellipseLabel")
        self.ellipseLabel.setMinimumSize(QSize(70, 25))
        self.ellipseLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_14.addWidget(self.ellipseLabel)


        self.horizontalLayout_3.addLayout(self.verticalLayout_14)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalSpacer_12 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_12)

        self.ellipseCenterXLabel = QLabel(EditRoiDialog)
        self.ellipseCenterXLabel.setObjectName(u"ellipseCenterXLabel")
        sizePolicy.setHeightForWidth(self.ellipseCenterXLabel.sizePolicy().hasHeightForWidth())
        self.ellipseCenterXLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_8.addWidget(self.ellipseCenterXLabel)

        self.ellipseCenterXBox = QDoubleSpinBox(EditRoiDialog)
        self.ellipseCenterXBox.setObjectName(u"ellipseCenterXBox")

        self.verticalLayout_8.addWidget(self.ellipseCenterXBox)


        self.horizontalLayout_3.addLayout(self.verticalLayout_8)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalSpacer_13 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_13)

        self.ellipseCenterYLabel = QLabel(EditRoiDialog)
        self.ellipseCenterYLabel.setObjectName(u"ellipseCenterYLabel")
        sizePolicy.setHeightForWidth(self.ellipseCenterYLabel.sizePolicy().hasHeightForWidth())
        self.ellipseCenterYLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_9.addWidget(self.ellipseCenterYLabel)

        self.ellipseCenterYBox = QDoubleSpinBox(EditRoiDialog)
        self.ellipseCenterYBox.setObjectName(u"ellipseCenterYBox")

        self.verticalLayout_9.addWidget(self.ellipseCenterYBox)


        self.horizontalLayout_3.addLayout(self.verticalLayout_9)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalSpacer_14 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_14)

        self.ellipseRadiusXLabel = QLabel(EditRoiDialog)
        self.ellipseRadiusXLabel.setObjectName(u"ellipseRadiusXLabel")
        sizePolicy.setHeightForWidth(self.ellipseRadiusXLabel.sizePolicy().hasHeightForWidth())
        self.ellipseRadiusXLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_10.addWidget(self.ellipseRadiusXLabel)

        self.ellipseRadiusXBox = QDoubleSpinBox(EditRoiDialog)
        self.ellipseRadiusXBox.setObjectName(u"ellipseRadiusXBox")

        self.verticalLayout_10.addWidget(self.ellipseRadiusXBox)


        self.horizontalLayout_3.addLayout(self.verticalLayout_10)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalSpacer_15 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_15)

        self.ellipseRadiusYLabel = QLabel(EditRoiDialog)
        self.ellipseRadiusYLabel.setObjectName(u"ellipseRadiusYLabel")
        sizePolicy.setHeightForWidth(self.ellipseRadiusYLabel.sizePolicy().hasHeightForWidth())
        self.ellipseRadiusYLabel.setSizePolicy(sizePolicy)

        self.verticalLayout_11.addWidget(self.ellipseRadiusYLabel)

        self.ellipseRadiusYBox = QDoubleSpinBox(EditRoiDialog)
        self.ellipseRadiusYBox.setObjectName(u"ellipseRadiusYBox")

        self.verticalLayout_11.addWidget(self.ellipseRadiusYBox)


        self.horizontalLayout_3.addLayout(self.verticalLayout_11)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)


        self.verticalLayout_16.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.polygonLabel = QLabel(EditRoiDialog)
        self.polygonLabel.setObjectName(u"polygonLabel")
        self.polygonLabel.setMinimumSize(QSize(70, 0))

        self.verticalLayout_15.addWidget(self.polygonLabel)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_4)


        self.horizontalLayout_4.addLayout(self.verticalLayout_15)

        self.polygonTableWidget = QTableWidget(EditRoiDialog)
        self.polygonTableWidget.setObjectName(u"polygonTableWidget")
        self.polygonTableWidget.setAlternatingRowColors(True)
        self.polygonTableWidget.setCornerButtonEnabled(False)
        self.polygonTableWidget.setRowCount(0)
        self.polygonTableWidget.setColumnCount(0)

        self.horizontalLayout_4.addWidget(self.polygonTableWidget)


        self.verticalLayout_16.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.copyButton = QPushButton(EditRoiDialog)
        self.copyButton.setObjectName(u"copyButton")

        self.horizontalLayout_5.addWidget(self.copyButton)

        self.copyForAllButton = QPushButton(EditRoiDialog)
        self.copyForAllButton.setObjectName(u"copyForAllButton")

        self.horizontalLayout_5.addWidget(self.copyForAllButton)

        self.okButton = QPushButton(EditRoiDialog)
        self.okButton.setObjectName(u"okButton")

        self.horizontalLayout_5.addWidget(self.okButton)

        self.cancelButton = QPushButton(EditRoiDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout_5.addWidget(self.cancelButton)


        self.verticalLayout_16.addLayout(self.horizontalLayout_5)


        self.retranslateUi(EditRoiDialog)

        QMetaObject.connectSlotsByName(EditRoiDialog)
    # setupUi

    def retranslateUi(self, EditRoiDialog):
        EditRoiDialog.setWindowTitle(QCoreApplication.translate("EditRoiDialog", u"Edit ROI", None))
        self.spaceLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Space:", None))
        self.spaceComboBox.setItemText(0, QCoreApplication.translate("EditRoiDialog", u"Pixel", None))
        self.spaceComboBox.setItemText(1, QCoreApplication.translate("EditRoiDialog", u"Phasor", None))

        self.rectLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Rectangle:", None))
        self.rectLeftXLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Left x [px]", None))
        self.rectTopYLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Top y [px]", None))
        self.rectWidthLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Width", None))
        self.rectHeightLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Height", None))
        self.circLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Circle:", None))
        self.circCenterXLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Center x [px]", None))
        self.circCenterYLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Center y [px]", None))
        self.circRLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Radius [px]", None))
        self.ellipseLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Ellipse:", None))
        self.ellipseCenterXLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Center x [px]", None))
        self.ellipseCenterYLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Center y [px]", None))
        self.ellipseRadiusXLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Radius x [px]", None))
        self.ellipseRadiusYLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Radius y [px]", None))
        self.polygonLabel.setText(QCoreApplication.translate("EditRoiDialog", u"Polygon:", None))
        self.copyButton.setText(QCoreApplication.translate("EditRoiDialog", u"Copy", None))
        self.copyForAllButton.setText(QCoreApplication.translate("EditRoiDialog", u"Copy for All Stacks", None))
        self.okButton.setText(QCoreApplication.translate("EditRoiDialog", u"OK", None))
        self.cancelButton.setText(QCoreApplication.translate("EditRoiDialog", u"Cancel", None))
    # retranslateUi

