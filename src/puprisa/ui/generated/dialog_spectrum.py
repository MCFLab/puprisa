# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'spectrum_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QDialog, QHBoxLayout,
    QLabel, QPlainTextEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from puprisa.ui.widgets.mpl_canvas import MatplotlibFigureCanvas

class Ui_spectrumDialog(object):
    def setupUi(self, spectrumDialog):
        if not spectrumDialog.objectName():
            spectrumDialog.setObjectName(u"spectrumDialog")
        spectrumDialog.resize(500, 500)
        self.verticalLayout = QVBoxLayout(spectrumDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.fftButton = QRadioButton(spectrumDialog)
        self.calcTypeButtonGroup = QButtonGroup(spectrumDialog)
        self.calcTypeButtonGroup.setObjectName(u"calcTypeButtonGroup")
        self.calcTypeButtonGroup.addButton(self.fftButton)
        self.fftButton.setObjectName(u"fftButton")

        self.horizontalLayout_2.addWidget(self.fftButton)

        self.psdButton = QRadioButton(spectrumDialog)
        self.calcTypeButtonGroup.addButton(self.psdButton)
        self.psdButton.setObjectName(u"psdButton")

        self.horizontalLayout_2.addWidget(self.psdButton)

        self.rinButton = QRadioButton(spectrumDialog)
        self.calcTypeButtonGroup.addButton(self.rinButton)
        self.rinButton.setObjectName(u"rinButton")

        self.horizontalLayout_2.addWidget(self.rinButton)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.spectrumCanvas = MatplotlibFigureCanvas(spectrumDialog)
        self.spectrumCanvas.setObjectName(u"spectrumCanvas")
        self.spectrumCanvas.setMinimumSize(QSize(0, 300))

        self.verticalLayout.addWidget(self.spectrumCanvas)

        self.resultLabel = QLabel(spectrumDialog)
        self.resultLabel.setObjectName(u"resultLabel")

        self.verticalLayout.addWidget(self.resultLabel)

        self.resultText = QPlainTextEdit(spectrumDialog)
        self.resultText.setObjectName(u"resultText")
        self.resultText.setReadOnly(True)

        self.verticalLayout.addWidget(self.resultText)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.calculateButton = QPushButton(spectrumDialog)
        self.calculateButton.setObjectName(u"calculateButton")

        self.horizontalLayout.addWidget(self.calculateButton)

        self.viewButton = QPushButton(spectrumDialog)
        self.viewButton.setObjectName(u"viewButton")

        self.horizontalLayout.addWidget(self.viewButton)

        self.exportButton = QPushButton(spectrumDialog)
        self.exportButton.setObjectName(u"exportButton")

        self.horizontalLayout.addWidget(self.exportButton)

        self.exitButton = QPushButton(spectrumDialog)
        self.exitButton.setObjectName(u"exitButton")

        self.horizontalLayout.addWidget(self.exitButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(spectrumDialog)

        QMetaObject.connectSlotsByName(spectrumDialog)
    # setupUi

    def retranslateUi(self, spectrumDialog):
        spectrumDialog.setWindowTitle(QCoreApplication.translate("spectrumDialog", u"Spectrum", None))
        self.fftButton.setText(QCoreApplication.translate("spectrumDialog", u"FFT", None))
        self.psdButton.setText(QCoreApplication.translate("spectrumDialog", u"PSD", None))
        self.rinButton.setText(QCoreApplication.translate("spectrumDialog", u"RIN", None))
        self.resultLabel.setText(QCoreApplication.translate("spectrumDialog", u"Result", None))
        self.calculateButton.setText(QCoreApplication.translate("spectrumDialog", u"Calculate", None))
        self.viewButton.setText(QCoreApplication.translate("spectrumDialog", u"View", None))
        self.exportButton.setText(QCoreApplication.translate("spectrumDialog", u"Export", None))
        self.exitButton.setText(QCoreApplication.translate("spectrumDialog", u"Exit", None))
    # retranslateUi

