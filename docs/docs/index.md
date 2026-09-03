# Puprisa

Puprisa is an application and Python package for processing and analysing pump-probe microscopy image stacks. It supports the full path from loading a stack to selecting spatial or phasor-space regions, plotting their average curves, and exporting results.

The desktop interface is built on a **Model-View-ViewModel (MVVM)** architecture: the numerical core and the session-state managers are pure Python and Qt-free, so the same operations remain available from notebooks and scripts, while Qt view models, controllers, and windows form the desktop presentation. See [Architecture](architecture.md) for details.

## Choose your path

- New to the application? Start with [Getting Started](getting_started.md).
- Running an experiment workflow? Read the [User Guide](user_guide.md).
- Understanding the MVVM design, or extending the application? See [Architecture](architecture.md) and [Data Flow](dev/data_flow.md).
- Calling Puprisa from a notebook or script? Browse the [API Reference](api/core.md), and use the Qt-free [Model API](api/model.md) directly if you need programmatic session state.

## Core capabilities

Puprisa treats a dataset as a `PPS` stack with shape `(frame, row, column)`. Each frame has one axis value: a time delay in ps or a Z position in µm. A session can hold several stacks at once, so comparisons and derived stacks can remain side by side.

The desktop application provides:

- interactive frame viewing with configurable colormaps and ranges;
- stack preprocessing, including background subtraction, normalization, truncated-SVD denoising, downsampling, and arithmetic;
- exclusion masks and pixel-space ROI curves;
- phasor-density analysis and phasor-space ROI selection for time-delay data.

## Terminology

| Term | Meaning in Puprisa |
| --- | --- |
| Stack | A three-dimensional image array with one independent-axis value per frame. |
| Current stack | The selected stack; many GUI actions apply to it. |
| Mask layer | A boolean exclusion layer: `True` pixels are excluded. |
| Effective mask | The combined inclusion mask used for analysis: `True` pixels are kept. |
| ROI | A geometric region used to select pixels in image or phasor space. |
| Derived stack | A newly registered result of downsampling or stack arithmetic. |
