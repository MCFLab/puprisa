# puprisa/core/stack.py
import numpy as np
from .data import PPSDataClass
from .mask import PPSMaskManager
from .io import load_stack, export_as_tiff, export_as_pickle


class PPS:
    """In-memory pump-probe stack facade.

    Parameters
    ----------
    images : np.ndarray
        Stack with shape (n_frames, height, width).
    axis_values : np.ndarray
        1D coordinate for each frame. Interpretation depends on
        ``stack_axis``. Time delays are in ps; Z positions are in µm.
    axis_type : {"time", "z"}
        Type of the axis values. "time" for time delays, "z" for Z positions.
    """

    def __init__(self, images: np.ndarray, axis_values: np.ndarray, axis_type: str = "time"):

        self.images = np.asarray(images, dtype=np.float64)
        if self.images.ndim != 3:
            raise ValueError(f"Expected 3D image stack [n_frames, h, w], got {self.images.shape}")
        self.image_dimensions = self.images[0].shape

        self.axis_values = np.asarray(axis_values, dtype=np.float64)
        if len(self.axis_values) != len(self.images):
            raise ValueError("axis_values length must match number of frames")
        
        self.axis_type = axis_type
        if axis_type not in ("time", "z"):
            raise ValueError('axis_type must be "time" or "z"')

        # Mask managers
        self._mask_manager = PPSMaskManager(self.image_dimensions)

        # Background subtraction state
        self._original_images = self.images.copy()
        self._background_map = np.zeros(self.image_dimensions, dtype=np.float64)

        # Classification results
        self.results: dict = {}

        # Metadata
        self.filename = ""

    # ------------------------------------------------------------------
    # Loading and saving
    # ------------------------------------------------------------------
    @classmethod
    def load(cls, path, axis_type: str | None = None, dataType = None):
        """Load a stack from file via ``core.io``.

        Parameters
        ----------
        path : str or Path
            Path to the stack file.
        axis_type : {"time", "z"}, optional
            Type of the axis values. "time" for time delays, "z" for Z positions.
            If None, it will be guessed from the file (e.g. from TIFF metadata).
        dataType : str, optional
            Type of the data. If None, it will be guessed from the file extension.

        Returns
        -------
        PPS instance with the loaded data.
        """
        data = load_stack(path, axis_type=axis_type, dataType=dataType)
        return cls._from_dataclass(data)

    def save(self, path, format="tiff"):
        data = self._to_dataclass()
        if format == "tiff":
            export_as_tiff(path, data.images, axis_values=data.axis_values, axis_type=data.axis_type)
        elif format == "pickle":
            export_as_pickle(path, data)
        else:
            raise ValueError(f"Unsupported format: {format!r}. Use 'tiff' or 'pickle'.")

    # ------------------------------------------------------------------
    # Mask (delegated to PPSMaskManager)
    # ------------------------------------------------------------------
    @property
    def mask(self) -> np.ndarray:
        """Effective analysis mask."""
        return self._mask_manager.get_effective_mask()

    def add_mask(self, mask, label="", enabled=True, mask_id=None):
        return self._mask_manager.add_mask(
            mask, label=label, enabled=enabled, mask_id=mask_id
        )

    def remove_mask(self, mask_id):
        return self._mask_manager.remove_mask(mask_id)

    def set_mask_enabled(self, mask_id, enabled):
        self._mask_manager.set_mask_enabled(mask_id, enabled)

    def set_mask_label(self, mask_id, label):
        self._mask_manager.set_mask_label(mask_id, label)

    def get_mask(self, mask_id):
        return self._mask_manager.get_mask(mask_id)

    def reverse_mask(self, mask_id):
        return self._mask_manager.reverse_mask(mask_id)

    def get_all_mask_ids(self):
        return self._mask_manager.get_all_mask_ids()

    def get_all_masks(self):
        return self._mask_manager.get_all_masks()

    def get_effective_mask(self):
        return self._mask_manager.get_effective_mask()

    def get_mask_manager(self) -> PPSMaskManager:
        return self._mask_manager

    def clear_all_masks(self):
        self._mask_manager.clear_all_masks()

    def save_mask(self, path, format="json"):
        data = self._mask_manager.to_serializable()
        if format == "json":
            import json
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        elif format == "pickle":
            import pickle
            with open(path, "wb") as f:
                pickle.dump(data, f)
        else:
            raise ValueError(f"Unsupported format: {format!r}. Use 'json' or 'pickle'.")

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------
    def total(self, mask_on=True):
        """Compute the sum of all stack frames, optionally applying the mask."""
        total = np.sum(self.images, axis=0)
        if mask_on:
            total = np.where(self.mask, total, 0)
        return total

    def avg(self, mask_on: bool = True):
        """Compute the average curve of the stack, optionally applying the mask."""
        if mask_on:
            return [float(np.mean(img[self.mask])) for img in self.images]
        return [float(np.mean(img)) for img in self.images]

    def project(self, mask_on: bool = True):
        """Compute the projection of the stack, optionally applying the mask. Projection is defined as the sum of absolute values across frames."""
        from .process import compute_projection

        mask = self.mask if mask_on else None
        return compute_projection(self.images, mask=mask)

    def statistics(self, mask_on: bool = True):
        """Compute basic statistics (min, max, mean, std) of the stack, optionally applying the mask."""
        if mask_on:
            masked_images = [img[self.mask] for img in self.images]
            all_pixels = np.concatenate(masked_images)
        else:
            all_pixels = self.images.flatten()

        return {
            "min": float(np.min(all_pixels)),
            "max": float(np.max(all_pixels)),
            "mean": float(np.mean(all_pixels)),
            "std": float(np.std(all_pixels)),
        }

    def downsample(self, factor: int):
        """Create a downsampled copy of this stack.

        Migrates the effective mask, individual mask layers, background
        subtraction state, and metadata. Processing results (e.g.,
        classification) are not copied because they become invalid after
        resampling.

        :param factor: Integer downsampling factor along both spatial axes.
        :return: A new PPS instance with resampled images and analysis masks.
        """
        from .process import downsample_mean, downsample_mask

        new_images = downsample_mean(self.images, factor)
        new_pps = PPS(new_images, self.axis_values, axis_type=self.axis_type)

        # --- Migrate mask layers individually, preserving IDs/labels ---
        for mask_id in self.get_all_mask_ids():
            mask = self.get_mask(mask_id)
            if mask is None:
                continue
            mask_downsampled = downsample_mask(mask["mask"], factor)
            new_pps.add_mask(
                mask_downsampled,
                label=mask.get("label", ""),
                enabled=mask.get("enabled", True),
                mask_id=mask_id,
            )

        # --- Migrate background subtraction state ---
        if self._original_images is not None:
            new_pps._original_images = downsample_mean(self._original_images, factor)
        if self._background_map is not None:
            new_pps._background_map = downsample_mean(self._background_map, factor)

        # Metadata
        new_pps.filename = self.filename
        return new_pps

    def normalize(self, norm="minmax", mask_on=True):
        """Normalize the image stack in place (only minmax supported).

        Every pixel is divided by the maximum absolute value of the average
        curve. The background-subtraction state is scaled by the same factor
        to remain consistent.

        :param norm: 'minmax' or None.
        :param mask_on: Whether to use the effective mask when computing
                        the average curve.
        """
        from .process import normalize_minmax

        if norm is None:
            return self
        if norm != "minmax":
            raise ValueError(f"Unsupported norm: {norm!r}")

        # Compute scale factor from ORIGINAL data **before** modifying images.
        avg_curve = np.array(self.avg(mask_on=mask_on), dtype=np.float64)
        scaled_images, scale_factor = normalize_minmax(self.images, avg_curve)

        # Apply normalization.
        self.images = scaled_images

        # Keep original image and background map consistent.
        if scale_factor > 1e-12:
            self._original_images = self._original_images / scale_factor
            self._background_map = self._background_map / scale_factor

        return self

    def apply_background_subtraction(self, indices, pixelwise=True):
        """Update display images by subtracting a background map."""
        from .process import compute_background_map, subtract_background

        bg_map = compute_background_map(self._original_images, indices, pixelwise=pixelwise)
        self._background_map = bg_map
        self.images = subtract_background(self._original_images, bg_map)

    def reset_background_subtraction(self):
        """Restore original images."""
        self._background_map = np.zeros(self.image_dimensions, dtype=np.float64)
        self.images = self._original_images.copy()

    # ------------------------------------------------------------------
    # Phasor
    # ------------------------------------------------------------------
    def phasor(self, freq=0.25, remove_zero=False):
        """Compute (g,s) phasor coordinates for every pixel.

        Parameters
        ----------
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
        from .phasor import compute_phasor
        return compute_phasor(
            self.images, self.axis_values, freq=freq, remove_zero=remove_zero
        )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify(self, classifier, downsample_factor=1, norm="minmax"):
        """Classify pixels and store the result matrix in ``self.results``."""
        from .ml import classify_pixels

        matrix, stats = classify_pixels(
            self.images,
            self.mask,
            classifier,
            downsample_factor=downsample_factor,
            norm=norm,
        )
        self.results["class_matrix"] = matrix
        self.results["class_stats"] = stats
        return matrix, stats

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    @classmethod
    def _from_dataclass(cls, data: PPSDataClass):
        pps = cls(data.images, data.axis_values, data.axis_type)
        
        # Restore masks
        if data.masks:
            pps._mask_manager.from_serializable(data.masks)
        
        # Background & original images
        pps._original_images = data.original_images if data.original_images is not None else pps.images.copy()
        pps._background_map = data.background_map if data.background_map is not None else np.zeros(pps.image_dimensions)
        
        pps.results = data.results.copy() if data.results else {}
        pps.filename = data.filename

        return pps
    
    def _to_dataclass(self) -> PPSDataClass:
        return PPSDataClass(
            images=self.images.copy(),
            image_dimensions=self.image_dimensions,
            axis_values=self.axis_values.copy(),
            axis_type=self.axis_type,
            masks=self._mask_manager.to_serializable(),
            original_images=self._original_images.copy(),
            background_map=self._background_map.copy(),
            results=self.results.copy(),
            filename=self.filename,
        )
    
    # ------------------------------------------------------------------
    # Axis helpers
    # ------------------------------------------------------------------
    def get_axis_values(self) -> np.ndarray:
        """Return the 1D coordinate array for the current stack axis."""
        return self.axis_values.copy()

    def get_axis_label(self) -> str:
        """Human-readable label for the stack axis."""
        return "Time delay" if self.axis_type == "time" else "Z position"

    def get_axis_unit(self) -> str:
        """Unit string for the stack axis."""
        return "ps" if self.axis_type == "time" else "µm"