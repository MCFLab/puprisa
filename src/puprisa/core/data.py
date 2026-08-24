from dataclasses import dataclass, field
import numpy as np

@dataclass
class PPSDataClass:
    images: np.ndarray
    axis_values: np.ndarray
    axis_type: str
    image_dimensions: tuple | None = None
    masks: dict = field(default_factory=dict)
    original_images: np.ndarray | None = None
    background_map: np.ndarray | None = None
    results: dict = field(default_factory=dict)
    filename: str = ""