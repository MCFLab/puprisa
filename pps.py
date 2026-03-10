# -*- coding: utf-8 -*-
"""
Pump-Probe Spectroscopy (PPS) Analysis Module

This module provides comprehensive tools for analyzing pump-probe spectroscopy imaging data,
with a focus on time-resolved transient absorption microscopy.

Classes
-------
PPS
    Main class for pump-probe stack analysis and visualization. Handles data import from
    multiple formats (DukeScan, Mathematica, pickle), processing (normalization, masking,
    downsampling), and analysis (phasor, classification, thresholding).

Functions
---------
main
    Example usage and testing function demonstrating phasor analysis workflow.

Key Features
------------
- Import from multiple data formats (DukeScan, Mathematica, pickle)
- Time delay selection and averaging
- Background subtraction and normalization
- Spatial masking and ROI analysis
- Phasor analysis for frequency domain visualization
- Machine learning classification support
- Intensity threshold-based segmentation
- Image projection and downsampling
- Linear combination of multiple stacks

Example Usage
-------------
>>> # Load a pump-probe stack from DukeScan format
>>> stack = PPS("data_DS_CH1.tif", dataType="DukeScan")
>>>
>>> # Subtract background and normalize
>>> stack.subtractFirst(n=3)
>>> stack.normalize(norm="minmax")
>>>
>>> # Apply intensity threshold masking
>>> stack.intensity_threshold(threshold=0.1, sigma=5)
>>>
>>> # Perform phasor analysis
>>> phasor_data = stack.phasor(freq=0.25, remove_zero=True)
>>> stack.phasor_show(freq=0.25)
>>>
>>> # Save processed stack
>>> stack.save("processed_stack.pkl")

Notes
-----
The PPS class maintains image stacks with associated time delays and spatial masks.
All analysis methods respect the mask attribute to focus on regions of interest.

Created on Thu May 11 14:25:04 2023
@author: david
"""
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib as mlp
from skimage import io
from skimage.transform import downscale_local_mean
import re
from pathlib import Path
import tifffile


