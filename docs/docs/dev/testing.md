# Testing and Validation

The repository does not currently include an automated test suite. Until one is added, changes should be validated at the smallest appropriate layer before manual GUI checks.

## Core checks

Use small synthetic arrays to exercise pure functions and `PPS` methods:

- construct a `(frame, row, column)` array with a known axis;
- verify projection, average, masking, normalization, and background subtraction numerically;
- verify shape and axis validation failures;
- test TIFF/pickle round trips with a temporary output path;
- test phasor shape and masked-pixel `NaN` behavior for time stacks; confirm that Z stacks are rejected.

For example:

```python
import numpy as np
from puprisa.core.pps import PPS

pps = PPS(np.ones((3, 4, 5)), np.array([-1.0, 0.0, 1.0]))
assert pps.project().shape == (4, 5)
pps.apply_background_subtraction([0])
assert np.allclose(pps.images, 0)
```

## Manager checks

Exercise managers without Qt. Confirm that invalid stack IDs, frame indices, incompatible stack math, duplicate mask IDs, and invalid ROI spaces/shapes raise clear exceptions. Attach a small callback and verify emitted event names for adds, removals, processing updates, and mask changes.

## GUI smoke test

After installing with `python -m pip install -e .`, run `puprisa` and check:

1. Open the included DukeScan example and confirm the recovered time axis and slice labels.
2. Add, rename, hide, and delete a stack.
3. Create and toggle an intensity mask; add an ROI and confirm the curve updates.
4. Apply and reset background subtraction; create a downsampled stack; try compatible stack arithmetic.
5. Open the phasor window for the example, change frequency, add a phasor ROI, and verify its spatial overlay.
6. Save a TIFF, pickle, mask JSON, and curve CSV to temporary locations; reopen the pickle and mask JSON.

## Documentation build

Build the documentation after changing any page or API directive:

```bash
python -m pip install mkdocs-material mkdocstrings[python]
mkdocs build -f docs/mkdocs.yml --strict
```

`--strict` turns broken internal links and configuration warnings into failures. It is the preferred documentation validation command for continuous integration once a CI workflow exists.
