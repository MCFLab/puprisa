# Model API

The model layer is Qt-free. Managers own session state, validate operations, and emit callback events that presentation code can observe.

## Shared entities

::: puprisa.model.entities.StackItem

::: puprisa.model.entities.MaskItem

::: puprisa.model.entities.RoiItem

::: puprisa.model.entities.CurveItem

## Stack management

::: puprisa.model.stack_manager.StackManager

::: puprisa.model.stack_manager.StackEvent

## Processing and display state

::: puprisa.model.processing_manager.ProcessingManager

::: puprisa.model.processing_manager.ProcessingEvent

::: puprisa.model.plot_manager.PlotManager

::: puprisa.model.plot_manager.PlotEvent

## Masks, ROIs, and curves

::: puprisa.model.mask_manager.MaskManager

::: puprisa.model.mask_manager.MaskEvent

::: puprisa.model.roi_manager.RoiManager

::: puprisa.model.roi_manager.RoiEvent

::: puprisa.model.curve_manager.CurveManager

::: puprisa.model.curve_manager.CurveEvent
