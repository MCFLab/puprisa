# puprisa/core/mask.py
"""Pure mask helpers: threshold creation and JSON serialization. """
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from skimage.filters import gaussian, threshold_li
from puprisa.core.process import nan_inf_to_zero

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
    smoothed = gaussian(nan_inf_to_zero(projection), sigma=sigma)

    if threshold == "Li":
        cutoff = threshold_li(smoothed) if np.ptp(smoothed) > 0 else float(smoothed.flat[0])
    elif isinstance(threshold, (int, float)):
        cutoff = threshold
    else:
        raise ValueError(f"threshold must be 'Li' or a number, got {threshold!r}")

    result = smoothed > cutoff
    if mask is not None:
        result = result & mask
    return result

def load_mask_from_json(path: str | Path) -> np.ndarray | None:
    """Load multiple JSON mask layers and collapse them into one keep mask.

    The JSON file must contain a ``"masks"`` list of layer dictionaries,
    each having at least a ``"mask"`` key. Enabled layers are combined
    with a logical AND, because every layer is a keep mask. Disabled
    layers are ignored.

    Returns ``None`` if the file contains no usable layers.
    """
    path = Path(path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Mask file must contain a JSON object")
    items = data.get("masks", [])
    if not isinstance(items, list):
        raise ValueError("'masks' must be a list")

    combined: np.ndarray | None = None
    for item in items:
        if not isinstance(item, dict) or "mask" not in item:
            raise ValueError("Every mask must contain 'mask'")
        if not item.get("enabled", True):
            continue

        layer = np.asarray(item["mask"], dtype=bool)
        if combined is None:
            combined = layer.copy()
        else:
            if combined.shape != layer.shape:
                raise ValueError(
                    f"Mask shape mismatch: {combined.shape} vs {layer.shape}"
                )
            combined &= layer

    return combined


def export_mask_to_json(path: str | Path, mask: np.ndarray, label: str = "", enabled: bool = True) -> None:
    """Export a single keep mask using the MaskManager JSON format.
    The written file contains a single layer in a ``"masks"`` list, with
    ``label``, ``mask``, and ``enabled`` fields.
    """
    path = Path(path)
    payload = {
        "masks": [
            {
                "label": label,
                "mask": np.asarray(mask).tolist(),
                "enabled": bool(enabled),
            }
        ]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)