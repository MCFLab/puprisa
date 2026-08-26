# Core API

The core package contains the Qt-independent numerical API. `PPS` is the main entry point for loaded or in-memory data; the remaining modules provide lower-level utilities.

## Pump-probe stack

::: puprisa.core.pps.PPS

## File I/O

::: puprisa.core.io.PPSDataClass

::: puprisa.core.io.load_stack

::: puprisa.core.io.export_as_tiff

::: puprisa.core.io.export_as_pickle

## Processing

::: puprisa.core.process.compute_projection

::: puprisa.core.process.compute_background_map

::: puprisa.core.process.normalize_minmax

::: puprisa.core.process.gaussian_threshold_mask

::: puprisa.core.process.downsample_mean

::: puprisa.core.process.svd_reconstruct

## Masks

::: puprisa.core.mask.PPSMask

## Phasor analysis

::: puprisa.core.phasor.compute_phasor

::: puprisa.core.phasor.universal_semicircle

## Fitting models

::: puprisa.core.fit.decay_single

::: puprisa.core.fit.decay_infinite

::: puprisa.core.fit.decay_instantaneous
