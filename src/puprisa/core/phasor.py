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
    mask: np.ndarray | None = None,
) -> np.ndarray:
    """
    Compute (g, s) phasor coordinates for every pixel.

    Pixels excluded by ``mask`` get ``np.nan`` coordinates.

    Parameters
    ----------
    images : np.ndarray, shape (n_frames, h, w)
        Image stack with time as the leading axis.
    axis_values : np.ndarray, shape (n_frames,)
        1D array giving the independent (time) value for each frame.
    freq : float, default 0.25
        Modulation frequency used to build the harmonic basis.
    mask : np.ndarray | None, optional
        Boolean array of shape (h, w). Only pixels
        where ``mask`` is True are processed; excluded pixels receive
        ``np.nan`` coordinates. If None, every pixel is processed.

    Returns
    -------
    np.ndarray, shape (h * w, 2)
        Row-major phasor coordinates ``(g, s)`` per pixel. Pixels excluded
        by ``mask`` are ``np.nan``.

    Raises
    ------
    ValueError
        If ``axis_values`` is not 1D, does not match the number of frames,
        or contains non-finite values.
    """
    ta_curves = np.nan_to_num(flatten_stack(images), nan=0.0, posinf=0.0, neginf=0.0)
    h, w = images.shape[1], images.shape[2]

    # Validate axis and prepare basis (common to all branches)
    omega = 2.0 * np.pi * float(freq)
    axis_values = np.asarray(axis_values, dtype=np.float64)
    if axis_values.ndim != 1 or axis_values.size != images.shape[0]:
        raise ValueError("axis_values must be 1D and match the number of frames")
    if not np.all(np.isfinite(axis_values)):
        raise ValueError("axis_values must contain only finite values")
    sin_basis = np.sin(axis_values * omega)
    cos_basis = np.cos(axis_values * omega)

    # Determine which curves to compute
    if mask is not None:
        mask = np.asarray(mask, dtype=bool)
        valid_flat = mask.ravel()
        valid_indices = np.nonzero(valid_flat)[0]
        if valid_indices.size == 0:
            return np.full((h * w, 2), np.nan)
        curves = ta_curves[valid_indices]          # (n_valid, n_frames)
        result_indices = valid_indices
    else:
        curves = ta_curves
        result_indices = None

    # Normalization (per curve)
    norm = np.sum(np.abs(curves), axis=1, keepdims=True)
    norm = np.where(norm == 0, 1.0, norm)

    g = (curves @ cos_basis) / norm.ravel()
    s = (curves @ sin_basis) / norm.ravel()
    coords_valid = np.column_stack((g, s))

    if result_indices is None:
        return coords_valid
    else:
        coords = np.full((h * w, 2), np.nan)
        coords[result_indices] = coords_valid
        return coords

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
