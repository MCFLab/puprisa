import os
import re
import pickle
from pathlib import Path
from dataclasses import dataclass, field

import warnings

import numpy as np
import pandas as pd
import tifffile


@dataclass
class PPSDataClass:
    images: np.ndarray
    axis_values: np.ndarray
    axis_type: str
    axis_unit: str
    image_dimensions: tuple | None = None
    mask: np.ndarray | None = None
    original_images: np.ndarray | None = None
    background_map: np.ndarray | None = None
    results: dict = field(default_factory=dict)
    filename: str = ""

def load_stack(path, axis_type: str | None, axis_unit: str | None, dataType=None) -> PPSDataClass:
    if dataType is None:
        dataType = _guess_type_from_extension(path)
    if dataType == "DukeScan":
        return load_dukescan_stack(path, axis_type=axis_type, axis_unit=axis_unit)
    elif dataType == "pickle":
        return load_pickle_stack(path)
    elif dataType == "mathematica":
        return load_mathematica_stack(path, axis_type=axis_type, axis_unit=axis_unit)
    else:
        raise ValueError(f"Unknown stack type: {dataType}")
    
def load_dukescan_stack(path, axis_type: str | None, axis_unit: str | None) -> PPSDataClass:
    path = str(path)

    with tifffile.TiffFile(path) as tif:
        # 1. Read all images from the TIFF stack
        images = tif.asarray()

        # 2. Extract axis values and axis unit based on axis_type
        if axis_type is None:
            axis_type = tiff_page285_axis_type_hint(path)
        if axis_type is None:
            raise ValueError(f"Cannot infer axis_type from {path}. ")
        if axis_type == "time":
            extracted_values, extracted_unit = extract_time_delays(path)
        elif axis_type == "z":
            extracted_values, extracted_unit = extract_pos_z(path)
        else:
            raise ValueError('axis_type must be "time" or "z"')
        axis_values = extracted_values
        if axis_unit is None:
            # If user did not specify, use extracted unit
            axis_unit = extracted_unit
        else:
            # If user specified a unit, check for consistency with extracted unit
            if extracted_unit is not None and extracted_unit != axis_unit:
                print(
                    f"Warning: user-specified axis_unit {axis_unit!r} conflicts "
                    f"with extracted unit {extracted_unit!r}; using user-specified "
                    f"{axis_unit!r}."
                )

    images = np.asarray(images, dtype=np.float64)
    original_shape = images.shape
    images = np.squeeze(images)
    if images.ndim == 2:
        images = images[np.newaxis, :, :]
    elif images.ndim == 4:
        if images.shape[0] == 1:
            images = images[0, :, :, :]
        elif images.shape[1] == 1:
            images = images[:, 0, :, :]
        else:
            images = images[0, :, :, :]
    elif images.ndim != 3:
        raise ValueError(f"Unexpected image array shape: {original_shape} -> {images.shape}, expected 3D array [n_images, height, width]")

    n_images = len(images)
    if len(axis_values) != n_images:
        raise ValueError(f"Length of axis_values ({len(axis_values)}) does not match number of images ({n_images})")

    image_dimensions = images[0].shape
    if len(image_dimensions) != 2:
        raise ValueError(f"Expected 2D image dimensions, got {image_dimensions}")

    return PPSDataClass(
        images=images,
        image_dimensions=image_dimensions,
        axis_values=axis_values,
        axis_type=axis_type,
        axis_unit=axis_unit,
        filename=Path(path).name,
    )

def load_mathematica_stack(path, axis_type: str | None, axis_unit: str | None) -> PPSDataClass:
    temp = _import_mathematica_binary(path)
    images = np.array(temp[0], dtype=np.float64)
    axis_values = np.array(temp[1])
    filename = Path(path).name
    image_dimensions = images[0].shape
    
    return PPSDataClass(
        images=images,
        image_dimensions=image_dimensions,
        axis_values=axis_values,
        axis_type=axis_type,
        axis_unit=axis_unit,
        filename=filename,
    )

