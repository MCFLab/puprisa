"""Melanoma sample data management utilities.

This module provides functions for loading, processing, and managing melanoma sample data
from pump-probe imaging experiments. It handles metadata from Excel files, path conversions
for cross-platform compatibility, and extraction of surgical ink mask positions.

Key Features:
    - Load melanoma patient data with recurrence and SLNB information
    - Convert file paths between Windows and Linux systems
    - Extract and adjust region-of-interest (ROI) identifiers
    - Parse manual mask positions for surgical ink locations

Typical Usage:
    >>> df = get_elpis("path/to/elpis.xlsx", "path/to/georgia.xlsx", wavelength="770-730")
    >>> # Returns DataFrame with merged patient and imaging metadata
"""

import os
import re
import sys
import pandas as pd


def convert_windows_to_linux_path(win_path, linux_mnt="/mnt/W/"):
    """Convert Windows file path to Linux-style path.

    Transforms Windows paths (with backslashes and drive letters) to Linux paths
    suitable for mounted Windows drives on Linux systems.

    Args:
        win_path (str): Windows file path (e.g., "W:\\data\\file.tif")
        linux_mnt (str, optional): Linux mount point for Windows drive.
            Defaults to "/mnt/W/".

    Returns:
        str: Linux-style path with forward slashes (e.g., "/mnt/W/data/file.tif")

    Examples:
        >>> convert_windows_to_linux_path("W:\\data\\sample.tif")
        '/mnt/W/data/sample.tif'
        >>> convert_windows_to_linux_path("W:\\data\\sample.tif", "/mnt/win/")
        '/mnt/win/data/sample.tif'
    """
    return win_path.replace("W:\\", linux_mnt).replace("\\", "/")


def adjust_roi(row):
    """Adjust ROI identifier to include slide number.

    Ensures that each region-of-interest (ROI) identifier includes a slide number prefix.
    Extracts slide number from sample identifier and prepends it to the ROI string.
    If no slide number is found, defaults to slide "1".

    Args:
        row (pd.Series): DataFrame row containing 'sample identifier' and 'continent/ROI' columns.
            Expected format for sample identifier: "elpis_<PATIENT_ID>_<SLIDE_NUM>_<SUFFIX>"
            Example: "elpis_AB123_2_A" -> slide number is 2

    Returns:
        str: ROI identifier with slide number prefix (e.g., "2_C01-ROI01")

    Examples:
        Sample identifier "elpis_AB123_2" with ROI "C01-ROI01" -> "2_C01-ROI01"
        Sample identifier "elpis_AB123" with ROI "C01-ROI01" -> "1_C01-ROI01"
        If ROI already has slide number ("2_C01-ROI01"), returns unchanged
    """
    search_string = r"^elpis_([A-Z0-9]+)(_([1-9]))?(?:_[A-Z0-9])?"
    match = re.search(search_string, row["sample identifier"])
    if match:
        if match.group(3) is None:
            result = "1_" + row["continent/ROI"]
        else:
            # does continent/ROI already contain slide number?
            match_roi = re.search(r"^\d_C0\d-ROI\d{2}", row["continent/ROI"])
            if match_roi:
                result = row["continent/ROI"]
            else:
                result = match.group(3) + "_" + row["continent/ROI"]
    else:
        result = "1_" + row["continent/ROI"]

    return result


