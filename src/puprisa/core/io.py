import numpy as np
import os
import pandas as pd
from skimage import io
import re
from pathlib import Path
from .data import PPSDataClass
import tifffile

def load_stack(path, axis_type, dataType=None) -> PPSDataClass:
    if dataType is None:
        dataType = _guess_type_from_extension(path)
    if dataType == "DukeScan":
        if axis_type is None:
            axis_type = tiff_page285_axis_hint(path)
        return load_dukescan_stack(path, axis_type=axis_type)
    elif dataType == "pickle":
        return load_pickle_stack(path, axis_type=axis_type)
    elif dataType == "mathematica":
        return load_mathematica_stack(path, axis_type=axis_type)
    else:
        raise ValueError(f"Unknown stack type: {dataType}")
    
def load_dukescan_stack(path, axis_type):
    path = str(path)

    with tifffile.TiffFile(path) as tif:
        # 1. Read all images from the TIFF stack
        images = tif.asarray()

        # 2. Extract axis values based on axis_type
        if axis_type == "time":
            axis_values = extract_time_delays(path)
        elif axis_type == "z":
            axis_values = extract_pos_z(path)
        else:
            raise ValueError('axis_type must be "time" or "z"')

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
        filename=Path(path).name,
    )

def load_mathematica_stack(path, axis_type) -> PPSDataClass:
    if isinstance(path, str):
        temp = _import_mathematica_binary(path)
        images = np.array(temp[0], dtype=np.float64)
        axis_values = np.array(temp[1])
        filename = Path(path).name
        image_dimensions = images[0].shape
    else:
        raise ValueError("path must be a string")
    axis_type = axis_type
    return PPSDataClass(
        images=images,
        image_dimensions=image_dimensions,
        axis_values=axis_values,
        axis_type=axis_type,
        filename=filename,
    )

def load_pickle_stack(path, axis_type):
    import pickle
    with open(path, "rb") as f:
        save_object = pickle.load(f)

        return PPSDataClass(
            images=save_object["images"],
            image_dimensions=save_object["image_dimensions"],
            axis_values = save_object["axis_values"],
            axis_type = save_object["axis_type"],
            masks = save_object.get("masks", {}),
            original_images = save_object.get("original_images", None),
            background_map = save_object.get("background_map", None),
            results = save_object.get("results", {}),
            filename = save_object["filename"],
    )

def export_as_pickle(path, data: PPSDataClass):
    import pickle
    save_object = {
        "images": data.images,
        "image_dimensions": data.image_dimensions,
        "axis_values": data.axis_values,
        "axis_type": data.axis_type,
        "masks": data.masks,
        "original_images": data.original_images,
        "background_map": data.background_map,
        "results": data.results,
        "filename": data.filename,
    }
    with open(path, "wb") as f:
        pickle.dump(save_object, f)

