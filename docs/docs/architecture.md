# Architecture

Puprisa's desktop application follows a **Model-View-ViewModel (MVVM)** architecture, augmented with lightweight **controllers** that translate user commands into model calls. The central design rule is that analysis and state code never depends on Qt: the `core` and `model` packages are pure Python and can be imported from notebooks and scripts, while Qt is confined to the presentation layers (`viewmodels`, `controllers`, `ui`).

```text
src/puprisa/
  core/          Qt-free numerical domain and algorithms (PPS, I/O, ...)
  model/         Qt-free session state (entities + event-emitting managers)
  viewmodels/    Qt view models that bind a manager to widgets/scenes
  controllers/   Qt command handlers (dialogs + manager orchestration)
  ui/            Thin windows, dialogs, custom widgets, Designer forms
  utils/         Shared helpers used by several layers
```

## The MVVM roles

| Layer | Folder | MVVM role | Responsibility | Examples |
| --- | --- | --- | --- | --- |
| Domain data | `core` | The *data* the application analyses | Numerical model, file I/O, pure algorithms; never imports Qt | `PPS`, TIFF/pickle I/O, masking, processing, phasor transform |
| Model | `model` | The *state* the views present | Qt-free session state, validation, events, stack-addressed operations | `StackManager`, `MaskManager`, `RoiManager`, `ProcessingManager`, `CurveManager`, `PlotManager` |
| View model | `viewmodels` | Adapts model events to a concrete view, and widget edits back to the model | Subscribes to manager events and keeps one widget/scene current | `StackViewModel`, `MaskViewModel`, `RoiViewModel`, `PPSPlotViewModel`, `PhasorPlotViewModel`, `CurveViewModel` |
| Controller | `controllers` | Command handler | Interprets a GUI command, shows dialogs, calls a manager | open file, ask for SVD rank, export curves, slice slider |
| View | `ui` | The passive *view* the user interacts with | Qt windows, dialog classes, custom widgets, generated form bindings | `MainWindow`, `PhasorWindow`, graphics views |
| Shared | `utils` | — | Small helpers (geometry, parsing, colours, plotting) used by several layers | `geometry_utils`, `range_parser_utils`, `color_utils`, `curve_plot_utils` |

**Controllers versus view models.** A *controller* implements one user intent (a menu item or button): it may open a dialog and then calls a single manager method. It owns no persistent view state and no business rules. A *view model* is bound to a long-lived view (a list widget, a graphics scene, a matplotlib canvas): it subscribes to manager events, redraws that view when they fire, and forwards widget edits back to the model. The distinction is visible in the code — for example `mask_controller.py` and `roi_controller.py` explicitly state they never touch list widgets or graphics items, because those belong to the view models.

## The Qt-free domain (`core`)

`PPS` is the core stack facade. Its image array is always `(n_frames, height, width)` with a matching one-dimensional axis, and it owns mask layers, a copy of the baseline images for background subtraction, a background map, optional results, and filename metadata. `core` also provides the loaders/exporters in `io.py`, the pure mask helpers in `mask.py`, the phasor transform in `phasor.py`, array-level processing in `process.py`, decay-model fitting in `fit.py`, and Qt-free rendering helpers in `visualize.py`.

Everything here is deliberately free of PySide6 imports so it can be exercised numerically in a notebook.

## The Model layer (`model`)

The model layer is the heart of MVVM: it holds all session state and emits events that presentation code observes. It is built from small dataclass **entities** and callback-based **managers**.

### Entities (`model/entities.py`)

- `StackItem` — one loaded `PPS` plus session metadata (ID, display name, visibility, colour) and a runtime `phasor_coords` cache. Created by `StackItem.from_pps(...)`.
- `MaskItem` — one exclusion layer (`True` = keep pixels) with an `enabled` flag and JSON serialization.
- `RoiItem` — one region in `pixel` or `phasor` space (rectangle, circle, ellipse, polygon), with JSON serialization. It also carries a `graphics_item` back-pointer that the ROI view model fills in so model edits can reach the matching `QGraphicsItem`.
- `CurveItem` — one computed ROI average curve (`x`, `y`, label, colour).

### Managers and events

Every manager implements the same Qt-free plumbing: `add_listener(callback)` / `remove_listener(callback)` and a private `_notify(event)` that iterates a copy of the listener list. Event objects are frozen dataclasses with a string discriminator such as `StackEvent(event="added", ...)`.

