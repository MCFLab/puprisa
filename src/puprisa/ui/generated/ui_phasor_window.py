# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'phasor_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QGraphicsView,
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSlider, QStatusBar, QVBoxLayout,
    QWidget)

from puprisa.ui.widgets.mpl_canvas import MatplotlibFigureCanvas
from puprisa.ui.widgets.scrollable_graphics_view import ScrollableGraphicsView

class Ui_PhasorWindow(object):
    def setupUi(self, PhasorWindow):
        if not PhasorWindow.objectName():
            PhasorWindow.setObjectName(u"PhasorWindow")
        PhasorWindow.resize(1000, 500)
        self.actionOpenStack = QAction(PhasorWindow)
        self.actionOpenStack.setObjectName(u"actionOpenStack")
        self.actionNormalizeCurve = QAction(PhasorWindow)
        self.actionNormalizeCurve.setObjectName(u"actionNormalizeCurve")
        self.actionNormalizeCurve.setCheckable(True)
        self.actionExit = QAction(PhasorWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(PhasorWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionSaveView = QAction(PhasorWindow)
        self.actionSaveView.setObjectName(u"actionSaveView")
        self.actionSavePhasorView = QAction(PhasorWindow)
        self.actionSavePhasorView.setObjectName(u"actionSavePhasorView")
        self.actionViewCurve = QAction(PhasorWindow)
        self.actionViewCurve.setObjectName(u"actionViewCurve")
        self.actionExportCurve = QAction(PhasorWindow)
        self.actionExportCurve.setObjectName(u"actionExportCurve")
        self.actionEdit_ROI = QAction(PhasorWindow)
        self.actionEdit_ROI.setObjectName(u"actionEdit_ROI")
        self.actionClear_All_ROI = QAction(PhasorWindow)
        self.actionClear_All_ROI.setObjectName(u"actionClear_All_ROI")
        self.actionCurveFit = QAction(PhasorWindow)
        self.actionCurveFit.setObjectName(u"actionCurveFit")
        self.centralwidget = QWidget(PhasorWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_6 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.phasorGraphicsView = ScrollableGraphicsView(self.centralwidget)
        self.phasorGraphicsView.setObjectName(u"phasorGraphicsView")

        self.verticalLayout.addWidget(self.phasorGraphicsView)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.Frequency = QLabel(self.centralwidget)
        self.Frequency.setObjectName(u"Frequency")

        self.horizontalLayout.addWidget(self.Frequency)

        self.freqSlider = QSlider(self.centralwidget)
        self.freqSlider.setObjectName(u"freqSlider")
        self.freqSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout.addWidget(self.freqSlider)

        self.freqSpinBox = QDoubleSpinBox(self.centralwidget)
        self.freqSpinBox.setObjectName(u"freqSpinBox")
        self.freqSpinBox.setMinimum(0.000000000000000)

        self.horizontalLayout.addWidget(self.freqSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.horizontalLayout_6.addLayout(self.verticalLayout)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.plotCanvas = MatplotlibFigureCanvas(self.centralwidget)
        self.plotCanvas.setObjectName(u"plotCanvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotCanvas.sizePolicy().hasHeightForWidth())
        self.plotCanvas.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.plotCanvas)

        self.ppsGraphicsView = QGraphicsView(self.centralwidget)
        self.ppsGraphicsView.setObjectName(u"ppsGraphicsView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ppsGraphicsView.sizePolicy().hasHeightForWidth())
        self.ppsGraphicsView.setSizePolicy(sizePolicy1)

        self.verticalLayout_3.addWidget(self.ppsGraphicsView)

        self.verticalLayout_3.setStretch(0, 2)
        self.verticalLayout_3.setStretch(1, 1)

        self.horizontalLayout_6.addLayout(self.verticalLayout_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.stackMgrLabel = QLabel(self.centralwidget)
        self.stackMgrLabel.setObjectName(u"stackMgrLabel")

        self.verticalLayout_2.addWidget(self.stackMgrLabel)

        self.stackListWidget = QListWidget(self.centralwidget)
        self.stackListWidget.setObjectName(u"stackListWidget")

        self.verticalLayout_2.addWidget(self.stackListWidget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.stackAddButton = QPushButton(self.centralwidget)
        self.stackAddButton.setObjectName(u"stackAddButton")

        self.horizontalLayout_2.addWidget(self.stackAddButton)

        self.stackRenameButton = QPushButton(self.centralwidget)
        self.stackRenameButton.setObjectName(u"stackRenameButton")

        self.horizontalLayout_2.addWidget(self.stackRenameButton)

        self.stackDeleteButton = QPushButton(self.centralwidget)
        self.stackDeleteButton.setObjectName(u"stackDeleteButton")

        self.horizontalLayout_2.addWidget(self.stackDeleteButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.phasorRoiMgrLabel = QLabel(self.centralwidget)
        self.phasorRoiMgrLabel.setObjectName(u"phasorRoiMgrLabel")

        self.verticalLayout_2.addWidget(self.phasorRoiMgrLabel)

        self.phasorRoiListWidget = QListWidget(self.centralwidget)
        self.phasorRoiListWidget.setObjectName(u"phasorRoiListWidget")

        self.verticalLayout_2.addWidget(self.phasorRoiListWidget)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.phasorRoiShapeLabel = QLabel(self.centralwidget)
        self.phasorRoiShapeLabel.setObjectName(u"phasorRoiShapeLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.phasorRoiShapeLabel.sizePolicy().hasHeightForWidth())
        self.phasorRoiShapeLabel.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.phasorRoiShapeLabel)

        self.phasorRoiShapeComboBox = QComboBox(self.centralwidget)
        self.phasorRoiShapeComboBox.addItem("")
        self.phasorRoiShapeComboBox.addItem("")
        self.phasorRoiShapeComboBox.addItem("")
        self.phasorRoiShapeComboBox.addItem("")
        self.phasorRoiShapeComboBox.setObjectName(u"phasorRoiShapeComboBox")

        self.horizontalLayout_3.addWidget(self.phasorRoiShapeComboBox)

        self.phasorRoiAddButton = QPushButton(self.centralwidget)
        self.phasorRoiAddButton.setObjectName(u"phasorRoiAddButton")

        self.horizontalLayout_3.addWidget(self.phasorRoiAddButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.phasorRoiRenameButton = QPushButton(self.centralwidget)
        self.phasorRoiRenameButton.setObjectName(u"phasorRoiRenameButton")

        self.horizontalLayout_4.addWidget(self.phasorRoiRenameButton)

        self.phasorRoiDeleteButton = QPushButton(self.centralwidget)
        self.phasorRoiDeleteButton.setObjectName(u"phasorRoiDeleteButton")

        self.horizontalLayout_4.addWidget(self.phasorRoiDeleteButton)

        self.phasorRoiConvertToMaskButton = QPushButton(self.centralwidget)
        self.phasorRoiConvertToMaskButton.setObjectName(u"phasorRoiConvertToMaskButton")

        self.horizontalLayout_4.addWidget(self.phasorRoiConvertToMaskButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.maskMgrLabel = QLabel(self.centralwidget)
        self.maskMgrLabel.setObjectName(u"maskMgrLabel")

        self.verticalLayout_2.addWidget(self.maskMgrLabel)

        self.maskListWidget = QListWidget(self.centralwidget)
        self.maskListWidget.setObjectName(u"maskListWidget")

        self.verticalLayout_2.addWidget(self.maskListWidget)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.maskReverseButton = QPushButton(self.centralwidget)
        self.maskReverseButton.setObjectName(u"maskReverseButton")

        self.horizontalLayout_5.addWidget(self.maskReverseButton)

        self.maskRenameButton = QPushButton(self.centralwidget)
        self.maskRenameButton.setObjectName(u"maskRenameButton")

        self.horizontalLayout_5.addWidget(self.maskRenameButton)

        self.maskDeleteButton = QPushButton(self.centralwidget)
        self.maskDeleteButton.setObjectName(u"maskDeleteButton")

        self.horizontalLayout_5.addWidget(self.maskDeleteButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_6.addLayout(self.verticalLayout_2)

        self.horizontalLayout_6.setStretch(0, 2)
        self.horizontalLayout_6.setStretch(1, 2)
        self.horizontalLayout_6.setStretch(2, 1)
        PhasorWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(PhasorWindow)
        self.statusbar.setObjectName(u"statusbar")
        PhasorWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(PhasorWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuExport = QMenu(self.menubar)
        self.menuExport.setObjectName(u"menuExport")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuCurve = QMenu(self.menubar)
        self.menuCurve.setObjectName(u"menuCurve")
        self.menuROI = QMenu(self.menubar)
        self.menuROI.setObjectName(u"menuROI")
        PhasorWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuROI.menuAction())
        self.menubar.addAction(self.menuCurve.menuAction())
        self.menubar.addAction(self.menuExport.menuAction())
        self.menuFile.addAction(self.actionOpenStack)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuExport.addAction(self.actionAbout)
        self.menuView.addAction(self.actionSavePhasorView)
        self.menuView.addAction(self.actionSaveView)
        self.menuCurve.addAction(self.actionNormalizeCurve)
        self.menuCurve.addAction(self.actionCurveFit)
        self.menuCurve.addSeparator()
        self.menuCurve.addAction(self.actionViewCurve)
        self.menuCurve.addAction(self.actionExportCurve)
        self.menuROI.addAction(self.actionEdit_ROI)
        self.menuROI.addAction(self.actionClear_All_ROI)

        self.retranslateUi(PhasorWindow)

        QMetaObject.connectSlotsByName(PhasorWindow)
    # setupUi

    def retranslateUi(self, PhasorWindow):
        PhasorWindow.setWindowTitle(QCoreApplication.translate("PhasorWindow", u"Phasor Window", None))
        self.actionOpenStack.setText(QCoreApplication.translate("PhasorWindow", u"Open Stack", None))
        self.actionNormalizeCurve.setText(QCoreApplication.translate("PhasorWindow", u"Normalize Curve", None))
        self.actionExit.setText(QCoreApplication.translate("PhasorWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("PhasorWindow", u"About", None))
        self.actionSaveView.setText(QCoreApplication.translate("PhasorWindow", u"Save View...", None))
        self.actionSavePhasorView.setText(QCoreApplication.translate("PhasorWindow", u"Save Phasor View...", None))
        self.actionViewCurve.setText(QCoreApplication.translate("PhasorWindow", u"View Curve...", None))
        self.actionExportCurve.setText(QCoreApplication.translate("PhasorWindow", u"Export Curve...", None))
        self.actionEdit_ROI.setText(QCoreApplication.translate("PhasorWindow", u"Edit ROI...", None))
        self.actionClear_All_ROI.setText(QCoreApplication.translate("PhasorWindow", u"Clear All ROI", None))
        self.actionCurveFit.setText(QCoreApplication.translate("PhasorWindow", u"Curve Fit...", None))
        self.Frequency.setText(QCoreApplication.translate("PhasorWindow", u"Frequency", None))
        self.stackMgrLabel.setText(QCoreApplication.translate("PhasorWindow", u"Multi Stack Manager", None))
        self.stackAddButton.setText(QCoreApplication.translate("PhasorWindow", u"Add", None))
        self.stackRenameButton.setText(QCoreApplication.translate("PhasorWindow", u"Rename", None))
        self.stackDeleteButton.setText(QCoreApplication.translate("PhasorWindow", u"Delete", None))
        self.phasorRoiMgrLabel.setText(QCoreApplication.translate("PhasorWindow", u"Phasor ROI Manager", None))
        self.phasorRoiShapeLabel.setText(QCoreApplication.translate("PhasorWindow", u"Shape:", None))
        self.phasorRoiShapeComboBox.setItemText(0, QCoreApplication.translate("PhasorWindow", u"Rectangle", None))
        self.phasorRoiShapeComboBox.setItemText(1, QCoreApplication.translate("PhasorWindow", u"Circle", None))
        self.phasorRoiShapeComboBox.setItemText(2, QCoreApplication.translate("PhasorWindow", u"Ellipse", None))
        self.phasorRoiShapeComboBox.setItemText(3, QCoreApplication.translate("PhasorWindow", u"Polygon", None))

        self.phasorRoiAddButton.setText(QCoreApplication.translate("PhasorWindow", u"Add", None))
        self.phasorRoiRenameButton.setText(QCoreApplication.translate("PhasorWindow", u"Rename", None))
        self.phasorRoiDeleteButton.setText(QCoreApplication.translate("PhasorWindow", u"Delete", None))
        self.phasorRoiConvertToMaskButton.setText(QCoreApplication.translate("PhasorWindow", u"Convert to Mask", None))
        self.maskMgrLabel.setText(QCoreApplication.translate("PhasorWindow", u"Mask Manager", None))
        self.maskReverseButton.setText(QCoreApplication.translate("PhasorWindow", u"Reverse", None))
        self.maskRenameButton.setText(QCoreApplication.translate("PhasorWindow", u"Rename", None))
        self.maskDeleteButton.setText(QCoreApplication.translate("PhasorWindow", u"Delete", None))
        self.menuFile.setTitle(QCoreApplication.translate("PhasorWindow", u"File", None))
        self.menuExport.setTitle(QCoreApplication.translate("PhasorWindow", u"Help", None))
        self.menuView.setTitle(QCoreApplication.translate("PhasorWindow", u"View", None))
        self.menuCurve.setTitle(QCoreApplication.translate("PhasorWindow", u"Curve", None))
        self.menuROI.setTitle(QCoreApplication.translate("PhasorWindow", u"ROI", None))
    # retranslateUi

