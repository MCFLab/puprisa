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
    QSizePolicy, QSlider, QSplitter, QStatusBar,
    QVBoxLayout, QWidget)

from puprisa.ui.widgets.mpl_canvas import MatplotlibFigureCanvas
from puprisa.ui.widgets.scrollable_graphics_view import ScrollableGraphicsView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 500)
        self.actionOpenStack = QAction(MainWindow)
        self.actionOpenStack.setObjectName(u"actionOpenStack")
        self.actionNormalizeCurve = QAction(MainWindow)
        self.actionNormalizeCurve.setObjectName(u"actionNormalizeCurve")
        self.actionNormalizeCurve.setCheckable(True)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionSaveView = QAction(MainWindow)
        self.actionSaveView.setObjectName(u"actionSaveView")
        self.actionSavePhasorView = QAction(MainWindow)
        self.actionSavePhasorView.setObjectName(u"actionSavePhasorView")
        self.actionViewCurve = QAction(MainWindow)
        self.actionViewCurve.setObjectName(u"actionViewCurve")
        self.actionExportCurve = QAction(MainWindow)
        self.actionExportCurve.setObjectName(u"actionExportCurve")
        self.centralwidget = QWidget(MainWindow)
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

        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.plotCanvas = MatplotlibFigureCanvas(self.splitter)
        self.plotCanvas.setObjectName(u"plotCanvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotCanvas.sizePolicy().hasHeightForWidth())
        self.plotCanvas.setSizePolicy(sizePolicy)
        self.splitter.addWidget(self.plotCanvas)
        self.ppsGraphicsView = QGraphicsView(self.splitter)
        self.ppsGraphicsView.setObjectName(u"ppsGraphicsView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ppsGraphicsView.sizePolicy().hasHeightForWidth())
        self.ppsGraphicsView.setSizePolicy(sizePolicy1)
        self.splitter.addWidget(self.ppsGraphicsView)

        self.horizontalLayout_6.addWidget(self.splitter)

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
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
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
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuCurve.menuAction())
        self.menubar.addAction(self.menuExport.menuAction())
        self.menuFile.addAction(self.actionOpenStack)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuExport.addAction(self.actionAbout)
        self.menuView.addAction(self.actionSavePhasorView)
        self.menuView.addAction(self.actionSaveView)
        self.menuCurve.addAction(self.actionNormalizeCurve)
        self.menuCurve.addSeparator()
        self.menuCurve.addAction(self.actionViewCurve)
        self.menuCurve.addAction(self.actionExportCurve)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpenStack.setText(QCoreApplication.translate("MainWindow", u"Open Stack", None))
        self.actionNormalizeCurve.setText(QCoreApplication.translate("MainWindow", u"Normalize Curve", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionSaveView.setText(QCoreApplication.translate("MainWindow", u"Save View...", None))
        self.actionSavePhasorView.setText(QCoreApplication.translate("MainWindow", u"Save Phasor View...", None))
        self.actionViewCurve.setText(QCoreApplication.translate("MainWindow", u"View Curve...", None))
        self.actionExportCurve.setText(QCoreApplication.translate("MainWindow", u"Export Curve...", None))
        self.Frequency.setText(QCoreApplication.translate("MainWindow", u"Frequency", None))
        self.stackMgrLabel.setText(QCoreApplication.translate("MainWindow", u"Multi Stack Manager", None))
        self.stackAddButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.stackRenameButton.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
        self.stackDeleteButton.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.phasorRoiMgrLabel.setText(QCoreApplication.translate("MainWindow", u"Phasor ROI Manager", None))
        self.phasorRoiShapeLabel.setText(QCoreApplication.translate("MainWindow", u"Shape:", None))
        self.phasorRoiShapeComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Rectangle", None))
        self.phasorRoiShapeComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Circle", None))
        self.phasorRoiShapeComboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"Ellipse", None))
        self.phasorRoiShapeComboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"Polygon", None))

        self.phasorRoiAddButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.phasorRoiRenameButton.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
        self.phasorRoiDeleteButton.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.phasorRoiConvertToMaskButton.setText(QCoreApplication.translate("MainWindow", u"Convert to Mask", None))
        self.maskMgrLabel.setText(QCoreApplication.translate("MainWindow", u"Mask Manager", None))
        self.maskReverseButton.setText(QCoreApplication.translate("MainWindow", u"Reverse", None))
        self.maskRenameButton.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
        self.maskDeleteButton.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuExport.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuCurve.setTitle(QCoreApplication.translate("MainWindow", u"Curve", None))
    # retranslateUi

