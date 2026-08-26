# Data Flow

## Loading a stack

```text
File dialog
  → StackController
  → PPS.load(path)
  → core.io.load_stack(...)
  → StackManager.add_stack(pps)
  → StackEvent("added"), StackEvent("current_changed")
  → list, image, slice, plot, ROI, and phasor view models refresh
```

`PPS.load` converts file data into a validated `PPS` object. `StackManager` adds session metadata and changes the current stack. It never depends on a Qt widget.

## Processing a stack

```text
Processing control
  → ProcessingController
  → ProcessingManager operation(stack_id, ...)
  → PPS method / core function
  → ProcessingEvent("data_changed")
  → Plot range refresh; image, curve, and phasor views refresh
```

The processing manager resolves `stack_id` at call time so it cannot retain a stale `PPS` reference after a user selects another stack. Destructive operations clear that stack's phasor-coordinate cache. Downsampling and stack math instead register a new stack and emit a `stack_created` processing event as well as `StackManager`'s normal add/current events.

## Masks and ROIs

```text
Mask or ROI action
  → MaskManager / RoiManager
  → underlying PPS mask layer or RoiItem
  → MaskEvent / RoiEvent
  → affected list, curve, plot, and phasor view models refresh
```

An ROI becomes a two-dimensional keep-mask when `RoiManager.build_roi_mask` is called. Pixel ROIs generate masks from image coordinates. Phasor ROIs generate masks by applying the same geometry to cached `(g, s)` coordinates and reshaping the result back to image dimensions.

`CurveManager.compute_curves` intersects the ROI keep-mask with the stack effective mask before computing one mean signal per frame. This is why masks are analysis-wide restrictions rather than merely visual overlays.

## Phasor calculation

```text
time stack + frequency + effective mask
  → PPS.phasor
  → core.phasor.compute_phasor
  → (g, s) per pixel
  → StackItem.phasor_coords cache
  → density plot and phasor-ROI spatial overlay
```

The transform flattens each pixel's time curve, projects it onto sine and cosine bases, and normalizes by the sum of the curve's absolute values. Pixels outside the effective mask are returned as `NaN`. The phasor view owns cache population and invalidation; the model manager only supplies the stack state.

## Persistence boundaries

- TIFF export writes processed images and optional axis metadata, not mask or ROI state.
- Pickle export writes the `PPS` images, axis, mask layers, background state, results, and filename metadata.
- Mask JSON export writes only mask layers; it is valid only for a stack with the same image dimensions when imported.
- Session stacks, ROI geometry, display colour, and visibility are not stored as a project/session file in the current implementation.
