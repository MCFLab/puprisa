#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
puprisa_gui.py
Pump-Probe Image Stack Analysis GUI entry point.

Launches the channel view as the main window. Use File → Open Stack to load data.
Use File → New window for another independent viewer in the same process.

Created: 2025
"""

import sys

from PySide6.QtWidgets import QApplication

from pump_probe_analysis.puprisa_channel_view import PuprisaChannelViewWindow


def get_or_create_qapplication():
    """Return the singleton QApplication, creating it if this process has none."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def open_channel_view(filename=None):
    """
    Create and show a channel-view window in the current process.

    Closing one window only closes that window; when the last window closes,
    Qt quits the application by default (quitOnLastWindowClosed).

    Parameters
    ----------
    filename : str, optional
        Path to a stack file; format is auto-detected (DukeScan TIFF, pickle, etc.).

    Returns
    -------
    PuprisaChannelViewWindow
        The new window.
    """
    get_or_create_qapplication()
    win = PuprisaChannelViewWindow(pps_obj=None)
    win.show()
    if filename:
        win.load_stack_from_path(str(filename))
    return win


def puprisa(filename=None):
    """
    Start the GUI: a channel-view window (optional path to load on startup).

    Parameters
    ----------
    filename : str, optional
        Path to a stack file; format is auto-detected (DukeScan TIFF, pickle, etc.).

    Returns
    -------
    QApplication
        The Qt application instance.
    """
    open_channel_view(filename)
    return get_or_create_qapplication()


def main():
    """Run PUPRISA: ``python -m pump_probe_analysis`` or ``pump-probe-gui``."""
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    app = puprisa(filename)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
