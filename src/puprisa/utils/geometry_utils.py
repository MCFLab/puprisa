# puprisa/utils/geometry.py

import numpy as np
from matplotlib.path import Path
from matplotlib.patches import Rectangle, Circle, Ellipse, Polygon

def points_in_rectangle(x, y, width, height, xs, ys):
    """Return a boolean mask of points inside an axis-aligned rectangle.

    The rectangle spans ``[x, x + width)`` horizontally and
    ``[y, y + height)`` vertically (upper edge and left edge inclusive,
    right edge and bottom edge exclusive).

    Args:
        x (float): Left edge of the rectangle.
        y (float): Top edge of the rectangle.
        width (float): Width of the rectangle.
        height (float): Height of the rectangle.
        xs (np.ndarray): X-coordinates of the points to test.
        ys (np.ndarray): Y-coordinates of the points to test.

    Returns:
        np.ndarray: Boolean array with the same shape as ``xs``/``ys``
            where ``True`` marks points inside the rectangle.
    """
    return (xs >= x) & (xs < x + width) & (ys >= y) & (ys < y + height)

def points_in_circle(cx, cy, radius, xs, ys):
    """Return a boolean mask of points inside a circle.

    Args:
        cx (float): X-coordinate of the circle center.
        cy (float): Y-coordinate of the circle center.
        radius (float): Radius of the circle.
        xs (np.ndarray): X-coordinates of the points to test.
        ys (np.ndarray): Y-coordinates of the points to test.

    Returns:
        np.ndarray: Boolean array with the same shape as ``xs``/``ys``
            where ``True`` marks points inside (or on) the circle.
    """
    return (xs - cx)**2 + (ys - cy)**2 <= radius**2

def points_in_ellipse(cx, cy, rx, ry, xs, ys):
    """Return a boolean mask of points inside an axis-aligned ellipse.

    Args:
        cx (float): X-coordinate of the ellipse center.
        cy (float): Y-coordinate of the ellipse center.
        rx (float): Semi-major axis length along X.
        ry (float): Semi-major axis length along Y.
        xs (np.ndarray): X-coordinates of the points to test.
        ys (np.ndarray): Y-coordinates of the points to test.

    Returns:
        np.ndarray: Boolean array with the same shape as ``xs``/``ys``
            where ``True`` marks points inside (or on) the ellipse.
    """
    return ((xs - cx) / (rx + 1e-10))**2 + ((ys - cy) / (ry + 1e-10))**2 <= 1.0

def points_in_polygon(vertices, xs, ys):
    """Return a boolean mask of points inside a polygon.

    Args:
        vertices (array-like): Sequence of ``(x, y)`` vertex pairs
            defining the polygon.
        xs (np.ndarray): X-coordinates of the points to test.
        ys (np.ndarray): Y-coordinates of the points to test.

    Returns:
        np.ndarray: Boolean array with the same shape as ``xs``/``ys``
            where ``True`` marks points inside the polygon.
    """
    path = Path(vertices)
    points = np.column_stack((xs.ravel(), ys.ravel()))
    return path.contains_points(points).reshape(xs.shape)

def shape_to_mask(shape, params, xs, ys):
    """Generate a boolean mask of points contained within a geometric shape.

    Supported shapes and their required ``params`` keys:

    - ``"rectangle"``: ``x``, ``y``, ``width``, ``height``
    - ``"circle"``: ``center_x``, ``center_y``, ``radius``
    - ``"ellipse"``: ``center_x``, ``center_y``, ``radius_x``, ``radius_y``
    - ``"polygon"``: ``vertices`` (sequence of ``(x, y)`` pairs)

    Args:
        shape (str): Name of the shape to test against. Must be one of
            ``"rectangle"``, ``"circle"``, ``"ellipse"`` or ``"polygon"``.
        params (dict): Keyword parameters describing the shape, as
            detailed above.
        xs (np.ndarray): X-coordinates of the points to test.
        ys (np.ndarray): Y-coordinates of the points to test.

    Returns:
        np.ndarray: Boolean array with the same shape as ``xs``/``ys``
            where ``True`` marks points inside the given shape.

    Raises:
        ValueError: If ``shape`` is not one of the supported shapes.
    """
    if shape == "rectangle":
        return points_in_rectangle(params["x"], params["y"], params["width"], params["height"], xs, ys)
    elif shape == "circle":
        return points_in_circle(params["center_x"], params["center_y"], params["radius"], xs, ys)
    elif shape == "ellipse":
        return points_in_ellipse(params["center_x"], params["center_y"], params["radius_x"], params["radius_y"], xs, ys)
    elif shape == "polygon":
        return points_in_polygon(params.get("vertices", []), xs, ys)
    else:
        raise ValueError(f"Unsupported shape: {shape}")

def shape_to_patch(shape: str, params: dict, **kwargs):
    """Create a matplotlib patch for a ROI shape.

    Parameters
    ----------
    shape : str
        One of ``"rectangle"``, ``"circle"``, ``"ellipse"``, or
        ``"polygon"``.
    params : dict
        Geometry parameters matching the shape type:

        - rectangle: ``{"x", "y", "width", "height"}``
        - circle:    ``{"center_x", "center_y", "radius"}``
        - ellipse:   ``{"center_x", "center_y", "radius_x", "radius_y"}``
        - polygon:   ``{"vertices": [[x1,y1], [x2,y2], ...]}``

    **kwargs
        Additional keyword arguments are passed to the matplotlib patch
        constructor.  Typical values are ``fill=False``,
        ``edgecolor='red'``, ``linewidth=1.5``.

    Returns
    -------
    matplotlib.patches.Patch or None
        The created patch, or ``None`` if the shape is unsupported or
        the required parameters are missing.
    """
    if shape == "rectangle":
        return Rectangle(
            (params["x"], params["y"]),
            params["width"],
            params["height"],
            **kwargs,
        )

    if shape == "circle":
        return Circle(
            (params["center_x"], params["center_y"]),
            params["radius"],
            **kwargs,
        )

    if shape == "ellipse":
        return Ellipse(
            (params["center_x"], params["center_y"]),
            2 * params["radius_x"],
            2 * params["radius_y"],
            **kwargs,
        )

    if shape == "polygon":
        vertices = [(v[0], v[1]) for v in params.get("vertices", [])]
        if not vertices:
            return None
        return Polygon(vertices, closed=True, **kwargs)

    return None