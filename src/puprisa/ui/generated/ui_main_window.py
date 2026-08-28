# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSlider,
    QSplitter, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

from puprisa.ui.widgets.mpl_canvas import MatplotlibFigureCanvas
from puprisa.ui.widgets.scrollable_graphics_view import ScrollableGraphicsView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 469)
        MainWindow.setTabShape(QTabWidget.TabShape.Rounded)
        self.actionOpenStack = QAction(MainWindow)
        self.actionOpenStack.setObjectName(u"actionOpenStack")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionStandardDeviation = QAction(MainWindow)
        self.actionStandardDeviation.setObjectName(u"actionStandardDeviation")
        self.actionFullRange = QAction(MainWindow)
        self.actionFullRange.setObjectName(u"actionFullRange")
        self.actionCustomRange = QAction(MainWindow)
        self.actionCustomRange.setObjectName(u"actionCustomRange")
        self.actionDefault = QAction(MainWindow)
        self.actionDefault.setObjectName(u"actionDefault")
        self.actionRdBuR = QAction(MainWindow)
        self.actionRdBuR.setObjectName(u"actionRdBuR")
        self.actionViridis = QAction(MainWindow)
        self.actionViridis.setObjectName(u"actionViridis")
        self.actionGray = QAction(MainWindow)
        self.actionGray.setObjectName(u"actionGray")
        self.actionSubNegativeTime = QAction(MainWindow)
        self.actionSubNegativeTime.setObjectName(u"actionSubNegativeTime")
        self.actionSubFirstLastNFrames = QAction(MainWindow)
        self.actionSubFirstLastNFrames.setObjectName(u"actionSubFirstLastNFrames")
        self.actionSaveStackTIFF = QAction(MainWindow)
        self.actionSaveStackTIFF.setObjectName(u"actionSaveStackTIFF")
        self.actionImportROI = QAction(MainWindow)
        self.actionImportROI.setObjectName(u"actionImportROI")
        self.actionExportROI = QAction(MainWindow)
        self.actionExportROI.setObjectName(u"actionExportROI")
        self.actionClearAllROI = QAction(MainWindow)
        self.actionClearAllROI.setObjectName(u"actionClearAllROI")
        self.actionImportMask = QAction(MainWindow)
        self.actionImportMask.setObjectName(u"actionImportMask")
        self.actionExportMask = QAction(MainWindow)
        self.actionExportMask.setObjectName(u"actionExportMask")
        self.actionClearAllMasks = QAction(MainWindow)
        self.actionClearAllMasks.setObjectName(u"actionClearAllMasks")
        self.actionCurveFit = QAction(MainWindow)
        self.actionCurveFit.setObjectName(u"actionCurveFit")
        self.actionExportCurve = QAction(MainWindow)
        self.actionExportCurve.setObjectName(u"actionExportCurve")
        self.actionSaveStackPickle = QAction(MainWindow)
        self.actionSaveStackPickle.setObjectName(u"actionSaveStackPickle")
        self.actionDownsample = QAction(MainWindow)
        self.actionDownsample.setObjectName(u"actionDownsample")
        self.actionMaskMath = QAction(MainWindow)
        self.actionMaskMath.setObjectName(u"actionMaskMath")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionPhasor = QAction(MainWindow)
        self.actionPhasor.setObjectName(u"actionPhasor")
        self.actionNormalizeCurve = QAction(MainWindow)
        self.actionNormalizeCurve.setObjectName(u"actionNormalizeCurve")
        self.actionNormalizeCurve.setCheckable(True)
        self.actionNormalizeCurve.setChecked(False)
        self.actionNoise = QAction(MainWindow)
        self.actionNoise.setObjectName(u"actionNoise")
        self.actionViewCurve = QAction(MainWindow)
        self.actionViewCurve.setObjectName(u"actionViewCurve")
        self.actionSaveView = QAction(MainWindow)
        self.actionSaveView.setObjectName(u"actionSaveView")
        self.actionResetBackgroundSubtraction = QAction(MainWindow)
        self.actionResetBackgroundSubtraction.setObjectName(u"actionResetBackgroundSubtraction")
        self.actionSubFixedValue = QAction(MainWindow)
        self.actionSubFixedValue.setObjectName(u"actionSubFixedValue")
        self.actionMaskAllZeroPixels = QAction(MainWindow)
        self.actionMaskAllZeroPixels.setObjectName(u"actionMaskAllZeroPixels")
        self.actionMaskIntensityThreshold = QAction(MainWindow)
        self.actionMaskIntensityThreshold.setObjectName(u"actionMaskIntensityThreshold")
        self.actionExportSelectedMask = QAction(MainWindow)
        self.actionExportSelectedMask.setObjectName(u"actionExportSelectedMask")
        self.actionStackMath = QAction(MainWindow)
        self.actionStackMath.setObjectName(u"actionStackMath")
        self.actionEditROI = QAction(MainWindow)
        self.actionEditROI.setObjectName(u"actionEditROI")
        self.actionSVDDenoise = QAction(MainWindow)
        self.actionSVDDenoise.setObjectName(u"actionSVDDenoise")
        self.actionStack_Slice = QAction(MainWindow)
        self.actionStack_Slice.setObjectName(u"actionStack_Slice")
        self.actionSlice = QAction(MainWindow)
        self.actionSlice.setObjectName(u"actionSlice")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_6 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.sliceViewVLayout = QVBoxLayout(self.layoutWidget)
        self.sliceViewVLayout.setObjectName(u"sliceViewVLayout")
        self.sliceViewVLayout.setContentsMargins(0, 0, 0, 0)
        self.ppsGraphicsView = ScrollableGraphicsView(self.layoutWidget)
        self.ppsGraphicsView.setObjectName(u"ppsGraphicsView")
        self.ppsGraphicsView.setMinimumSize(QSize(0, 0))
        self.ppsGraphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ppsGraphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.sliceViewVLayout.addWidget(self.ppsGraphicsView)

        self.colorbar = MatplotlibFigureCanvas(self.layoutWidget)
        self.colorbar.setObjectName(u"colorbar")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.colorbar.sizePolicy().hasHeightForWidth())
        self.colorbar.setSizePolicy(sizePolicy)
        self.colorbar.setMinimumSize(QSize(0, 40))
        self.colorbar.setMaximumSize(QSize(16777215, 80))

        self.sliceViewVLayout.addWidget(self.colorbar)

        self.sliderLayout = QHBoxLayout()
        self.sliderLayout.setObjectName(u"sliderLayout")
        self.sliceNumberLabel = QLabel(self.layoutWidget)
        self.sliceNumberLabel.setObjectName(u"sliceNumberLabel")

        self.sliderLayout.addWidget(self.sliceNumberLabel)

        self.sliceSlider = QSlider(self.layoutWidget)
        self.sliceSlider.setObjectName(u"sliceSlider")
        self.sliceSlider.setOrientation(Qt.Orientation.Horizontal)

        self.sliderLayout.addWidget(self.sliceSlider)

        self.axisLabel = QLabel(self.layoutWidget)
        self.axisLabel.setObjectName(u"axisLabel")

        self.sliderLayout.addWidget(self.axisLabel)


        self.sliceViewVLayout.addLayout(self.sliderLayout)

        self.splitter.addWidget(self.layoutWidget)
        self.plotCanvas = MatplotlibFigureCanvas(self.splitter)
        self.plotCanvas.setObjectName(u"plotCanvas")
        self.plotCanvas.setMinimumSize(QSize(0, 0))
        self.plotCanvas.setMaximumSize(QSize(16777215, 16777215))
        self.splitter.addWidget(self.plotCanvas)

        self.horizontalLayout_6.addWidget(self.splitter)

        self.managerVLayout = QVBoxLayout()
        self.managerVLayout.setObjectName(u"managerVLayout")
        self.stackMgrLabel = QLabel(self.centralwidget)
        self.stackMgrLabel.setObjectName(u"stackMgrLabel")

        self.managerVLayout.addWidget(self.stackMgrLabel)

        self.stackListWidget = QListWidget(self.centralwidget)
        self.stackListWidget.setObjectName(u"stackListWidget")

        self.managerVLayout.addWidget(self.stackListWidget)

        self.stackHLayout = QHBoxLayout()
        self.stackHLayout.setObjectName(u"stackHLayout")
        self.stackAddButton = QPushButton(self.centralwidget)
        self.stackAddButton.setObjectName(u"stackAddButton")

        self.stackHLayout.addWidget(self.stackAddButton)

        self.stackRenameButton = QPushButton(self.centralwidget)
        self.stackRenameButton.setObjectName(u"stackRenameButton")

        self.stackHLayout.addWidget(self.stackRenameButton)

        self.stackDeleteButton = QPushButton(self.centralwidget)
        self.stackDeleteButton.setObjectName(u"stackDeleteButton")

        self.stackHLayout.addWidget(self.stackDeleteButton)


        self.managerVLayout.addLayout(self.stackHLayout)

        self.roiMgrLabel = QLabel(self.centralwidget)
        self.roiMgrLabel.setObjectName(u"roiMgrLabel")

        self.managerVLayout.addWidget(self.roiMgrLabel)

        self.roiListWidget = QListWidget(self.centralwidget)
        self.roiListWidget.setObjectName(u"roiListWidget")

        self.managerVLayout.addWidget(self.roiListWidget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.roiShapeLabel = QLabel(self.centralwidget)
        self.roiShapeLabel.setObjectName(u"roiShapeLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.roiShapeLabel.sizePolicy().hasHeightForWidth())
        self.roiShapeLabel.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.roiShapeLabel)

        self.roiShapeComboBox = QComboBox(self.centralwidget)
        self.roiShapeComboBox.addItem("")
        self.roiShapeComboBox.addItem("")
        self.roiShapeComboBox.addItem("")
        self.roiShapeComboBox.addItem("")
        self.roiShapeComboBox.setObjectName(u"roiShapeComboBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.roiShapeComboBox.sizePolicy().hasHeightForWidth())
        self.roiShapeComboBox.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.roiShapeComboBox)

        self.roiAddButton = QPushButton(self.centralwidget)
        self.roiAddButton.setObjectName(u"roiAddButton")

        self.horizontalLayout_2.addWidget(self.roiAddButton)


        self.managerVLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")

        self.managerVLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.roiRenameButton = QPushButton(self.centralwidget)
        self.roiRenameButton.setObjectName(u"roiRenameButton")

        self.horizontalLayout_4.addWidget(self.roiRenameButton)

        self.roiDeleteButton = QPushButton(self.centralwidget)
        self.roiDeleteButton.setObjectName(u"roiDeleteButton")

        self.horizontalLayout_4.addWidget(self.roiDeleteButton)

        self.roiConvertToMaskButton = QPushButton(self.centralwidget)
        self.roiConvertToMaskButton.setObjectName(u"roiConvertToMaskButton")

        self.horizontalLayout_4.addWidget(self.roiConvertToMaskButton)


        self.managerVLayout.addLayout(self.horizontalLayout_4)

        self.maskMgrLabel = QLabel(self.centralwidget)
        self.maskMgrLabel.setObjectName(u"maskMgrLabel")

        self.managerVLayout.addWidget(self.maskMgrLabel)

        self.maskListWidget = QListWidget(self.centralwidget)
        self.maskListWidget.setObjectName(u"maskListWidget")

        self.managerVLayout.addWidget(self.maskListWidget)

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


        self.managerVLayout.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_6.addLayout(self.managerVLayout)

        self.horizontalLayout_6.setStretch(0, 3)
        self.horizontalLayout_6.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1000, 33))
        self.menubar.setDefaultUp(False)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuColorbarScale = QMenu(self.menuView)
        self.menuColorbarScale.setObjectName(u"menuColorbarScale")
        self.menuColormap = QMenu(self.menuView)
        self.menuColormap.setObjectName(u"menuColormap")
        self.menuProcess = QMenu(self.menubar)
        self.menuProcess.setObjectName(u"menuProcess")
        self.menuBackground_Subtraction = QMenu(self.menuProcess)
        self.menuBackground_Subtraction.setObjectName(u"menuBackground_Subtraction")
        self.menuROI = QMenu(self.menubar)
        self.menuROI.setObjectName(u"menuROI")
        self.menuMask = QMenu(self.menubar)
        self.menuMask.setObjectName(u"menuMask")
        self.menuPhasor = QMenu(self.menubar)
        self.menuPhasor.setObjectName(u"menuPhasor")
        self.menuNoise = QMenu(self.menubar)
        self.menuNoise.setObjectName(u"menuNoise")
        self.menuAbout = QMenu(self.menubar)
        self.menuAbout.setObjectName(u"menuAbout")
        self.menuCurve = QMenu(self.menubar)
        self.menuCurve.setObjectName(u"menuCurve")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuProcess.menuAction())
        self.menubar.addAction(self.menuROI.menuAction())
        self.menubar.addAction(self.menuMask.menuAction())
        self.menubar.addAction(self.menuCurve.menuAction())
        self.menubar.addAction(self.menuPhasor.menuAction())
        self.menubar.addAction(self.menuNoise.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.menuFile.addAction(self.actionOpenStack)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSaveStackTIFF)
        self.menuFile.addAction(self.actionSaveStackPickle)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuView.addAction(self.menuColormap.menuAction())
        self.menuView.addAction(self.menuColorbarScale.menuAction())
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionSaveView)
        self.menuColorbarScale.addAction(self.actionStandardDeviation)
        self.menuColorbarScale.addAction(self.actionFullRange)
        self.menuColorbarScale.addAction(self.actionCustomRange)
        self.menuColormap.addAction(self.actionDefault)
        self.menuColormap.addAction(self.actionRdBuR)
        self.menuColormap.addAction(self.actionViridis)
        self.menuColormap.addAction(self.actionGray)
        self.menuProcess.addAction(self.menuBackground_Subtraction.menuAction())
        self.menuProcess.addAction(self.actionDownsample)
        self.menuProcess.addAction(self.actionSlice)
        self.menuProcess.addAction(self.actionSVDDenoise)
        self.menuProcess.addAction(self.actionStackMath)
        self.menuBackground_Subtraction.addAction(self.actionSubNegativeTime)
        self.menuBackground_Subtraction.addAction(self.actionSubFirstLastNFrames)
        self.menuBackground_Subtraction.addAction(self.actionSubFixedValue)
        self.menuBackground_Subtraction.addSeparator()
        self.menuBackground_Subtraction.addAction(self.actionResetBackgroundSubtraction)
        self.menuROI.addAction(self.actionEditROI)
        self.menuROI.addAction(self.actionClearAllROI)
        self.menuMask.addAction(self.actionImportMask)
        self.menuMask.addAction(self.actionExportSelectedMask)
        self.menuMask.addAction(self.actionExportMask)
        self.menuMask.addSeparator()
        self.menuMask.addAction(self.actionMaskAllZeroPixels)
        self.menuMask.addAction(self.actionMaskIntensityThreshold)
        self.menuMask.addSeparator()
        self.menuMask.addAction(self.actionMaskMath)
        self.menuMask.addAction(self.actionClearAllMasks)
        self.menuPhasor.addAction(self.actionPhasor)
        self.menuNoise.addAction(self.actionNoise)
        self.menuAbout.addAction(self.actionAbout)
        self.menuCurve.addAction(self.actionNormalizeCurve)
        self.menuCurve.addAction(self.actionCurveFit)
        self.menuCurve.addSeparator()
        self.menuCurve.addAction(self.actionViewCurve)
        self.menuCurve.addAction(self.actionExportCurve)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpenStack.setText(QCoreApplication.translate("MainWindow", u"Open Stack", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionStandardDeviation.setText(QCoreApplication.translate("MainWindow", u"Standard Deviation", None))
        self.actionFullRange.setText(QCoreApplication.translate("MainWindow", u"Full Range", None))
        self.actionCustomRange.setText(QCoreApplication.translate("MainWindow", u"Custom Range...", None))
        self.actionDefault.setText(QCoreApplication.translate("MainWindow", u"Default", None))
        self.actionRdBuR.setText(QCoreApplication.translate("MainWindow", u"RdBu_r", None))
        self.actionViridis.setText(QCoreApplication.translate("MainWindow", u"Viridis", None))
        self.actionGray.setText(QCoreApplication.translate("MainWindow", u"Gray", None))
        self.actionSubNegativeTime.setText(QCoreApplication.translate("MainWindow", u"Subtract Negative Time Frames", None))
        self.actionSubFirstLastNFrames.setText(QCoreApplication.translate("MainWindow", u"Subtract First/Last N Frames...", None))
        self.actionSaveStackTIFF.setText(QCoreApplication.translate("MainWindow", u"Save Stack as TIFF", None))
        self.actionImportROI.setText(QCoreApplication.translate("MainWindow", u"Import ROI...", None))
        self.actionExportROI.setText(QCoreApplication.translate("MainWindow", u"Export ROI...", None))
        self.actionClearAllROI.setText(QCoreApplication.translate("MainWindow", u"Clear All ROI", None))
        self.actionImportMask.setText(QCoreApplication.translate("MainWindow", u"Import Mask...", None))
        self.actionExportMask.setText(QCoreApplication.translate("MainWindow", u"Export Mask...", None))
        self.actionClearAllMasks.setText(QCoreApplication.translate("MainWindow", u"Clear All Masks", None))
        self.actionCurveFit.setText(QCoreApplication.translate("MainWindow", u"Curve Fit...", None))
        self.actionExportCurve.setText(QCoreApplication.translate("MainWindow", u"Export Curve...", None))
        self.actionSaveStackPickle.setText(QCoreApplication.translate("MainWindow", u"Save Stack as Pickle", None))
        self.actionDownsample.setText(QCoreApplication.translate("MainWindow", u"Downsample...", None))
        self.actionMaskMath.setText(QCoreApplication.translate("MainWindow", u"Mask Math...", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionPhasor.setText(QCoreApplication.translate("MainWindow", u"Phasor Analysis", None))
        self.actionNormalizeCurve.setText(QCoreApplication.translate("MainWindow", u"Normalize Curve", None))
        self.actionNoise.setText(QCoreApplication.translate("MainWindow", u"Noise Analysis", None))
        self.actionViewCurve.setText(QCoreApplication.translate("MainWindow", u"View Curve...", None))
        self.actionSaveView.setText(QCoreApplication.translate("MainWindow", u"Save View...", None))
        self.actionResetBackgroundSubtraction.setText(QCoreApplication.translate("MainWindow", u"Reset Background Subtraction", None))
        self.actionSubFixedValue.setText(QCoreApplication.translate("MainWindow", u"Subtract Fixed Value", None))
        self.actionMaskAllZeroPixels.setText(QCoreApplication.translate("MainWindow", u"Mask all-zero pixels", None))
        self.actionMaskIntensityThreshold.setText(QCoreApplication.translate("MainWindow", u"Mask from threshold...", None))
        self.actionExportSelectedMask.setText(QCoreApplication.translate("MainWindow", u"Export Selected Mask...", None))
        self.actionStackMath.setText(QCoreApplication.translate("MainWindow", u"Stack Math...", None))
        self.actionEditROI.setText(QCoreApplication.translate("MainWindow", u"Edit ROI...", None))
        self.actionSVDDenoise.setText(QCoreApplication.translate("MainWindow", u"SVD Denoise...", None))
        self.actionStack_Slice.setText(QCoreApplication.translate("MainWindow", u"Slice Stack...", None))
        self.actionSlice.setText(QCoreApplication.translate("MainWindow", u"Slice...", None))
        self.sliceNumberLabel.setText(QCoreApplication.translate("MainWindow", u"Slice", None))
        self.axisLabel.setText(QCoreApplication.translate("MainWindow", u"AxisLabel", None))
        self.stackMgrLabel.setText(QCoreApplication.translate("MainWindow", u"Multi Stack Manager", None))
        self.stackAddButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.stackRenameButton.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
        self.stackDeleteButton.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.roiMgrLabel.setText(QCoreApplication.translate("MainWindow", u"ROI Manager", None))
        self.roiShapeLabel.setText(QCoreApplication.translate("MainWindow", u"Shape:", None))
        self.roiShapeComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Rectangle", None))
        self.roiShapeComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Circle", None))
        self.roiShapeComboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"Ellipse", None))
        self.roiShapeComboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"Polygon", None))

        self.roiAddButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.roiRenameButton.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
        self.roiDeleteButton.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.roiConvertToMaskButton.setText(QCoreApplication.translate("MainWindow", u"Convert to Mask", None))
        self.maskMgrLabel.setText(QCoreApplication.translate("MainWindow", u"Mask Manager", None))
        self.maskReverseButton.setText(QCoreApplication.translate("MainWindow", u"Reverse", None))
        self.maskRenameButton.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
        self.maskDeleteButton.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuColorbarScale.setTitle(QCoreApplication.translate("MainWindow", u"Colorbar Scale", None))
        self.menuColormap.setTitle(QCoreApplication.translate("MainWindow", u"Colormap", None))
        self.menuProcess.setTitle(QCoreApplication.translate("MainWindow", u"Process", None))
        self.menuBackground_Subtraction.setTitle(QCoreApplication.translate("MainWindow", u"Background Subtraction", None))
        self.menuROI.setTitle(QCoreApplication.translate("MainWindow", u"ROI", None))
        self.menuMask.setTitle(QCoreApplication.translate("MainWindow", u"Mask", None))
        self.menuPhasor.setTitle(QCoreApplication.translate("MainWindow", u"Phasor", None))
        self.menuNoise.setTitle(QCoreApplication.translate("MainWindow", u"Noise", None))
        self.menuAbout.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuCurve.setTitle(QCoreApplication.translate("MainWindow", u"Curve", None))
    # retranslateUi