def get_elpis(path_elpis, path_georgia, wavelength="770-730", melanoma_only=True):
    """Load and merge melanoma patient data with imaging metadata.

    Loads sample imaging metadata from the Elpis experiment Excel file and merges it
    with patient clinical information (recurrence status, sentinel lymph node biopsy results)
    from the Georgia Excel file. Performs path adjustments for cross-platform compatibility,
    extracts surgical ink mask positions, and optionally filters for melanoma samples only.

    Args:
        path_elpis (str): Path to Excel file containing imaging experiment metadata.
            Expected sheet: "propper run 2" for wavelength="770-730"
        path_georgia (str): Path to Excel file containing patient clinical data.
            Expected sheet: "Data" with columns: 'unique', '1=yes recu', 'SLNB'
        wavelength (str, optional): Wavelength combination for data selection.
            Currently only "770-730" is implemented. Defaults to "770-730".
        melanoma_only (bool, optional): If True, filter for melanoma samples only
            (where melanoma column equals 1). Defaults to True.

    Returns:
        pd.DataFrame or None: Merged DataFrame with columns:
            - Sample imaging metadata (folder paths, identifiers, ROI info)
            - Clinical data (recurrence status, SLNB results)
            - Computed fields (folder_eva, adjusted ROI, mask positions)
            Returns None if wavelength is not "770-730".

    Processing Steps:
        1. Load Elpis imaging data and Georgia clinical data
        2. Create evaluation folder paths
        3. Convert paths for Linux systems if needed
        4. Adjust ROI identifiers to include slide numbers
        5. Extract patient IDs from sample identifiers
        6. Parse surgical ink mask positions from CSV files
        7. Merge datasets on patient identifier
        8. Filter for melanoma samples if specified

    Examples:
        >>> df = get_elpis("elpis_data.xlsx", "georgia_data.xlsx")
        >>> # Returns DataFrame with melanoma samples only
        >>>
        >>> df_all = get_elpis("elpis_data.xlsx", "georgia_data.xlsx", melanoma_only=False)
        >>> # Returns DataFrame with all samples

    Notes:
        - On Linux systems, Windows paths are automatically converted using convert_windows_to_linux_path()
        - Sample identifiers follow format: "elpis_<PATIENT_ID>_<SLIDE>_<SUFFIX>"
        - Surgical ink mask positions are loaded from "positions_v03.csv" if available
    """
    if wavelength == "770-730":
        df_elpis = pd.read_excel(path_elpis, sheet_name="propper run 2")
    else:
        print("no wavelength combination besisdes 770-730 has been implemented")
        return None

    # load table that contains recurrence and SLNB information
    df_georgia = pd.read_excel(path_georgia, sheet_name="Data")
    # drop useless columns
    df_georgia = df_georgia[["unique", "1=yes recu", "SLNB"]]
    # rename recurrence column
    df_georgia = df_georgia.rename(columns={"1=yes recu": "recurrence"})

    # create evaluation folder column
    df_elpis["folder_eva"] = df_elpis["folder"] + "_evaluation"

    # adjust paths  based on operating system
    if sys.platform.startswith("linux"):
        df_elpis["folder"] = df_elpis["folder"].apply(convert_windows_to_linux_path)
        df_elpis["folder_eva"] = df_elpis["folder_eva"].apply(
            convert_windows_to_linux_path
        )
        df_elpis["pre-imaging folder"] = df_elpis["pre-imaging folder"].apply(
            convert_windows_to_linux_path
        )

    # drop useless columns
    df_elpis = df_elpis.drop(columns=["stitched", "surgical ink", "pixel / scan ampli"])

    # adjust ROI to contain slide number
    df_elpis["continent/ROI"] = df_elpis.apply(adjust_roi, axis=1)

    # crop sample identifier to solely contain patient identifier
    search_string = r"^elpis_([A-Z0-9]+)(_([1-9]))?(?:_[A-Z0-9])?"
    df_elpis["sample identifier"] = df_elpis["sample identifier"].apply(
        lambda x: re.search(search_string, x).group(1)
    )

    # get manual masks positions for all samples, these masks contain surgical ink locations
    df_elpis["mask manual slices"] = df_elpis.apply(
        lambda x: manual_positions_from_file(x, ds=1), axis=1
    )

    # merge both dataframes
    df = (
        pd.merge(
            df_elpis,
            df_georgia,
            how="left",
            left_on="sample identifier",
            right_on="unique",
        )
        .drop(columns="unique")
        .reset_index(drop=True)
    )

    # filter for melanoma samples only
    if melanoma_only:
        return df[df["melanoma"] == 1].reset_index(drop=True)
    else:
        return df.reset_index(drop=True)


