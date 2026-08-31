# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'curve_fit_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QDialog,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(900, 660)
        self.verticalLayout_10 = QVBoxLayout(Dialog)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.fitFuncLabel = QLabel(Dialog)
        self.fitFuncLabel.setObjectName(u"fitFuncLabel")

        self.horizontalLayout.addWidget(self.fitFuncLabel)

        self.instCheckBox = QCheckBox(Dialog)
        self.instCheckBox.setObjectName(u"instCheckBox")
        self.instCheckBox.setChecked(True)

        self.horizontalLayout.addWidget(self.instCheckBox)

        self.expDecay1CheckBox = QCheckBox(Dialog)
        self.expDecay1CheckBox.setObjectName(u"expDecay1CheckBox")
        self.expDecay1CheckBox.setChecked(True)

        self.horizontalLayout.addWidget(self.expDecay1CheckBox)

        self.expDecay2CheckBox = QCheckBox(Dialog)
        self.expDecay2CheckBox.setObjectName(u"expDecay2CheckBox")

        self.horizontalLayout.addWidget(self.expDecay2CheckBox)

        self.expDecay3CheckBox = QCheckBox(Dialog)
        self.expDecay3CheckBox.setObjectName(u"expDecay3CheckBox")

        self.horizontalLayout.addWidget(self.expDecay3CheckBox)

        self.expDecayInfCheckBox = QCheckBox(Dialog)
        self.expDecayInfCheckBox.setObjectName(u"expDecayInfCheckBox")

        self.horizontalLayout.addWidget(self.expDecayInfCheckBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout_10.addLayout(self.horizontalLayout)

        self.horizontalLayout_29 = QHBoxLayout()
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.pulseWidthLabel = QLabel(Dialog)
        self.pulseWidthLabel.setObjectName(u"pulseWidthLabel")
        self.pulseWidthLabel.setTextFormat(Qt.TextFormat.AutoText)

        self.horizontalLayout_29.addWidget(self.pulseWidthLabel)

        self.infoIcon = QLabel(Dialog)
        self.infoIcon.setObjectName(u"infoIcon")

        self.horizontalLayout_29.addWidget(self.infoIcon)

        self.specifyPulseWidthRadioButton = QRadioButton(Dialog)
        self.buttonGroup = QButtonGroup(Dialog)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.specifyPulseWidthRadioButton)
        self.specifyPulseWidthRadioButton.setObjectName(u"specifyPulseWidthRadioButton")

        self.horizontalLayout_29.addWidget(self.specifyPulseWidthRadioButton)

        self.pulseWidthLineEdit = QLineEdit(Dialog)
        self.pulseWidthLineEdit.setObjectName(u"pulseWidthLineEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pulseWidthLineEdit.sizePolicy().hasHeightForWidth())
        self.pulseWidthLineEdit.setSizePolicy(sizePolicy)

        self.horizontalLayout_29.addWidget(self.pulseWidthLineEdit)

        self.pulseWidthUnitLabel = QLabel(Dialog)
        self.pulseWidthUnitLabel.setObjectName(u"pulseWidthUnitLabel")

        self.horizontalLayout_29.addWidget(self.pulseWidthUnitLabel)

        self.fitPulseWidthRadioButton = QRadioButton(Dialog)
        self.buttonGroup.addButton(self.fitPulseWidthRadioButton)
        self.fitPulseWidthRadioButton.setObjectName(u"fitPulseWidthRadioButton")
        self.fitPulseWidthRadioButton.setChecked(True)

        self.horizontalLayout_29.addWidget(self.fitPulseWidthRadioButton)

        self.iniTpLabel = QLabel(Dialog)
        self.iniTpLabel.setObjectName(u"iniTpLabel")

        self.horizontalLayout_29.addWidget(self.iniTpLabel)

        self.iniTpLineEdit = QLineEdit(Dialog)
        self.iniTpLineEdit.setObjectName(u"iniTpLineEdit")

        self.horizontalLayout_29.addWidget(self.iniTpLineEdit)

        self.iniTpUnitLabel = QLabel(Dialog)
        self.iniTpUnitLabel.setObjectName(u"iniTpUnitLabel")

        self.horizontalLayout_29.addWidget(self.iniTpUnitLabel)

        self.lowerlimTpLabel = QLabel(Dialog)
        self.lowerlimTpLabel.setObjectName(u"lowerlimTpLabel")

        self.horizontalLayout_29.addWidget(self.lowerlimTpLabel)

        self.lowerlimTpLineEdit = QLineEdit(Dialog)
        self.lowerlimTpLineEdit.setObjectName(u"lowerlimTpLineEdit")

        self.horizontalLayout_29.addWidget(self.lowerlimTpLineEdit)

        self.upperlimTpLabel = QLabel(Dialog)
        self.upperlimTpLabel.setObjectName(u"upperlimTpLabel")

        self.horizontalLayout_29.addWidget(self.upperlimTpLabel)

        self.upperlimTpLineEdit = QLineEdit(Dialog)
        self.upperlimTpLineEdit.setObjectName(u"upperlimTpLineEdit")

        self.horizontalLayout_29.addWidget(self.upperlimTpLineEdit)


        self.verticalLayout_10.addLayout(self.horizontalLayout_29)

        self.horizontalLayout_30 = QHBoxLayout()
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.t0Label = QLabel(Dialog)
        self.t0Label.setObjectName(u"t0Label")

        self.horizontalLayout_30.addWidget(self.t0Label)

        self.specifyt0RadioButton = QRadioButton(Dialog)
        self.specifyt0RadioButton.setObjectName(u"specifyt0RadioButton")

        self.horizontalLayout_30.addWidget(self.specifyt0RadioButton)

        self.t0LineEdit = QLineEdit(Dialog)
        self.t0LineEdit.setObjectName(u"t0LineEdit")

        self.horizontalLayout_30.addWidget(self.t0LineEdit)

        self.t0unitLabel = QLabel(Dialog)
        self.t0unitLabel.setObjectName(u"t0unitLabel")

        self.horizontalLayout_30.addWidget(self.t0unitLabel)

        self.fitt0RadioButton = QRadioButton(Dialog)
        self.fitt0RadioButton.setObjectName(u"fitt0RadioButton")
        self.fitt0RadioButton.setChecked(True)

        self.horizontalLayout_30.addWidget(self.fitt0RadioButton)

        self.init0Label = QLabel(Dialog)
        self.init0Label.setObjectName(u"init0Label")

        self.horizontalLayout_30.addWidget(self.init0Label)

        self.initt0LineEdit = QLineEdit(Dialog)
        self.initt0LineEdit.setObjectName(u"initt0LineEdit")

        self.horizontalLayout_30.addWidget(self.initt0LineEdit)

        self.init0UnitLabel = QLabel(Dialog)
        self.init0UnitLabel.setObjectName(u"init0UnitLabel")

        self.horizontalLayout_30.addWidget(self.init0UnitLabel)

        self.lowerlimt0Label = QLabel(Dialog)
        self.lowerlimt0Label.setObjectName(u"lowerlimt0Label")

        self.horizontalLayout_30.addWidget(self.lowerlimt0Label)

        self.lowerlimt0LineEdit = QLineEdit(Dialog)
        self.lowerlimt0LineEdit.setObjectName(u"lowerlimt0LineEdit")

        self.horizontalLayout_30.addWidget(self.lowerlimt0LineEdit)

        self.upperlimt0Label = QLabel(Dialog)
        self.upperlimt0Label.setObjectName(u"upperlimt0Label")

        self.horizontalLayout_30.addWidget(self.upperlimt0Label)

        self.upperlimt0LineEdit = QLineEdit(Dialog)
        self.upperlimt0LineEdit.setObjectName(u"upperlimt0LineEdit")

        self.horizontalLayout_30.addWidget(self.upperlimt0LineEdit)


        self.verticalLayout_10.addLayout(self.horizontalLayout_30)

        self.horizontalLayout_32 = QHBoxLayout()
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.instPicture = QLabel(self.groupBox)
        self.instPicture.setObjectName(u"instPicture")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.instPicture.sizePolicy().hasHeightForWidth())
        self.instPicture.setSizePolicy(sizePolicy1)
        self.instPicture.setMinimumSize(QSize(260, 195))
        self.instPicture.setMaximumSize(QSize(260, 195))
        self.instPicture.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.instPicture)

        self.A0Label = QLabel(self.groupBox)
        self.A0Label.setObjectName(u"A0Label")

        self.verticalLayout.addWidget(self.A0Label)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.iniA0Label = QLabel(self.groupBox)
        self.iniA0Label.setObjectName(u"iniA0Label")

        self.horizontalLayout_2.addWidget(self.iniA0Label)

        self.iniA0LineEdit = QLineEdit(self.groupBox)
        self.iniA0LineEdit.setObjectName(u"iniA0LineEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.iniA0LineEdit.sizePolicy().hasHeightForWidth())
        self.iniA0LineEdit.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.iniA0LineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lowerlimA0Label = QLabel(self.groupBox)
        self.lowerlimA0Label.setObjectName(u"lowerlimA0Label")

        self.horizontalLayout_3.addWidget(self.lowerlimA0Label)

        self.lowerlimA0LineEdit = QLineEdit(self.groupBox)
        self.lowerlimA0LineEdit.setObjectName(u"lowerlimA0LineEdit")

        self.horizontalLayout_3.addWidget(self.lowerlimA0LineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.upperlimA0Label = QLabel(self.groupBox)
        self.upperlimA0Label.setObjectName(u"upperlimA0Label")

        self.horizontalLayout_4.addWidget(self.upperlimA0Label)

        self.upperlimA0LineEdit = QLineEdit(self.groupBox)
        self.upperlimA0LineEdit.setObjectName(u"upperlimA0LineEdit")

        self.horizontalLayout_4.addWidget(self.upperlimA0LineEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_32.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(Dialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.expDecayPicture = QLabel(self.groupBox_3)
        self.expDecayPicture.setObjectName(u"expDecayPicture")
        self.expDecayPicture.setMinimumSize(QSize(260, 195))
        self.expDecayPicture.setMaximumSize(QSize(260, 195))
        self.expDecayPicture.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_9.addWidget(self.expDecayPicture)

        self.ExpDecayTab = QTabWidget(self.groupBox_3)
        self.ExpDecayTab.setObjectName(u"ExpDecayTab")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_11 = QHBoxLayout(self.tab)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.A1Label = QLabel(self.tab)
        self.A1Label.setObjectName(u"A1Label")

        self.verticalLayout_2.addWidget(self.A1Label)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.iniA1Label = QLabel(self.tab)
        self.iniA1Label.setObjectName(u"iniA1Label")

        self.horizontalLayout_5.addWidget(self.iniA1Label)

        self.iniA1LineEdit = QLineEdit(self.tab)
        self.iniA1LineEdit.setObjectName(u"iniA1LineEdit")

        self.horizontalLayout_5.addWidget(self.iniA1LineEdit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.lowerlimA1Label = QLabel(self.tab)
        self.lowerlimA1Label.setObjectName(u"lowerlimA1Label")

        self.horizontalLayout_6.addWidget(self.lowerlimA1Label)

        self.lowerlimA1LineEdit = QLineEdit(self.tab)
        self.lowerlimA1LineEdit.setObjectName(u"lowerlimA1LineEdit")

        self.horizontalLayout_6.addWidget(self.lowerlimA1LineEdit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.upperlimA1Label = QLabel(self.tab)
        self.upperlimA1Label.setObjectName(u"upperlimA1Label")

        self.horizontalLayout_7.addWidget(self.upperlimA1Label)

        self.upperlimA1LineEdit = QLineEdit(self.tab)
        self.upperlimA1LineEdit.setObjectName(u"upperlimA1LineEdit")

        self.horizontalLayout_7.addWidget(self.upperlimA1LineEdit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)


        self.horizontalLayout_11.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.T1Label = QLabel(self.tab)
        self.T1Label.setObjectName(u"T1Label")

        self.verticalLayout_3.addWidget(self.T1Label)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.iniT1Label = QLabel(self.tab)
        self.iniT1Label.setObjectName(u"iniT1Label")

        self.horizontalLayout_8.addWidget(self.iniT1Label)

        self.iniT1LineEdit = QLineEdit(self.tab)
        self.iniT1LineEdit.setObjectName(u"iniT1LineEdit")

        self.horizontalLayout_8.addWidget(self.iniT1LineEdit)

        self.iniT1UnitLabel = QLabel(self.tab)
        self.iniT1UnitLabel.setObjectName(u"iniT1UnitLabel")

        self.horizontalLayout_8.addWidget(self.iniT1UnitLabel)


        self.verticalLayout_3.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.lowerlimT1Label = QLabel(self.tab)
        self.lowerlimT1Label.setObjectName(u"lowerlimT1Label")

        self.horizontalLayout_9.addWidget(self.lowerlimT1Label)

        self.lowerlimT1LineEdit = QLineEdit(self.tab)
        self.lowerlimT1LineEdit.setObjectName(u"lowerlimT1LineEdit")

        self.horizontalLayout_9.addWidget(self.lowerlimT1LineEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.upperlimT1Label = QLabel(self.tab)
        self.upperlimT1Label.setObjectName(u"upperlimT1Label")

        self.horizontalLayout_10.addWidget(self.upperlimT1Label)

        self.upperlimT1LineEdit = QLineEdit(self.tab)
        self.upperlimT1LineEdit.setObjectName(u"upperlimT1LineEdit")

        self.horizontalLayout_10.addWidget(self.upperlimT1LineEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_10)


        self.horizontalLayout_11.addLayout(self.verticalLayout_3)

        self.ExpDecayTab.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.horizontalLayout_18 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.A2Label = QLabel(self.tab_2)
        self.A2Label.setObjectName(u"A2Label")

        self.verticalLayout_4.addWidget(self.A2Label)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.iniA2Label = QLabel(self.tab_2)
        self.iniA2Label.setObjectName(u"iniA2Label")

        self.horizontalLayout_12.addWidget(self.iniA2Label)

        self.iniA2LineEdit = QLineEdit(self.tab_2)
        self.iniA2LineEdit.setObjectName(u"iniA2LineEdit")

        self.horizontalLayout_12.addWidget(self.iniA2LineEdit)


        self.verticalLayout_4.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.lowerlimA2Label = QLabel(self.tab_2)
        self.lowerlimA2Label.setObjectName(u"lowerlimA2Label")

        self.horizontalLayout_13.addWidget(self.lowerlimA2Label)

        self.lowerlimA2LineEdit = QLineEdit(self.tab_2)
        self.lowerlimA2LineEdit.setObjectName(u"lowerlimA2LineEdit")

        self.horizontalLayout_13.addWidget(self.lowerlimA2LineEdit)


        self.verticalLayout_4.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.upperlimA2Label = QLabel(self.tab_2)
        self.upperlimA2Label.setObjectName(u"upperlimA2Label")

        self.horizontalLayout_14.addWidget(self.upperlimA2Label)

        self.upperlimA2LineEdit = QLineEdit(self.tab_2)
        self.upperlimA2LineEdit.setObjectName(u"upperlimA2LineEdit")

        self.horizontalLayout_14.addWidget(self.upperlimA2LineEdit)


        self.verticalLayout_4.addLayout(self.horizontalLayout_14)


        self.horizontalLayout_18.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.T2Label = QLabel(self.tab_2)
        self.T2Label.setObjectName(u"T2Label")

        self.verticalLayout_5.addWidget(self.T2Label)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.iniT2Label = QLabel(self.tab_2)
        self.iniT2Label.setObjectName(u"iniT2Label")

        self.horizontalLayout_15.addWidget(self.iniT2Label)

        self.iniT2LineEdit = QLineEdit(self.tab_2)
        self.iniT2LineEdit.setObjectName(u"iniT2LineEdit")

        self.horizontalLayout_15.addWidget(self.iniT2LineEdit)

        self.initT2UnitLabel = QLabel(self.tab_2)
        self.initT2UnitLabel.setObjectName(u"initT2UnitLabel")

        self.horizontalLayout_15.addWidget(self.initT2UnitLabel)


        self.verticalLayout_5.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.lowerlimT2Label = QLabel(self.tab_2)
        self.lowerlimT2Label.setObjectName(u"lowerlimT2Label")

        self.horizontalLayout_16.addWidget(self.lowerlimT2Label)

        self.lowerlimT2LineEdit = QLineEdit(self.tab_2)
        self.lowerlimT2LineEdit.setObjectName(u"lowerlimT2LineEdit")

        self.horizontalLayout_16.addWidget(self.lowerlimT2LineEdit)


        self.verticalLayout_5.addLayout(self.horizontalLayout_16)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.upperlimT2Label = QLabel(self.tab_2)
        self.upperlimT2Label.setObjectName(u"upperlimT2Label")

        self.horizontalLayout_17.addWidget(self.upperlimT2Label)

        self.upperlimT2LineEdit = QLineEdit(self.tab_2)
        self.upperlimT2LineEdit.setObjectName(u"upperlimT2LineEdit")

        self.horizontalLayout_17.addWidget(self.upperlimT2LineEdit)


        self.verticalLayout_5.addLayout(self.horizontalLayout_17)


        self.horizontalLayout_18.addLayout(self.verticalLayout_5)

        self.ExpDecayTab.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.horizontalLayout_25 = QHBoxLayout(self.tab_3)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.A3Label = QLabel(self.tab_3)
        self.A3Label.setObjectName(u"A3Label")

        self.verticalLayout_6.addWidget(self.A3Label)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.iniA3Label = QLabel(self.tab_3)
        self.iniA3Label.setObjectName(u"iniA3Label")

        self.horizontalLayout_19.addWidget(self.iniA3Label)

        self.iniA3LineEdit = QLineEdit(self.tab_3)
        self.iniA3LineEdit.setObjectName(u"iniA3LineEdit")

        self.horizontalLayout_19.addWidget(self.iniA3LineEdit)


        self.verticalLayout_6.addLayout(self.horizontalLayout_19)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.lowerlimA3Label = QLabel(self.tab_3)
        self.lowerlimA3Label.setObjectName(u"lowerlimA3Label")

        self.horizontalLayout_20.addWidget(self.lowerlimA3Label)

        self.lowerlimA3LineEdit = QLineEdit(self.tab_3)
        self.lowerlimA3LineEdit.setObjectName(u"lowerlimA3LineEdit")

        self.horizontalLayout_20.addWidget(self.lowerlimA3LineEdit)


        self.verticalLayout_6.addLayout(self.horizontalLayout_20)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.upperlimA3Label = QLabel(self.tab_3)
        self.upperlimA3Label.setObjectName(u"upperlimA3Label")

        self.horizontalLayout_21.addWidget(self.upperlimA3Label)

        self.upperlimA3LineEdit = QLineEdit(self.tab_3)
        self.upperlimA3LineEdit.setObjectName(u"upperlimA3LineEdit")

        self.horizontalLayout_21.addWidget(self.upperlimA3LineEdit)


        self.verticalLayout_6.addLayout(self.horizontalLayout_21)


        self.horizontalLayout_25.addLayout(self.verticalLayout_6)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.T3Label = QLabel(self.tab_3)
        self.T3Label.setObjectName(u"T3Label")

        self.verticalLayout_7.addWidget(self.T3Label)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.iniT3Label = QLabel(self.tab_3)
        self.iniT3Label.setObjectName(u"iniT3Label")

        self.horizontalLayout_22.addWidget(self.iniT3Label)

        self.iniT3LineEdit = QLineEdit(self.tab_3)
        self.iniT3LineEdit.setObjectName(u"iniT3LineEdit")

        self.horizontalLayout_22.addWidget(self.iniT3LineEdit)

        self.initT3UnitLabel = QLabel(self.tab_3)
        self.initT3UnitLabel.setObjectName(u"initT3UnitLabel")

        self.horizontalLayout_22.addWidget(self.initT3UnitLabel)


        self.verticalLayout_7.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.lowerlimT3Label = QLabel(self.tab_3)
        self.lowerlimT3Label.setObjectName(u"lowerlimT3Label")

        self.horizontalLayout_23.addWidget(self.lowerlimT3Label)

        self.lowerlimT3LineEdit = QLineEdit(self.tab_3)
        self.lowerlimT3LineEdit.setObjectName(u"lowerlimT3LineEdit")

        self.horizontalLayout_23.addWidget(self.lowerlimT3LineEdit)


        self.verticalLayout_7.addLayout(self.horizontalLayout_23)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.upperlimT3Label = QLabel(self.tab_3)
        self.upperlimT3Label.setObjectName(u"upperlimT3Label")

        self.horizontalLayout_24.addWidget(self.upperlimT3Label)

        self.upperlimT3LineEdit = QLineEdit(self.tab_3)
        self.upperlimT3LineEdit.setObjectName(u"upperlimT3LineEdit")

        self.horizontalLayout_24.addWidget(self.upperlimT3LineEdit)


        self.verticalLayout_7.addLayout(self.horizontalLayout_24)


        self.horizontalLayout_25.addLayout(self.verticalLayout_7)

        self.ExpDecayTab.addTab(self.tab_3, "")

        self.verticalLayout_9.addWidget(self.ExpDecayTab)


        self.horizontalLayout_32.addWidget(self.groupBox_3)

        self.groupBox_2 = QGroupBox(Dialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.expDecayInfPicture = QLabel(self.groupBox_2)
        self.expDecayInfPicture.setObjectName(u"expDecayInfPicture")
        self.expDecayInfPicture.setMinimumSize(QSize(260, 195))
        self.expDecayInfPicture.setMaximumSize(QSize(260, 195))
        self.expDecayInfPicture.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_8.addWidget(self.expDecayInfPicture)

        self.A4Label = QLabel(self.groupBox_2)
        self.A4Label.setObjectName(u"A4Label")

        self.verticalLayout_8.addWidget(self.A4Label)

        self.horizontalLayout_26 = QHBoxLayout()
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.iniA4Label = QLabel(self.groupBox_2)
        self.iniA4Label.setObjectName(u"iniA4Label")

        self.horizontalLayout_26.addWidget(self.iniA4Label)

        self.iniA4LineEdit = QLineEdit(self.groupBox_2)
        self.iniA4LineEdit.setObjectName(u"iniA4LineEdit")

        self.horizontalLayout_26.addWidget(self.iniA4LineEdit)


        self.verticalLayout_8.addLayout(self.horizontalLayout_26)

        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.lowerlimA4Label = QLabel(self.groupBox_2)
        self.lowerlimA4Label.setObjectName(u"lowerlimA4Label")

        self.horizontalLayout_27.addWidget(self.lowerlimA4Label)

        self.lowerlimA4LineEdit = QLineEdit(self.groupBox_2)
        self.lowerlimA4LineEdit.setObjectName(u"lowerlimA4LineEdit")

        self.horizontalLayout_27.addWidget(self.lowerlimA4LineEdit)


        self.verticalLayout_8.addLayout(self.horizontalLayout_27)

        self.horizontalLayout_28 = QHBoxLayout()
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.upperlimA4Label = QLabel(self.groupBox_2)
        self.upperlimA4Label.setObjectName(u"upperlimA4Label")

        self.horizontalLayout_28.addWidget(self.upperlimA4Label)

        self.upperlimA4LineEdit = QLineEdit(self.groupBox_2)
        self.upperlimA4LineEdit.setObjectName(u"upperlimA4LineEdit")

        self.horizontalLayout_28.addWidget(self.upperlimA4LineEdit)


        self.verticalLayout_8.addLayout(self.horizontalLayout_28)


        self.horizontalLayout_32.addWidget(self.groupBox_2)


        self.verticalLayout_10.addLayout(self.horizontalLayout_32)

        self.resultLabel = QLabel(Dialog)
        self.resultLabel.setObjectName(u"resultLabel")

        self.verticalLayout_10.addWidget(self.resultLabel)

        self.resultPlainTextEdit = QPlainTextEdit(Dialog)
        self.resultPlainTextEdit.setObjectName(u"resultPlainTextEdit")
        self.resultPlainTextEdit.setReadOnly(True)

        self.verticalLayout_10.addWidget(self.resultPlainTextEdit)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_31.addItem(self.horizontalSpacer_3)

        self.fitPushButton = QPushButton(Dialog)
        self.fitPushButton.setObjectName(u"fitPushButton")

        self.horizontalLayout_31.addWidget(self.fitPushButton)

        self.exitPushButton = QPushButton(Dialog)
        self.exitPushButton.setObjectName(u"exitPushButton")

        self.horizontalLayout_31.addWidget(self.exitPushButton)


        self.verticalLayout_10.addLayout(self.horizontalLayout_31)


        self.retranslateUi(Dialog)

        self.ExpDecayTab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.fitFuncLabel.setText(QCoreApplication.translate("Dialog", u"Fitting Function:", None))
        self.instCheckBox.setText(QCoreApplication.translate("Dialog", u"Instantaneous", None))
        self.expDecay1CheckBox.setText(QCoreApplication.translate("Dialog", u"Exp Decay 1", None))
        self.expDecay2CheckBox.setText(QCoreApplication.translate("Dialog", u"Exp Decay 2", None))
        self.expDecay3CheckBox.setText(QCoreApplication.translate("Dialog", u"Exp Decay 3", None))
        self.expDecayInfCheckBox.setText(QCoreApplication.translate("Dialog", u"Exp Decay (\u03c4=\u221e)", None))
        self.pulseWidthLabel.setText(QCoreApplication.translate("Dialog", u"Pulse Width:", None))
#if QT_CONFIG(tooltip)
        self.infoIcon.setToolTip(QCoreApplication.translate("Dialog", u"pulse width = sqrt(t_pump**2 + t_probe**2)", None))
#endif // QT_CONFIG(tooltip)
        self.infoIcon.setText(QCoreApplication.translate("Dialog", u"info", None))
        self.specifyPulseWidthRadioButton.setText(QCoreApplication.translate("Dialog", u"Specify", None))
        self.pulseWidthLineEdit.setText(QCoreApplication.translate("Dialog", u"100", None))
        self.pulseWidthUnitLabel.setText(QCoreApplication.translate("Dialog", u"fs", None))
        self.fitPulseWidthRadioButton.setText(QCoreApplication.translate("Dialog", u"Let the program fit", None))
        self.iniTpLabel.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.iniTpLineEdit.setText(QCoreApplication.translate("Dialog", u"100", None))
        self.iniTpUnitLabel.setText(QCoreApplication.translate("Dialog", u"fs", None))
        self.lowerlimTpLabel.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimTpLineEdit.setText(QCoreApplication.translate("Dialog", u"1e-6", None))
        self.upperlimTpLabel.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimTpLineEdit.setText(QCoreApplication.translate("Dialog", u"inf", None))
        self.t0Label.setText(QCoreApplication.translate("Dialog", u"Time Shift (t0):", None))
        self.specifyt0RadioButton.setText(QCoreApplication.translate("Dialog", u"Specify", None))
        self.t0LineEdit.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.t0unitLabel.setText(QCoreApplication.translate("Dialog", u"ps", None))
        self.fitt0RadioButton.setText(QCoreApplication.translate("Dialog", u"Let the program fit", None))
        self.init0Label.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.initt0LineEdit.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.init0UnitLabel.setText(QCoreApplication.translate("Dialog", u"ps", None))
        self.lowerlimt0Label.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimt0LineEdit.setText(QCoreApplication.translate("Dialog", u"-1", None))
        self.upperlimt0Label.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimt0LineEdit.setText(QCoreApplication.translate("Dialog", u"1", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Instantaneous", None))
        self.instPicture.setText(QCoreApplication.translate("Dialog", u"Instantaneous Picture", None))
        self.A0Label.setText(QCoreApplication.translate("Dialog", u"Coefficient A0", None))
        self.iniA0Label.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.iniA0LineEdit.setText(QCoreApplication.translate("Dialog", u"1.00", None))
        self.lowerlimA0Label.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimA0LineEdit.setText(QCoreApplication.translate("Dialog", u"-inf", None))
        self.upperlimA0Label.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimA0LineEdit.setText(QCoreApplication.translate("Dialog", u"inf", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Dialog", u"Exponential Decay", None))
        self.expDecayPicture.setText(QCoreApplication.translate("Dialog", u"Exp Decay Picture", None))
        self.A1Label.setText(QCoreApplication.translate("Dialog", u"Coefficient A1", None))
        self.iniA1Label.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.iniA1LineEdit.setText(QCoreApplication.translate("Dialog", u"1.00", None))
        self.lowerlimA1Label.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimA1LineEdit.setText(QCoreApplication.translate("Dialog", u"-inf", None))
        self.upperlimA1Label.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimA1LineEdit.setText(QCoreApplication.translate("Dialog", u"inf", None))
        self.T1Label.setText(QCoreApplication.translate("Dialog", u"Lifetime \u03c41", None))
        self.iniT1Label.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.iniT1LineEdit.setText(QCoreApplication.translate("Dialog", u"1.00", None))
        self.iniT1UnitLabel.setText(QCoreApplication.translate("Dialog", u"ps", None))
        self.lowerlimT1Label.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimT1LineEdit.setText(QCoreApplication.translate("Dialog", u"1e-6", None))
        self.upperlimT1Label.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimT1LineEdit.setText(QCoreApplication.translate("Dialog", u"inf", None))
        self.ExpDecayTab.setTabText(self.ExpDecayTab.indexOf(self.tab), QCoreApplication.translate("Dialog", u"Decay 1", None))
        self.A2Label.setText(QCoreApplication.translate("Dialog", u"Coefficient A2", None))
        self.iniA2Label.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.iniA2LineEdit.setText(QCoreApplication.translate("Dialog", u"1.00", None))
        self.lowerlimA2Label.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimA2LineEdit.setText(QCoreApplication.translate("Dialog", u"-inf", None))
        self.upperlimA2Label.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimA2LineEdit.setText(QCoreApplication.translate("Dialog", u"inf", None))
        self.T2Label.setText(QCoreApplication.translate("Dialog", u"Lifetime \u03c42", None))
        self.iniT2Label.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.iniT2LineEdit.setText(QCoreApplication.translate("Dialog", u"10.00", None))
        self.initT2UnitLabel.setText(QCoreApplication.translate("Dialog", u"ps", None))
        self.lowerlimT2Label.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimT2LineEdit.setText(QCoreApplication.translate("Dialog", u"1e-6", None))
        self.upperlimT2Label.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimT2LineEdit.setText(QCoreApplication.translate("Dialog", u"inf", None))
        self.ExpDecayTab.setTabText(self.ExpDecayTab.indexOf(self.tab_2), QCoreApplication.translate("Dialog", u"Decay 2", None))
        self.A3Label.setText(QCoreApplication.translate("Dialog", u"Coefficient A3", None))
        self.iniA3Label.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.iniA3LineEdit.setText(QCoreApplication.translate("Dialog", u"1.00", None))
        self.lowerlimA3Label.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimA3LineEdit.setText(QCoreApplication.translate("Dialog", u"-inf", None))
        self.upperlimA3Label.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimA3LineEdit.setText(QCoreApplication.translate("Dialog", u"inf", None))
        self.T3Label.setText(QCoreApplication.translate("Dialog", u"Lifetime \u03c43", None))
        self.iniT3Label.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.iniT3LineEdit.setText(QCoreApplication.translate("Dialog", u"0.10", None))
        self.initT3UnitLabel.setText(QCoreApplication.translate("Dialog", u"ps", None))
        self.lowerlimT3Label.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimT3LineEdit.setText(QCoreApplication.translate("Dialog", u"1e-6", None))
        self.upperlimT3Label.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimT3LineEdit.setText(QCoreApplication.translate("Dialog", u"inf", None))
        self.ExpDecayTab.setTabText(self.ExpDecayTab.indexOf(self.tab_3), QCoreApplication.translate("Dialog", u"Decay 3", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"Exponential Decay (\u03c4=\u221e)", None))
        self.expDecayInfPicture.setText(QCoreApplication.translate("Dialog", u"Exp Decay Inf Picture", None))
        self.A4Label.setText(QCoreApplication.translate("Dialog", u"Coefficient A4", None))
        self.iniA4Label.setText(QCoreApplication.translate("Dialog", u"Initial Value:", None))
        self.iniA4LineEdit.setText(QCoreApplication.translate("Dialog", u"1.00", None))
        self.lowerlimA4Label.setText(QCoreApplication.translate("Dialog", u"Lower Bound:", None))
        self.lowerlimA4LineEdit.setText(QCoreApplication.translate("Dialog", u"-inf", None))
        self.upperlimA4Label.setText(QCoreApplication.translate("Dialog", u"Upper Bound:", None))
        self.upperlimA4LineEdit.setText(QCoreApplication.translate("Dialog", u"inf", None))
        self.resultLabel.setText(QCoreApplication.translate("Dialog", u"Results", None))
        self.fitPushButton.setText(QCoreApplication.translate("Dialog", u"Fit", None))
        self.exitPushButton.setText(QCoreApplication.translate("Dialog", u"Exit", None))
    # retranslateUi

