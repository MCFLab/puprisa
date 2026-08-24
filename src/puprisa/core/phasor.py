# puprisa/core/phasor.py
"""Pure phasor-transform helpers."""

import numpy as np

def flatten_stack(images: np.ndarray) -> np.ndarray:
    """Flatten an image stack into pixel * time curves.

    Parameters
    ----------
    images : shape (n_frames, h, w)

    Returns
    -------
    ta_curves : shape (n_pixels, n_frames)
        Row-major pixel order, i.e. pixel i corresponds to
        ``images[:, i // w, i % w]``.
    """
    n_frames = images.shape[0]
    return images.reshape(n_frames, -1).T


def compute_phasor(
    images: np.ndarray,
    axis_values: np.ndarray,
    freq: float = 0.25,
    remove_zero: bool = False,
) -> np.ndarray:
    """Compute (g, s) phasor coordinates for every pixel.

    Parameters
    ----------
    images : shape (n_frames, h, w)
    axis_values : 1D array of length n_frames
        Time delays in ps. For Z stacks this function does not apply.
    freq : float
        Phasor frequency in THz.
    remove_zero : bool
        If True, pixels whose TA curve is exactly zero everywhere are
        removed. Their corresponding rows would otherwise be undefined.

    Returns
    -------
    coords : shape (n_pixels, 2) or (n_valid_pixels, 2)
        Columns are ``g`` and ``s``. When ``remove_zero=False``, row order
        matches ``flatten_stack(images)``.
    """
    ta_curves = flatten_stack(images)

    if remove_zero:
        valid = np.any(ta_curves != 0, axis=1)
        ta_curves = ta_curves[valid]

    omega = 2.0 * np.pi * float(freq)
    sin_basis = np.sin(np.asarray(axis_values, dtype=np.float64) * omega)
    cos_basis = np.cos(np.asarray(axis_values, dtype=np.float64) * omega)

    # |I| normalization avoids division by zero.
    norm = np.sum(np.abs(ta_curves), axis=1, keepdims=True)
    norm = np.where(norm == 0, 1.0, norm)

    g = (ta_curves @ cos_basis) / norm.ravel()
    s = (ta_curves @ sin_basis) / norm.ravel()
    return np.column_stack((g, s))


def universal_semicircle(n_points: int = 400) -> tuple[np.ndarray, np.ndarray]:
    """Return (g, s) coordinates of the universal semicircle.

    Returns
    -------
    g, s : 1D arrays of length n_points
        The standard universal phasor circle for single-exponential decay.
    """
    theta = np.linspace(0.0, np.pi, n_points)
    g = 0.5 * (1.0 + np.cos(theta))
    s = 0.5 * np.sin(theta)
    return g, s