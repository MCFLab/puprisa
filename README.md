# Pump-Probe Spectroscopy Analysis

A comprehensive Python package for analyzing pump-probe imaging data, with a focus on time-resolved transient absorption microscopy.

## Overview

This package provides end-to-end analysis tools for pump-probe spectroscopy experiments, enabling researchers to process, analyze, and visualize time-resolved optical data. The toolkit supports multiple data formats, advanced processing techniques, and sophisticated visualization methods including phasor analysis.

Here is a link to a google doc to show the roadmap of future features/bugfixes and for test users to leave feedback:

https://docs.google.com/document/d/1uNBoRhGl6r8pxomQA-IgmFEcgjlpmZBz5Xu39qViVS8/edit?usp=sharing

## Features

- **Multiple Data Format Support**: Import from DukeScan, Mathematica, and pickle formats with intelligent parsing
- **Data Processing**: Background subtraction, normalization, spatial masking, and downsampling
- **Phasor Analysis**: Frequency-domain visualization for identifying and classifying decay patterns
- **Machine Learning Classification**: Pixel-wise classification of different material types
- **Intensity Thresholding**: Automated (Li, etc.) and manual masking based on signal intensity
- **Fitting Tools**: Cross-correlation fitting and transient absorption decay models
- **Visualization Tools**: Interactive plotting of TA curves, projections, and phasor plots
- **Linear Combinations**: Arithmetic operations on multiple stacks for comparative analysis

## Installation

### Prerequisites

- **Python 3.10 or newer** (see `requires-python` in `pyproject.toml`)
- **Git** (to clone the repository) or a copy of the `pump_probe_analysis` source tree
- **pip** (bundled with recent Python installers)

All steps below assume your shell’s working directory is the **repository root** — the folder that contains `pyproject.toml` and `src/` (i.e. `pump_probe_analysis/` after you clone or unpack the project).

### Virtual environment: pick **one** (`venv` **or** Conda)

Install this package into a **virtual environment** — a self-contained Python environment for this project only. That isolates dependencies from your **system Python** (the interpreter macOS/Linux ship or you installed globally), so upgrades here do not break other tools, and you can delete the env folder to remove the project cleanly. It also pins what you install for reproducible analysis.

You need **some** virtual environment; you do **not** need both mechanisms below.

| Use | If you… |
|-----|--------|
| **`venv`** | Want the standard library only—no Conda—and are fine with `python` + `pip`. |
| **Conda** | Already use Conda/Mamba for science stacks, or prefer `conda` envs. |

Follow **either** the `venv` tutorial **or** the Conda tutorial—not both. Creating a `.venv` beside the repo *and* a separate Conda env for the same checkout is unnecessary and easy to confuse; pick one workflow and stick with it.

---

### Tutorial: get the code with Git (branch `pyprisa`)

The active development line for this package lives on the **`pyprisa`** branch. Clone that branch so your checkout matches the instructions below.

1. **Clone** the repository and check out `pyprisa` in one step (replace the URL with your fork or the upstream remote — HTTPS or SSH is fine):

   Example with SSH:

   ```bash
   git clone -b pyprisa git@gitlab.oit.duke.edu:dg208/pump_probe_analysis.git
   cd pump_probe_analysis
   ```

2. **If you already cloned** the default branch (e.g. `main`), switch to `pyprisa`:

   ```bash
   cd pump_probe_analysis
   git fetch origin
   git checkout pyprisa
   ```

3. **Confirm** you are on the right branch (optional):

   ```bash
   git branch --show-current
   # should print: pyprisa
   ```

You are now at the repository root. Continue with **one** of the installation tutorials below: **install with `venv`** or **install with Conda** (pick a single path—not both).

---

### Tutorial: install with `venv` (standard library)

**If you are using Conda for this project, skip this section** and use the Conda tutorial below instead.

`venv` creates an isolated Python environment next to your project. No extra tools are required beyond Python itself.

1. **Create the virtual environment** (the name `.venv` is conventional; you can pick another directory name):

   ```bash
   python3 -m venv .venv
   ```

   On Windows, if `python3` is not on your PATH, use:

   ```bat
   py -3.10 -m venv .venv
   ```

