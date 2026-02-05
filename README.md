# Pump-Probe Spectroscopy Analysis

A comprehensive Python package for analyzing pump-probe imaging data, with a focus on time-resolved transient absorption microscopy.

## Overview

This package provides end-to-end analysis tools for pump-probe spectroscopy experiments, enabling researchers to process, analyze, and visualize time-resolved optical data. The toolkit supports multiple data formats, advanced processing techniques, and sophisticated visualization methods including phasor analysis.

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

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository:
```bash
git clone <repository-url>
cd pump_probe_analysis
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from pps import PPS
from pathlib import Path

# Load a pump-probe stack from DukeScan format
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

## Module Structure

### `pps.py`
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

**David** (@david)

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