def export_as_tiff(path, images: np.ndarray, axis_values = None, axis_type = None):
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
        "time" -> Tag 285 string: "t = <value> ps"
        "z"    -> Tag 285 string: "z = <value>"
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
                    tag_str = f"t = {axis_values[i]:.6g} ps"
                else:  # "z"
                    tag_str = f"z = {axis_values[i]:.6g}"
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
    2. TIFF tags embedded in the TIFF file (via delays_from_tiff)
    3. DukeScan .log file (via delays_from_log)

    Returns an empty array if all methods fail.

    Parameters
    ----------
    path : str or Path
        Filename of pump-probe stack (TIFF file) from DukeScan.

    Returns
    -------
    np.ndarray
        1D array of time delays in picoseconds. Empty array if extraction fails.

    See Also
    --------
    extract_time_delays_from_tiff : Extract delays from TIFF tag 285
    extract_time_delays_from_log : Extract delays from DukeScan .log file
    """
    # check if (older) x-axis file still exists (case-insensitive .tif)
    p = Path(path)
    if p.suffix.lower() == ".tif":
        p_new = str(p.with_name(p.stem + "_xaxis.txt"))
    else:
        p_new = str(p) + "_xaxis.txt"
    if os.path.isfile(p_new):
        times = pd.read_table(p_new, header=None).iloc[:, 0].to_numpy()
        return times

    # if no x-axis file, try to extract delays from TIFF tags
    try:
        return extract_time_delays_from_tiff(path)
    except Exception as e:
        print("Error extracting delays from TIFF tags:", e)

    # if no x-axis file and no TIFF tags, try extracting delays from log file
    try:
        return extract_time_delays_from_log(path)
    except Exception as e:
        print("Error extracting delays from log file:", e)

    return np.array([])

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
    if p.suffix.lower() == ".tif":
        p_new = str(p.with_suffix(".log"))
    else:
        p_new = str(p) + ".log"
    try:
        with open(p_new, "r", encoding="utf-8") as f:
            log = f.read()
    except UnicodeDecodeError:
        with open(p_new, "r", encoding="latin1") as f:
            log = f.read()

    match = re.search(r"(?:delayArr_ps = )([\-0-9,.]+).*", log)
    if match:
        times = np.array(match.group(1).split(","), dtype=float)
    else:
        print("there was a problem importing time delays with", path)
        times = []
    return times

def extract_time_delays_from_tiff(path):
    """Extract time delays from TIFF tag 285 metadata.

    Reads time delay information embedded in TIFF tag 285 (PageName) for
    each page/frame in the TIFF file. Expected format: "t = <value> ps".

    Parameters
    ----------
    path : str or Path
        Path to the pump-probe stack TIFF file.

    Returns
    -------
    list
        List of time delays in picoseconds, one per TIFF page.

    Notes
    -----
    The function looks for tag 285 values starting with "t = " and ending
    with " ps", extracting the numeric value between them.
    """
    delays = []
    with tifffile.TiffFile(path) as tif:
        for page in tif.pages:
            if 285 in page.tags:
                tag_value = page.tags[285].value
                if isinstance(tag_value, bytes):
                    tag_value = tag_value.decode("utf-8", errors="replace")
                if tag_value.startswith(r"t = "):
                    delay = float(tag_value[4:-3])
                    delays.append(delay)
    return delays

def tiff_page285_axis_hint(path):
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
            if s.startswith("t ="):
                return "time"
            if s.startswith("z ="):
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
    np.ndarray
        1D array of Z positions in µm. Length may differ from number of images;
        caller must validate.

    Raises
    ------
    ValueError
        If no Z positions could be extracted from either TIFF tags or .log file.
    """
    pz = extract_pos_z_from_tiff(path)
    if pz.size > 0:
        return pz

    pz_log = extract_pos_z_from_log(path)
    if pz_log.size > 0:
        return pz_log

    raise ValueError(
        f"Could not extract Z positions from {path}. "
        "Expected TIFF tag 285 (z = ...) or companion .log with posZArr_um."
    )

def extract_pos_z_from_tiff(path):
    """Extract Z positions (µm) from TIFF tag 285 on each page.

    Expects each page's PageName to start with ``z =`` followed by a float
    (legacy MATLAB ``ReadImageStack_TIFF`` convention). Optional text after
    the number is ignored.

    Parameters
    ----------
    path : str or Path
        Multi-page TIFF path.

    Returns
    -------
    np.ndarray
        One Z value per page (µm). Empty array if no ``z =`` entries found.
    """
    values = []
    z_pat = re.compile(
        r"^\s*z\s*=\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)",
        re.IGNORECASE,
    )
    with tifffile.TiffFile(path) as tif:
        for page in tif.pages:
            if 285 not in page.tags:
                continue
            tag_value = page.tags[285].value
            if isinstance(tag_value, bytes):
                tag_value = tag_value.decode("utf-8", errors="replace")
            m = z_pat.match(str(tag_value).strip())
            if m:
                values.append(float(m.group(1)))
    return np.array(values, dtype=np.float64)

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
    np.ndarray
        1D array of Z positions in µm. Empty array if ``posZArr_um`` is not found
        or parsing fails.
    """
    p = Path(path)
    if p.suffix.lower() == ".tif":
        p_log = str(p.with_suffix(".log"))
    else:
        p_log = str(p) + ".log"
    if not os.path.isfile(p_log):
        return np.array([], dtype=np.float64)
    try:
        with open(p_log, "r", encoding="utf-8") as f:
            log = f.read()
    except UnicodeDecodeError:
        with open(p_log, "r", encoding="latin1") as f:
            log = f.read()
    except OSError:
        return np.array([], dtype=np.float64)

    raw = None
    for line in log.splitlines():
        s = line.strip()
        if s.lower().startswith("poszarr_um"):
            m = re.match(r"posZArr_um\s*=\s*(.+)", s, re.IGNORECASE)
            if m:
                raw = m.group(1).strip()
                break
    if not raw:
        return np.array([], dtype=np.float64)
    parts = [x.strip() for x in raw.split(",") if x.strip()]
    if not parts:
        return np.array([], dtype=np.float64)
    try:
        return np.array([float(x) for x in parts], dtype=np.float64)
    except ValueError:
        return np.array([], dtype=np.float64)

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
    # open file as read-binary with no buffering
    f = open(path, "rb", buffering=0)

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

    # close file
    f.close()

    return [images, time]