class PPS:

    def __init__(self, data, dataType="DukeScan", filename="unkown", mask=None):
        """
        Import and initialize a pump-probe stack.

        Supports multiple input formats including DukeScan TIFF files (including
        stitched ImageJ files), Mathematica binary format, pickle files, and raw
        [images, delays] arrays. Automatically extracts time delays and generates
        a mask based on non-zero pixels.

        Parameters
        ----------
        data : str, Path, or [images, delays]
            If str or Path: filename of DukeScan (.tif), Mathematica, or pickle
            (.pkl) file. For DukeScan, handles both standard and stitched ("stich")
            files. If array: data in form of [images, delays].
        dataType : str, optional
            Format type: "mathematica", "DukeScan", "pickle", or "data".
            Default is "DukeScan".
        filename : str, optional
            If dataType="data", this string is saved as the filename attribute.
            Default is "unkown".
        mask : np.ndarray of bool, optional
            Boolean array to set as the mask. If None, automatically generates
            mask from non-zero pixels in the projected image. Default is None.

        Returns
        -------
        None.

        Notes
        -----
        For DukeScan files, time delays are extracted using time_delays() which
        checks for _xaxis.txt files, TIFF tags, or .log files in that order.
        Stitched files (containing "stich" in filename) are read with tifffile
        to handle different TIFF levels.

        """
        if dataType == "mathematica":
            if isinstance(data, str):
                temp = PPS._import_stack_mathematica(data)
                self.images = np.array(temp[0], dtype=np.float64)
                self.times = np.array(temp[1])
                self.filename = data
                self.image_dimensions = self.images[0].shape
                # check if there are 0 value pixel and derive mask
                # becasue there is no mask array yet we can obviously not use
                # it to create the mask here:
                self.mask = self.project(maskOn=False) != 0

        elif dataType == "DukeScan":
            # convert Path to string because skimage.io.imread_collection does not accept Path objects
            if isinstance(data, Path):
                data = str(data)

            self.times = np.array(PPS.time_delays(data))

            # pump-probe stacks that were stitched together with ImageJ have less levels compared with
            # with DukeScan generated files. Also I introduced a typo into all filenames, I know it
            # should be stitched instead of stich...
            if "stich" in data:
                with tifffile.TiffFile(str(data)) as tif:
                    self.images = np.array(
                        [page.asarray() for page in tif.pages], dtype=np.float64
                    )
            else:
                self.images = np.array(io.imread_collection(data)[0], dtype=np.float64)

            self.filename = data
            self.image_dimensions = self.images[0].shape

            # check if there are 0 value pixel and derive mask
            # becasue there is no mask array yet we can obviously not use it to
            # create the mask here:
            self.mask = self.project(maskOn=False) != 0

        elif dataType == "pickle":
            import pickle

            with open(data, "rb") as f:
                save_object = pickle.load(f)

            self.images = save_object["images"]
            self.times = save_object["times"]
            self.filename = save_object["filename"]
            self.image_dimensions = save_object["image_dimensions"]
            self.mask = save_object["mask"]

        elif dataType == "data":
            if isinstance(data, (str, Path, os.PathLike)):
                print("Data is a string or PathLike, expected [images, delays] array.")
                return None
            self.images = np.array(data[0], dtype=np.float64)
            self.times = np.array(data[1])
            self.filename = filename
            self.image_dimensions = self.images[0].shape

            # deal with mask
            if mask is None:
                # check if there are 0 value pixel and derive mask
                # becasue there is no mask array yet we can obviously not use
                # it to create the mask here:
                self.mask = self.project(maskOn=False) != 0

            else:
                self.mask = mask

        else:
            print("PPS constructor failed")

        self.results = {}

    def save(self, filename):
        """
        Save stack (PPS instance) into filename.

        Parameters
        ----------
        filename : str
            Filename of saved stack.

        Returns
        -------
        None.

        """
        import pickle

        save_object = {
            "images": self.images,
            "times": self.times,
            "filename": self.filename,
            "image_dimensions": self.image_dimensions,
            "mask": self.mask,
        }

        with open(filename, "wb") as f:
            pickle.dump(save_object, f)

    @staticmethod
    def time_delays(fn):
        """Import time delays from DukeScan files with cascading fallback.

        Attempts to read time delay information using multiple methods in order:
        1. Legacy _xaxis.txt file (older format)
        2. TIFF tags embedded in the TIFF file (via delays_from_tiff)
        3. DukeScan .log file (via delays_from_log)

        Returns an empty array if all methods fail.

        Parameters
        ----------
        fn : str or Path
            Filename of pump-probe stack (TIFF file) from DukeScan.

        Returns
        -------
        np.ndarray
            1D array of time delays in picoseconds. Empty array if extraction fails.

        See Also
        --------
        delays_from_tiff : Extract delays from TIFF tag 285
        delays_from_log : Extract delays from DukeScan .log file
        """
        # check if (older) x-axis file still exists
        fn_new = fn.replace(".tif", "_xaxis.txt")
        if os.path.isfile(fn_new):

            times = pd.read_table(fn_new, header=None).iloc[:, 0].to_numpy()
            return times

        # if no x-axis file, try to extract delays from TIFF tags
        try:
            return PPS.delays_from_tiff(fn)
        except Exception as e:
            print("Error extracting delays from TIFF tags:", e)

        # if no x-axis file and no TIFF tags, try extracting delays from log file
        try:
            return PPS.delays_from_log(fn)
        except Exception as e:
            print("Error extracting delays from log file:", e)

        return np.array([])

    @staticmethod
    def delays_from_log(filename):
        """Extract time delays from DukeScan .log file.

        Parses the delayArr_ps field from the DukeScan log file using regex.
        Supports all four DukeScan channels (_DS_CH1 through _DS_CH4) and
        handles both UTF-8 and Latin-1 file encodings.

        Parameters
        ----------
        filename : str
            Filename of pump-probe stack TIFF file. The .log file is inferred
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
        # import conventional log file
        if filename.endswith("_DS_CH1.tif"):
            fn_new = filename.replace("_DS_CH1.tif", ".log")
        elif filename.endswith("_DS_CH2.tif"):
            fn_new = filename.replace("_DS_CH2.tif", ".log")
        elif filename.endswith("_DS_CH3.tif"):
            fn_new = filename.replace("_DS_CH3.tif", ".log")
        elif filename.endswith("_DS_CH4.tif"):
            fn_new = filename.replace("_DS_CH4.tif", ".log")
        try:
            with open(fn_new, "r", encoding="utf-8") as f:
                log = f.read()
        except UnicodeDecodeError:
            with open(fn_new, "r", encoding="latin1") as f:
                log = f.read()

        fn_new = filename.replace("_DS_CH1.tif", ".log")

        with open(fn_new, "r") as f:
            log = f.read()
        match = re.search(r"(?:delayArr_ps = )([\-0-9,.]+).*", log)
        if match:
            times = np.fromstring(match.group(1), dtype=float, sep=",")
        else:
            print("there was a problem importing time delays with", filename)
            times = []
        return times

    @staticmethod
    def delays_from_tiff(filename):
        """Extract time delays from TIFF tag 285 metadata.

        Reads time delay information embedded in TIFF tag 285 (PageName) for
        each page/frame in the TIFF file. Expected format: "t = <value> ps".

        Parameters
        ----------
        filename : str or Path
            Filename of pump-probe stack TIFF file.

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
        with tifffile.TiffFile(filename) as tif:
            for page in tif.pages:
                if 285 in page.tags:
                    tag_value = page.tags[285].value
                    if tag_value.startswith(r"t = "):
                        delay = float(tag_value[4:-3])
                        delays.append(delay)
        return delays

    @staticmethod
    def _substack_index_1d(size_image, size_sub):
        """Compute 1D substack indices for dividing an image dimension.

        Parameters
        ----------
        size_image : int
            Total size of the image dimension.
        size_sub : int
            Size of each sub-image along this dimension.

        Returns
        -------
        np.ndarray
            2D array where each row contains [start_index, end_index] for a sub-image.
        """
        # comput number of sub images along 1-d
        n_sub_images = int(np.ceil(size_image / size_sub))

        index = []
        for i in range(n_sub_images):
            if (i + 1) * size_sub < size_image:
                index.append([i * size_sub, (i + 1) * size_sub])
            else:
                index.append([i * size_sub, size_image])
        return np.array(index)

    def _substack_index(self, size):
        """Compute 2D substack indices for both image dimensions.

        Parameters
        ----------
        size : int
            Size of each sub-image in both x and y dimensions.

        Returns
        -------
        list
            List containing [index_x, index_y] where each is a 2D array of indices.
        """
        index_x = PPS._substack_index_1d(self.image_dimensions[0], size)
        index_y = PPS._substack_index_1d(self.image_dimensions[1], size)
        return [index_x, index_y]

    @staticmethod
    def _import_stack_mathematica(filename):
        """Load pump-probe stack saved in Mathematica binary format.

        The format consists of binary data with dimensions followed by time axis
        and image data. Images are stored as float64 values.

        Parameters
        ----------
        filename : str
            Path to the Mathematica format file.

        Returns
        -------
        list
            List containing [images, time_axis] where images is a list of 2D arrays
            and time_axis is a 1D array of time delays.
        """
        # open file as read-binary with no buffering
        f = open(filename, "rb", buffering=0)

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
        f.close

        return [images, time]

    def average_times(self, time_averages, inplace=True):
        """Average multiple time delay images together to reduce noise.

        This method replaces the original time delays and images with averaged
        versions based on the specified groupings.

        Parameters
        ----------
        time_averages : list of lists
            Each inner list contains time delay values to be averaged together.
            Example: [[0.1, 0.15], [0.5, 0.55]] will create two new averaged images.
        inplace : bool, optional
            If True, modifies this instance's times and images in place.
            Default is True.

        Returns
        -------
        PPS
            A PPS instance with the averaged times and images. If inplace is True,
            the current instance is modified and a new instance with the same
            data is returned. If inplace is False, the current instance remains
            unchanged and a new instance with averaged data is returned.
        """
        # find indicies of time delays to be averaged -> positions
        positions = []
        for j in time_averages:
            temp_j = []
            for i in j:
                temp = np.argwhere(np.array(self.times) == i)[0, 0]
                temp_j.append(temp)
            positions.append(temp_j)

        # compute avegrae time delays and images
        new_times = []
        new_images = []
        for i in positions:
            new_times.append(np.mean(np.array(self.times)[i]))
            new_images.append(np.mean(self.images[i], axis=0))

        # redefine time delays and image stacks
        if inplace:
            self.times = np.array(new_times)
            self.images = np.array(new_images)
            return self

        else:
            return PPS(
                [np.array(new_images), np.array(new_times)],
                mask=self.mask,
                filename=self.filename,
                dataType="data",
            )

    def select_delays(self, delays="melanoma1", inplace=True):
        """Select and filter specific time delays from the image stack.

        Reduces the stack to only the specified time delays, useful for
        focusing analysis on specific time windows.

        Parameters
        ----------
        delays : str or list of float, optional
            Time delays to keep. If "melanoma1", uses a predefined set of
            delays optimized for melanoma analysis. Otherwise, provide a list
            of time delay values (in ps) to retain. Default is "melanoma1".

            The "melanoma1" preset includes delays:
            [-1.0, -0.5, -0.1, 0.0, 0.1, 0.25, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
             2.5, 2.0, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
             15.0, 20.0, 29.0, 40.0, 50.0, 60.0, 70.0, 80.0]
        inplace : bool, optional
            If True, modifies this instance's times and images in place.
            Default is True.

        Returns
        -------
        PPS
            A PPS instance with the selected time delays. If inplace is True,
            the current instance is modified and a new instance with the same
            data is returned. If inplace is False, the current instance remains
            unchanged and a new instance with selected delays is returned.
        """
        # check if delays are standard delays for machine learning melanoma
        # attempts
        if (type(delays) is str) and (delays == "melanoma1"):
            delays = [
                -1.0,
                -0.5,
                -0.1,
                0.0,
                0.1,
                0.25,
                0.5,
                0.6,
                0.7,
                0.8,
                0.9,
                1.0,
                2.5,
                2.0,
                3.0,
                3.5,
                4.0,
                4.5,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                15.0,
                20.0,
                29.0,
                40.0,
                50.0,
                60.0,
                70.0,
                80.0,
            ]
        # find array indicies of delays
        pos = []
        for i in delays:
            pos.append(np.where(self.times == i)[0][0])

        # redefine time delays and image stacks
        if inplace:
            self.times = np.array(self.times[pos])
            self.images = np.array(self.images[pos])
            return self

        else:
            return PPS(
                [np.array(self.images[pos]), np.array(self.times[pos])],
                mask=self.mask,
                filename=self.filename,
                dataType="data",
            )

    def subtractFirst(self, n=1, inplace=True):
        """Subtract average of first n images from entire stack.

        Performs background subtraction by removing the average of early time
        delays (typically negative delays before pump pulse arrives).

        Parameters
        ----------
        n : int, optional
            Number of initial images to average for background subtraction.
            Default is 1.
        inplace : bool, optional
            If True, modifies this instance. If False, returns new instance.
            Default is True.

        Returns
        -------
        PPS
            Background-subtracted stack. Returns self if inplace=True, otherwise
            returns new PPS instance.
        """
        mean = np.mean(self.images[:n], axis=0)
        images_subtracted = self.images - mean
        if inplace:
            self.images = np.array(images_subtracted)
            return self
        else:
            return PPS(
                [np.array(images_subtracted), np.array(self.times)],
                mask=self.mask,
                filename=self.filename,
                dataType="data",
            )

    def normalize(self, norm="minmax", inPlace=False):
        """
        Normalize pp stack.

        Parameters
        ----------
        norm : str, optional
            Normalization method. Currently supports 'minmax' which normalizes
            by the maximum absolute value. Default is 'minmax'.
        inPlace : bool, optional
            If True, modifies this instance in place. If False, returns a new
            normalized PPS instance. Default is False.

        Returns
        -------
        PPS
            Normalized PPS stack. If inPlace is True, returns self; otherwise
            returns a new instance.
        """
        if norm is None:
            pass
        elif norm == "minmax":
            avg = self.avg()
            extremum = np.max(np.abs([np.min(avg), np.max(avg)]))

        if inPlace:
            self.images = self.images / extremum
            return self
        else:
            return PPS(
                [self.images / extremum, self.times], mask=self.mask, dataType="data"
            )

    def avg(self, maskOn=True, norm=None):
        """
        Compute average TA curve of pp stack.

        Parameters
        ----------
        maskOn : Boolean, optional
            Use mask for computation. The default is True.
        norm : str, optional
            Use norm for avg computation, i.e. minmax. The default is None.

        Returns
        -------
        avg : np array of float
            Averaged TA curve.

        """
        if maskOn is True:
            avg = [np.mean(i[self.mask]) for i in self.images]
        else:
            avg = [np.mean(i) for i in self.images]

        if norm is None:
            pass
        elif norm == "minmax":
            extremum = np.max(np.abs([np.min(avg), np.max(avg)]))
            if extremum != 0:
                avg = avg / extremum

        return avg

    def avg_ta(self, size=-1, maskOn=True, norm=None, cutoff=10):
        """
        Compute average TA curves of substacks of given size.

        Parameters
        ----------
        size : int, optional
            Size of substacks. If -1 average over whole stack is computed.
            The default is -1.
        maskOn : Boolean, optional
            Use mask for computation. The default is True.
        norm : str, optional
            Use norm for avg computation, i.e. minmax. The default is None.
        cutoff : int, optional
            If substack has less than cutoff non-zero pixel this substack in
            particular is discarded. The default is 10.

        Returns
        -------
        ta_curves : list of np array of float
            List of averaged TA curves.
        """
        # average over whole stack
        if size == -1:
            ta_curves = np.array([np.array(self.avg(norm=norm, maskOn=maskOn)).ravel()])
        # average over substacks of given size
        else:
            # compute substacks and average TA curves
            substacks = self.substacks(size=size, cutoff=cutoff)
            ta_curves = [
                np.array(i.avg(norm=norm, maskOn=maskOn)).ravel() for i in substacks
            ]

        return ta_curves

    def avg_show(self, maskOn=True, norm=None, ax=None):
        """Display the average transient absorption curve.
        Parameters
        ----------
        maskOn : bool, optional
            If True, use mask for computation. Default is True.
        norm : str, optional
            Normalization method (e.g., 'minmax'). Default is None.
        ax : matplotlib.axes.Axes, optional
            Axes to plot on. If None, creates new figure.
        Returns
        -------
        matplotlib.axes.Axes
            The axes object containing the plot.
        """
        if ax is None:
            fig, ax = plt.subplots()
            show_plot = True
        else:
            show_plot = False

        ax.plot(self.times, self.avg(maskOn=maskOn, norm=norm))
        ax.set_xlabel("Time")
        ax.set_ylabel("$\Delta A$")
        ax.grid(True)

        if show_plot:
            plt.show()

        return ax

    def project(self, maskOn=True):
        """
        Compute projection (sum of abs) of pp stack.

        Parameters
        ----------
        maskOn : Boolean, optional
            Use mask. The default is True.

        Returns
        -------
        result : 2d nparray
            Projection (sum and abs) of pp stack.

        """
        result = np.zeros(self.image_dimensions, dtype=np.float64)
        for i in self.images:
            np.add(result, np.abs(i), out=result)

        if maskOn is True:
            result = result * self.mask

        return result

    def total(self, maskOn=True):
        """
        Compute sum (no abs values) of stack.

        Parameters
        ----------
        maskOn : Boolean, optional
            Use mask. The default is True.

        Returns
        -------
        total : 2d np array
            Sum of all images in stack.

        """
        # compute sum of pp stack
        total = np.sum(self.images, axis=0)

        # apply mask
        if maskOn is True:
            total = np.where(self.mask, total, 0)

        return total

    def project_show(self, maskOn=True, export=None, ax=None):
        """
        Display pp stack projection.
        Parameters
        ----------
        maskOn : Boolean, optional
            Use mask. The default is True.
        export : str, optional
            Saves plot into export. The default is None.
        ax : matplotlib.axes.Axes, optional
            Axes to plot on. If None, creates new figure.
        Returns
        -------
        matplotlib.axes.Axes
            The axes object containing the plot.
        """
        # Choose a base colormap
        base_cmap = mlp.cm.get_cmap("viridis")
        # Create a new colormap from the base, setting the first color (for 0)
        # to white
        new_colors = base_cmap(np.linspace(0, 1, 256))
        new_colors[0, :] = np.array([1, 1, 1, 1])  # RGBA for white
        new_cmap = mlp.colors.ListedColormap(new_colors)

        if ax is None:
            fig, ax = plt.subplots()
            show_plot = True
        else:
            fig = ax.get_figure()
            show_plot = False

        cax = ax.imshow(self.project(maskOn=maskOn), cmap=new_cmap)
        fig.colorbar(cax, ax=ax)  # Specify which ax the colorbar is for

        if export is not None:
            plt.savefig(export, transparent=True)

        if show_plot:
            plt.show()

        return ax

    def mask_slices(self, slices):
        """
        Set mask of slices to 0.

        Parameters
        ----------
        slices : list of slices
            Areas to mask out in, i.e. array(
                [[slice(None, None, None), slice(None, None, None)]],
                dtype=object
                )

        Returns
        -------
        None.

        """
        if slices is not None:
            for i in slices:
                self.mask[i] = False

    def count_nonzero_pixel(self):
        """Count the number of non-zero pixels in the stack projection.

        Returns
        -------
        int
            Number of non-zero pixels in the projected stack.
        """
        return np.count_nonzero(self.project())

    def substacks(self, size, cutoff=0):
        """Divide stack into smaller spatial substacks.

        Creates non-overlapping substacks of specified size, useful for
        analyzing spatial heterogeneity or processing large images in chunks.

        Parameters
        ----------
        size : int
            Side length of square substacks in pixels.
        cutoff : int, optional
            Minimum number of non-zero pixels required for a substack to be
            included in the output. Default is 0 (include all).

        Returns
        -------
        list of PPS
            List of PPS instances, each containing a spatial subregion of the
            original stack with the same time delays.
        """
        stacks = []
        [index_x, index_y] = self._substack_index(size)

        for i in index_x:
            for j in index_y:
                temp_stack = PPS(
                    [self.images[:, i[0] : i[1], j[0] : j[1]], self.times],
                    dataType="data",
                    filename=self.filename,
                    mask=self.mask[i[0] : i[1], j[0] : j[1]],
                )
                if temp_stack.count_nonzero_pixel() >= cutoff:
                    stacks.append(temp_stack)

        return stacks

    def downsample(self, size, obsolete_version=False, inplace=False):
        """Downsample the stack to reduce resolution and improve SNR.

        Uses local mean downsampling to average neighboring pixels, reducing
        spatial resolution while improving signal-to-noise ratio.

        Parameters
        ----------
        size : int
            Downsampling factor. Each dimension is reduced by this factor.
        obsolete_version : bool, optional
            If True, use the older implementation. Default is False.

        Returns
        -------
        PPS
            New downsampled PPS instance with reduced image dimensions.
        """
        if obsolete_version:
            return self._downsample_obsolete(size)

        images_ds = [downscale_local_mean(img, (size, size)) for img in self.images]
        mask_ds = downscale_local_mean(self.mask.astype(float), (size, size)) > 0

        if inplace:
            self.images = np.array(images_ds)
            self.mask = np.array(mask_ds)
            self.image_dimensions = self.images[0].shape
            return self

        else:
            return PPS(
                [np.array(images_ds), np.array(self.times)],
                dataType="data",
                filename=self.filename,
                mask=np.array(mask_ds),
            )

    def _downsample_obsolete(self, size):
        """
        Downsample stack by factor size.

        Parameters
        ----------
        size : int
            Size of new pixel in downsampled stack.

        Returns
        -------
        PPS stack
            Downsampled stack with reduced resolution and better SNR.

        """
        # create indicies for avergaing and an empty template
        erg = []
        mask = []
        [index_x, index_y] = self._substack_index(size)
        len_x = len(index_x)
        len_y = len(index_y)

        # loop over k(time delays), x(i) and y(j) and average
        for k in range(0, len(self.times)):
            temp = np.zeros((len_x, len_y), dtype=float)
            for i in range(0, len_x):
                for j in range(0, len_y):
                    block = self.images[
                        k,
                        index_x[i][0] : index_x[i][1],
                        index_y[j][0] : index_y[j][1],
                    ]
                    temp[i, j] = np.mean(block)
            erg.append(temp)

        mask = np.full((len_x, len_y), fill_value=True)
        for i in range(0, len_x):
            for j in range(0, len_y):
                block = self.mask[
                    index_x[i][0] : index_x[i][1],
                    index_y[j][0] : index_y[j][1],
                ]
                mask[i, j] = np.any(block)

        print(mask)
        try:
            print(mask.dtype)
        except:
            print("mask is apparently not an np array")
        print(type(mask))

        return PPS(
            [erg, self.times],
            dataType="data",
            filename=self.filename,
            mask=mask,
        )

    def classify(self, classifier, downsample=1, norm="minmax"):
        """Classify each pixel using a trained classifier.

        Applies a machine learning classifier to the transient absorption curve
        of each pixel to identify different material types or states.

        Parameters
        ----------
        classifier : sklearn classifier
            Trained classifier with predict() method and classes_ attribute.
        downsample : int, optional
            Downsampling factor before classification. Default is 1 (no downsampling).
        norm : str, optional
            Normalization method for TA curves. Default is 'minmax'.

        Returns
        -------
        None
            Results stored in self.results dictionary with keys:
            'pigments' : class names
            'stats' : classification statistics
            'matrix' : 2D array of class assignments
        """
        # generate 1 pixel stacks of downasmpled stack
        stack_ds = self.downsample(downsample)
        stacks = stack_ds.substacks(1, cutoff=-1)

        # writes all classes into instance attribute
        self.results["pigments"] = classifier.classes_

        # initialize counter, traces and color coding for each class
        traces = []
        counter_classes = {}
        color_numerical = {}
        j = 1
        for i in classifier.classes_:
            counter_classes[i] = 0
            color_numerical[i] = j
            j += 1

        # classify and count classifications
        for i in stacks:
            temp = i.avg(norm=norm)
            if np.abs(np.sum(temp)) == 0:
                traces.append(0)
            else:
                status = classifier.predict([temp])[0]
                for j in classifier.classes_:
                    if status == j:
                        counter_classes[j] += 1
                        traces.append(color_numerical[j])
                        break

        # re-shape array back into matrix form
        result_matrix = np.array(traces).reshape(stack_ds.image_dimensions)

        # compute ratios in pixel stats
        total = 0
        for i in classifier.classes_:
            total += counter_classes[i]
        for i in classifier.classes_:
            counter_classes[i + "_n"] = counter_classes[i] / total
        self.results["stats"] = counter_classes
        self.results["matrix"] = result_matrix

    def classify_accuracy(self, correct_classes):
        """Compute classification accuracy for known correct classes.

        Evaluates how well the classification identified the expected classes
        in the sample.

        Parameters
        ----------
        correct_classes : list of str
            List of class names that should be present in the sample.

        Returns
        -------
        None
            Updates self.results['stats'] with 'correct_identified' and
            'correct_percentage' keys.
        """
        # check if stack has been classified already
        correct_percentage = 0
        correct_identified = []
        pigments = self.results["pigments"]
        sorted_subset = sorted(
            pigments, key=lambda k: self.results["stats"][k], reverse=True
        )
        counter = 0
        if self.results == {}:
            print("stack has not been classified")
        else:
            for i in correct_classes:
                correct_percentage += self.results["stats"][i + "_n"]
                if i in sorted_subset[:2]:
                    counter += 1
                    correct_identified.append(i)

        self.results["stats"]["correct_identified"] = correct_identified
        self.results["stats"]["correct_percentage"] = correct_percentage

    def classify_show(
        self, classifier, downsample=1, norm="minmax", export=None, alpha=1
    ):
        """Classify and display false-color classification map.

        Runs classification and creates a visualization showing which class
        was assigned to each pixel.

        Parameters
        ----------
        classifier : sklearn classifier
            Trained classifier with predict() method and classes_ attribute.
        downsample : int, optional
            Downsampling factor before classification. Default is 1.
        norm : str, optional
            Normalization method for TA curves. Default is 'minmax'.
        export : str, optional
            If provided, saves the figure to this filename. Default is None.
        alpha : float, optional
            Transparency of the classification overlay. Default is 1 (opaque).

        Returns
        -------
        None
            Displays a matplotlib figure with color-coded classification results.
        """
        n = len(classifier.classes_)

        # classify stack with classifier
        self.classify(classifier, downsample=downsample, norm=norm)

        # generate false coloring
        set1_colors = [
            "white",
            "#d62728",
            "#1f77b4",
            "#ff7f0e",
            "#8c564b",
            "#2ca02c",
            "#17becf",
            "gold",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
        ]
        cmap = mlp.colors.ListedColormap(set1_colors[: n + 1])

        # create label
        label = []
        for i in classifier.classes_:
            a = self.results["stats"][i + "_n"]
            label.append(i + " " + f"{a*100:.2f} %")
        label = np.insert(label, 0, "nothing")

        # plotting
        fig, ax = plt.subplots()
        im = ax.matshow(
            self.results["matrix"],
            cmap=cmap,
            vmin=-0.5,
            vmax=n + 0.5,
            alpha=alpha,
        )
        cax = fig.colorbar(im, ticks=np.arange(0, n + 1))
        cax.set_ticks(np.arange(0, n + 1), labels=label)
        # im = ax.imshow([[0,1,2],[3,3,5],[6,7,0]], cmap=cmap)
        # cbar = fig.colorbar(im, ax=ax)
        # cbar.set_ticks(np.linspace(0.5, n-0.5, num=8), labels=label)
        # cbar = plt.colorbar(cax, ticks=np.linspace(1, n+2, num=n+1),
        #                    fraction=0.046, pad=0.1)
        # cbar.ax.set_yticklabels(label)
        ax.set_title(self.filename)

        if export is None:
            plt.show()
        else:
            plt.savefig(export, transparent=True)
            plt.show()

    def phasor(self, freq=0.25, remove_zero=False):
        """Compute phasor coordinates for all pixels.

        Transforms time-domain TA curves into frequency-domain phasor
        representation (g, s) coordinates. Useful for visualizing dynamics
        and identifying different decay patterns.

        Parameters
        ----------
        freq : float, optional
            Phasor analysis frequency in THz. Default is 0.25 THz.
        remove_zero : bool, optional
            If True, exclude pixels with all-zero TA curves from analysis.
            Default is False.

        Returns
        -------
        np.ndarray
            2D array of phasor coordinates [g, s] for each pixel. Shape is
            (n_pixels, 2).
        """
        # define sin, cos of time delays, and prepare list containing TA curve
        # of each pixel
        self.freq = freq * 2 * np.pi
        self.sin = np.sin(self.times * self.freq)
        self.cos = np.cos(self.times * self.freq)
        self.ta_curves = self._phasor_flatten_stack(remove_zero=remove_zero)

        self.phasor_coor = np.apply_along_axis(
            self._phasor_compute, axis=1, arr=self.ta_curves
        )

        return self.phasor_coor

    def phasor_show(self, freq=0.25, remove_zero=True, color="red", ax=None):
        """Compute and display phasor plot with semicircular boundaries.
        Creates a 2D histogram of phasor coordinates overlaid on the universal
        semicircle, which represents the theoretical bounds for single-exponential
        decay processes.
        Parameters
        ----------
        freq : float, optional
            Phasor analysis frequency in THz. Default is 0.25 THz.
        remove_zero : bool, optional
            If True, exclude pixels with all-zero TA curves. Default is True.
        color : str, optional
            Base color for the phasor histogram. Default is 'red'.
        ax : matplotlib.axes.Axes, optional
            Axes to plot on. If None, creates new figure.
        Returns
        -------
        matplotlib.axes.Axes
            The axes object containing the plot.
        """
        # compute phasor
        self.phasor(freq=freq, remove_zero=remove_zero)
        # compute semi circle
        theta = np.linspace(-(np.pi) / 2, np.pi / 2, 100)
        x1 = (1 - np.sin(theta)) / 2
        y1 = np.cos(theta) / 2
        x2 = (-1 + np.sin(-theta)) / 2
        y2 = -np.cos(-theta) / 2
        x = np.concatenate((x1, x2))
        y = np.concatenate((y1, y2))
        # define false color scheme
        colors = [
            (plt.cm.colors.to_rgba(color, alpha)) for alpha in np.linspace(0, 1, 256)
        ]
        cmapp = mlp.colors.LinearSegmentedColormap.from_list("transparent_red", colors)

        if ax is None:
            fig, ax = plt.subplots(1, 1)
            show_plot = True
        else:
            show_plot = False

        # plot semicircle
        ax.plot(x, y, linestyle="dashed", color="grey")
        # plot phasor histogram
        ax.hist2d(
            self.phasor_coor[:, 0],
            self.phasor_coor[:, 1],
            bins=(np.arange(-1, 1, 0.01), np.arange(-1, 1, 0.01)),
            cmap=cmapp,
        )
        # other plot settings
        ax.set_aspect("equal")  # Set the aspect ratio to equal
        ax.grid(True)
        ax.set_xlabel("g")
        ax.set_ylabel("s")
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_title("phasor frequency: " + str(self.freq / 2 / np.pi))

        if show_plot:
            plt.show()

        return ax

    def _phasor_flatten_stack(self, remove_zero=False):
        """Flatten stack into array of transient absorption curves.

        Parameters
        ----------
        remove_zero : bool, optional
            If True, remove pixels with all-zero TA curves. Default is False.

        Returns
        -------
        np.ndarray
            2D array where each row is a TA curve for one pixel.
        """
        # flatten images into list of TA curves
        ta_curves = self.images.reshape(len(self.times), -1).T
        if remove_zero is True:
            ta_curves = ta_curves[np.all(ta_curves != 0, axis=1)]

        return ta_curves

    def _phasor_compute(self, ta_curve):
        """Compute phasor coordinates for a single TA curve.

        Calculates the real (g) and imaginary (s) phasor coordinates by
        projecting the TA curve onto cosine and sine basis functions.

        Parameters
        ----------
        ta_curve : np.ndarray
            1D array containing the transient absorption values at each time delay.

        Returns
        -------
        np.ndarray
            Array [g, s] containing the phasor coordinates.
        """
        norm = np.sum(np.abs(ta_curve))
        phasor_coor = np.array(
            [
                np.dot(self.cos, ta_curve) / norm,
                np.dot(self.sin, ta_curve) / norm,
            ]
        )
        return phasor_coor

    def intensity_threshold(
        self, threshold="Li", sigma=5, projection_use_mask=True, inplace=False
    ):
        """
        Compute intensity threshold mask.

        Compute stack projection with absolute value and derive intensity
        thresholded mask, either by Li threshold or by numeric value threshold.

        Parameters
        ----------
        threshold : str or number, optional
            If Li a Li threshold cutoff is used, if numeric this number is used
            as cutoff for the mask. The default is 'Li'.
        sigma : numeric, optional
            Gaussian filter sigma. The default is 5.
        projection_use_mask : boolean, optional
            If False the mask of this stack is not used for the projection.
            The default is True.
        inplace : boolean, optional
            Update current mask if True. The default is False.

        Returns
        -------
        None.

        """
        # import filter
        from skimage import filters

        # compute intensity projection and do gaussian smoothing
        projection = filters.gaussian(
            self.project(maskOn=projection_use_mask), sigma=sigma
        )
        mask_zero = projection != 0

        # compute mask
        if threshold == "Li":
            cutoff = filters.threshold_li(projection[mask_zero])
            mask = self.mask & np.where(projection > cutoff, True, False)

        elif isinstance(threshold, (int, float)):
            mask = self.mask & np.where(projection > threshold, True, False)
        else:
            print("invalid use of threshold variable")

        if inplace:
            self.mask = mask
            return self

        else:
            return PPS(
                [self.images, self.times],
                dataType="data",
                filename=self.filename,
                mask=mask,
            )

    @staticmethod
    def intensity_threshold_shared(stacks, threshold, sigma=5):
        """
        Return intensity threshold mask based on multiple pump-probe stacks.

        Absolute value of all images in all stacks are summed up, Gaussian
        filtered and intensity thresholded with cutoff.

        Parameters
        ----------
        stacks : list of stacks
            list of stacks.
        threshold : number
            cutoff threshold.
        sigma : float, optional
            Sigma value for Gaussian filter. The default is 5.

        Returns
        -------
        array of booleans
            Intensity mask.

        """
        from skimage.filters import gaussian

        # combine all images into single array
        all_images = np.concatenate([i.images for i in stacks])

        # compute projection
        projection = gaussian(
            np.sum([np.abs(i) for i in all_images], axis=0), sigma=sigma
        )

        # return mask
        return np.where(projection > threshold, True, False)

    def mask_show(self):
        """
        Show mask and masked projection of stack.

        Returns
        -------
        None.

        """
        # --- Custom colormap for the "normal" image ---
        base_cmap = mlp.cm.get_cmap("viridis")
        new_colors = base_cmap(np.linspace(0, 1, 256))
        new_colors[0, :] = np.array([1, 1, 1, 1])  # lowest value → white
        new_cmap = mlp.colors.ListedColormap(new_colors)

        # --- Discrete colormap for mask ---
        low_color = mlp.cm.get_cmap("viridis")(0.0)  # violet/blue end
        high_color = new_cmap(1.0)  # yellow end
        cmap_mask = mlp.colors.ListedColormap([low_color, high_color])

        bounds = [0, 1, 2]
        norm_mask = mlp.colors.BoundaryNorm(bounds, cmap_mask.N)

        # --- Side-by-side plots ---
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))

        # Left: binary mask
        cax1 = axes[0].imshow(self.mask, cmap=cmap_mask, norm=norm_mask)
        axes[0].set_title("Mask")
        axes[0].axis("off")
        fig.colorbar(cax1, ax=axes[0], ticks=[0, 1], fraction=0.046, pad=0.04)

        # Right: normal image with custom cmap
        cax2 = axes[1].imshow(self.project(), cmap=new_cmap)
        axes[1].set_title("Image")
        axes[1].axis("off")
        cb2 = fig.colorbar(cax2, ax=axes[1], fraction=0.046, pad=0.04)

        # Put ticks at the edges of the colorbar
        vmin, vmax = cax2.get_clim()
        cb2.set_ticks([vmin, vmax])
        cb2.ax.set_yticklabels([f"{vmin:.2f}", f"{vmax:.2f}"])

        plt.tight_layout()
        plt.show()

    def mask_update(self, mask):
        """
        Update mask of stack with mask.

        The mask property of this stack is updated (logical and) with mask.

        Parameters
        ----------
        mask : array of bool
            Mask to be updated with.

        Returns
        -------
        None.

        """
        self.mask = self.mask & mask

    @staticmethod
    def linear_combination(stack1, coeff1, stack2, coeff2):
        """Compute linear combination of two pump-probe stacks.

        Creates a new stack from the weighted sum of two input stacks. Useful
        for background subtraction, signal averaging, or creating difference
        maps. Time delays must match between stacks.

        Parameters
        ----------
        stack1 : PPS
            First stack for linear combination.
        coeff1 : float
            Coefficient (weight) for stack1.
        stack2 : PPS
            Second stack for linear combination.
        coeff2 : float
            Coefficient (weight) for stack2.

        Returns
        -------
        PPS or None
            New PPS instance containing coeff1 * stack1 + coeff2 * stack2.
            Returns None if time delays don't match between stacks.
        """
        if np.allclose(stack1.times, stack2.times):
            images = coeff1 * stack1.images + coeff2 * stack2.images
            mask = stack1.mask & stack2.mask
            return PPS([images, stack1.times], mask=mask)
        else:
            print("time delays of stack1 and stack2 differ")
            return None


def main(): ...


if __name__ == "__main__":
    main()
