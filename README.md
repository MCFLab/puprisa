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

## Installation

Python 3.10 or later is required.

### Option 1: Install from PyPI (recommended for most users)

```bash
pip install puprisa
```

Once installed, launch the desktop application:

```bash
puprisa
```

### Option 2: Install from source

This method is suitable for users who need the latest development version or who plan to modify the code.

Clone the repository and navigate into it:

```bash
git clone <repository-url>
cd <repository-directory>
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install the project:

```bash
python -m pip install .
```

Alternatively, for an editable installation (development mode), which allows changes to the source code to take effect immediately:

```bash
python -m pip install -e .
```

After installation, start the application:

```bash
puprisa
```

## Typical workflow

1. Open one or more stacks with **File / Open Stack**.
2. Select a stack, browse frames with the slice control, and choose an appropriate color scale.
3. Apply background subtraction, normalization, or SVD denoising if required. These operations modify the selected stack; downsampling and stack math instead create a new derived stack.
4. Build an exclusion mask with **Mask / Mask from threshold**, or draw a pixel ROI and convert it to a mask.
5. Add pixel-space ROIs to calculate spatially resolved average curves. Use **Curve / Export Curve** to write CSV output.
6. For a time-axis stack, open **Phasor / Phasor Analysis**. Choose a modulation frequency, draw phasor-space ROIs, and inspect their spatial projections and average curves.

For detailed operating instructions, see the [user guide](docs/docs/user_guide.md). The complete MkDocs site lives under `docs/`.

## Using Puprisa from Python

```python
from puprisa.core.pps import PPS

stack = PPS.load("data/melanin_DS_CH1.tif")
stack.apply_background_subtraction(indices=range(3), pixelwise=True)
stack.create_mask_from_threshold()
stack.plot_slice(slice_index=1)

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

## Architecture

The desktop application follows a **Model-View-ViewModel (MVVM)** design, with small controller objects for command handling:

```text
src/puprisa/
  core/          Qt-free numerical domain: PPS stack, I/O, processing, masks, phasor, fitting
  model/         Qt-free session state: entities and event-emitting managers
  viewmodels/    Qt view models that bind each manager to a widget/graphics scene
  controllers/   Qt command handlers (open dialogs, then call a manager)
  ui/            Thin windows, dialogs, custom widgets, and Designer forms
  utils/         Shared helpers (geometry, parsing, colours, plotting)
```

The `core` and `model` layers never import Qt, so the numerical `PPS` API **and** the session-state managers (`StackManager`, `MaskManager`, `RoiManager`, `CurveManager`, `ProcessingManager`, `PlotManager`) are fully usable from notebooks and scripts. View models subscribe to manager callback events and redraw their views; controllers translate menu and button actions into manager calls. Both windows share one `ApplicationContext`, so they see the same session data. See the [architecture guide](docs/docs/architecture.md) and the [data-flow notes](docs/docs/dev/data_flow.md) for the full picture.

## Important analysis semantics

- A mask layer uses `True` for pixels to keep. The effective mask is calculated and saved in `PPS.mask` .
- A processing operation acts on the selected stack and invalidates its cached phasor coordinates. Background reset restores the stack's baseline image copy; it does not completely undo normalization or other destructive operations.
- ROI curves include both the selected ROI and the stack's effective analysis mask.
- Phasor analysis is available only for stacks whose axis type is `time`.

## Development

`ApplicationContext` is the composition root: it builds the Qt-free model managers in dependency order, wires cross-manager listeners, and lazily constructs `MainWindow` and `PhasorWindow`. The windows are thin MVVM shells that instantiate view models and controllers and connect them to the shared managers.

- Model managers are Qt-free and emit callback events that presentation code observes.
- View models subscribe to those events and keep a specific widget, list, or graphics scene current.
- Controllers own dialogs and call exactly one manager method per user action.

Keep new analysis in `core`, expose state changes through a validated `model` manager method, and only then add a controller action or a view-model response. See the [architecture guide](docs/docs/architecture.md) and [developer documentation](docs/docs/dev/data_flow.md).

There is no automated test suite in the current repository. The validation guidance in the documentation describes focused checks for contributors.

## Dependencies

Core dependencies:

- **numpy**: Numerical array operations and linear algebra
- **matplotlib**: Plotting and visualization
- **scikit-image**: Image processing, filtering, and thresholding algorithms
- **scipy**: Scientific computing, optimization, and special functions
- **pandas**: Data import and manipulation
- **pyside6**: GUI

See [pyproject.toml](pyproject.toml) for complete list with pinned versions.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows Python best practices and includes appropriate documentation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for the full license text.

## Citation

If you use Puprisa in your research, please cite:

```latex
@software{puprisa2026,
  author       = {Su, Ryan and Feng, Xiaotian and Grass, David and Fischer, Martin C. and Warren, Warren S.},
  title        = {Puprisa: Pump-Probe Image Stack Analysis},
  year         = {2026},
  publisher    = {Duke University},
  url          = {?}
}
```

## Support

For questions, issues, or feature requests:

- Open an issue on the repository
- Contact: [martin.fischer@duke.edu](mailto: martin.fischer@duke.edu)