| Manager | Holds | Emits (event names) | Notes |
| --- | --- | --- | --- |
| `StackManager` | the open stacks and the current-stack index | `added`, `removed`, `renamed`, `color_changed`, `visibility_changed`, `current_changed` | Central store; `add_stack` fires `added` then `current_changed`. |
| `MaskManager` | mask layers per stack | `added`, `removed`, `enabled_changed`, `label_changed`, `reversed`, `cleared`, `effective_changed` | Writes the combined keep-mask into `PPS.mask` and emits `effective_changed`. |
| `RoiManager` | ROIs across all stacks and both spaces | `added`, `removed`, `params_changed`, `label_changed`, `color_changed`, `visibility_changed` | Builds ROI keep-masks and can convert an ROI into a mask layer. |
| `CurveManager` | nothing durable | `computed` | Stateless; computes curves on demand from ROI + effective mask. |
| `ProcessingManager` | nothing durable | `data_changed`, `stack_created` | Resolves the stack ID at call time; clears that stack's phasor cache after destructive operations. |
| `PlotManager` | colormap and colour-scale presentation state | `colormap_changed`, `color_scale_changed` | Qt-free holder of display settings that `PPSPlotViewModel` reads. |

Managers that depend on other managers also expose a `handle_*_event` method so they can be chained onto another manager's listener list (for example, `RoiManager.handle_stack_event` reacts to stacks being added or removed).

## The View Model layer (`viewmodels`)

Each view model is a `QObject` that takes one or more managers and one concrete Qt view, then keeps the two in agreement. There is no data-binding framework: the wiring is hand-rolled and always has two directions.

- **Model → View:** the constructor calls `manager.add_listener(self._on_*_event)`. Handlers filter on the event name and refresh only the affected part of the view, using `QSignalBlocker` while rebuilding so that repopulating a widget does not echo edits back into the model.
- **View → Model:** Qt widget signals (such as `QListWidget.itemChanged` or `currentRowChanged`) call a manager setter, which updates state and emits a fresh model event.

| View model | View it maintains | Subscribes to |
| --- | --- | --- |
| `StackViewModel` | stack `QListWidget` (checkboxes, colour swatches) | `StackManager` |
| `MaskViewModel` | mask list for the current stack | `MaskManager`, `StackManager` |
| `RoiViewModel` | ROI list and a `QGraphicsScene` of draggable items (one per space) | `RoiManager`, `StackManager` |
| `PPSPlotViewModel` | image `QGraphicsView` pixmap + colour bar | `StackManager`, `MaskManager`, `ProcessingManager`, `PlotManager` |
| `PhasorPlotViewModel` | phasor density scene and spatial-projection scene | `StackManager`, `ProcessingManager`, `RoiManager`, `MaskManager` |
| `CurveViewModel` | matplotlib curve canvas | `StackManager`, `RoiManager`, `MaskManager`, `ProcessingManager`, `CurveManager` |

Two more classes complete the view-model story:

- `RoiSceneBridge` (with `PixelRoiSceneBridge` and `PhasorRoiSceneBridge`) maps between an `RoiItem`'s data-space parameters and `QGraphicsItem` geometry. The view model delegates all coordinate arithmetic to the bridge injected at construction time, so pixel-space (identity mapping) and phasor-space (a `(g, s) ∈ [-1, 1]²` domain mapped onto a fixed-size scene) ROIs share one `RoiViewModel`.
- The phasor cache lives with the view: `PhasorPlotViewModel` owns the semantics of `StackItem.phasor_coords`. It computes coordinates with `pps.phasor(freq, use_mask=True)` on demand, invalidates the cache when the frequency, masks, or processed data change, and rebuilds its density and spatial overlays.

## The Controller layer (`controllers`)

Controllers are `QObject`s that own dialogs, file dialogs, and messages but not analytical state or persistent view state. They are driven by widget signals (menu actions, buttons, sliders) rather than by model events. For example, `StackController` opens file/colour dialogs and calls `StackManager.add_stack(...)`; `ProcessingController` opens the background-subtraction, stack-math, and SVD dialogs and calls `ProcessingManager`; `CurveController` opens the curve-fit and spectrum dialogs and calls `CurveManager.compute_curves`.

