# Getting Started

## Install

Puprisa requires Python 3.10 or newer. Create and activate a virtual environment, then install from the repository root:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux, use `source .venv/bin/activate`.

## Launch the application

```bash
puprisa
```

The command creates the application context and opens the main image-stack window. You can also use `python -m puprisa` when the package is installed or `src/` is on `PYTHONPATH`.

## Open the included example

Use **File → Open Stack** and select `data/example_stack_DS_CH1.tif`. The matching `example_stack.log` is in the same directory, so Puprisa can recover its time-delay axis automatically.

After loading, move the slice slider to inspect individual frames. The label shows the frame number and its time value. Mouse-wheel input over the image view also changes the slice.

## First analysis

1. Select **Process → Background Subtraction → Subtract Negative Time Frames** to subtract the average pre-time-zero signal, if negative-delay frames are appropriate background frames for your measurement.
2. Draw a pixel ROI using the shape selector and **Add** button. Drag or resize it in the image view.
3. The curve plot updates with the ROI-average signal. Use **Curve → Export Curve** to save the numerical data as CSV.
4. Select **Phasor → Phasor Analysis** for a time-axis stack. Adjust the frequency, create a phasor ROI, and read its corresponding spatial selection and curve.

See the [User Guide](user_guide.md) for processing semantics, masks, exports, and caveats.