def load_pickle_stack(path) -> PPSDataClass:
    with open(path, "rb") as f:
        save_object = pickle.load(f)

    if "axis_values" in save_object:
        return PPSDataClass(
            images=save_object["images"],
            image_dimensions=save_object["image_dimensions"],
            axis_values=save_object["axis_values"],
            axis_type=save_object["axis_type"],
            axis_unit=save_object.get("axis_unit", "ps"),
            mask=save_object.get("mask", None),
            original_images=save_object.get("original_images", None),
            background_map=save_object.get("background_map", None),
            results=save_object.get("results", {}),
            filename=save_object["filename"],
        )

    # Legacy support for older pickle files that used "times" instead of "axis_values"
    # Will be removed in future versions.
    return PPSDataClass(
        images=save_object["images"],
        image_dimensions=save_object["image_dimensions"],
        axis_values=save_object["times"],
        axis_type="time",
        axis_unit="ps",
        mask=save_object.get("mask", None),
        original_images=None,
        background_map=None,
        results={},
        filename=save_object["filename"],
    )

def export_as_pickle(path, data: PPSDataClass):
    save_object = {
        "images": data.images,
        "image_dimensions": data.image_dimensions,
        "axis_values": data.axis_values,
        "axis_type": data.axis_type,
        "axis_unit": data.axis_unit,
        "mask": data.mask,
        "original_images": data.original_images,
        "background_map": data.background_map,
        "results": data.results,
        "filename": data.filename,
    }
    with open(path, "wb") as f:
        pickle.dump(save_object, f)

def export_as_tiff(path, images: np.ndarray, axis_values = None, axis_type = None, axis_unit = None):
    """Save a 3D image stack to a multi-page TIFF file, embedding axis values.

    Parameters
    ----------
    path : str or Path
        Output filename for the TIFF stack.
    images : np.ndarray
        3D array of shape (n_frames, height, width) to save as a TIFF stack.
    axis_values : np.ndarray, optional
        1D array of axis values (one per frame). If None, only images are saved.
    axis_type : str, optional
        Must be provided if axis_values are given. Either "time" or "z".
        "time" -> Tag 285 string: "t = <value> <unit>"
        "z"    -> Tag 285 string: "z = <value> <unit>"
    axis_unit : str, optional
        The unit of the axis values. If None, defaults to "ps" for time and "um" for z.
    """
    if images.ndim != 3:
        raise ValueError(f"Expected 3D array for images, got shape {images.shape}")

    if axis_values is not None:
        if axis_values.ndim != 1 or len(axis_values) != images.shape[0]:
            raise ValueError(
                f"axis_values must be 1D array of length {images.shape[0]}, "
                f"got shape {axis_values.shape}"
            )
        if axis_type not in ["time", "z"]:
            raise ValueError(f"axis_type must be 'time' or 'z', got {axis_type}")

    with tifffile.TiffWriter(path, imagej=False) as tif:
        for i in range(images.shape[0]):
            frame = images[i].astype(np.float32)
            extras = []
            if axis_values is not None:
                if axis_type == "time":
                    unit = axis_unit or 'ps'
                    tag_str = f"t = {axis_values[i]:.6g} {unit}"
                else:  # "z"
                    unit = axis_unit or 'um'
                    tag_str = f"z = {axis_values[i]:.6g} {unit}"
                extras = [(285, 's', len(tag_str), tag_str.encode('utf-8'), False)]
            tif.write(
                frame,
                photometric='minisblack',  # or 'miniswhite' depending on your data
                metadata=None,
                extratags=extras
            )

# ---------------------------------------------------------------------
# 2. Auxiliary functions for extracting time delays from DukeScan files
# ---------------------------------------------------------------------
def extract_time_delays(path):
    """Import time delays from DukeScan files with cascading fallback.

    Attempts to read time delay information using multiple methods in order:
    1. Legacy _xaxis.txt file (older format)
    2. RegA Lab dat file (via extract_time_delays_from_dat)
    3. TIFF tags embedded in the TIFF file (via delays_from_tiff)
    4. DukeScan .log file (via delays_from_log)

    Returns an empty array if all methods fail.

    Parameters
    ----------
    path : str or Path
        Filename of pump-probe stack (TIFF file) from DukeScan.

    Returns
    -------
    tuple[numpy.ndarray, str | None]
        Array of delay values and their unit (or None if extraction fails).

    See Also
    --------
    extract_time_delays_from_dat : Extract delays from RegA Lab dat file
    extract_time_delays_from_tiff : Extract delays from TIFF tag 285
    extract_time_delays_from_log : Extract delays from DukeScan .log file
    """
    # 1. Legacy _xaxis.txt file (older format)
    p = Path(path)
    if p.suffix.lower() in {".tif", ".tiff"}:
        p_new = str(p.with_name(p.stem + "_xaxis.txt"))
    else:
        p_new = str(p) + "_xaxis.txt"
    if os.path.isfile(p_new):
        times = pd.read_table(p_new, header=None).iloc[:, 0].to_numpy()
        return times, 'ps'

    # 2. RegA Lab dat file
    try:
        values, unit = extract_time_delays_from_dat(path)
        if values.size > 0:
            return values, unit
    except (OSError, ValueError) as exc:
        warnings.warn(
            f"Could not read time delays from the .dat for {path}: {exc}",
            RuntimeWarning,
        )

    # 3. If no x-axis file, try TIFF tag 285
    try:
        values, unit = extract_time_delays_from_tiff(path)
        if values.size > 0:
            return values, unit
    except (OSError, ValueError, tifffile.TiffFileError) as exc:
        warnings.warn(
            f"Could not read time delays from TIFF metadata in {path}: {exc}",
            RuntimeWarning,
        )

    # 4. DukeScan log
    try:
        values, unit = extract_time_delays_from_log(path)
        if values.size > 0:
            return values, unit
    except (OSError, ValueError) as exc:
        warnings.warn(
            f"Could not read time delays from the log for {path}: {exc}",
            RuntimeWarning,
        )

    return np.array([], dtype=np.float64), None

