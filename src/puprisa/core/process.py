# puprisa/core/processing.py
"""Pure image-stack processing helpers.

These functions are intentionally free of Qt and free of the ``PPS`` class.
They operate on NumPy arrays and return NumPy arrays / scalars.
"""

import numpy as np
from skimage.transform import downscale_local_mean
from skimage import filters


def nan_inf_to_zero(values: np.ndarray) -> np.ndarray:
    """Return floating data with non-finite samples replaced by zero.

    Invalid detector samples must not poison an entire projection, fit input,
    or threshold calculation.  The original stack is left untouched; callers
    that need an invalid-pixel audit can retain it separately.
    """
    return np.nan_to_num(np.asarray(values, dtype=np.float64), nan=0.0,
                         posinf=0.0, neginf=0.0)

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
    projection = np.sum(np.abs(nan_inf_to_zero(images)), axis=0)
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
    indices = list(indices)
    if not indices:
        raise ValueError("At least one background frame index is required")
    background_frames = np.asarray(images, dtype=np.float64)[indices]
    if pixelwise:
        with np.errstate(invalid="ignore"):
            return np.nan_to_num(np.nanmean(background_frames, axis=0), nan=0.0,
                                 posinf=0.0, neginf=0.0)
    finite = background_frames[np.isfinite(background_frames)]
    scalar = float(np.mean(finite)) if finite.size else 0.0
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
    result = np.asarray(images, dtype=np.float64) - np.asarray(background_map, dtype=np.float64)[np.newaxis, :, :]
    return np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)


def normalize_by_avg_curve(images: np.ndarray, avg_curve=None) -> tuple[np.ndarray, float]:
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
        with np.errstate(invalid="ignore"):
            avg_curve = np.nanmean(np.asarray(images, dtype=np.float64), axis=(1, 2))
    finite_curve = np.asarray(avg_curve, dtype=np.float64)
    finite_curve = finite_curve[np.isfinite(finite_curve)]

    extremum = float(np.max(np.abs(finite_curve))) if finite_curve.size else 0.0
    extremum = max(extremum, 1e-9) # Avoid division by zero
    return np.nan_to_num(np.asarray(images, dtype=np.float64) / extremum,
                         nan=0.0, posinf=0.0, neginf=0.0), extremum

def downsample_mask(mask: np.ndarray, factor: int) -> np.ndarray:
    """Downsample a 2D boolean mask using local averaging.

    Output is True where any input pixel in the corresponding block
    was True (conservative, matches legacy behavior).
    """
    return downscale_local_mean(mask.astype(np.float64), (factor, factor)) > 0

def downsample_local_mean(images: np.ndarray, factor: int) -> np.ndarray:
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
    return downscale_local_mean(images, (1, factor, factor))


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
        The projection to smooth and threshold.
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
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    smoothed = filters.gaussian(nan_inf_to_zero(projection), sigma=sigma)

    if threshold == "Li":
        cutoff = filters.threshold_li(smoothed) if np.ptp(smoothed) > 0 else float(smoothed.flat[0])
    elif isinstance(threshold, (int, float)):
        cutoff = threshold
    else:
        raise ValueError(f"threshold must be 'Li' or a number, got {threshold!r}")

    result = smoothed > cutoff
    if mask is not None:
        result = result & mask
    return result

def svd_reconstruct(images: np.ndarray, n_components: int) -> np.ndarray:
    """Denoise an image stack with a rank-n_components truncated SVD.

    No mean-centering is applied, matching the original MATLAB workflow.

    Parameters
    ----------
    images : np.ndarray
        Shape: (n_frames, height, width).
    n_components : int
        Number of leading singular components to retain.

    Returns
    -------
    np.ndarray
        Reconstructed stack with the same shape as ``images``.
    """
    images = np.asarray(images, dtype=np.float64)

    if images.ndim != 3:
        raise ValueError(
            f"Expected images with shape (n_frames, h, w), got {images.shape}."
        )
    if not np.all(np.isfinite(images)):
        raise ValueError("SVD reconstruction requires finite image values.")

    n_frames, h, w = images.shape
    max_components = min(n_frames, h * w)

    if not isinstance(n_components, (int, np.integer)):
        raise TypeError("n_components must be an integer.")
    if not 1 <= n_components <= max_components:
        raise ValueError(
            f"n_components must be between 1 and {max_components}, "
            f"got {n_components}."
        )

    delay_by_pixel = images.reshape(n_frames, h * w)

    # Perform SVD
    u, singular_values, vt = np.linalg.svd(delay_by_pixel, full_matrices=False)

    # Reconstruct the stack using only the leading n_components
    reconstructed = (u[:, :n_components] * singular_values[:n_components]) @ vt[:n_components, :]

    return reconstructed.reshape(n_frames, h, w)