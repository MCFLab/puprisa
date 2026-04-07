#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
puprisa_gui.py
Pump-Probe Image Stack Analysis GUI entry point.

Launches the channel view as the main window. Use File → Open Stack to load data.

Created: 2025
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from pump_probe_analysis.puprisa_channel_view import PuprisaChannelViewWindow


def puprisa(filename=None):
    """
    Start the GUI: a single channel-view window (optional path to load on startup).

    Parameters
    ----------
    filename : str, optional
        Path to a stack file; format is auto-detected (DukeScan TIFF, pickle, etc.).

    Returns
    -------
    QApplication
        The Qt application instance.
    """
    app = QApplication(sys.argv)
    win = PuprisaChannelViewWindow(pps_obj=None)
    win.show()
    if filename:
        win.load_stack_from_path(str(filename))
    return app


def main():
    """Run PUPRISA: ``python -m pump_probe_analysis`` or ``pump-probe-gui``."""
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    app = puprisa(filename)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
