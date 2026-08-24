# puprisa/controllers/phasor_roi_controller.py
"""Phasor-space ROI controller for the Phasor analysis window.

This subclass handles ROIs defined in (g, s) coordinates.  The scene is
the phasor histogram view.  Coordinate conversion uses the fixed limits
g, s ∈ [-1, 1] and the density pixmap rectangle maintained by
:class:`PhasorPlotController`.

The controller receives a shared :class:`StackManager` so that pps objects
can be resolved independently of the plot controller.
"""

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPolygonF

import numpy as np

from puprisa.controllers.base_roi_controller import BaseRoiController
from puprisa.ui.widgets.draggable_roi import DraggableROI, DraggablePolygonROI
from puprisa.controllers.phasor_plot_controller import PhasorPlotController
from puprisa.model.stack_manager import StackManager
from puprisa.utils.geometry_utils import shape_to_mask


class PhasorRoiController(BaseRoiController):
    """Manage ROI shapes in phasor (g, s) space.

    Unified parameter keys:

    - rectangle: ``x``, ``y``, ``width``, ``height``
    - circle: ``center_x``, ``center_y``, ``radius``
    - ellipse: ``center_x``, ``center_y``, ``radius_x``, ``radius_y``
    - polygon: ``vertices`` as list of ``[g, s]`` pairs
    """

    def __init__(
        self,
        stack_manager: StackManager,
        plot_controller: PhasorPlotController,
        roi_list_widget,
        shape_combo,
    ):
        super().__init__(
            roi_list_widget, shape_combo, plot_controller.phasorScene, stack_manager
        )
        self.plot_controller = plot_controller
        self.g_lim = plot_controller.g_lim
        self.s_lim = plot_controller.s_lim
        self.phasor_pixmap_rect = plot_controller.phasor_pixmap_rect

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------
    def _space_default_params(self, shape: str) -> dict:
        """Generate default parameters at the centre of the phasor plane."""
        cg, cs = 0.0, 0.0
        size_gs = 0.3

        if shape == "rectangle":
            return {
                "x": cg - size_gs / 2,
                "y": cs - size_gs / 2,
                "width": size_gs,
                "height": size_gs,
            }
        if shape == "circle":
            return {"center_x": cg, "center_y": cs, "radius": size_gs / 2}
        if shape == "ellipse":
            return {
                "center_x": cg,
                "center_y": cs,
                "radius_x": size_gs / 2,
                "radius_y": size_gs / 2,
            }
        if shape == "polygon":
            radius = size_gs / 2
            vertices = []
            for i in range(3):
                angle = 2 * np.pi * i / 3 - np.pi / 2
                vertices.append([
                    cg + radius * np.cos(angle),
                    cs + radius * np.sin(angle),
                ])
            return {"vertices": vertices}
        raise ValueError(f"Unsupported shape: {shape}")

    def _space_create_graphics_item(self, roi: dict):
        """Create a DraggableROI or DraggablePolygonROI in the phasor scene."""
        shape = roi["shape"]
        params = roi["params"]
        color = roi["color"]

        if shape == "polygon":
            scene_poly = self._gs_vertices_to_scene_polygon(params)
            item = DraggablePolygonROI(scene_poly, color=color)
        else:
            scene_rect = self._gs_params_to_scene_rect(shape, params)
            if scene_rect is None:
                roi["graphics_item"] = None
                return
            item_rect = QRectF(0, 0, scene_rect.width(), scene_rect.height())
            item = DraggableROI(item_rect, color=color, shape_type=shape)
            item.setPos(scene_rect.topLeft())

        item.set_roi_changed_callback(
            lambda: self._on_graphics_item_changed(roi["id"])
        )
        item.set_movement_bounds(self.phasor_pixmap_rect)
        item.setZValue(10)
        self.scene.addItem(item)

        roi["graphics_item"] = item
        self._update_graphics_item_visibility(roi)

    def _space_update_params_from_item(self, roi: dict):
        """Extract (g, s) parameters from the ROI's graphics item."""
        item = roi.get("graphics_item")
        if item is None:
            return

        shape = roi["shape"]
        if shape == "polygon":
            roi["params"] = self._scene_polygon_to_gs_vertices(item)
        else:
            scene_rect = item.get_scene_rect()
            params = self._scene_rect_to_gs_params(shape, scene_rect)
            if params is not None:
                roi["params"] = params

    def _space_build_mask(self, roi: dict, pps) -> np.ndarray | None:
        """Build a 2D pixel keep-mask from the ROI's phasor-space geometry.

        The mask is constructed by applying ``shape_to_mask`` to the
        stack's cached ``phasor_coords`` array.  This array is maintained
        by :class:`PhasorWindow` and maps each flattened pixel to its
        (g, s) coordinates at the current frequency.
        """
        stack_item = self.stack_manager.get_item_by_id(roi["stack_id"])
        if stack_item is None:
            return None

        coords = stack_item.get("phasor_coords")
        if coords is None:
            return None

        g = coords[:, 0]
        s = coords[:, 1]
        mask_1d = shape_to_mask(roi["shape"], roi["params"], g, s)
        if mask_1d is None:
            return None

        h, w = pps.image_dimensions
        return mask_1d.reshape(h, w)

    # ------------------------------------------------------------------
    # Phasor coordinate conversions: scene <-> (g, s)
    # ------------------------------------------------------------------
    def _scene_point_to_gs(self, pt: QPointF) -> tuple[float, float]:
        """Scene point -> (g, s) coordinates."""
        g = self.g_lim[0] + (pt.x() / self.phasor_pixmap_rect.width()) * (
            self.g_lim[1] - self.g_lim[0]
        )
        s = self.s_lim[1] - (pt.y() / self.phasor_pixmap_rect.height()) * (
            self.s_lim[1] - self.s_lim[0]
        )
        return g, s

    def _gs_to_scene_point(self, g: float, s: float) -> QPointF:
        """(g, s) coordinates -> scene point."""
        x = (g - self.g_lim[0]) / (self.g_lim[1] - self.g_lim[0]) * self.phasor_pixmap_rect.width()
        y = (self.s_lim[1] - s) / (self.s_lim[1] - self.s_lim[0]) * self.phasor_pixmap_rect.height()
        return QPointF(x, y)

    def _scene_rect_to_gs_params(self, shape: str, scene_rect: QRectF) -> dict | None:
        """Scene rectangle -> (g, s) geometry parameters."""
        p1 = self._scene_point_to_gs(scene_rect.topLeft())
        p2 = self._scene_point_to_gs(scene_rect.bottomRight())
        g_left, s_top = p1[0], p1[1]
        g_right, s_bottom = p2[0], p2[1]

        w = g_right - g_left
        h = s_top - s_bottom
        cg = (g_left + g_right) / 2.0
        cs = (s_top + s_bottom) / 2.0

        if shape == "rectangle":
            return {"x": g_left, "y": s_bottom, "width": w, "height": h}
        if shape == "circle":
            return {"center_x": cg, "center_y": cs, "radius": min(w, h) / 2.0}
        if shape == "ellipse":
            return {
                "center_x": cg,
                "center_y": cs,
                "radius_x": w / 2.0,
                "radius_y": h / 2.0,
            }
        return None

    def _gs_params_to_scene_rect(self, shape: str, params: dict) -> QRectF | None:
        """(g, s) parameters -> scene QRectF."""
        if shape == "rectangle":
            g_left = params["x"]
            g_right = g_left + params["width"]
            s_bottom = params["y"]
            s_top = s_bottom + params["height"]
        elif shape == "circle":
            cg = params["center_x"]
            cs = params["center_y"]
            r = params["radius"]
            g_left, g_right = cg - r, cg + r
            s_bottom, s_top = cs - r, cs + r
        elif shape == "ellipse":
            cg = params["center_x"]
            cs = params["center_y"]
            rg = params["radius_x"]
            rs = params["radius_y"]
            g_left, g_right = cg - rg, cg + rg
            s_bottom, s_top = cs - rs, cs + rs
        else:
            return None

        p1 = self._gs_to_scene_point(g_left, s_top)
        p2 = self._gs_to_scene_point(g_right, s_bottom)
        return QRectF(p1, p2)

    def _scene_polygon_to_gs_vertices(self, polygon_item) -> dict:
        """Scene polygon -> (g, s) vertices."""
        scene_poly = polygon_item.get_scene_polygon()
        vertices = []
        for pt in scene_poly:
            g, s = self._scene_point_to_gs(pt)
            vertices.append([g, s])
        return {"vertices": vertices}

    def _gs_vertices_to_scene_polygon(self, params: dict) -> QPolygonF:
        """(g, s) vertices -> scene polygon."""
        vertices = params.get("vertices", [])
        pts = [self._gs_to_scene_point(v[0], v[1]) for v in vertices]
        return QPolygonF(pts)