def extract_time_delays_from_log(path):
    """Extract time delays from DukeScan .log file.

    Parses the delayArr_ps field from the DukeScan log file using regex.
    Supports all four DukeScan channels (_DS_CH1 through _DS_CH4) and
    handles both UTF-8 and Latin-1 file encodings.

    Parameters
    ----------
    path : str or Path
        Path to the pump-probe stack TIFF file. The .log file is inferred
        by replacing _DS_CH#.tif with .log.

    Returns
    -------
    np.ndarray or list
        1D array of time delays in picoseconds extracted from the log file.
        Returns empty list if delayArr_ps pattern not found.

    Notes
    -----
    The function searches for the pattern "delayArr_ps = <values>" in the
    log file and extracts comma-separated numeric values.
    """
    # Companion .log next to the TIFF (any _DS_CH#; case-insensitive .tif/.TIF)
    p = Path(path)
    if p.suffix.lower() in {".tif", ".tiff"}:
        log_path = p.with_suffix(".log")
    else:
        log_path = Path(f"{p}.log")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            log = f.read()
    except UnicodeDecodeError:
        with open(log_path, "r", encoding="latin1") as f:
            log = f.read()
    except OSError:
        return np.array([], dtype=np.float64), None

    match = re.search(r"(?:delayArr_ps = )([\-0-9,.]+).*", log)
    if match:
        times = np.array(match.group(1).split(","), dtype=float)
    else:
        raise ValueError(f"Could not find delayArr_ps in {log_path}.")
    return times, 'ps'

def extract_time_delays_from_tiff(path):
    """Extract time delays and their unit from TIFF tag 285 metadata.

    Each page's tag 285 (PageName) is expected to contain a string like
    ``"t = <value> <unit>"`` (e.g. ``"t = 1.6 ms"``).  The unit is
    extracted from the trailing word. If no unit is present, ``None`` 
    is returned for the unit.

    Returns
    -------
    tuple[numpy.ndarray, str]
        Array of delay values and the unit string.
    """
    delays = []
    unit = None
    # Match "t = <number> <unit>"
    pattern = re.compile(
        r'^\s*t\s*=\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*([a-zA-Zµ]+)?\s*$',
        re.IGNORECASE,
    )
    with tifffile.TiffFile(path) as tif:
        for page in tif.pages:
            if 285 not in page.tags:
                continue
            tag_value = page.tags[285].value
            if isinstance(tag_value, bytes):
                tag_value = tag_value.decode("utf-8", errors="replace")
            match = pattern.match(str(tag_value).strip())
            if match:
                delays.append(float(match.group(1)))
                if unit is None and match.group(2):
                    unit = match.group(2).strip().lower()
                elif unit is not None and match.group(2) and unit != match.group(2).strip().lower():
                    print(f"Warning: inconsistent units in TIFF tags")
    if not delays:
        return np.array([], dtype=np.float64), None
    return np.array(delays, dtype=np.float64), unit

