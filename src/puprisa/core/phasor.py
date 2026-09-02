# puprisa/core/phasor.py
"""Pure phasor-transform helpers."""

import numpy as np
from scipy.signal import welch

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

def compute_fft(
    signal: np.ndarray,
    axis_values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the single-sided amplitude spectrum of a real signal.

    The mean is removed before calculating the FFT.

    Parameters
    ----------
    signal : 1D array
        Input signal.
    axis_values : 1D array
        Independent variable corresponding to the signal. It must be
        finite, strictly increasing, and uniformly spaced.

    Returns
    -------
    freq : np.ndarray
        Non-negative frequencies in reciprocal units of ``axis_values``.
    spectrum : np.ndarray
        Single-sided peak-amplitude spectrum. For a sinusoid with peak
        amplitude A whose frequency falls exactly on an FFT bin, the
        corresponding spectral peak is A.
    """
    signal = np.asarray(signal, dtype=np.float64)
    axis_values = np.asarray(axis_values, dtype=np.float64)

    if signal.size != axis_values.size:
        raise ValueError("signal and axis_values must have the same length")
    
    sampling_intervals = np.diff(axis_values)
    if not np.all(sampling_intervals > 0):
        raise ValueError("axis_values must be strictly increasing")
    dt = sampling_intervals[0]
    if not np.allclose(sampling_intervals, dt, rtol=1e-6, atol=0.0):
        raise ValueError("axis_values must be uniformly spaced")

    signal_ac = signal - np.mean(signal)
    n = signal_ac.size

    freq = np.fft.rfftfreq(n,d=dt)
    spectrum = (np.abs(np.fft.rfft(signal_ac)) / n)

    # Convert the two-sided spectrum to a single-sided one.
    # DC and Nyquist must not be doubled.
    if n % 2 == 0:
        spectrum[1:-1] *= 2.0
    else:
        spectrum[1:] *= 2.0
    return freq, spectrum


def compute_psd(
    signal: np.ndarray,
    axis_values: np.ndarray,
    normalize: bool = False,
    nperseg: int | None = None,
    db: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the PSD of a signal using Welch's method.

    The mean is removed before calculating the PSD. If ``normalize`` is
    True, the fluctuation is divided by the mean signal, producing the
    relative intensity noise (RIN) PSD.

    Parameters
    ----------
    signal : 1D array
        Input signal.
    axis_values : 1D array
        Independent variable corresponding to the signal. It must be
        finite, strictly increasing, and uniformly spaced.
    normalize : bool, default False
        If False, calculate the ordinary PSD of the signal fluctuation.
        If True, normalize the fluctuation by the mean signal and
        calculate the RIN PSD.
    nperseg : int or None, default None
        Number of samples in each Welch segment. If None,
        ``min(256, max(2, N // 4))`` is used, where N is the signal length.
    db : bool, default False
        If True, return ``10 * log10(PSD)``. Otherwise, return the
        linear PSD.

    Returns
    -------
    freq : np.ndarray
        Non-negative frequencies in reciprocal units of
        ``axis_values``.
    power_spectral_density : np.ndarray
        One-sided power spectral density.

        If ``normalize=False``, its unit is the squared signal unit per
        frequency unit, such as V^2/Hz.

        If ``normalize=True``, it is the RIN PSD with units of inverse
        frequency, such as 1/Hz. Its logarithmic representation is
        commonly expressed in dBc/Hz.
    """
    signal = np.asarray(signal, dtype=np.float64)
    axis_values = np.asarray(axis_values, dtype=np.float64)

    if signal.size != axis_values.size:
        raise ValueError("signal and axis_values must have the same length")
    sampling_intervals = np.diff(axis_values)
    if not np.all(sampling_intervals > 0):
        raise ValueError("axis_values must be strictly increasing")
    dt = sampling_intervals[0]
    if not np.allclose(sampling_intervals,dt,rtol=1e-6,atol=0.0):
        raise ValueError("axis_values must be uniformly spaced")

    mean_signal = np.mean(signal)
    signal_fluctuation = signal - mean_signal

    if normalize:
        signal_scale = np.max(np.abs(signal))
        mean_tolerance = (np.finfo(np.float64).eps * max(signal_scale, 1.0))
        if abs(mean_signal) <= mean_tolerance:
            raise ValueError("mean signal is too close to zero for normalization")
        analyzed_signal = signal_fluctuation / mean_signal
    else:
        analyzed_signal = signal_fluctuation

    number_of_samples = signal.size
    fs = 1.0 / dt # sampling frequency

    if nperseg is None:
        nperseg = min(256, max(2, number_of_samples // 4))

    freq, psd = welch(
        analyzed_signal,
        fs=fs,
        window="hann",
        nperseg=nperseg,
        noverlap=nperseg // 2,
        detrend="constant",
        return_onesided=True,
        scaling="density",
    )

    if db:
        minimum_positive_value = np.finfo(np.float64).tiny
        psd = 10.0 * np.log10(np.maximum(psd,minimum_positive_value))

    return freq, psd