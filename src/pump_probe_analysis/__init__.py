"""Pump-probe spectroscopy analysis (PPS) and optional Qt GUI."""

from importlib.metadata import version, PackageNotFoundError

from pump_probe_analysis.pps import PPS

try:
    __version__ = version("pump-probe-analysis")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["PPS", "__version__"]
