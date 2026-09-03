import numpy as np
import matplotlib

matplotlib.use("Agg")

from puprisa.core.pps import PPS
from puprisa.core.visualize import _phasor_histogram, render_phasor_rgba


def test_render_phasor_rgba_keeps_sparse_bins_visible():
    """A strong origin bin must not hide a separate one-point bin."""
    coords = np.vstack((np.zeros((800, 2)), [[0.5, 0.25]]))

    rgba = render_phasor_rgba(coords, "#ff0000", size=128)

    # The sparse point's bin is away from the origin and has nonzero alpha.
    assert rgba[47, 96, 3] > 0


def test_phasor_histogram_discards_nan_coordinates():
    coords = np.array([[0.0, 0.0], [np.nan, 0.2], [0.4, np.inf]])

    hist, _, _ = _phasor_histogram(coords, (-1, 1), (-1, 1), bins=8)

    assert hist.sum() == 1


def test_pps_exposes_phasor_hist2d_plot():
    images = np.ones((4, 2, 2))
    pps = PPS(images, np.arange(4.0))

    ax = pps.plot_phasor_hist2d(bins=16, show_semicircle=False)

    assert ax.get_title().startswith("Phasor 2D histogram")
