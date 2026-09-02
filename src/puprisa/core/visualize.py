"""Pure rendering helpers for pump-probe stacks.

This module is intentionally free of Qt and application UI dependencies.
It works directly with :class:`~puprisa.core.pps.PPS` instances and plain
NumPy arrays so it can be reused by GUI layers and standalone scripts.

All functions follow the same conventions:

* Image-like arrays are returned as contiguous ``np.uint8`` arrays.
* RGB images have shape ``(height, width, 3)``; RGBA images have shape
  ``(height, width, 4)``.
* Colors are specified either as Matplotlib color names/hex strings or
  as ``(R, G, B)`` tuples with values in the 0-255 range.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.axes import Axes
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from puprisa.core.pps import PPS
from puprisa.utils.color_utils import apply_colormap


# ------------------------------------------------------------------
# Render / Plot stack slice
# ------------------------------------------------------------------
def render_slice_rgb(
    pps: PPS,
    slice_index: int,
    colormap: str = "pumpprobe",
    vmin: float | None = None,
    vmax: float | None = None,
    mask_color: tuple[int, int, int] = (200, 200, 200),
) -> np.ndarray:
    """Render a single frame of a PPS stack as a uint8 RGB image.

    The frame is color-mapped with :func:`apply_colormap`, then every
    pixel excluded by the effective mask of ``pps`` is replaced by
    ``mask_color``. This is the core image-generation routine used by
    both graphical views and exported figures.

    Parameters
    ----------
    pps : PPS
        The stack from which to render a frame.
    slice_index : int
        Index of the frame in ``pps.images`` to render.
    colormap : str, default "pumpprobe"
        Matplotlib colormap name passed to :func:`apply_colormap`.
    vmin, vmax : float or None, optional
        Lower/upper color scale bounds. When either is ``None``, the
        corresponding bound is inferred from the data by
        :func:`apply_colormap`.
    mask_color : tuple[int, int, int], default gray (200, 200, 200)
        RGB color (0-255) applied to pixels where ``pps.mask`` is False.

    Returns
    -------
    np.ndarray
        Contiguous array of shape ``(height, width, 3)`` and dtype
        ``np.uint8``. The last axis is ordered as red, green, blue.

    Notes
    -----
    The returned array is suitable for immediate display with
    ``matplotlib.axes.Axes.imshow`` or conversion to a QImage.
    """

    image = pps.images[slice_index]
    rgb, _, _ = apply_colormap(image, vmin=vmin, vmax=vmax, cmap=colormap)

    mask = np.asarray(pps.mask, dtype=bool)
    rgb[~mask] = mask_color

    return np.ascontiguousarray(rgb, dtype=np.uint8)

def plot_slice(
    pps: PPS,
    slice_index: int,
    ax=None,
    colormap: str = "pumpprobe",
    vmin: float | None = None,
    vmax: float | None = None,
    mask_color: tuple[int, int, int] = (200, 200, 200),
    colorbar: bool = True,
) -> Axes:
    """Render a PPS slice and display it on a Matplotlib axis.

    Unlike :func:`render_slice_rgb`, this function also returns the
    colorbar (by default) so the numeric color scale is visible.
    """
    if ax is None:
        _, ax = plt.subplots()

    image = pps.images[slice_index]
    mask = np.asarray(pps.mask, dtype=bool)

    valid_image = image[mask] if np.any(mask) else image
    if vmin is None:
        vmin = float(valid_image.min())
    if vmax is None:
        vmax = float(valid_image.max())
        if vmax <= vmin:
            vmax = vmin + 1.0

    rgb, vmin_used, vmax_used = apply_colormap(
        image, vmin=vmin, vmax=vmax, cmap=colormap
    )
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
    rgb[~mask] = mask_color

    ax.imshow(rgb)
    ax.set_axis_off()
    ax.set_title(f"{pps.filename or 'Pump Probe Image Stack'} - Slice {slice_index}")

    if colorbar:
        sm = ScalarMappable(
            norm=Normalize(vmin=vmin_used, vmax=vmax_used),
            cmap=plt.get_cmap(colormap),
        )
        sm.set_array([])
        plt.colorbar(sm, ax=ax)

    return ax

# ------------------------------------------------------------------
# Render / Plot stack projection
# ------------------------------------------------------------------
def render_projection_rgb(
    pps: PPS,
    colormap: str = "gray",
    vmin: float | None = None,
    vmax: float | None = None,
    mask_color: tuple[int, int, int] = (200, 200, 200),
) -> np.ndarray:
    """Render the spatial projection of a PPS stack as a uint8 RGB image.

    The projection is computed with :meth:`PPS.project` using
    ``mask_on=False``. By default the image is rendered in grayscale;
    any Matplotlib colormap name (``"viridis"``, ``"RdBu_r"``,
    ``"pumpprobe"``, etc.) may be supplied. Pixels excluded by the
    effective mask are replaced by ``mask_color``.

    Parameters
    ----------
    pps : PPS
        The stack whose spatial projection is rendered.
    colormap : str, default "gray"
        Colormap name passed to :func:`apply_colormap`.
    vmin, vmax : float or None, optional
        Color scale limits. If None, they are inferred from valid
        (non-masked) pixels.
    mask_color : tuple[int, int, int], default gray (200, 200, 200)
        RGB color (0-255) applied to pixels where ``pps.mask`` is False.

    Returns
    -------
    np.ndarray
        Contiguous array of shape ``(height, width, 3)`` and dtype
        ``np.uint8``. The last axis is ordered as red, green, blue.
    """
    projection = pps.project(mask_on=False)
    projection = np.nan_to_num(projection, nan=0.0, posinf=0.0, neginf=0.0)

    mask_2d = np.asarray(pps.mask, dtype=bool)

    valid_proj = projection[mask_2d] if np.any(mask_2d) else projection
    if vmin is None:
        vmin = float(valid_proj.min())
    if vmax is None:
        vmax = float(valid_proj.max())
        if vmax <= vmin:
            vmax = vmin + 1.0

    rgb, _, _ = apply_colormap(projection, vmin=vmin, vmax=vmax, cmap=colormap)
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
    rgb[~mask_2d] = mask_color
    return rgb

def plot_projection(
    pps: PPS,
    ax=None,
    colormap: str = "gray",
    vmin: float | None = None,
    vmax: float | None = None,
    mask_color: tuple[int, int, int] = (200, 200, 200),
    colorbar: bool = True,
) -> Axes:
    """Render the spatial projection and display it with a colorbar.

    Parameters
    ----------
    pps : PPS
        The stack whose projection is displayed.
    ax : matplotlib.axes.Axes or None, optional
        Axis on which to draw. If None, a new figure and axis are created.
    colormap : str, default "gray"
        Colormap name passed to :func:`apply_colormap`.
    vmin, vmax : float or None, optional
        Color scale limits. If None, they are inferred from valid pixels.
    mask_color : tuple[int, int, int]
        RGB color (0-255) used for masked-out pixels.
    colorbar : bool, default True
        Whether to add a colorbar to the plot.

    Returns
    -------
    matplotlib.axes.Axes
        The axis containing the displayed image.
    """
    if ax is None:
        _, ax = plt.subplots()

    projection = pps.project(mask_on=False)
    projection = np.nan_to_num(projection, nan=0.0, posinf=0.0, neginf=0.0)

    mask_2d = np.asarray(pps.mask, dtype=bool)
    valid_proj = projection[mask_2d] if np.any(mask_2d) else projection
    if vmin is None:
        vmin = float(valid_proj.min())
    if vmax is None:
        vmax = float(valid_proj.max())
        if vmax <= vmin:
            vmax = vmin + 1.0

    rgb, vmin_used, vmax_used = apply_colormap(
        projection, vmin=vmin, vmax=vmax, cmap=colormap
    )
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
    rgb[~mask_2d] = mask_color

    ax.imshow(rgb)
    ax.set_axis_off()
    ax.set_title(f"{pps.filename or 'Pump Probe Image Stack'} - projection")

    if colorbar:
        sm = ScalarMappable(
            norm=Normalize(vmin=vmin_used, vmax=vmax_used),
            cmap=plt.get_cmap(colormap),
        )
        sm.set_array([])
        plt.colorbar(sm, ax=ax)

    return ax

# ------------------------------------------------------------------
# Render / Plot phasor
# ------------------------------------------------------------------
def render_phasor_rgba(
    coords: np.ndarray,
    color_hex: str,
    g_lim: tuple[float, float] = (-1.0, 1.0),
    s_lim: tuple[float, float] = (-1.0, 1.0),
    size: int = 512,
) -> np.ndarray:
    """Render phasor coordinates as a single-color RGBA density image.

    A 2D histogram of the phasor coordinates is computed and normalized to
    its maximum. The histogram is then composited into a fixed-color RGBA
    image where the alpha channel encodes density. The image is suitable
    for immediate display with ``imshow`` and can be overlaid on other
    phasor plots.

    Parameters
    ----------
    coords : np.ndarray
        Phasor coordinates with shape ``(n_points, 2)``. The first column
        is ``g`` and the second is ``s``.
    color_hex : str
        Matplotlib color specification for the density overlay.
    g_lim : tuple[float, float], default (-1.0, 1.0)
        Lower and upper bounds of the ``g`` axis.
    s_lim : tuple[float, float], default (-1.0, 1.0)
        Lower and upper bounds of the ``s`` axis.
    size : int, default 512
        Output image size in pixels. The returned image is square.

    Returns
    -------
    np.ndarray
        Contiguous array of shape ``(size, size, 4)`` and dtype
        ``np.uint8``. The first three channels are the requested color;
        the alpha channel is the normalized histogram scaled to 0-180.

    Notes
    -----
    The image has its origin at the upper-left corner. Row 0 corresponds
    to the maximum ``s`` value and row ``size-1`` to the minimum ``s``
    value, matching the convention used by ``imshow`` with
    ``origin="upper"``.
    """
    g = coords[:, 0]
    s = coords[:, 1]

    bins_g = np.linspace(g_lim[0], g_lim[1], size + 1)
    bins_s = np.linspace(s_lim[0], s_lim[1], size + 1)
    hist, _, _ = np.histogram2d(g, s, bins=[bins_g, bins_s])
    hist = hist.T[::-1, :]  # image rows: high s at top

    if np.any(hist > 0):
        hist = hist / hist.max()

    rgb_color = np.array(mcolors.to_rgb(color_hex)) * 255.0
    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    rgba[..., 0] = int(rgb_color[0])
    rgba[..., 1] = int(rgb_color[1])
    rgba[..., 2] = int(rgb_color[2])
    rgba[..., 3] = (hist * 180).astype(np.uint8)

    return np.ascontiguousarray(rgba)

def universal_semicircle(
    n_points: int = 400,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return points describing the universal phasor semicircle.

    The universal semicircle is the reference curve for single-exponential
    decays in phasor space. It consists of an upper branch in the first
    quadrant and a symmetric lower branch.

    Parameters
    ----------
    n_points : int, default 400
        Number of points used to sample each branch.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        Four 1D arrays of length ``n_points``:

        * ``g_upper``, ``s_upper``: upper branch.
        * ``g_lower``, ``s_lower``: lower branch, obtained by reflecting
          the upper branch through the origin.

    Notes
    -----
    This function returns coordinate arrays only. Actual drawing (e.g. in
    a Matplotlib axis or a Qt graphics scene) is left to the caller.
    """

    theta = np.linspace(0.0, np.pi, n_points)
    g_upper = 0.5 * (1.0 + np.cos(theta))
    s_upper = 0.5 * np.sin(theta)
    g_lower = -g_upper
    s_lower = -0.5 * np.sin(theta)

    return g_upper, s_upper, g_lower, s_lower

