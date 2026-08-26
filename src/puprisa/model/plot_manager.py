# puprisa/model/plot_manager.py
"""Qt-free manager for colormap and color-scale presentation state."""

from dataclasses import dataclass
from typing import Callable

from puprisa.model.processing_manager import ProcessingManager
from puprisa.model.stack_manager import StackManager

@dataclass(frozen=True)
class PlotEvent:
    """Emitted whenever colormap or color-scale settings change."""
    event: str  # "colormap_changed" or "color_scale_changed"
    colormap: str | None = None
    color_scale_mode: str | None = None
    vmin: float | None = None
    vmax: float | None = None


class PlotManager:
    """Central state for colormap and color-scale settings."""

    MODE_STD_DEV = "std_dev"
    MODE_FULL_RANGE = "full_range"
    MODE_CUSTOM = "custom"

    def __init__(self, stack_manager: StackManager, processing_manager: ProcessingManager):
        self._stack_manager = stack_manager
        self._processing_manager = processing_manager

        self._colormap = "pumpprobe"
        self._color_scale_mode = self.MODE_STD_DEV
        self._vmin: float | None = None
        self._vmax: float | None = None

        self._listeners: list[Callable[[PlotEvent], None]] = []

    # ------------------------------------------------------------------
    # Listener management
    # ------------------------------------------------------------------

    def add_listener(self, callback: Callable[[PlotEvent], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[PlotEvent], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, event: PlotEvent) -> None:
        for cb in list(self._listeners):
            cb(event)

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------
    @property
    def colormap(self):
        return self._colormap

    @property
    def color_scale_mode(self):
        return self._color_scale_mode

    @property
    def vmin(self):
        return self._vmin
    
    @property
    def vmax(self):
        return self._vmax

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_colormap(self, name: str) -> None:
        name = str(name).strip()
        if not name or name == self._colormap:
            return
        self._colormap = name
        self._notify(PlotEvent(event="colormap_changed", colormap=name))

    def set_color_scale_mode(self, mode: str) -> None:
        """Set the color scale mode.

        Accepts the ``std_dev`` or ``full_range`` modes. Custom mode is not
        allowed here and must be set via :meth:`set_custom_range`.

        Args:
            mode: The color scale mode to activate. Must be one of
                ``MODE_STD_DEV`` or ``MODE_FULL_RANGE``.

        Raises:
            ValueError: If ``mode`` is ``MODE_CUSTOM``.

        """
        if mode == self._color_scale_mode:
            return
        if mode == self.MODE_CUSTOM:
            raise ValueError("Cannot set custom mode without a valid range.")
        self._color_scale_mode = mode
        self._refresh_range()

    def set_custom_range(self, vmin: float, vmax: float) -> None:
        """Set a custom color scale range and activate custom mode."""
        if vmin >= vmax:
            raise ValueError("vmin must be smaller than vmax")
        self._vmin = vmin
        self._vmax = vmax
        self._color_scale_mode = self.MODE_CUSTOM
        self._notify(PlotEvent(event="color_scale_changed", color_scale_mode=self.MODE_CUSTOM, vmin=self._vmin, vmax=self._vmax))

    # ------------------------------------------------------------------
    # Range calculations
    # ------------------------------------------------------------------
    def get_reference_ranges(self) -> dict:
        item = self._stack_manager.get_current_item()
        if item is None:
            return {"std_min": None, "std_max": None,
                    "full_min": None, "full_max": None}
        stats = item.pps.statistics(mask_on=False)
        mean, std = stats["mean"], stats["std"]
        abs_max = max(abs(mean - 4 * std), abs(mean + 4 * std))
        return {
            "std_min": -abs_max,
            "std_max": abs_max,
            "full_min": stats["min"],
            "full_max": stats["max"],
        }

    def _refresh_range(self) -> None:
        if self._color_scale_mode == self.MODE_STD_DEV:
            ref = self.get_reference_ranges()
            new_vmin, new_vmax = ref["std_min"], ref["std_max"]
        elif self._color_scale_mode == self.MODE_FULL_RANGE:
            ref = self.get_reference_ranges()
            new_vmin, new_vmax = ref["full_min"], ref["full_max"]
        else: # MODE_CUSTOM, should not change because it is user-defined
            return
        if new_vmin != self._vmin or new_vmax != self._vmax:
            self._vmin = new_vmin
            self._vmax = new_vmax
            self._notify(PlotEvent(
                event="color_scale_changed",
                color_scale_mode=self._color_scale_mode,
                vmin=self._vmin,
                vmax=self._vmax,
            ))
    # ------------------------------------------------------------------
    # Data-change reactions
    # ------------------------------------------------------------------
    def handle_stack_event(self, event):
        if event.event in ("current_changed", "added", "removed"):
            self._refresh_range()

    def handle_processing_event(self, event):
        if event.event == "data_changed":
            self._refresh_range()