def extract_time_delays_from_dat(path):
    """Extract time delays and unit from a DukeScan companion ``.dat`` file.

    Typical DukeScan ``.dat`` header contains comment lines starting with
    ``#``, including ``# xUnits = ps``. Following the comments there may be
    a single marker line (e.g. ``pos``) and then one value per line, or
    multiple columns separated by whitespace. The first column is used as
    the axis values.

    Parameters
    ----------
    path : str or Path
        TIFF path whose companion ``.dat`` file is read.

    Returns
    -------
    tuple[numpy.ndarray, str | None]
        Array of axis values and their unit (or None if missing).
        Empty array if the ``.dat`` file cannot be parsed.
    """
    p = Path(path)
    stem = p.stem
    #  Remove channel suffixes like _DS_CH1, _CH1, etc. to find the base .dat file
    #  foo_DS_CH1.tif -> foo.dat
    #  foo_CH1.tif    -> foo.dat
    #  foo.tif        -> foo.dat
    stem = re.sub(r"(?:^|_)(?:DS_)?CH\d+$", "", stem, flags=re.IGNORECASE)
    dat_path = p.with_name(f"{stem}.dat")
    if not dat_path.exists():
        return np.array([], dtype=np.float64), None
    
    values: list[float] = []
    unit: str | None = None
    data_started = False

    try:
        with open(dat_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                if s.startswith("#"):
                    match = re.search(r"xUnits\s*=\s*([^\s#]+)", s, re.IGNORECASE)
                    if match:
                        unit = match.group(1).strip().lower()
                    continue
                tokens = s.split()
                if not tokens:
                    continue
                if not data_started:
                    try:
                        float(tokens[0])
                        data_started = True
                    except ValueError:
                        continue
                if data_started:
                    try:
                        values.append(float(tokens[0]))
                    except ValueError:
                        continue
    except OSError:
        return np.array([], dtype=np.float64), None
    if not values:
        return np.array([], dtype=np.float64), None
    return np.array(values, dtype=np.float64), unit

def tiff_page285_axis_type_hint(path):
    """Inspect first TIFF page tag 285 (PageName) for *t* vs *z* prefix.

    Returns ``\"t\"``, ``\"z\"``, or ``None`` if missing/unrecognized (caller may still load).
    """
    try:
        with tifffile.TiffFile(path) as tif:
            if not tif.pages:
                return None
            page = tif.pages[0]
            if 285 not in page.tags:
                return None
            tag_value = page.tags[285].value
            if isinstance(tag_value, bytes):
                tag_value = tag_value.decode("utf-8", errors="replace")
            s = str(tag_value).strip().lower()
            if re.match(r'^\s*t\s*=', s, re.IGNORECASE):
                return "time"
            if re.match(r'^\s*z\s*=', s, re.IGNORECASE):
                return "z"
            return None
    except Exception:
        return None

# -----------------------------------------------------
# 3. Auxiliary functions for extracting Z positions from DukeScan files
# -----------------------------------------------------
def extract_pos_z(path):
    """Resolve Z positions (µm): TIFF ``z =`` tags first, then companion ``.log``.

    This is the main entry point for Z-position extraction. It raises if neither
    source provides any Z values; caller is responsible for checking the array length.

    Parameters
    ----------
    path : str or Path
        DukeScan TIFF path.

    Returns
    -------
    tuple[numpy.ndarray, str | None]
        1D array of Z positions in µm and their unit (or None if extraction fails).
        Length may differ from number of images; caller must validate.

    Raises
    ------
    ValueError
        If no Z positions could be extracted from either TIFF tags or .log file.
    """
    pz, unit = extract_pos_z_from_tiff(path)
    if pz.size > 0:
        return pz, unit

    pz_log, unit = extract_pos_z_from_log(path)
    if pz_log.size > 0:
        return pz_log, unit

    raise ValueError(
        f"Could not extract Z positions from {path}. "
        "Expected TIFF tag 285 (z = ...) or companion .log with posZArr_um."
    )

def extract_pos_z_from_tiff(path):
    """Extract Z positions and their unit from TIFF tag 285 on each page.

    Each page's PageName is expected to contain a string like
    ``"z = <value> <unit>"`` (e.g. ``"z = 12.5 um"``).  The unit is
    extracted from the trailing word; if no unit is present, ``"um"`` is
    assumed (legacy MATLAB ``ReadImageStack_TIFF`` convention).

    Parameters
    ----------
    path : str or Path
        Multi-page TIFF path.

    Returns
    -------
    tuple[numpy.ndarray, str | None]
        Array of Z position values and the unit string.
        Empty array and ``None`` if no ``z =`` entries found.
    """
    values = []
    unit = None
    # Match "z = <number> <unit>
    z_pat = re.compile(
        r'^\s*z\s*=\s*'
        r'([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)'
        r'\s*([a-zA-Z]+)?\s*$',
        re.IGNORECASE,
    )

    with tifffile.TiffFile(path) as tif:
        for page in tif.pages:
            if 285 not in page.tags:
                continue
            tag_value = page.tags[285].value
            if isinstance(tag_value, bytes):
                tag_value = tag_value.decode("utf-8", errors="replace")
            match = z_pat.match(str(tag_value).strip())
            if match:
                values.append(float(match.group(1)))
                extracted_unit = match.group(2)
                if extracted_unit is not None:
                    extracted_unit = extracted_unit.strip().lower()
                    if unit is None:
                        unit = extracted_unit
                    elif unit != extracted_unit:
                        print(f"Warning: inconsistent units in TIFF tags: {unit} vs {extracted_unit}")
    if not values:
        return np.array([], dtype=np.float64), None
    return np.array(values, dtype=np.float64), unit

def extract_pos_z_from_log(path):
    """Extract Z positions (µm) from a DukeScan companion ``.log`` file (silent if missing).

    Reads ``[StackConfig]`` field ``posZArr_um = -1.0,2.0,...`` as used for Z-stack
    acquisitions (``fileType = ZS``, ``multiDepth = 1``). Same path rule as
    :meth:`delays_from_log`: ``path/to/stack.tif`` -> ``path/to/stack.log``.

    Parameters
    ----------
    path : str or Path
        Path to the TIFF stack; the ``.log`` next to it is opened.

    Returns
    -------
    tuple[numpy.ndarray, str | None]
        1D array of Z positions in µm and their unit (or None if extraction fails).
        Length may differ from number of images; caller must validate.
    """
    p = Path(path)
    if p.suffix.lower() == ".tif":
        p_log = str(p.with_suffix(".log"))
    else:
        p_log = str(p) + ".log"
    try:
        with open(p_log, "r", encoding="utf-8") as f:
            log = f.read()
    except UnicodeDecodeError:
        with open(p_log, "r", encoding="latin1") as f:
            log = f.read()
    except OSError:
        return np.array([], dtype=np.float64), None

    raw = None
    for line in log.splitlines():
        s = line.strip()
        if s.lower().startswith("poszarr_um"):
            m = re.match(r"posZArr_um\s*=\s*(.+)", s, re.IGNORECASE)
            if m:
                raw = m.group(1).strip()
                break
    if not raw:
        return np.array([], dtype=np.float64), None
    parts = [x.strip() for x in raw.split(",") if x.strip()]
    if not parts:
        return np.array([], dtype=np.float64), None
    try:
        return np.array([float(x) for x in parts], dtype=np.float64), 'um'
    except ValueError:
        return np.array([], dtype=np.float64), None

def _guess_type_from_extension(path):
    """Guess the stack type based on file extension."""
    ext = Path(path).suffix.lower()
    if ext in [".tif", ".tiff"]:
        return "DukeScan"
    elif ext in [".pkl", ".pickle"]:
        return "pickle"
    elif ext in [".m", ".mathematica"]:
        return "mathematica"
    else:
        raise ValueError(f"Unknown stack type for extension: {ext}")

def _import_mathematica_binary(path):
    """Load pump-probe stack saved in Mathematica binary format.

    The format consists of binary data with dimensions followed by time axis
    and image data. Images are stored as float64 values.

    Parameters
    ----------
    path : str
        Path to the Mathematica format file.

    Returns
    -------
    list
        List containing [images, time_axis] where images is a list of 2D arrays
        and time_axis is a 1D array of time delays.
    """
    with open(path, "rb", buffering=0) as f:
        # import first three int16 which are the time, x and y dimension
        # convert dim to int64, because int16 is not big enougth for
        # multiplications
        dim = np.fromfile(f, dtype=np.int16, count=3)
        dim = dim.astype(np.int64)

        # import the time axis
        time = np.fromfile(f, dtype=np.float64, count=dim[0])

        # import stack, loop over time dimension dim[0] and reshape to image
        # dimensions
        images = []
        for i in range(dim[0]):
            temp = np.fromfile(f, dtype=np.float64, count=dim[1] * dim[2])
            images.append(temp.reshape((dim[1], dim[2])))
        
        return [images, time]