def plot_phasor(
    pps: PPS,
    color_hex: str,
    freq: float = 0.25,
    use_mask: bool = True,
    ax=None,
    g_lim: tuple[float, float] = (-1.0, 1.0),
    s_lim: tuple[float, float] = (-1.0, 1.0),
    size: int = 512,
    show_semicircle: bool = True,
) -> Axes:
    """Compute and display a phasor density image.

    By default the universal phasor semicircle is overlaid as a gray
    dashed reference line. Use ``show_semicircle=False`` to hide it.

    Parameters
    ----------
    pps : PPS
        The stack whose phasor coordinates are computed.
    color_hex : str
        Matplotlib color specification for the density overlay.
    freq : float, default 0.25
        Phasor frequency expressed in the reciprocal unit of
        ``pps.axis_unit``.
    use_mask : bool, default True
        Whether the effective mask is applied when computing phasor
        coordinates.
    ax : matplotlib.axes.Axes or None, optional
        Axis on which to draw. If None, a new figure and axis are created.
    g_lim, s_lim : tuple[float, float]
        Bounds of the phasor ``(g, s)`` coordinate axes.
    size : int, default 512
        Output square image size in pixels.
    show_semicircle : bool, default True
        If True, the universal phasor semicircle is drawn as a reference.

    Returns
    -------
    matplotlib.axes.Axes
        The axis containing the density image.
    """
    if ax is None:
        _, ax = plt.subplots()

    coords = pps.phasor(freq=freq, use_mask=use_mask)
    rgba = render_phasor_rgba(
        coords,
        color_hex,
        g_lim=g_lim,
        s_lim=s_lim,
        size=size,
    )

    ax.imshow(
        rgba,
        extent=[g_lim[0], g_lim[1], s_lim[0], s_lim[1]],
        origin="upper",
        interpolation="nearest",
        aspect="equal",
    )

    if show_semicircle:
        g_upper, s_upper, g_lower, s_lower = universal_semicircle()
        ax.plot(g_upper, s_upper, color="gray", linestyle="--", linewidth=1.0)
        ax.plot(g_lower, s_lower, color="gray", linestyle="--", linewidth=1.0)

    ax.set_xlabel("g")
    ax.set_ylabel("s")
    ax.set_title(f"Phasor @ {freq:.2f} {pps.get_phasor_unit()}")
    ax.set_xlim(g_lim)
    ax.set_ylim(s_lim)

    return ax

