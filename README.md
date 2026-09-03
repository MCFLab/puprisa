# Puprisa

**Puprisa** is a desktop and Python toolkit for analysing pump-probe microscopy image stacks. It combines stack loading, preprocessing, spatial and phasor-region analysis, and curve export in one PySide6 application, while keeping the numerical `PPS` API available for notebooks and scripts.

The package is designed for time-resolved transient-absorption data and also supports Z stacks. Time-axis stacks can be analysed in phasor space; Z stacks retain the same loading, masking, plotting, and basic-processing workflow.

## What it provides

- Load DukeScan TIFF stacks, saved Puprisa pickle stacks, and Mathematica binary stacks.
- Recover time delays or Z positions from DukeScan metadata when possible.
- Work with several open stacks and derive new ones through downsampling or stack arithmetic.
- Subtract backgrounds, normalize signals, run truncated-SVD denoising, and control image display ranges.
- Create layered exclusion masks from intensity thresholds or ROI selections.
- Draw rectangular, circular, elliptical, or polygonal ROIs in pixel space.
- Compute phasor coordinates for time-axis stacks, select phasor-space ROIs, and inspect their spatial locations.
- Plot, normalize, and export ROI Average curves as CSV.
- Save processed stacks as TIFF or pickle; save mask layers as JSON.

## Quick start

Puprisa requires Python 3.10 or later. From the repository root:

```bash
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS or Linux
source .venv/bin/activate
```

Install the project in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Launch the desktop application:

```bash
puprisa
```

The checked-in example data can be opened directly from `data/example_stack_DS_CH1.tif`. Its companion log file supplies the time-delay axis.

## Typical workflow

1. Open one or more stacks with **File → Open Stack**.
2. Select a stack, browse frames with the slice control, and choose an appropriate colour scale.
3. Apply background subtraction, normalization, or SVD denoising if required. These operations modify the selected stack; downsampling and stack math instead create a new derived stack.
4. Build an exclusion mask with **Mask → Mask from threshold**, or draw a pixel ROI and convert it to a mask.
5. Add pixel-space ROIs to calculate spatially resolved average curves. Use **Curve → Export Curve** to write CSV output.
6. For a time-axis stack, open **Phasor → Phasor Analysis**. Choose a modulation frequency, draw phasor-space ROIs, and inspect their spatial projections and average curves.

For detailed operating instructions, see the [user guide](docs/docs/user_guide.md). The complete MkDocs site lives under `docs/`.

## Using Puprisa from Python

```python
from puprisa.core.pps import PPS

stack = PPS.load("data/example_stack_DS_CH1.tif")
stack.apply_background_subtraction(
    indices=[i for i, delay in enumerate(stack.axis_values) if delay < 0]
)

projection = stack.project()
phasor_coordinates = stack.phasor(freq=0.25)
stack.save("processed_stack.pkl", format="pickle")
```

`images` use the shape `(n_frames, height, width)`. Time values are expressed in picoseconds and Z positions in micrometres.

## Data formats

| Format | Extensions | Notes |
| --- | --- | --- |
| DukeScan TIFF | `.tif`, `.tiff` | Time (`t = … ps`) or Z (`z = …`) axis is inferred from TIFF tag 285 when available. Time delay loading also falls back to a companion `_xaxis.txt` or `.log` file. |
| Puprisa pickle | `.pkl`, `.pickle` | Preserves images, axis data, masks, background-subtraction state, results, and filename metadata. |
| Mathematica binary | `.m`, `.mathematica` | Supported by the Python loader when the axis type is supplied programmatically. The current desktop file dialog exposes TIFF and pickle files. |

## Documentation site

The documentation is written for MkDocs Material and uses `mkdocstrings` to render API reference pages from `src/`.

```bash
python -m pip install mkdocs-material mkdocstrings[python]
mkdocs serve -f docs/mkdocs.yml
```

Build a static site with:

```bash
mkdocs build -f docs/mkdocs.yml
```

## Project layout

```text
src/puprisa/       Package source
  core/            Numerical data, I/O, processing, masking, and phasor functions
  model/           Application state and event-driven managers
  controllers/     Qt action handlers
  viewmodels/      Qt presentation and scene coordination
  ui/              Windows, dialogs, forms, and custom widgets
docs/              MkDocs configuration and source pages
data/              Example DukeScan stack and associated metadata
examples/          Notebook example
```

## Important analysis semantics

- A mask layer uses `True` for pixels to **exclude**. The effective `PPS.mask` uses `True` for pixels that remain in the analysis.
- A processing operation acts on the selected stack and invalidates its cached phasor coordinates. Background reset restores the stack's baseline image copy; it does not undo every later destructive operation.
- ROI curves include both the selected ROI and the stack's effective analysis mask.
- Phasor analysis is available only for stacks whose axis type is `time`.

## Development

The app is assembled by `ApplicationContext`: model managers are Qt-free and emit callback events; controllers perform user actions; view models keep Qt scenes and widgets current. See the [architecture guide](docs/docs/architecture.md) and [developer documentation](docs/docs/dev/data_flow.md).

There is no automated test suite in the current repository. The validation guidance in the documentation describes focused checks for contributors.
