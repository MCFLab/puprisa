# User Guide

## Loading and managing stacks

Open one or more stacks with **File → Open Stack** or the add-stack button. The application accepts TIFF and pickle files in the desktop dialog. Each loaded stack receives a session-local identifier, display colour, name, and visibility state. Selecting a stack makes it the current stack for image viewing and most operations.

For DukeScan TIFF files, Puprisa determines whether the independent axis is time or Z from TIFF page-name metadata (`t = …` or `z = …`). Time delay metadata is read in this order: a legacy `_xaxis.txt` file, TIFF tag 285, and then a companion `.log` file. A time stack must have one recovered delay per image frame.

Use **File → Save Stack as TIFF** to export the current processed images with their axis values embedded in TIFF page metadata. Use **File → Save Stack as Pickle** to preserve the full Puprisa state, including mask layers and background state.

## Viewing a stack

The image view shows one frame of the current stack. Use the slider or the mouse wheel over the image to select a frame. The axis label reports a time in ps for time stacks and a Z position in µm for Z stacks.

The display settings do not change pixel data:

- choose the default pump-probe, `RdBu_r`, viridis, or grey colormap;
- use a standard-deviation range, full data range, or an explicit custom range;
- open a standalone Matplotlib view when you need a separate figure.

## Preprocessing

Preprocessing actions apply to the current stack. They operate on the stack's in-memory data and refresh dependent plots and phasor coordinates.

| Action | Result |
| --- | --- |
| Subtract negative time | Averages all frames with time `< 0` and subtracts the result. This is available only for time stacks with negative-delay frames. |
| Subtract first/last selected frames | Subtracts either a pixelwise map or one scalar derived from selected frame indices. |
| Subtract fixed value | Subtracts a constant from every pixel in every frame. |
| Reset background subtraction | Restores the internal baseline image copy used by background subtraction. |
| Normalize | Divides the stack by the largest absolute value in its average curve. The effective mask can participate in the average calculation. |
| SVD denoise | Reconstructs the image stack from a chosen number of leading singular components. |
| Downsample | Creates a new stack by spatial local-mean downsampling. Existing mask layers and background state are migrated. |
| Stack math | Creates a new scaled, added, subtracted, or divided stack. Input stacks must have matching shapes and compatible axes for two-stack operations. |

!!! warning
    Normalization, background subtraction, and SVD reconstruction modify the selected stack. Save a pickle or TIFF before trying an irreversible analysis variant. Downsampling and stack math create separate derived stacks instead.

## Masks

Masks are layered exclusions. Within a stored mask layer, `True` means *exclude this pixel*. The effective `PPS.mask` is the inverse of the union of enabled exclusions, so `True` there means *include this pixel in analysis*.

You can:

- create an intensity mask using a Gaussian-smoothed absolute-value projection and either Li's automatic threshold or a numeric threshold;
- enable, disable, reverse, rename, or delete individual layers;
- convert a pixel or phasor ROI into an exclusion layer that keeps only the ROI;
- export all layers as JSON and import them later for a matching image shape;
- export one layer as NPZ for external use.

Masks are stack-specific. ROI curves, masked projections, and masked phasor calculations use the effective mask. The main image display itself is not a guarantee that masked pixels have been removed from view; consult the analysis result and mask list.

## Pixel-space ROIs and curves

Select a shape—rectangle, circle, ellipse, or polygon—and add an ROI to the current stack. Drag the ROI in the image scene to refine its geometry. Visible pixel ROIs contribute one average curve each.

For every frame, Puprisa averages pixels inside the ROI *and* inside the stack's effective mask. Curves can be normalized individually by their maximum absolute amplitude. Exported CSV files contain paired `x_n` and `y_<label>` columns; the x values are the stack axis values.

Turning off a stack also turns off its associated ROIs. Deleting a stack removes its ROIs from the session.

## Phasor analysis

Open **Phasor → Phasor Analysis** for a time-axis stack. Puprisa calculates one `(g, s)` coordinate per pixel from the full delay curve using the selected frequency in THz. Pixels excluded by the effective mask receive no phasor coordinate.

The phasor view overlays density maps for all visible stacks and displays a universal-semicircle guide. The current stack also has a spatial projection. Create ROIs in phasor space to select a cluster; the matching pixels are colour-overlaid in the spatial view and their average curves appear below.

Changing the frequency, changing masks, or processing a stack recomputes its phasor cache. Phasor analysis deliberately rejects Z stacks because its transform requires time-delay values.

## Programmatic use

The GUI is optional. Create or load a `PPS` object to use the same numerical operations in a notebook:

```python
from puprisa.core.pps import PPS

pps = PPS.load("my_stack.tif")
pps.apply_background_subtraction(indices=[0, 1, 2], pixelwise=True)
keep_projection = pps.project(mask_on=True)

if pps.axis_type == "time":
    coordinates = pps.phasor(freq=0.25)
```

See [Core API](api/core.md) for the available public methods.