# ------------------------------------------------------------------
# Plot Average Curve
# ------------------------------------------------------------------
def plot_average_curve(
    pps: PPS,
    ax=None,
    normalize: bool = False,
    color: str | None = None,
    linewidth: float = 1.5,
) -> Axes:
    """Plot the average curve of a PPS stack.

    The curve is computed from the pixels inside the effective mask using
    :meth:`PPS.avg` with ``mask_on=True``.

    Parameters
    ----------
    pps : PPS
        The stack whose average curve is plotted.
    ax : matplotlib.axes.Axes or None, optional
        Axis on which to draw. If None, a new figure and axis are created.
    normalize : bool, default False
        If True, the curve is scaled so its maximum absolute value is 1.
    color : str or None, optional
        Matplotlib color for the curve.
    linewidth : float, default 1.5
        Line width.

    Returns
    -------
    matplotlib.axes.Axes
        The axis containing the average curve.
    """
    if ax is None:
        _, ax = plt.subplots()

    y = np.asarray(pps.avg(mask_on=True), dtype=np.float64)
    if normalize:
        max_abs = np.max(np.abs(y))
        if max_abs > 1e-12:
            y = y / max_abs

    x = np.asarray(pps.get_axis_values(), dtype=np.float64)

    ax.plot(x, y, color=color, linewidth=linewidth)
    ax.set_xlabel(f"{pps.get_axis_label()} ({pps.get_axis_unit()})")
    ax.set_ylabel("Normalized signal (a.u.)" if normalize else "Average signal (a.u.)")
    ax.set_title(f"{pps.filename or 'Average Curve'}")
    ax.grid(True, alpha=0.3)
    # ax.legend(fontsize=8, loc="best")

    return ax