2. **Activate** the environment so `python` and `pip` point inside `.venv`:

   - **macOS / Linux:**

     ```bash
     source .venv/bin/activate
     ```

   - **Windows (Command Prompt):**

     ```bat
     .venv\Scripts\activate.bat
     ```

   - **Windows (PowerShell):**

     ```powershell
     .venv\Scripts\Activate.ps1
     ```

   Your prompt will usually show `(.venv)` when activation succeeded.

3. **Upgrade pip** (recommended before installing the package):

   ```bash
   python -m pip install -U pip setuptools wheel
   ```

4. **Install this package in editable mode** from the repo root:

   ```bash
   pip install -e ".[gui]"
   ```

   - **`.[gui]`** includes **PySide6** and console scripts for the GUI. Omit the extra to install only the analysis library:

     ```bash
     pip install -e .
     ```

5. **Verify** (optional):

   ```bash
   python -c "import pump_probe_analysis; print('OK')"
   ```

   With `[gui]` installed:

   ```bash
   pump-probe-gui --help
   ```

6. **Deactivate** when you are done (optional):

   ```bash
   deactivate
   ```

---

### Tutorial: install with Conda (Anaconda, Miniconda, or Mambaforge)

**If you already installed with `venv` above, skip this entire section**—you already have an environment.

Conda manages a separate Python and packages per environment. This package is installed **from your local checkout with pip** inside that environment (editable install is not published on conda-forge by default).

1. **Install** [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download) if you do not already have `conda`. Initialize your shell so `conda activate` works (the installer usually offers to do this).

2. **Create** an environment with a compatible Python version:

   ```bash
   conda create -n pump-probe python=3.10 -y
   ```

   You can use `3.11` or `3.12` instead, as long as it satisfies `>=3.10`.

3. **Activate** the environment:

   ```bash
   conda activate pump-probe
   ```

4. **Go to the repository root** (where `pyproject.toml` lives):

   ```bash
   cd /path/to/pump_probe_analysis
   ```

5. **Install the package with pip** (still inside the activated conda env):

   ```bash
   python -m pip install -U pip setuptools wheel
   pip install -e ".[gui]"
   ```

   Use `pip install -e .` if you do not need the GUI.

6. **Verify** as in the `venv` section above.

7. **Leave** the environment when finished:

   ```bash
   conda deactivate
   ```

**Note:** Inside a **single** Conda environment, using `conda install` for some libraries and `pip install -e` for this repo is normal. That is not the same as using both a `.venv` and a Conda env for one checkout—avoid the latter. Prefer installing **this** project with `pip` from the local tree so the editable install tracks your edits to `src/`.

---

### After installation: run the GUI or use the library in code

Do these steps **inside the same environment** you chose (`venv` or Conda): activate it (`source .venv/bin/activate`, `conda activate pump-probe`, etc.) before running commands or Python.

#### Open the GUI (PUPRISA)

1. **Install the GUI extra** if you have not already (from the repository root, env activated):

   ```bash
   pip install -e ".[gui]"
   ```

   This pulls in **PySide6** and registers the `pump-probe-gui` command.

2. **Launch** the application:

   ```bash
   pump-probe-gui
   ```

   Optional: open a file immediately:

   ```bash
   pump-probe-gui /path/to/stack.tif
   ```

   Equivalent entry point:

   ```bash
   python -m pump_probe_analysis
   ```

3. **In the app**, the launcher opens the **channel view** (one stack at a time). Use **File → Open Stack…** to load data:

   - **DukeScan**: any single-channel TIFF (e.g. `*_DS_CH1.tif` … `*_DS_CH4.tif`, `.tif` or `.TIF`)
   - **Pickle**: a stack saved with `PPS.save` (`.pkl` / `.pickle`)
   - **Mathematica**: binary stack path (choose format when the extension is ambiguous)

   **File → Open Stack…** auto-detects format from the extension; if it cannot, you are prompted. Opening a new file resets the session (ROIs, masks, plots, phasor window).

#### Use the package without the GUI (scripts, notebooks, REPL)

You do **not** need PySide6 or `pump-probe-gui` for programmatic analysis.

1. **Install** the core package only (no GUI), from the repo root with your env activated:

   ```bash
   pip install -e .
   ```

   If you already ran `pip install -e ".[gui]"`, you can keep that install—the library imports the same; the GUI extra only adds optional dependencies and the launcher.

