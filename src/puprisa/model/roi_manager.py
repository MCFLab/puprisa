# puprisa/model/roi_manager.py
"""Qt-free manager for all ROI shapes across all stacks."""
from dataclasses import dataclass
from typing import Callable
from pathlib import Path
import json
import numpy as np

from puprisa.model.entities import RoiItem, StackItem
from puprisa.model.mask_manager import MaskManager
from puprisa.model.stack_manager import StackEvent, StackManager
from puprisa.utils.color_utils import MATLAB_COLORS
from puprisa.utils.geometry_utils import shape_to_mask


@dataclass(frozen=True)
class RoiEvent:
    """Emitted whenever ROI collection or metadata changes."""
    event: str                  # "added" / "removed" / "params_changed" / "label_changed" /
                                # "color_changed" / "visibility_changed"
    roi_id: str | None = None
    roi: RoiItem | None = None
    stack_id: str | None = None


class RoiManager:
    def __init__(self, stack_manager: StackManager, mask_manager: MaskManager, color_palette: list[str] | None = None):
        self._stack_manager = stack_manager
        self._mask_manager = mask_manager
        self._palette = color_palette or MATLAB_COLORS
        self._items: list[RoiItem] = []
        self._listeners: list[Callable[[RoiEvent], None]] = []
        self._id_counter = 0
        self._color_index = 0

    # ------------------------------------------------------------------
    # Listener management
    # ------------------------------------------------------------------
    def add_listener(self, callback: Callable[[RoiEvent], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[RoiEvent], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, event: RoiEvent) -> None:
        for cb in list(self._listeners):
            cb(event)

    # ------------------------------------------------------------------
    # Stack context
    # ------------------------------------------------------------------
    def handle_stack_visibility_changed(self, stack_id: str, visible: bool) -> None:
        for roi in self._items:
            if roi.stack_id == stack_id and roi.visible != visible:
                roi.visible = visible
                self._notify(RoiEvent(
                    event="visibility_changed",
                    roi_id=roi.id,
                    roi=roi,
                    stack_id=stack_id,
                ))

    def handle_stack_deleted(self, stack_id: str) -> int:
        to_remove = [r for r in self._items if r.stack_id == stack_id]
        for roi in to_remove:
            self._items.remove(roi)
            self._notify(RoiEvent(
                event="removed",
                roi_id=roi.id,
                roi=roi,
                stack_id=stack_id,
            ))
        return len(to_remove)

    def handle_stack_event(self, event: StackEvent) -> None:
        if event.event == "removed":
            self.handle_stack_deleted(event.stack_id)
        elif event.event == "visibility_changed":
            self.handle_stack_visibility_changed(event.stack_id, event.stack_item.visible)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get_all_rois(self) -> list[RoiItem]:
        return list(self._items)

    def get_roi_by_id(self, roi_id: str) -> RoiItem | None:
        return next((r for r in self._items if r.id == roi_id), None)

    def get_rois_for_stack(self, stack_id: str) -> list[RoiItem]:
        return [r for r in self._items if r.stack_id == stack_id]

    def get_analysis_visible_rois(self) -> list[RoiItem]:
        """ROIs whose visible flag is True (stack visibility has already been applied)."""
        return [r for r in self._items if r.visible]

    def get_scene_visible_rois(self) -> list[RoiItem]:
        """Analysis-visible ROIs belonging to the current stack."""
        current_stack_id = self._stack_manager.get_current_stack_id()
        if current_stack_id is None:
            return []
        return [r for r in self.get_analysis_visible_rois()
                if r.stack_id == current_stack_id]

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------
    def add_roi(
        self,
        stack_id: str,
        space: str,
        shape: str,
        params: dict | None = None,
        label: str | None = None,
        color: str | None = None,
        visible: bool = True,
    ) -> RoiItem:
        """Create a new ROI. If params is None, generate sensible defaults."""
        stack_item = self._stack_manager.get_item_by_id(stack_id)
        if stack_item is None:
            raise KeyError(f"Unknown stack_id: {stack_id!r}")
        if space not in ("pixel", "phasor"):
            raise ValueError(f"Unsupported space: {space!r}")
        if shape not in ("rectangle", "circle", "ellipse", "polygon"):
            raise ValueError(f"Unsupported shape: {shape!r}")
        if params is None:
            params = self._generate_default_params(stack_item, space, shape)

        roi_id = self._generate_roi_id()
        roi = RoiItem(
            id=roi_id,
            stack_id=stack_id,
            space=space,
            shape=shape,
            params=params,
            label=label or self._default_label(roi_id, stack_id),
            color=color or self._next_color(),
            visible=visible and stack_item.visible
        )
        self._items.append(roi)
        self._notify(RoiEvent(event="added", roi_id=roi.id, roi=roi, stack_id=stack_id))
        return roi

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------
    def update_params(self, roi_id: str, params: dict) -> None:
        roi = self.get_roi_by_id(roi_id)
        if roi is None or self._params_equal(roi.params, params):
            return
        roi.params = params
        self._notify(RoiEvent(event="params_changed", roi_id=roi.id, roi=roi, stack_id=roi.stack_id))

    def update_label(self, roi_id: str, label: str) -> None:
        roi = self.get_roi_by_id(roi_id)
        if roi is None or roi.label == label:
            return
        roi.label = label
        self._notify(RoiEvent(event="label_changed", roi_id=roi.id, roi=roi, stack_id=roi.stack_id))

    def update_color(self, roi_id: str, color: str) -> None:
        roi = self.get_roi_by_id(roi_id)
        if roi is None or roi.color == color:
            return
        roi.color = color
        self._notify(RoiEvent(event="color_changed", roi_id=roi.id, roi=roi, stack_id=roi.stack_id))

    def set_visible(self, roi_id: str, visible: bool) -> None:
        """Set ROI visible flag."""
        roi = self.get_roi_by_id(roi_id)
        if roi is None or roi.visible == visible:
            return
        roi.visible = visible
        self._notify(RoiEvent(event="visibility_changed", roi_id=roi.id, roi=roi, stack_id=roi.stack_id))

    def delete_roi(self, roi_id: str) -> str:
        roi = self.get_roi_by_id(roi_id)
        if roi is None:
            raise KeyError(f"Unknown roi_id: {roi_id!r}")
        self._items.remove(roi)
        self._notify(RoiEvent(event="removed", roi_id=roi.id, roi=roi, stack_id=roi.stack_id))
        return roi.id

    # ------------------------------------------------------------------
    # Mask building / conversion
    # ------------------------------------------------------------------
    def build_roi_mask(self, roi: RoiItem) -> np.ndarray | None:
        """Build a 2D keep-mask (True = inside ROI) in pixel space."""
        stack_item = self._stack_manager.get_item_by_id(roi.stack_id)
        if stack_item is None:
            return None

        pps = stack_item.pps
        h, w = pps.image_dimensions

        if roi.space == "pixel":
            xx, yy = np.meshgrid(np.arange(w), np.arange(h))
            return shape_to_mask(roi.shape, roi.params, xx, yy)

        elif roi.space == "phasor":
            coords = stack_item.phasor_coords
            if coords is None:
                return None
            g = coords[:, 0]
            s = coords[:, 1]
            valid = ~np.isnan(g) & ~np.isnan(s)
            mask_1d = np.zeros(valid.shape, dtype=bool)
            if np.any(valid):
                mask_1d[valid] = shape_to_mask(roi.shape, roi.params, g[valid], s[valid])
            return mask_1d.reshape(h, w)
        
        raise ValueError(f"Unsupported ROI space: {roi.space!r}")

    def convert_roi_to_mask(self, roi_id: str) -> str:
        roi = self.get_roi_by_id(roi_id)
        if roi is None:
            raise KeyError(f"Unknown roi_id: {roi_id!r}")

        keep_mask = self.build_roi_mask(roi)
        if keep_mask is None:
            raise ValueError("Cannot build ROI mask (missing phasor coords or stack)")
        if not np.any(keep_mask):
            raise ValueError("ROI mask is empty")

        label = f"From ROI {roi.label}"
        return self._mask_manager.add_mask(roi.stack_id, keep_mask, label=label, enabled=True)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def import_rois_from_json(
        self,
        path: str | Path,
        stack_id: str,
        space: str | None = None,
    ) -> list[str]:
        """Import ROIs from JSON into the given stack.

        If ``space`` is given, only ROIs of that space are imported. Returns
        the list of new ROI IDs. Uses :meth:`add_roi` so all validation,
        initialization, and event notifications are handled consistently.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("ROI file must contain a JSON object")

        items = data.get("rois", [])
        if not isinstance(items, list):
            raise ValueError("'rois' must be a list")

        new_ids: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Every ROI entry must be an object")
            roi_space = item.get("space")
            if space is not None and roi_space != space:
                continue
            new_roi = self.add_roi(
                stack_id=stack_id,
                space=roi_space,
                shape=item.get("shape"),
                params=item.get("params"),
                label=item.get("label"),
                color=item.get("color"),
                visible=item.get("visible", True),
            )
            new_ids.append(new_roi.id)

        if not new_ids:
            raise ValueError(f"No ROI imported. File may be empty or all ROIs were filtered by space={space!r}.")

        return new_ids

    def export_rois_to_json(self, path: str | Path, rois: list[RoiItem]) -> None:
        """Write a list of ROIs to a JSON file."""
        payload = {"rois": [roi.to_serializable() for roi in rois]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    # ------------------------------------------------------------------
    # Default parameter generation (data-space)
    # ------------------------------------------------------------------
    def _generate_default_params(self, stack_item: StackItem, space: str, shape: str) -> dict:
        pps = stack_item.pps
        if space == "pixel":
            h, w = pps.image_dimensions
            cx, cy = w / 2.0, h / 2.0
            size = min(w, h) * 0.1
        elif space == "phasor":
            cx, cy = 0.0, 0.0
            size = 0.3
        else:
            raise ValueError(f"Unsupported ROI space: {space!r}")

        if shape == "rectangle":
            return {"x": cx - size / 2, "y": cy - size / 2,
                    "width": size, "height": size}
        if shape == "circle":
            return {"center_x": cx, "center_y": cy, "radius": size / 2}
        if shape == "ellipse":
            return {"center_x": cx, "center_y": cy,
                    "radius_x": size / 2, "radius_y": size / 2}
        if shape == "polygon":
            radius = size / 2
            vertices = []
            for i in range(3):
                angle = 2 * np.pi * i / 3 - np.pi / 2
                vertices.append([cx + radius * np.cos(angle),
                                 cy + radius * np.sin(angle)])
            return {"vertices": vertices}
        raise ValueError(f"Unsupported shape: {shape!r}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _generate_roi_id(self) -> str:
        existing = {r.id for r in self._items}
        while True:
            self._id_counter += 1
            candidate = f"roi_{self._id_counter}"
            if candidate not in existing:
                return candidate

    def _next_color(self) -> str:
        color = self._palette[self._color_index % len(self._palette)]
        self._color_index += 1
        return color

    def _default_label(self, roi_id: str, stack_id: str) -> str:
        return f"{roi_id} in {stack_id}"

    @staticmethod
    def _params_equal(a: dict, b: dict) -> bool:
        def norm(v):
            if isinstance(v, (int, float, np.number)):
                return round(float(v), 4)
            if isinstance(v, list):
                return [norm(x) for x in v]
            return v
        return norm(a) == norm(b)