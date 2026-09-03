"""
Plotting helpers for ROI average curves.
"""

from __future__ import annotations
from matplotlib.axes import Axes
from puprisa.model.entities import CurveItem


def draw_roi_curves(
    ax: Axes,
    curves: list[CurveItem],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "ROI Average Curves",
    current_slice_x: float | None = None,
) -> Axes:
    """Draw a list of ROI average curves onto a Matplotlib axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis on which to draw.
    curves : list of CurveItem
        The curves to plot. Each item provides ``x``, ``y``, ``color``,
        and ``label``.
    xlabel, ylabel, title : str, optional
        Axis labels and plot title.
    current_slice_x : float or None, optional
        If provided, draw a vertical dashed line at this x position.

    Returns
    -------
    matplotlib.axes.Axes
        The axis containing the drawn curves.
    """
    for curve in curves:
        ax.plot(curve.x, curve.y, color=curve.color, label=curve.label)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    if current_slice_x is not None:
        ax.axvline(current_slice_x, color="gray", linestyle="--", linewidth=1.2, alpha=0.8)

    if curves:
        ax.legend(fontsize=8, loc="best")

    return ax