def manual_positions_from_file(row, filename="positions_v03.csv", ds=2):
    """Extract manually annotated mask positions from CSV file.

    Loads surgical ink mask positions that were manually annotated and saved in a CSV file
    within the evaluation directory. Converts position data from center/size format to
    numpy slice objects for image indexing.

    Args:
        row (pd.Series): DataFrame row containing 'folder' column with the base data directory.
        filename (str, optional): Name of the CSV file containing mask positions.
            Defaults to "positions_v03.csv" (format from Mathematica notebook image_preprocessing_v03.nb).
        ds (int, optional): Downsampling factor used during mask creation. Positions are
            scaled by this factor to match original image resolution. Defaults to 2.

    Returns:
        np.ndarray or None: Array of slice tuples for masking, where each element is a tuple
            of (slice_y, slice_x) for indexing 2D images. Returns None if:
            - File does not exist
            - File is empty
            - File parsing fails

    File Format:
        CSV with three columns (no header): center, size, image size
        Each value is formatted as "{x, y}" (e.g., "{512.5, 768.0}")
        Example row: "{512.5, 768.0},{100.0, 150.0},{1024.0, 1536.0}"

    Examples:
        >>> row = pd.Series({'folder': 'W:\\data\\sample001'})
        >>> slices = manual_positions_from_file(row, ds=2)
        >>> # Use slices to mask image: masked_image = image[slices[0]]

    Notes:
        - Positions created with Mathematica notebook image_preprocessing_v03.nb use ds=2
        - Slice boundaries are clipped to image dimensions to prevent indexing errors
        - The evaluation directory is expected to be at <folder>_evaluation
    """
    evaluation_directory = row["folder"] + "_evaluation"
    filename_full = os.path.join(evaluation_directory, filename)

    # for positions files created with mathematica notebook
    # image_preprocessing_v03.nb, downsampling = 2
    if filename == "positions_v03.csv":
        if os.path.isfile(filename_full) is True:
            try:
                df = pd.read_csv(filename_full, names=["center", "size", "image size"])
                if len(df) == 0:
                    slices = None
                else:
                    slices = df.apply(
                        lambda x: row_to_coordinates(x, ds=ds), axis=1
                    ).to_numpy()
            except:
                slices = None
        else:
            slices = None

    return slices


def row_to_coordinates(row, ds):
    """Convert mask position data from center/size format to coordinate slices.

    Parses position strings (in Mathematica format) and converts them to numpy slice
    objects for array indexing. Calculates bounding box coordinates from center position
    and size, then scales by downsampling factor. Ensures coordinates stay within image bounds.

    Args:
        row (pd.Series): DataFrame row with 'center', 'size', and 'image size' columns.
            Each column contains a string in format "{x, y}" (e.g., "{512.5, 768.0}").
        ds (int): Downsampling factor to scale coordinates to original image resolution.
            Coordinates are multiplied by this factor.

    Returns:
        tuple: Tuple of two slice objects (slice_y, slice_x) for 2D array indexing.
            Format: (slice(y_min, y_max), slice(x_min, x_max))

    Coordinate Calculation:
        - x_min = max(0, ds * (center_x - ds * size_x / 2))
        - x_max = min(ds * image_size_x, ds * (center_x + ds * size_x / 2))
        - Similar calculations for y coordinates
        - Boundaries are clipped to [0, ds * image_size] to prevent out-of-bounds indexing

    Examples:
        >>> row = pd.Series({
        ...     'center': '{512.0, 768.0}',
        ...     'size': '{100.0, 150.0}',
        ...     'image size': '{1024.0, 1536.0}'
        ... })
        >>> slices = row_to_coordinates(row, ds=2)
        >>> # Returns: (slice(1336, 1636), slice(824, 1024))
        >>> # Use for indexing: image[slices]

    Notes:
        - First slice (y) corresponds to rows, second slice (x) corresponds to columns
        - Mathematica format uses {x, y} convention (column, row)
        - Output uses Python convention (row, column)
    """
    center = re.search(r"(?:^\{)(\d+.\d*), (\d+.\d*)(?:\}$)", row["center"])
    size = re.search(r"(?:^\{)(\d+.\d*), (\d+.\d*)(?:\}$)", row["size"])
    image_size = re.search(r"(?:^\{)(\d+.\d*), (\d+.\d*)(?:\}$)", row["image size"])

    slices = (
        slice(
            max(0, ds * int(float(center.group(1)) - ds * float(size.group(1)) / 2)),
            min(
                ds * int(float(image_size.group(1))),
                ds * int(float(center.group(1)) + ds * float(size.group(1)) / 2),
            ),
        ),
        slice(
            max(0, ds * int(float(center.group(2)) - ds * float(size.group(2)) / 2)),
            min(
                ds * int(float(image_size.group(2))),
                ds * int(float(center.group(2)) + ds * float(size.group(2)) / 2),
            ),
        ),
    )
    return slices
