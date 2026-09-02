import numpy as np
from puprisa.core.mask import PPSMask, MaskItem
from puprisa.core.io import PPSDataClass, load_stack, export_as_tiff, export_as_pickle
from puprisa.core.process import gaussian_threshold_mask

class PPS:
    """
    Pump Probe Image Stack (PPS) class for handling 3D image stacks with associated axis values and analysis masks.

    Parameters
    ----------
    images : np.ndarray
        Stack with shape (n_frames, height, width).
    axis_values : np.ndarray
        1D coordinate for each frame. Interpretation depends on
        ``stack_axis``. Time delays are in ps; Z positions are in um.
    axis_type : {"time", "z"}
        Type of the axis values. "time" for time delays, "z" for Z positions.
    axis_unit : str, optional
        Unit of the axis values. Supported units depend on axis_type:
        - time: "ps", "ns", "us", "ms", "s"
        - z: "um", "mm", "cm"
        Defaults based on axis_type and ``axis_unit`` (or "ps"/"um" if None).
    """

    def __init__(self, images: np.ndarray, axis_values: np.ndarray, axis_type: str = "time", axis_unit: str = "ps"):

        self.images = np.asarray(images, dtype=np.float64, copy=True)
        if self.images.ndim != 3:
            raise ValueError(f"Expected 3D image stack [n_frames, h, w], got {self.images.shape}")
        if self.images.shape[0] == 0 or self.images.shape[1] == 0 or self.images.shape[2] == 0:
            raise ValueError("Image stack dimensions must all be non-zero")
        self.image_dimensions = self.images[0].shape

        self.axis_values = np.asarray(axis_values, dtype=np.float64, copy=True)
        if len(self.axis_values) != len(self.images):
            raise ValueError("axis_values length must match number of frames")
        if not np.all(np.isfinite(self.axis_values)):
            raise ValueError("axis_values must contain only finite values")
        
        self.axis_type = axis_type
        if axis_type == "time":
            self.axis_unit = axis_unit or "ps"
            if self.axis_unit not in ("ps", "ns", "us", "ms", "s"):
                raise ValueError(f"Invalid axis_unit for time axis: {self.axis_unit!r}. Must be one of ('ps', 'ns', 'us', 'ms', 's').")
        elif axis_type == "z":
            self.axis_unit = axis_unit or "um"
            if self.axis_unit not in ("um", "mm", "cm"):
                raise ValueError(f"Invalid axis_unit for z axis: {self.axis_unit!r}. Must be one of ('um', 'mm', 'cm').")
        else:
            raise ValueError(f"Invalid axis_type: {axis_type!r}. Must be 'time' or 'z'.")

        # Mask handler
        self._mask_handler = PPSMask(self.image_dimensions)

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
    def load(cls, path, axis_type: str | None = None, axis_unit: str | None = None, dataType = None):
        """Load a stack from file via ``core.io``.

        Parameters
        ----------
        path : str or Path
            Path to the stack file.
        axis_type : {"time", "z"}, optional
            Type of the axis values. "time" for time delays, "z" for Z positions.
            If None, it will be guessed from the file (e.g. from TIFF metadata).
        axis_unit : str, optional
            Unit of the axis values.
            Supported units: "ps", "ns", "us", "ms", "s" for time; "um", "mm", "cm" for Z.
            If None, it will be guessed from the file (e.g. from TIFF metadata).
        dataType : str, optional
            Type of the data. If None, it will be guessed from the file extension.

        Returns
        -------
        PPS instance with the loaded data.
        """
        data = load_stack(path, axis_type=axis_type, axis_unit=axis_unit, dataType=dataType)
        return cls._from_dataclass(data)

    def save(self, path, format="tiff"):
        data = self._to_dataclass()
        if format == "tiff":
            export_as_tiff(path, data.images, axis_values=data.axis_values, axis_type=data.axis_type, axis_unit=data.axis_unit)
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
        return self._mask_handler.get_effective_mask()

    def add_mask(self, mask, label="", enabled=True, mask_id=None):
        return self._mask_handler.add_mask(mask, label=label, enabled=enabled, mask_id=mask_id)

    def remove_mask(self, mask_id) -> None:
        self._mask_handler.remove_mask(mask_id)

    def set_mask_enabled(self, mask_id, enabled):
        self._mask_handler.set_mask_enabled(mask_id, enabled)

    def set_mask_label(self, mask_id, label):
        self._mask_handler.set_mask_label(mask_id, label)

    def get_mask(self, mask_id):
        return self._mask_handler.get_mask(mask_id)

    def reverse_mask(self, mask_id) -> None:
        self._mask_handler.reverse_mask(mask_id)

    def get_all_mask_ids(self):
        return self._mask_handler.get_all_mask_ids()

    def get_all_masks(self):
        return self._mask_handler.get_all_masks()

    def get_effective_mask(self):
        return self._mask_handler.get_effective_mask()

    def get_mask_handler(self) -> PPSMask:
        return self._mask_handler

    def clear_all_masks(self):
        self._mask_handler.clear_all_masks()

    def add_mask_from_threshold(self, threshold: str | float = "Li", sigma: float = 5.0, mask_on: bool = False, label: str | None = None) -> str:
        """Add a mask by thresholding the projected intensity.

        The projection is smoothed with a Gaussian filter and then thresholded so
        that pixels with intensities below the threshold are masked out (kept
        disabled), producing a mask of the low-intensity regions.

        Parameters
        ----------
        threshold : str | float, optional
            Intensity threshold below which pixels are masked. Either a float
            value or a string label such as ``"Li"`` selecting a predefined
            threshold (see ``gaussian_threshold_mask``). Defaults to ``"Li"``.
        sigma : float, optional
            Standard deviation of the Gaussian smoothing kernel applied to the
            projection before thresholding. Defaults to ``5.0``.
        mask_on : bool, optional
            If True, restrict the thresholding to the region currently covered
            by this PPS instance's effective mask; otherwise the full projection
            is considered. Defaults to ``False``.
        label : str | None, optional
            Label for the new mask layer. Defaults to ``"Intensity threshold"``.

        Returns
        -------
        str
            The id of the newly created mask layer.
        """
        projection = self.project(mask_on=False)
        effective_mask = np.asarray(self.mask, dtype=bool) if mask_on else None
        keep_mask = gaussian_threshold_mask(projection, threshold=threshold, sigma=sigma, mask=effective_mask)
        label = label or f"Gaussian threshold"
        return self.add_mask(~keep_mask, label=label, enabled=True)

    def load_mask(self, path, format="json") -> None:
        """Load and replace this PPS instance's mask layers."""
        if format == "json":
            import json
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        elif format == "pickle":
            import pickle
            with open(path, "rb") as f:
                data = pickle.load(f)
        else:
            raise ValueError(f"Unsupported format: {format!r}. Use 'json' or 'pickle'.")
        self._mask_handler.from_serializable(data)

    def save_mask(self, path, format="json") -> None:
        data = self._mask_handler.to_serializable()
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
        total = np.sum(np.nan_to_num(self.images, nan=0.0, posinf=0.0, neginf=0.0), axis=0)
        if mask_on:
            total = np.where(self.mask, total, 0)
        return total

    def avg(self, mask_on: bool = True):
        """Compute the average of each frame, optionally applying the mask."""
        if mask_on:
            if not np.any(self.mask):
                return [0.0] * len(self.images)
            # Compute the average of each frame using only the pixels within the mask.
            return np.nanmean(self.images[:, self.mask], axis=1)
        # Compute the average of each frame using all pixels.
        return np.nanmean(self.images, axis=(1, 2))

    def project(self, mask_on: bool = True):
        """Compute the projection of the stack, optionally applying the mask. Projection is defined as the sum of absolute values across frames."""
        from .process import compute_projection

        mask = self.mask if mask_on else None
        return compute_projection(self.images, mask=mask)

    def statistics(self, mask_on: bool = True):
        """Compute basic statistics (min, max, mean, std)."""
        if mask_on:
            if not np.any(self.mask):
                return {
                    "min": 0.0,
                    "max": 0.0,
                    "mean": 0.0,
                    "std": 0.0,
                }
            masked_images = [img[self.mask] for img in self.images]
            all_pixels = np.concatenate(masked_images)
        else:
            all_pixels = self.images.flatten()

        all_pixels = all_pixels[np.isfinite(all_pixels)]
        if not all_pixels.size:
            return {"min": 0.0, "max": 0.0, "mean": 0.0, "std": 0.0}

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

        Parameters
        ----------
        factor : int
            Integer downsampling factor along both spatial axes.

        Returns
        -------
        PPS
            A new PPS instance with resampled images and analysis masks.
        """
        from .process import downsample_local_mean, downsample_mask

        new_images = downsample_local_mean(self.images, factor)
        new_pps = self.__class__(new_images, self.axis_values, axis_type=self.axis_type, axis_unit=self.axis_unit)

        for mask_item in self.get_all_masks():
            mask_downsampled = downsample_mask(mask_item.mask, factor)
            new_pps.add_mask(
                mask_downsampled,
                label=mask_item.label,
                enabled=mask_item.enabled,
                mask_id=mask_item.id,
            )
        new_pps.filename = self.filename

        return new_pps
    
    def substacks(self, size: int, cutoff: int = 0) -> list["PPS"]:
        """Split the stack into non-overlapping square spatial substacks.

        Each substack is a new :class:`PPS` instance that shares the same
        axis values, axis type and axis unit. Every mask layer from this
        stack is cropped to the same spatial region, preserving mask IDs,
        labels and enabled states.

        Edge substacks may be smaller than ``size`` when the image
        dimension is not an exact multiple of ``size``.

        Parameters
        ----------
        size : int
            Side length of the square sub-blocks in pixels.
        cutoff : int, default 0
            Minimum number of non-zero valid projection pixels required
            for a substack to be included. A value of 0 (or negative)
            includes all substacks.

        Returns
        -------
        list of PPS
            New PPS instances in row-major order.
        """
        if not isinstance(size, (int, np.integer)) or size <= 0:
            raise ValueError("size must be a positive integer")

        h, w = self.image_dimensions

        # Compute [start, end) intervals for each axis. Edge blocks are
        # truncated to the image boundary.
        def _intervals(total: int, block: int) -> list[tuple[int, int]]:
            starts = list(range(0, total, block))
            return [(start, min(start + block, total)) for start in starts]
        row_intervals = _intervals(h, size)
        col_intervals = _intervals(w, size)
        substacks: list[PPS] = []

        for r0, r1 in row_intervals:
            for c0, c1 in col_intervals:
                images_sub = self.images[:, r0:r1, c0:c1]
                sub = self.__class__(
                    images_sub,
                    self.axis_values,
                    axis_type=self.axis_type,
                    axis_unit=self.axis_unit,
                )
                # Migrate every mask layer, cropped to this spatial block.
                for mask_item in self.get_all_masks():
                    mask_sub = mask_item.mask[r0:r1, c0:c1]
                    sub.add_mask(
                        mask_sub,
                        label=mask_item.label,
                        enabled=mask_item.enabled,
                        mask_id=mask_item.id,
                    )
                sub.filename = self.filename
                if cutoff > 0:
                    valid_pixels = int(np.count_nonzero(sub.project(mask_on=True)))
                    if valid_pixels < cutoff:
                        continue
                substacks.append(sub)
        return substacks
    
    def normalize(self, norm="minmax", mask_on=True):
        """Normalize the image stack in place (only minmax supported).

        Every pixel is divided by the maximum absolute value of the average
        curve. The background-subtraction state is scaled by the same factor
        to remain consistent.

        Parameters
        ----------
        norm : str or None.
            The normalization method to use.
        mask_on : bool
            Whether to use the effective mask when computing the average curve.

        Returns
        -------
        PPS
            The same PPS instance, with images and background map modified in place.
        """
        from .process import normalize_by_avg_curve

        if norm is None:
            return self
        if norm != "minmax":
            raise ValueError(f"Unsupported norm: {norm!r}")

        # Compute scale factor from ORIGINAL data **before** modifying images.
        avg_curve = np.array(self.avg(mask_on=mask_on), dtype=np.float64)
        scaled_images, scale_factor = normalize_by_avg_curve(self.images, avg_curve)

        # Apply normalization.
        self.images = scaled_images

        # Keep original image and background map consistent.
        if scale_factor > 1e-12:
            self._original_images = self._original_images / scale_factor
            self._background_map = self._background_map / scale_factor

        return self

    def slice(self, indices: list[int]):
        """Create a new PPS instance with only the selected frames.

        Parameters
        ----------
        indices : list of int
            List of frame indices to keep.

        Returns
        -------
        PPS
            A new PPS instance with the selected frames.
        """
        if not indices:
            raise ValueError("No indices provided for slicing.")
        pps_sliced = self.__class__(self.images[indices], self.axis_values[indices], axis_type=self.axis_type, axis_unit=self.axis_unit)
        pps_sliced._mask_handler = self._mask_handler.copy()
        return pps_sliced

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

    def svd_reconstruct(self, n_components: int):
        """
        Reconstruct the stack using only the leading singular components.
        The images are replaced in place.

        Parameters
        ----------
        n_components : int
            Number of leading singular components to retain. Must be between 1
            and min(n_frames, h*w).
        """
        from .process import svd_reconstruct
        try:
            reconstructed_images = svd_reconstruct(self.images, n_components)
        except Exception as e:
            raise ValueError(f"Error occurred while reconstructing images: {e}")
        self.images = reconstructed_images

    # ------------------------------------------------------------------
    # Phasor
    # ------------------------------------------------------------------
    def phasor(self, freq=0.25, use_mask=True):
        """
        Compute (g,s) phasor coordinates for every pixel.

        Parameters
        ----------
        freq : float
            Phasor frequency expressed in the reciprocal unit of
            ``axis_unit`` (e.g. THz for ps, GHz for ns, kHz for ms).
        use_mask : bool
            If True, apply the effective mask to the computation. Pixels outside
            the mask will have NaN coordinates.
        Returns
        -------
        coords : shape (n_pixels, 2) or (n_valid_pixels, 2)
            Columns are ``g`` and ``s``. When ``remove_zero=False``, row order
            matches ``flatten_stack(images)``.
        """
        if self.axis_type != "time":
            raise ValueError("Phasor computation is only valid for time-delay stacks")
        mask = self.mask if use_mask else None
        from .phasor import compute_phasor
        return compute_phasor(self.images, self.axis_values, freq=freq, mask=mask)

    # ------------------------------------------------------------------
    # Operator Overloading
    # ------------------------------------------------------------------
    def __add__(self, other):
        if isinstance(other, PPS):
            self._validate_computable(other, "add")            
            new_images = self.images + other.images
            new_pps = PPS(new_images, axis_values=self.axis_values, axis_type=self.axis_type, axis_unit=self.axis_unit)
            return new_pps
        raise TypeError("Unsupported operand type for +")

    def __sub__(self, other):
        if isinstance(other, PPS):
            self._validate_computable(other, "subtract")
            new_images = self.images - other.images
            new_pps = PPS(new_images, axis_values=self.axis_values, axis_type=self.axis_type, axis_unit=self.axis_unit)
            return new_pps
        raise TypeError("Unsupported operand type for -")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            new_images = self.images * other
            new_pps = PPS(new_images, axis_values=self.axis_values, axis_type=self.axis_type, axis_unit=self.axis_unit)
            return new_pps
        raise TypeError("Unsupported operand type for *")

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                raise ValueError("Cannot divide by zero!")
            new_images = self.images / other
            new_pps = PPS(new_images, axis_values=self.axis_values, axis_type=self.axis_type, axis_unit=self.axis_unit)
            return new_pps
        elif isinstance(other, PPS):
            self._validate_computable(other, "divide")

            from .process import nan_inf_to_zero
            with np.errstate(divide='ignore', invalid='ignore'):
                new_images = np.true_divide(self.images, other.images)
                new_images = nan_inf_to_zero(new_images)  # Replace inf/nan with 0

            new_pps = PPS(new_images, axis_values=self.axis_values, axis_type=self.axis_type, axis_unit=self.axis_unit)
            return new_pps
        raise TypeError("Unsupported operand type for /")

    def _validate_computable(self, other: 'PPS', operation: str) -> None:
        """Raise ValueError when two PPS stacks cannot be combined."""
        if self.images.shape != other.images.shape:
            raise ValueError(f"Cannot {operation} PPS instances with different image shapes.")
        if self.axis_type != other.axis_type:
            raise ValueError(f"Cannot {operation} PPS instances with different axis types.")
        if self.axis_unit != other.axis_unit:
            raise ValueError(f"Cannot {operation} PPS instances with different axis units.")
        if not np.allclose(self.axis_values, other.axis_values):
            raise ValueError(f"Cannot {operation} PPS instances with different axis values.")

    # ------------------------------------------------------------------
    # Visuallization
    # ------------------------------------------------------------------
    def plot_slice(self, slice_index: int, ax=None, colormap: str = "pumpprobe", vmin: float | None = None, vmax: float | None = None, mask_color: tuple[int, int, int] = (200, 200, 200), colorbar: bool = True):
        """Display a single slice of this stack on a Matplotlib axis."""
        from puprisa.core.visualize import plot_slice
        return plot_slice(self, slice_index=slice_index, ax=ax, colormap=colormap, vmin=vmin, vmax=vmax, mask_color=mask_color, colorbar=colorbar)

    def plot_projection(self, ax=None, colormap: str = "gray", vmin: float | None = None, vmax: float | None = None, mask_color: tuple[int, int, int] = (200, 200, 200), colorbar: bool = True):
        """Display the spatial projection of this stack on a Matplotlib axis."""
        from puprisa.core.visualize import plot_projection
        return plot_projection(self, ax=ax, colormap=colormap, vmin=vmin, vmax=vmax, mask_color=mask_color, colorbar=colorbar)
    
    def plot_phasor(self, color_hex: str, freq: float = 0.25, use_mask: bool = True, ax=None, g_lim: tuple[float, float] = (-1.0, 1.0), s_lim: tuple[float, float] = (-1.0, 1.0), size: int = 512, show_semicircle: bool = True):
        """Display the phasor density of this stack on a Matplotlib axis."""
        from puprisa.core.visualize import plot_phasor
        return plot_phasor(self, color_hex=color_hex, freq=freq, use_mask=use_mask, ax=ax, g_lim=g_lim, s_lim=s_lim, size=size, show_semicircle=show_semicircle)
    
    def plot_average_curve(self, ax=None, normalize: bool = False, color: str | None = None, linewidth: float = 1.5):
        """Plot the average curve of this stack on a Matplotlib axis."""
        from puprisa.core.visualize import plot_average_curve
        return plot_average_curve(self, ax=ax, normalize=normalize, color=color, linewidth=linewidth)
    
    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    @classmethod
    def _from_dataclass(cls, data: PPSDataClass):
        pps = cls(data.images, data.axis_values, data.axis_type, data.axis_unit)
        
        # Restore masks
        if data.masks:
            pps._mask_handler.from_serializable(data.masks)
        
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
            axis_unit=self.axis_unit,
            masks=self._mask_handler.to_serializable(),
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
        return self.axis_unit

    def get_phasor_unit(self) -> str:
        """Unit string for the phasor frequency axis."""
        if self.axis_type == "time":
            if self.axis_unit == "ps":
                return "THz"
            if self.axis_unit == "ns":
                return "GHz"
            if self.axis_unit == "us":
                return "MHz"
            if self.axis_unit == "ms":
                return "kHz"
            if self.axis_unit == "s":
                return "Hz"
            raise ValueError("Unknown time unit for phasor frequency")
        if self.axis_type == "z":
            raise ValueError("Phasor frequency is not defined for Z position axis")
        raise ValueError("Unknown axis type for phasor frequency")