Two controllers are different: `PPSSliceController` and `PhasorFrequencyController` are pure widget-synchronizers that keep sliders/spin-boxes and labels aligned with the model. They re-emit Qt signals — `sliceChanged(int)` and `frequencyChanged(float)` — that the windows connect to `CurveViewModel.set_current_slice` and `PhasorPlotViewModel.set_frequency` respectively.

## The View layer (`ui`)

`MainWindow` and `PhasorWindow` are intentionally thin assembly shells: their docstrings describe them as creating view models and controllers from the `ApplicationContext` and wiring UI widgets to them, with no business logic. Each window:

1. instantiates the view models and controllers it needs;
2. injects the Qt views (list widgets, graphics views, matplotlib canvases) into the view models;
3. connects widget signals to controllers and re-emitted view-model/controller signals;
4. leaves rules and state to the managers.

Both windows receive the *same* `ApplicationContext`, so they share one session's stacks, masks, ROIs, and derived data. The `.ui` files under `ui/forms/` are the editable Qt Designer sources; `ui/generated/` holds generated Python bindings that should be regenerated rather than hand-edited when a form changes.

## Composition root

`ApplicationContext` (`app_context.py`) builds the shared model in dependency order and wires the cross-manager listeners once:

```text
ApplicationContext
 ├─ StackManager
 ├─ MaskManager ───────► StackManager
 ├─ RoiManager ────────► StackManager, MaskManager
 ├─ CurveManager ──────► StackManager, RoiManager
 ├─ ProcessingManager ─► StackManager
 └─ PlotManager ───────► StackManager, ProcessingManager
```

It also registers `MaskManager.handle_stack_event`, `RoiManager.handle_stack_event`, and `PlotManager.handle_stack_event` on the stack manager, and `PlotManager.handle_processing_event` on the processing manager. `create_main_window()` and `create_phasor_window()` lazily build the two windows, which then subscribe their own view models to the shared managers.

## Data flow through the layers

A complete user action crosses the layers in both directions:

```text
user clicks menu item                 (View)
  → controller action                 (Controller: dialog + one manager call)
  → manager method mutates state      (Model: entity update + _notify)
  → event delivered to listeners      (Model → ViewModel: callback)
  → view model redraws its view       (ViewModel → View)
```

For example, subtracting a background:

```text
Process menu  →  ProcessingController  →  ProcessingManager.apply_...
  →  PPS data changes; ProcessingEvent("data_changed")
  →  PPSPlotViewModel, CurveViewModel, PhasorPlotViewModel refresh
```

Two independent notification channels make this work:

1. **Callback listeners** (model → presentation). Managers keep a list of callables; view models subscribe in their constructors. This is the MVVM notification channel and it is fully Qt-free, so the same managers can drive headless scripts with no view models attached.
2. **Qt widget signals** (presentation → model, and between presentation objects). Widget edits call manager setters, and view models/controllers re-emit signals (`sliceChanged`, `frequencyChanged`, `colorChangeRequested`) for the windows to connect.

ROI dragging shows the loop that keeps graphics and state consistent:

```text
user drags DraggableROI
  → ROI item callback → RoiViewModel._on_graphics_item_changed
  → bridge.extract_params_from_item(roi)   (coordinate math lives in the bridge)
  → RoiManager.update_params(...)
  → RoiEvent("params_changed")
  → RoiViewModel re-syncs the item's geometry under a silent-geometry context
    so the model update does not fire another drag callback
```

## Events and freshness

Because state changes always travel through a manager event, dependent views cannot go stale:

- Processing operations invalidate the cached `StackItem.phasor_coords`, and emit `data_changed` so image, curve, and phasor views repaint.
- Mask changes rewrite `PPS.mask` and emit `effective_changed`; excluded pixels become `NaN` in phasor space, so the phasor cache for the affected stack is cleared.
- A frequency change invalidates phasor caches for all stacks.
- Curves are computed on demand from the current ROIs and effective mask rather than stored as durable state, so stale curve data cannot survive a mask or processing change.

## Extension guidance

1. Add the numerical algorithm in `core` first, with no Qt imports.
2. If it changes session data, expose it as a validated, event-emitting manager method in `model`.
3. Add a controller action only if there is a menu/button command that needs it.
4. Add a view-model response only where a specific widget must reflect the new model event.

This ordering keeps analytical behaviour independently usable from scripts and limits Qt-specific coupling to the presentation layers.

