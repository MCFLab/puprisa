# Data Flow

Data flows through the MVVM layers described in the [architecture guide](../architecture.md). In short: a **view** emits a widget signal, a **controller** turns it into one manager call, the **model** mutates state and notifies its callback listeners, and **view models** redraw their views. This page traces that flow for each feature area, naming the concrete classes involved.

## Loading a stack

```text
File dialog (View)
  → StackController (Controller)
  → PPS.load(path)
  → core.io.load_stack(...)
  → StackManager.add_stack(pps)                       (Model)
  → StackEvent("added"), StackEvent("current_changed")
  → listeners:
      MaskManager.handle_stack_event, RoiManager.handle_stack_event,
      PlotManager.handle_stack_event
  → StackViewModel, MaskViewModel, RoiViewModel, PPSPlotViewModel,
    PhasorPlotViewModel, CurveViewModel, PPSSliceController refresh
```

`PPS.load` converts file data into a validated `PPS` object. `StackManager` adds session metadata and makes the new stack current. Because `StackManager` lives in the Qt-free model layer, it never depends on a Qt widget and can be driven from a script without any view models attached.

## Processing a stack

```text
Process menu action (View)
  → ProcessingController (Controller: shows the parameter dialog)
  → ProcessingManager operation(stack_id, ...)        (Model)
  → PPS method / core function
  → ProcessingEvent("data_changed")
  → PlotManager.handle_processing_event (colour range refresh)
  → PPSPlotViewModel, CurveViewModel, PhasorPlotViewModel redraw
```

The processing manager resolves `stack_id` at call time so it cannot retain a stale `PPS` reference after the user selects another stack. Destructive operations clear that stack's phasor-coordinate cache. Downsampling and stack math instead register a new stack and emit a `stack_created` processing event in addition to `StackManager`'s normal add/current events.

## Masks and ROIs

```text
Mask or ROI action (View)
  → MaskController / RoiController (Controller)
  → MaskManager / RoiManager                        (Model)
  → underlying PPS mask layer or RoiItem
  → MaskEvent / RoiEvent
  → MaskViewModel, CurveViewModel, PPSPlotViewModel,
    PhasorPlotViewModel, RoiViewModel redraw
```

An ROI becomes a two-dimensional keep-mask when `RoiManager.build_roi_mask` is called. Pixel ROIs generate masks from image coordinates. Phasor ROIs generate masks by applying the same geometry to cached `(g, s)` coordinates and reshaping the result back to image dimensions. The coordinate arithmetic itself lives in the injected `RoiSceneBridge` (`PixelRoiSceneBridge` or `PhasorRoiSceneBridge`), never in the view model.

When the user drags an ROI on screen, the loop runs in reverse: the `DraggableROI` item calls back into `RoiViewModel`, which asks the bridge to extract fresh parameters and calls `RoiManager.update_params(...)`. The resulting `RoiEvent("params_changed")` lets the view model re-sync the item geometry under a silent context so the model update does not trigger another drag event.

`CurveManager.compute_curves` intersects the ROI keep-mask with the stack effective mask before computing one mean signal per frame. This is why masks are analysis-wide restrictions rather than merely visual overlays.

## Phasor calculation

```text
time stack + frequency + effective mask
  → PPS.phasor(freq, use_mask=True)
  → core.phasor.compute_phasor
  → (g, s) per pixel
  → StackItem.phasor_coords cache        (owned by PhasorPlotViewModel)
  → phasor density scene and phasor-ROI spatial overlay refresh
```

The transform flattens each pixel's time curve, projects it onto sine and cosine bases, and normalizes by the sum of the curve's absolute values. Pixels outside the effective mask are returned as `NaN`. `PhasorPlotViewModel` owns cache population and invalidation: a frequency change (via `PhasorFrequencyController.frequencyChanged` → `set_frequency`), a mask change, or processed data change clears the affected caches and triggers a re-render. The model managers only supply the stack state; they never draw.

## Persistence boundaries

- TIFF export writes processed images and optional axis metadata, not mask or ROI state.
- Pickle export writes the `PPS` images, axis, mask layers, background state, results, and filename metadata.
- Mask JSON export writes only mask layers; it is valid only for a stack with the same image dimensions when imported.
- Session stacks, ROI geometry, display colour, and visibility are not stored as a project/session file in the current implementation.
