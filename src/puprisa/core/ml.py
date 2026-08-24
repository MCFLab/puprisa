# puprisa/core/ml.py
"""Pure machine-learning classification helpers for image stacks."""

import numpy as np

def classify_pixels(
    images: np.ndarray,
    mask: np.ndarray,
    classifier,
    downsample_factor: int = 1,
    norm: str | None = "minmax",
) -> tuple[np.ndarray, dict]:
    """Classify each pixel using a pre-trained classifier.

    Parameters
    ----------
    images : shape (n_frames, h, w)
    mask : shape (h, w)
        Analysis mask. Pixels with ``mask == False`` are not classified and
        receive value 0 in the result matrix.
    classifier : classifier object
        Must have ``classes_`` and ``predict()`` (e.g. an sklearn estimator).
    downsample_factor : int
        Spatial downsampling factor applied before classification.
    norm : str or None
        Normalization passed to the mean-curve extraction; currently only
        ``"minmax"`` is supported. ``None`` disables normalization.

    Returns
    -------
    matrix : shape (out_h, out_w)
        Integer class codes. ``0`` means masked-out / zero signal.
    stats : dict
        Contains ``raw_counts`` and ``fractions`` per class.
    """
    # Optional downsampling
    from .process import downsample_mean

    working_images = images
    working_mask = mask
    if downsample_factor and downsample_factor > 1:
        working_images = downsample_mean(images, downsample_factor)
        # crude, but suitable for classification-only workflow
        working_mask = mask[::downsample_factor, ::downsample_factor]

    h, w = working_images.shape[1], working_images.shape[2]
    classes = list(classifier.classes_)
    class_to_code = {cls: i + 1 for i, cls in enumerate(classes)}  # 0 reserved

    curves = working_images.reshape(working_images.shape[0], -1).T  # (n_pixels, n_frames)
    flat_mask = working_mask.ravel()

    codes = np.zeros(curves.shape[0], dtype=int)
    counts = {cls: 0 for cls in classes}
    total_valid = 0

    for i, curve in enumerate(curves):
        if not flat_mask[i]:
            continue
        if np.all(curve == 0):
            continue

        # Normalize curve if requested
        sample = curve
        if norm == "minmax":
            scale = np.max(np.abs(sample))
            if scale > 0:
                sample = sample / scale

        predicted = classifier.predict([sample])[0]
        codes[i] = class_to_code[predicted]
        counts[predicted] = counts.get(predicted, 0) + 1
        total_valid += 1

    fractions = {
        cls: (counts[cls] / total_valid if total_valid > 0 else 0.0)
        for cls in classes
    }

    stats = {
        "raw_counts": counts,
        "fractions": fractions,
        "total_valid": total_valid,
    }

    matrix = codes.reshape(h, w)
    return matrix, stats


def compute_accuracy(
    stats: dict,
    correct_classes: list[str],
    top_k: int = 2,
) -> dict:
    """Compute simple accuracy metrics from classification stats.

    Parameters
    ----------
    stats : dict
        Must contain ``fractions`` key mapping class -> fraction.
    correct_classes : list of str
        Class names considered correct.
    top_k : int
        Number of most frequent classes to check against.

    Returns
    -------
    metrics : dict
        Contains ``correct_identified`` and ``correct_percentage``.
    """
    fractions = stats.get("fractions", {})
    sorted_classes = sorted(fractions, key=lambda k: fractions[k], reverse=True)
    top_classes = sorted_classes[:top_k]

    correct_percentage = sum(fractions.get(cls, 0.0) for cls in correct_classes)
    correct_identified = [cls for cls in correct_classes if cls in top_classes]

    return {
        "correct_identified": correct_identified,
        "correct_percentage": correct_percentage,
    }