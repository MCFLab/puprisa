# puprisa/core/processing.py
"""Pure image-stack processing helpers.

These functions are intentionally free of Qt and free of the ``PPS`` class.
They operate on NumPy arrays and return NumPy arrays / scalars.
"""

import numpy as np
from skimage.transform import downscale_local_mean
from skimage import filters

def compute_projection(images: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    """Sum of absolute values across stack frames.

    Parameters
    ----------
    images : shape (n_frames, h, w)
    mask : shape (h, w), optional
        If given, the projection is multiplied by this boolean mask.

    Returns
    -------
    projection : shape (h, w)
    """
    projection = np.sum(np.abs(images), axis=0)
    if mask is not None:
        projection = projection * mask
    return projection


def compute_background_map(images: np.ndarray, indices, pixelwise: bool = True) -> np.ndarray:
    """Compute 2D background map from a subset of frames.

    Parameters
    ----------
    images : shape (n_frames, h, w)
    indices : sequence of int
        Frame indices used for background estimation.
    pixelwise : bool
        If True each pixel is averaged independently. If False a single
        scalar is broadcast to the full image.

    Returns
    -------
    background : shape (h, w)
    """
    background_frames = images[list(indices)]
    if pixelwise:
        return np.mean(background_frames, axis=0)
    scalar = np.mean(background_frames)
    return np.full(images.shape[1:], float(scalar), dtype=np.float64)


def subtract_background(images: np.ndarray, background_map: np.ndarray) -> np.ndarray:
    """Subtract a 2D background map from every frame.

    Parameters
    ----------
    images : shape (n_frames, h, w)
    background_map : shape (h, w)

    Returns
    -------
    background-subtracted images, same shape as ``images``.
    """
    return images - background_map[np.newaxis, :, :]


def normalize_minmax(images: np.ndarray, avg_curve=None) -> tuple[np.ndarray, float]:
    """Normalize stack by the max absolute value of the average curve.

    Parameters
    ----------
    images : shape (n_frames, h, w)
    avg_curve : 1D array, optional
        Precomputed average curve. If None, it is computed as the mean of all
        pixels per frame.

    Returns
    -------
    scaled_images : shape (n_frames, h, w)
    scale_factor : float
        The factor by which images were divided.
    """
    if avg_curve is None:
        avg_curve = np.mean(images, axis=(1, 2))
    extremum = float(np.max(np.abs(avg_curve)))
    if extremum == 0:
        extremum = 1.0
    return images / extremum, extremum

def downsample_mask(mask: np.ndarray, factor: int) -> np.ndarray:
    """Downsample a 2D boolean mask using local averaging.

    Output is True where any input pixel in the corresponding block
    was True (conservative, matches legacy behavior).
    """
    return downscale_local_mean(mask.astype(np.float64), (factor, factor)) > 0

def downsample_mean(images: np.ndarray, factor: int) -> np.ndarray:
    """Downsample stack using local mean.

    Parameters
    ----------
    images : shape (n_frames, h, w)
    factor : int
        Downsampling factor along each spatial axis.

    Returns
    -------
    downsampled : shape (n_frames, h//factor, w//factor)
    """
    if factor <= 0:
        raise ValueError("Downsampling factor must be positive")
    return np.stack([downscale_local_mean(img, (factor, factor)) for img in images])


def average_groups(images: np.ndarray, groups_indices: list[list[int]]) -> np.ndarray:
    """Average frames according to explicit index groups.

    Parameters
    ----------
    images : shape (n_frames, h, w)
    groups_indices : list of lists of int
        Each inner list contains frame indices to average together.

    Returns
    -------
    averaged_images : shape (n_groups, h, w)
    """
    return np.stack(
        [np.mean(images[group], axis=0) for group in groups_indices]
    )


def gaussian_threshold_mask(
    projection: np.ndarray,
    threshold: float | str = "Li",
    sigma: float = 5,
    mask: np.ndarray | None = None,
) -> np.ndarray:
    """Smooth a projection and threshold it into a boolean mask.

    Parameters
    ----------
    projection : shape (h, w)
    threshold : float or "Li"
        Numeric threshold or Li auto-threshold.
    sigma : float
        Gaussian smoothing sigma.
    mask : shape (h, w), optional
        Existing mask that the result is ANDed with.

    Returns
    -------
    thresholded_mask : shape (h, w)
    """
    smoothed = filters.gaussian(projection, sigma=sigma)

    if threshold == "Li":
        cutoff = filters.threshold_li(smoothed)
    elif isinstance(threshold, (int, float)):
        cutoff = threshold
    else:
        raise ValueError(f"threshold must be 'Li' or a number, got {threshold!r}")

    result = smoothed > cutoff
    if mask is not None:
        result = result & mask
    return result