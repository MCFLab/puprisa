# puprisa/utils/color_utils.py
from PySide6.QtGui import QColor
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# MATLAB default color order (R2014b+)
MATLAB_COLORS = [
    '#0072BE',  # blue
    '#DA5319',  # orange
    '#EEB220',  # yellow
    '#7E2F8E',  # purple
    '#77AD30',  # green
    '#4DBFEF',  # light blue
    '#A3142F',  # red
]

PHASOR_COLORS = [
    '#023eff',  # blue
    '#ff7c00',  # orange
    '#ffc400',  # yellow
    '#8b2be2',  # purple
    '#1ac938',  # green
    '#00d7ff',  # cyan
    '#e8000b',  # red
 ]

def default_cmap():
    """Return the custom 'pumpprobe' colormap."""
    colors = [
        (0.0,   (0.0, 1.0, 1.0)),   # cyan
        (0.25,  (0.0, 0.0, 1.0)),   # blue
        (0.5,   (0.0, 0.0, 0.0)),   # black
        (0.75,  (1.0, 0.0, 0.0)),   # red
        (1.0,   (1.0, 1.0, 0.0)),   # yellow
    ]
    return mcolors.LinearSegmentedColormap.from_list("pumpprobe", colors)

matplotlib.colormaps.register(default_cmap(), name="pumpprobe")

def _matplotlib_color_to_qt(color_spec):
    """Convert matplotlib color (hex string or tuple) to QColor."""
    if isinstance(color_spec, QColor):
        return color_spec
    if isinstance(color_spec, str) and color_spec.startswith('#'):
        return QColor(color_spec)
    try:
        hex_color = mcolors.to_hex(color_spec)
        return QColor(hex_color)
    except (ValueError, TypeError):
        return QColor('#1f77b4')


def apply_colormap(
    data: np.ndarray,
    vmin: float | None = None,
    vmax: float | None = None,
    cmap: str = 'pumpprobe'
) -> tuple[np.ndarray, float, float]:
    """Apply a colormap to the data and return an RGB image.

    Args:
        data: Input data array to colormap.
        vmin: Minimum value for normalization. If None, uses minimum of data.
        vmax: Maximum value for normalization. If None, uses maximum of data.
        cmap: Colormap name ('pumpprobe', 'rdbu_r', 'viridis', 'gray'). Defaults to 'pumpprobe'.

    Returns:
        tuple: (rgb_image, vmin_used, vmax_used) where rgb_image is uint8 RGB array,
               vmin_used and vmax_used are the actual min/max values used for normalization.
    """
    data = np.asarray(data, dtype=np.float64)
    if vmin is None:
        vmin = np.nanmin(data)
    if vmax is None:
        vmax = np.nanmax(data)
    if vmax <= vmin:
        vmax = vmin + 1.0

    if cmap.lower() == 'pumpprobe':
        cm_obj = default_cmap()
        abs_max = max(abs(vmin), abs(vmax))
        vmin_used, vmax_used = -abs_max, abs_max
    elif cmap.lower() == 'rdbu_r':
        cm_obj = plt.cm.RdBu_r
        abs_max = max(abs(vmin), abs(vmax))
        vmin_used, vmax_used = -abs_max, abs_max
    elif cmap.lower() == 'viridis':
        cm_obj = plt.cm.viridis
        vmin_used, vmax_used = vmin, vmax
    elif cmap.lower() == 'gray':
        cm_obj = plt.cm.gray
        vmin_used, vmax_used = vmin, vmax
    else:
        cm_obj = default_cmap()
        abs_max = max(abs(vmin), abs(vmax))
        vmin_used, vmax_used = -abs_max, abs_max

    normalized = np.clip((data - vmin_used) / (vmax_used - vmin_used), 0.0, 1.0)
    rgba = cm_obj(normalized)
    rgb_image = (rgba[..., :3] * 255).astype(np.uint8)
    return rgb_image, vmin_used, vmax_used