2. **Use Python** anywhere your environment is active: scripts, Jupyter, or `python` in a terminal. Minimal example (paths relative to your current working directory):

   ```python
   from pathlib import Path
   from pump_probe_analysis.pps import PPS

   stack = PPS(Path("data/example_stack_DS_CH1.tif"), dataType="DukeScan")
   stack.subtractFirst(n=3)
   stack.normalize(norm="minmax")
   stack.avg_show()
   ```

3. **Go deeper** with [Quick Start](#quick-start) below and the notebook `examples/example.ipynb`. Example data paths in the docs assume a `data/` folder at the **repository root** when you run code from that tree.

### Legacy `requirements.txt`

You can still `pip install -r requirements.txt` for a loose dependency list, but **`pip install -e ".[gui]"`** (from the repo root, inside your chosen environment) is the supported way to install this package.

## Quick Start

### Basic Usage

```python
from pathlib import Path
from pump_probe_analysis.pps import PPS

# Load a pump-probe stack from DukeScan format (path relative to your cwd)
filename = Path("data/example_stack_DS_CH1.tif")
stack = PPS(filename, dataType="DukeScan")

# Subtract background (average of first 3 frames)
stack.subtractFirst(n=3)

# Normalize the data
stack.normalize(norm="minmax")

# View average transient absorption curve
stack.avg_show()

# View projection (sum of absolute values)
stack.project_show()
```

### Phasor Analysis

```python
# Perform phasor analysis at 0.25 THz
phasor_data = stack.phasor(freq=0.25, remove_zero=True)

# Visualize phasor plot
stack.phasor_show(freq=0.25)
```

### Intensity Thresholding

```python
# Apply automatic Li threshold
stack.intensity_threshold(threshold="Li", sigma=5)

# Or use manual threshold
stack.intensity_threshold(threshold=0.1, sigma=5)

# View the mask
stack.mask_show()
```

### Time Delay Selection

```python
# Select specific time delays
delays = [-1.0, 0.0, 0.5, 1.0, 5.0, 10.0, 50.0]
stack.select_delays(delays=delays)

# Or use predefined melanoma preset
stack.select_delays(delays="melanoma1")
```

### Downsampling

```python
# Downsample by factor of 2 to improve SNR
stack_ds = stack.downsample(size=2)
```

### Classification

```python
from sklearn.ensemble import RandomForestClassifier

# Train your classifier (example)
# classifier = train_classifier()  # Your training code

# Classify pixels
stack.classify_show(classifier, downsample=2, norm="minmax")
```

### Linear Combinations

```python
# Subtract two stacks
difference = PPS.linear_combination(stack1, 1, stack2, -1)

# Average two stacks
average = PPS.linear_combination(stack1, 0.5, stack2, 0.5)
```

## Layout

- **`src/pump_probe_analysis/`** — installable package (`import pump_probe_analysis`).
- **`examples/`** — notebooks (e.g. `example.ipynb`).
- **`data/`** — example inputs (e.g. logs); place companion `.tif` stacks here when available.

## Module Structure

### `pps.py` (under `src/pump_probe_analysis/`)
Main module containing the `PPS` class for pump-probe stack analysis and visualization.

**Key Methods:**
- `__init__()`: Import data from DukeScan, Mathematica, or pickle formats
- `save()`: Save stack to pickle format
- `subtractFirst()`: Background subtraction using first n frames
- `normalize()`: Data normalization (minmax, zscore, absmax)
- `avg()`, `avg_show()`: Average transient absorption curves
- `project()`, `project_show()`: Stack projections and visualization
- `phasor()`, `phasor_show()`: Phasor analysis and visualization
- `intensity_threshold()`: Automatic masking using various algorithms
- `classify()`, `classify_show()`: Machine learning classification
- `downsample()`: Spatial downsampling to improve signal-to-noise ratio
- `substacks()`: Divide stack into spatial regions
- `select_delays()`: Select or interpolate specific time delays
- `linear_combination()`: Static method for arithmetic operations on stacks

### `melanoma.py`
Utilities for loading and managing melanoma patient sample data from pump-probe imaging experiments.

**Key Functions:**
- `get_elpis(path_elpis, path_georgia, wavelength, melanoma_only)`: Load and merge imaging metadata with patient clinical data (recurrence, SLNB)
- `convert_windows_to_linux_path(win_path, linux_mnt)`: Convert Windows file paths to Linux mount paths for cross-platform compatibility
- `adjust_roi(row)`: Adjust ROI identifiers to include slide numbers
- `manual_positions_from_file(row, filename, ds)`: Extract manually annotated surgical ink mask positions from CSV files
- `row_to_coordinates(row, ds)`: Convert mask position data from center/size format to numpy slice objects

**Data Sources:**
- **Elpis File**: Excel file with imaging experiment metadata (folders, identifiers, ROI information)
- **Georgia File**: Excel file with patient clinical data (recurrence status, sentinel lymph node biopsy results)

**Features:**
- Automatic path conversion for Linux/Windows compatibility
- Extraction of patient IDs from sample identifiers using regex patterns
- Loading of surgical ink mask positions from Mathematica-generated CSV files
- Merging of imaging and clinical datasets
- Optional filtering for melanoma samples only

### `ta.py`
Transient absorption model functions for fitting decay dynamics.

**Functions:**
- `decay_single(t, tau, t_pump, t_probe)`: Single exponential decay model with Gaussian pulse convolution
- `decay_infinite(t, t_pump, t_probe)`: Infinite lifetime (step function) model with Gaussian pulse convolution

### `fit.py`
Functions for fitting experimental data.

**Functions:**
- `fit_xcorr(filename, delay_stage_passes, dt_default)`: Fit pulse width from cross-correlation measurements with automatic unit detection

## Data Formats

### DukeScan Format
TIFF stacks from DukeScan microscope software with time delay information extracted using cascading fallback logic.

**Filename format**: `*_DS_CH1.tif`, `*_DS_CH2.tif`, `*_DS_CH3.tif`, or `*_DS_CH4.tif`

**Time Delay Extraction** (in order of priority):
1. **Legacy `*_xaxis.txt` file**: Older format with simple text file containing time delays
2. **TIFF tag 285 (PageName)**: Embedded in each TIFF frame (format: `t = <value> ps`)
3. **DukeScan `.log` file**: JSON-like log file with `delayArr_ps` field

**Special Features**:
- **Stitched Files**: ImageJ-stitched files (containing "stich" or "stitch" in filename) are handled automatically with special TIFF reading for hierarchical structures
- **Encoding Support**: Log files support both UTF-8 and Latin-1 encodings for robust parsing
- **Automatic Channel Detection**: Automatically detects channel number from filename

### Mathematica Format
Binary format with dimensions, time axis, and image data stored as float64 values.

**Structure**:
- Image dimensions (height, width, number of frames)
- Time delay array
- Raw image data as 3D array

### Pickle Format
Serialized Python dictionary containing all analysis state and metadata.

**Dictionary Keys**:
- `images`: NumPy array of images (3D: time × height × width)
- `times`: Array of time delays in picoseconds
- `filename`: Original filename for traceability
- `image_dimensions`: Image shape tuple
- `mask`: Boolean mask array (optional, if masking applied)

This format allows for fast loading and preserves all preprocessing steps.

## Example Notebook

See [example.ipynb](example.ipynb) for a detailed walkthrough of the package functionality, including:
- Data import from DukeScan format
- Visualization of TA curves and projections
- Phasor analysis workflow
- Masking and thresholding techniques
- Complete analysis pipeline examples

## Dependencies

Core dependencies:
- **numpy**: Numerical array operations and linear algebra
- **matplotlib**: Plotting and visualization
- **scikit-image**: Image processing, filtering, and thresholding algorithms
- **scipy**: Scientific computing, optimization, and special functions
- **pandas**: Data import and manipulation
- **pillow**: Image file I/O (TIFF support)
- **scikit-learn**: Machine learning (optional, for classification features)

See [requirements.txt](requirements.txt) for complete list with pinned versions.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows Python best practices and includes appropriate documentation.

## License

[Add your license information here]

## Authors

**David Grass**
**Ryan Su** 

Created: May 11, 2023  
Last Updated: January 2026

## Citation

If you use this software in your research, please cite:

```
[Add citation information here]
```

## Support

For questions, issues, or feature requests:
- Open an issue on the repository
- Contact: [Add contact information]

## Acknowledgments

Development supported by [Add acknowledgments here]
