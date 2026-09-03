# Core API

The `core` package contains the Qt-independent numerical API. `PPS` is the main entry point for loaded or in-memory data; the remaining modules provide lower-level utilities (file I/O, masking, phasor transforms, processing, fitting, and rendering).

## Pump-probe stack

::: puprisa.core.pps.PPS

## File I/O

::: puprisa.core.io.PPSDataClass

::: puprisa.core.io.load_stack

::: puprisa.core.io.load_dukescan_stack

::: puprisa.core.io.load_pickle_stack

::: puprisa.core.io.export_as_tiff

::: puprisa.core.io.export_as_pickle

## Processing

::: puprisa.core.process.compute_projection

::: puprisa.core.process.compute_background_map

::: puprisa.core.process.subtract_background

::: puprisa.core.process.normalize_by_avg_curve

::: puprisa.core.process.downsample_local_mean

::: puprisa.core.process.downsample_mask

::: puprisa.core.process.average_groups

::: puprisa.core.process.svd_reconstruct

## Masks

::: puprisa.core.mask.gaussian_threshold_mask

::: puprisa.core.mask.load_mask_from_json

::: puprisa.core.mask.export_mask_to_json

## Phasor analysis

::: puprisa.core.phasor.compute_phasor

::: puprisa.core.phasor.flatten_stack

::: puprisa.core.phasor.compute_fft

::: puprisa.core.phasor.compute_psd

## Rendering helpers

Qt-free helpers that produce RGB/RGBA image arrays or draw onto a matplotlib `Axes`. They are used by the view models and are also usable from scripts.

::: puprisa.core.visualize.render_slice_rgb

::: puprisa.core.visualize.render_projection_rgb

::: puprisa.core.visualize.render_phasor_rgba

::: puprisa.core.visualize.universal_semicircle

::: puprisa.core.visualize.plot_phasor

::: puprisa.core.visualize.plot_average_curve

## Fitting models

::: puprisa.core.fit.FitOptions

::: puprisa.core.fit.FitResult

::: puprisa.core.fit.fit_curve

::: puprisa.core.fit.decay_single

::: puprisa.core.fit.decay_infinite

::: puprisa.core.fit.decay_instantaneous
