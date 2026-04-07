#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
puprisa_gui.py
Pump-Probe Image Stack Analysis GUI

Python port of puprisa.m MATLAB GUI
Jesse Wilson (2011) syrex314@gmail.com
Martin Fischer (2021) Martin.Fischer@duke.edu
Duke University

A visualization tool for pump-probe delay or Z-stacks of images.
Shows one slice at a time, and allows user to view the time delay trace
associated with a selected pixel in the slice. Also allows user to change
the currently viewed slice.

Created: 2025
"""

import sys
import os
from pathlib import Path
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QMenuBar, QStatusBar, QTextEdit, QFileDialog, QMessageBox,
    QApplication
)
from PySide6.QtCore import Qt, QSize
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pump_probe_analysis.pps import PPS
from pump_probe_analysis.puprisa_channel_view import PuprisaChannelViewWindow


class PuprisaMainWindow(QMainWindow):
    """
    Main window for PUPRISA GUI.
    Replicates functionality of puprisa.m MATLAB GUI.
    """
    
    def __init__(self, filename=None):
        super().__init__()
        
        # Window properties
        self.setWindowTitle('puprisa')
        self.setMinimumSize(800, 600)
        
        # Application data
        self.fileName = None
        self.nChannels = 0
        self.nSlices = 0
        self.currentSlice = 1
        # Store PPS objects (one per channel) instead of raw arrays
        self.ppsChannels = []  # List of PPS objects, one per channel
        self.fileHeader = {}
        self.stackType = None
        self.delays = []
        self.xPos = []
        self.yPos = []
        self.zPos = []
        self.yAxisOrientation = 'normal'  # 'normal' or 'reverse'
        
        # Channel layout: 2x2 grid
        self.nChanRow = 2
        self.nChanCol = 2
        self.maxNChannels = self.nChanRow * self.nChanCol
        
        # Initialize UI
        self.initUI()
        
        # Load file if provided
        if filename:
            self.loadData(filename)
    
    def initUI(self):
        """Initialize the user interface."""
        # Create central widget
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        # Main layout
        mainLayout = QVBoxLayout(centralWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        
        # Create channel display area
        self.channelWidget = QWidget()
        self.channelLayout = QGridLayout(self.channelWidget)
        self.channelLayout.setContentsMargins(5, 5, 5, 5)
        self.channelLayout.setSpacing(5)
        
        # Create matplotlib figures for each channel
        self.channelFigures = []
        self.channelCanvases = []
        self.channelAxes = []
        
        # Track open channel view windows to prevent garbage collection
        self.channelWindows = []
        
        for iChannel in range(self.maxNChannels):
            # Create figure
            fig = Figure(figsize=(4, 4))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.set_title(f'Channel {iChannel + 1}')
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Store references
            self.channelFigures.append(fig)
            self.channelCanvases.append(canvas)
            self.channelAxes.append(ax)
            
            # Add to grid (row, col)
            row = iChannel // self.nChanCol
            col = iChannel % self.nChanCol
            self.channelLayout.addWidget(canvas, row, col)
            
            # Connect click event to open channel view
            # Store channel index in canvas for callback
            canvas.channel_index = iChannel
            canvas.mpl_connect('button_press_event', self._makeChannelClickHandler(iChannel))
        
        # Add channel widget to main layout
        mainLayout.addWidget(self.channelWidget)
        
        # Create bottom panel with status bar and header text
        bottomPanel = QWidget()
        bottomLayout = QHBoxLayout(bottomPanel)
        bottomLayout.setContentsMargins(0, 0, 0, 0)
        bottomLayout.setSpacing(0)
        
        # Status bar (left side)
        self.statusBar = QStatusBar()
        self.statusBar.showMessage('puprisa ready.')
        bottomLayout.addWidget(self.statusBar, 1)
        
        # Header text (right side, 200px wide)
        self.headerText = QTextEdit()
        self.headerText.setMaximumWidth(200)
        self.headerText.setReadOnly(True)
        self.headerText.setPlainText('No File Opened')
        bottomLayout.addWidget(self.headerText)
        
        mainLayout.addWidget(bottomPanel)
        
        # Create menu bar
        self.initMenus()
        
        # Update status
        self.updateStatus('puprisa ready.')
    
    def _makeChannelClickHandler(self, channel):
        """Create a click handler function for a specific channel."""
        def handler(event):
            self.onChannelClick(event, channel)
        return handler
    
    def initMenus(self):
        """Initialize menu bar."""
        menubar = self.menuBar()
        
        # ImageAnalysis menu
        imageMenu = menubar.addMenu('ImageAnalysis')
        
        openAction = imageMenu.addAction('Open Image Stack...')
        openAction.triggered.connect(self.mnuOpenImageStack)
        
        
        imageMenu.addSeparator()
        
        aboutAction = imageMenu.addAction('About puprisa')
        aboutAction.triggered.connect(self.mnuAbout)
        
    
    def onChannelClick(self, event, channel):
        """Handle click on channel to open channel view window."""
        # Only respond to clicks on the axes (not outside the plot area)
        if event.inaxes is None:
            return
        
        # Only respond to left mouse button clicks
        if event.button != 1:
            return
        
        # Check if this channel has data loaded
        if channel >= len(self.ppsChannels) or len(self.ppsChannels) == 0:
            print(f"Channel {channel} not available (have {len(self.ppsChannels)} channels)")
            return
        
        # Open channel view window
        pps_obj = self.ppsChannels[channel]
        if pps_obj is None or len(pps_obj.images) == 0:
            QMessageBox.warning(
                self,
                'Channel View',
                f'Channel {channel + 1} has no data loaded.'
            )
            return
        
        print(f"Opening channel view for channel {channel + 1}")
        try:
            channelWindow = PuprisaChannelViewWindow(
                pps_obj, 
                channel_num=channel + 1,
                fileName=self.fileName,
                header=self.fileHeader
            )
            # Store reference to prevent garbage collection
            self.channelWindows.append(channelWindow)
            # Show and raise window to front
            channelWindow.show()
            channelWindow.raise_()
            channelWindow.activateWindow()
            print(f"Channel view window created and shown for channel {channel + 1}")
        except Exception as e:
            print(f"Error creating channel view window: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to open channel view:\n{str(e)}'
            )
    
    def mnuAbout(self):
        """Show About dialog."""
        QMessageBox.about(
            self,
            'About PUPRISA',
            'PUPRISA: PUmp PRobe Image Stack Analysis.\n'
            'Warren Lab: Duke University.\n'
            'Created 2011 by J. W. Wilson.\n'
            'Contributions by P. Samineni, M.J. Simpson, M.C. Fischer\n\n'
            'Python port created 2025'
        )
    
    def mnuOpenImageStack(self):
        """Open file dialog to select image stack."""
        # Get last working directory from preferences (or use current)
        # For now, use current directory
        wd = os.getcwd()
        
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            'Select a DukeScan Image Stack',
            wd,
            'DukeScan Files (*_DS_CH*.tif);;All Files (*)'
        )
        
        if fileName:
            self.loadData(fileName)
    
    
    def getPPS(self, channel=0):
        """
        Get PPS object for a specific channel.
        
        Parameters
        ----------
        channel : int, optional
            Channel index (0-based). Default is 0.
        
        Returns
        -------
        PPS or None
            The PPS object for the specified channel, or None if invalid.
        """
        if 0 <= channel < len(self.ppsChannels):
            return self.ppsChannels[channel]
        return None
    
    def getAllPPS(self):
        """
        Get all PPS objects.
        
        Returns
        -------
        list of PPS
            List of all PPS objects (one per channel).
        """
        return self.ppsChannels
    
    def applyToAllChannels(self, method_name, *args, **kwargs):
        """
        Apply a PPS method to all channels.
        
        Parameters
        ----------
        method_name : str
            Name of the PPS method to call.
        *args, **kwargs
            Arguments to pass to the PPS method.
        
        Returns
        -------
        list
            List of return values from each channel's method call.
        """
        results = []
        for pps_obj in self.ppsChannels:
            method = getattr(pps_obj, method_name, None)
            if method and callable(method):
                result = method(*args, **kwargs)
                results.append(result)
            else:
                results.append(None)
        # Update display after applying changes
        self.updateAll()
        return results
    
    def applyToChannel(self, channel, method_name, *args, **kwargs):
        """
        Apply a PPS method to a specific channel.
        
        Parameters
        ----------
        channel : int
            Channel index (0-based).
        method_name : str
            Name of the PPS method to call.
        *args, **kwargs
            Arguments to pass to the PPS method.
        
        Returns
        -------
        object or None
            Return value from the PPS method, or None if invalid.
        """
        pps_obj = self.getPPS(channel)
        if pps_obj:
            method = getattr(pps_obj, method_name, None)
            if method and callable(method):
                result = method(*args, **kwargs)
                self.updateAll()
                return result
        return None
    
    def loadData(self, fileName):
        """Load DukeScan format image stack and create PPS objects."""
        self.fileName = fileName
        
        # Set cursor to wait
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        
        try:
            fileName_str = str(fileName)
            
            # Check if this is a DukeScan format file
            if not (fileName_str.endswith('_DS_CH1.tif') or fileName_str.endswith('_DS_CH2.tif') or 
                    fileName_str.endswith('_DS_CH3.tif') or fileName_str.endswith('_DS_CH4.tif')):
                QApplication.restoreOverrideCursor()
                QMessageBox.warning(
                    self, 
                    'Load Error', 
                    'Only DukeScan format files (*_DS_CH*.tif) are supported.\n'
                    'Please select a file ending with _DS_CH1.tif, _DS_CH2.tif, etc.'
                )
                return
            
            # Load using PPS DukeScan format
            self._loadDukeScanFormat(fileName_str)
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, 'Load Error', f'Error loading file:\n{str(e)}')
        
        finally:
            QApplication.restoreOverrideCursor()
    
    def _loadDukeScanFormat(self, fileName):
        """Load DukeScan format file directly using PPS class."""
        # Check for multi-channel files
        base_name = fileName.replace('_DS_CH1.tif', '').replace('_DS_CH2.tif', '').replace('_DS_CH3.tif', '').replace('_DS_CH4.tif', '')
        
        self.ppsChannels = []
        channel_num = 1
        
        # Try to load channels sequentially
        while channel_num <= 4:
            ch_file = f"{base_name}_DS_CH{channel_num}.tif"
            if not os.path.exists(ch_file):
                break
            
            # Load using PPS DukeScan format
            pps_obj = PPS(ch_file, dataType="DukeScan")
            self.ppsChannels.append(pps_obj)
            channel_num += 1
        
        if len(self.ppsChannels) == 0:
            raise FileNotFoundError(f"Could not find any channel files starting with {base_name}_DS_CH")
        
        self.nChannels = len(self.ppsChannels)
        # Use first channel to get slice count (all channels should have same number)
        self.nSlices = len(self.ppsChannels[0].images)
        
        # Extract delays from first channel
        times = self.ppsChannels[0].times
        if hasattr(times, 'tolist'):
            self.delays = times.tolist()
        elif isinstance(times, (list, np.ndarray)):
            self.delays = list(times)
        else:
            # Fallback: create sequential delays if times is empty or invalid
            self.delays = list(range(self.nSlices))
        
        # Create header (stacks are assumed DukeScan TIFF layout; no imageOrigin key)
        self.fileHeader = {
            "fullHeaderText": (
                f"DukeScan Stack: {Path(fileName).name}\n"
                f"Slices: {self.nSlices}\n"
                f"Channels: {self.nChannels}\n"
                f"Dimensions: {self.ppsChannels[0].image_dimensions[0]} x {self.ppsChannels[0].image_dimensions[1]}"
            ),
            "nSlices": self.nSlices,
            "numofchannels": self.nChannels,
        }
        
        # Determine stack type
        self.determineStackType()
        
        # Match vertical image convention (same as former imageOrigin == top_left)
        self.yAxisOrientation = 'reverse'
        
        # Set default slice
        self.currentSlice = 1
        
        # Update display
        self.updateAll()
    
    def determineStackType(self):
        """Determine if stack is delay stack, z stack, or mosaic."""
        header = self.fileHeader
        
        # Check for mosaic
        if 'mosaic' in header and header['mosaic'] == 1:
            self.stackType = 'mosaic'
            return
        
        # Check scan axis
        if 'scanaxis' in header:
            isZStack = header['scanaxis']
        elif 'variableaxisZt' in header:
            isZStack = 1 - header['variableaxisZt']
        else:
            # Default to delay stack
            self.stackType = 'delay stack'
            return
        
        if isZStack:
            self.stackType = 'z stack'
        else:
            self.stackType = 'delay stack'
    
    def updateStatus(self, message):
        """Update status bar message."""
        self.statusBar.showMessage(message)
        QApplication.processEvents()
    
    def updateAll(self):
        """Update all channel displays with projections using PPS objects."""
        if self.nSlices == 0 or len(self.ppsChannels) == 0:
            return
        
        # Update each channel
        for iChannel in range(min(self.nChannels, self.maxNChannels)):
            if iChannel < len(self.ppsChannels):
                # Get projection from PPS object using project() method
                pps_obj = self.ppsChannels[iChannel]
                projection = pps_obj.project(maskOn=True)
                
                # Clear and update axes
                ax = self.channelAxes[iChannel]
                ax.clear()
                # Use interpolation='nearest' for pixel-perfect display
                # Set origin based on y-axis orientation
                # 'normal' = origin at bottom (like plots), 'reverse' = origin at top (like images)
                origin = 'lower' if self.yAxisOrientation == 'normal' else 'upper'
                ax.imshow(projection, cmap='gray', aspect='equal', interpolation='nearest', 
                         origin=origin)
                ax.set_title(f'Channel {iChannel + 1} Projection')
                ax.set_xticks([])
                ax.set_yticks([])
                
                # Refresh canvas
                self.channelCanvases[iChannel].draw()
        
        # Update status bar
        if self.fileName:
            fileName = Path(self.fileName).name
            self.updateStatus(f'{fileName}: showing projections ({self.nSlices} slices)')
        
        # Update header text
        if self.fileHeader and 'fullHeaderText' in self.fileHeader:
            self.headerText.setPlainText(self.fileHeader['fullHeaderText'])


def puprisa(filename=None):
    """
    Main entry point for PUPRISA GUI.
    
    Parameters
    ----------
    filename : str, optional
        Path to image stack file to load on startup.
    
    Returns
    -------
    QApplication
        The Qt application instance.
    """
    app = QApplication(sys.argv)
    
    window = PuprisaMainWindow(filename)
    window.show()
    
    return app


def main():
    """Main function to run PUPRISA GUI."""
    import sys
    
    # Check if filename provided as command line argument
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    
    app = puprisa(filename)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
