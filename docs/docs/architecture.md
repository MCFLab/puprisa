# Architecture

Puprisa follows an event-driven model-view-controller/view-model design. Its numerical and state-management layers do not depend on Qt; Qt is confined to windows, controllers, custom widgets, and view models. This separation allows `PPS` and the managers to be used from scripts as well as the desktop application.

## Composition root

`ApplicationContext` builds the application in dependency order:

```text
ApplicationContext
 ├─ StackManager
 ├─ MaskManager ───────► StackManager
 ├─ RoiManager ────────► StackManager, MaskManager
 ├─ CurveManager ──────► StackManager, RoiManager
 ├─ ProcessingManager ─► StackManager
 └─ PlotManager ───────► StackManager, ProcessingManager
```

It also wires stack events to ROI and plot managers, and processing events to the plot manager. The main and phasor windows receive the same context, so they share the session's stacks, masks, ROIs, and derived data.

## Layers

| Layer | Responsibility | Examples |
| --- | --- | --- |
| `core` | Numerical data model, file I/O, pure algorithms | `PPS`, TIFF/pickle I/O, masking, processing, phasor transform |
| `model` | Session state, validation, events, and stack-addressed operations | `StackManager`, `MaskManager`, `RoiManager`, `ProcessingManager` |
| `controllers` | Interpret a GUI command, show dialogs, and call a manager | open file, ask for SVD rank, export curves |
| `viewmodels` | Subscribe to model events and maintain Qt scenes/widgets | stack list, ROI scenes, image view, phasor density |
| `ui` | Qt windows, dialog classes, generated form bindings, widgets | `MainWindow`, `PhasorWindow`, graphics views |

## Data model

`PPS` is the core stack facade. Its image array is always `(n_frames, height, width)` with a matching one-dimensional axis. It owns mask layers, a copy of the baseline images for background subtraction, a background map, optional results, and filename metadata.

`StackManager` wraps each `PPS` in a `StackItem` that provides session metadata such as ID, display name, visibility, colour, and cached phasor coordinates. This is the source of truth for the current stack.

ROIs are `RoiItem` values tied to one stack and one coordinate space (`pixel` or `phasor`). Curves are generated on demand, rather than stored as durable state, so processing and mask changes cannot leave stale curve data behind.

## Events and freshness

Managers expose callback registration instead of Qt signals. A stack event describes collection/current-stack changes; mask, ROI, processing, curve, and plot managers publish their own event types. View models subscribe and redraw only the affected view state.

Processing operations invalidate the cached `StackItem.phasor_coords`. Mask changes do the same because excluded pixels must become `NaN` in phasor space. A frequency change invalidates phasor caches for all stacks.

## UI boundaries

`MainWindow` and `PhasorWindow` are intentionally thin assembly shells. They instantiate the appropriate controllers and view models, connect widgets to their actions, and leave business rules to the model managers. The `.ui` files are the editable Qt Designer sources; `ui/generated/` contains generated Python bindings and should be regenerated rather than hand-edited when a form changes.

## Extension guidance

Add a numerical algorithm in `core` first. If it changes persistent/session data, expose it as a validated, event-emitting manager method. Then add a controller action and a view-model response only where the GUI needs them. This keeps analytical behavior independently usable and limits Qt-specific coupling.
