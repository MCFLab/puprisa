import os
import re
import sys
import pandas as pd


def convert_windows_to_linux_path(win_path, linux_mnt="/mnt/W/"):
    """Convert Windows path to Linux path"""
    return win_path.replace("W:\\", linux_mnt).replace("\\", "/")


def adjust_roi(row):
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


def get_elpis(
    path_elpis, path_georgia, os_type="win", wavelength="770-730", melanoma_only=True
):
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

    # adjust paths and drop useless columns based on operating system
    if sys.platform == os_type:
        df_elpis["folder_eva"] = df_elpis["folder"] + "_evaluation"
        df_elpis = df_elpis.drop(
            columns=["stitched", "surgical ink", "pixel / scan ampli"]
        )
        df_elpis["folder"] = df_elpis["folder"].apply(convert_windows_to_linux_path)
        df_elpis["folder_eva"] = df_elpis["folder_eva"].apply(
            convert_windows_to_linux_path
        )

    elif sys.platform == "win32":
        df_elpis["folder_eva"] = df_elpis["folder"] + "_evaluation"
        df_elpis = df_elpis.drop(
            columns=["stitched", "surgical ink", "pixel / scan ampli"]
        )

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
