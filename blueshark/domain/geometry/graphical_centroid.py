"""
Filename: graphical_centroid.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13

Description:
    These functions calculate the graphical center of shapes
    for renderer placement or visualization purposes.

    NOTE:
        This centroid is for rendering/visual purposes. It is not the true
        area-weighted or mass centroid.
"""

from math import cos, sin, radians

from blueshark.domain.constants import PRECISION
from blueshark.domain.definitions import ShapeType, Geometry


def _polygon(points: list[tuple[float, float]]) -> tuple[float, float]:
    """
    Calculates the centroid of a polygon.

    Args:
        points: List of (x, y) coordinates defining the polygon vertices.

    Returns:
        Tuple (x, y) of graphical centroid.
    """
    num_points = len(points)
    signed_area = 0
    cx = 0
    cy = 0

    for i in range(num_points):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % num_points]
        a = (x0 * y1) - (x1 * y0)
        signed_area += a
        cx += (x0 + x1) * a
        cy += (y0 + y1) * a

    signed_area *= 0.5

    if signed_area == 0:
        msg = (
            "Polygon is degenerate or vertices "
            "are not in counter-clockwise order."
        )
        raise ValueError(msg)

    cx /= 6 * signed_area
    cy /= 6 * signed_area

    return (cx, cy)


def _circle(center: tuple[float, float]) -> tuple[float, float]:
    """
    Returns the center of a circle as its graphical centroid.

    Args:
        center: Tuple (x, y) of the circle center.

    Returns:
        Tuple (x, y) of graphical centroid.
    """
    return center


def _annulus_circle(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float
) -> tuple[float, float]:
    """
    Returns an approximate graphical centroid for an annulus circle.

    Args:
        center: Tuple (x, y) of the annulus center.
        r_outer: Outer radius.
        r_inner: Inner radius.

    Returns:
        Tuple (x, y) of graphical centroid.
    """
    radius = (r_outer + r_inner) / 2
    x_coord = center[0]
    y_coord = center[1] + radius
    return (x_coord, y_coord)


def _annulus_sector(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float
) -> tuple[float, float]:
    """
    Returns an approximate graphical centroid for an annulus sector.

    Args:
        center: Tuple (x, y) of the annulus center.
        r_outer: Outer radius.
        r_inner: Inner radius.
        start_angle: Start angle in degrees.
        end_angle: End angle in degrees.

    Returns:
        Tuple (x, y) of graphical centroid.
    """
    start_angle %= 360
    end_angle %= 360
    angle_delta = (end_angle - start_angle) % 360
    angle_bisector = (start_angle + angle_delta / 2) % 360
    angle = radians(angle_bisector)
    radius = (r_outer + r_inner) / 2

    x_coord = radius * cos(angle) + center[0]
    y_coord = radius * sin(angle) + center[1]

    return (x_coord, y_coord)


def centroid_point(geometry: Geometry) -> tuple[float, float]:
    """
    Returns the graphical centroid of a shape for rendering.

    NOTE:
        This centroid is for rendering/visual purposes. It is not the true
        area-weighted or mass centroid.

    Args:
        geometry (Geometry): Dictionary describing shape and dimensions.

    Returns:
        Tuple (x, y) of graphical centroid.

    Raises:
        NotImplementedError: If shape is unsupported
    """
    if not geometry or "shape" not in geometry:
        raise ValueError("Geometry dictionary must contain a 'shape' key")

    shape = geometry.get("shape")

    match shape:
        case ShapeType.POLYGON | ShapeType.RECTANGLE:
            coords = _polygon(geometry.get("points"))

        case ShapeType.CIRCLE:
            coords = _circle(geometry.get("center"))

        case ShapeType.ANNULUS_CIRCLE:
            coords = _annulus_circle(
                geometry.get("center"),
                geometry.get("radius_outer"),
                geometry.get("radius_inner")
            )

        case ShapeType.ANNULUS_SECTOR:
            coords = _annulus_sector(
                geometry.get("center"),
                geometry.get("radius_outer"),
                geometry.get("radius_inner"),
                geometry.get("start_angle"),
                geometry.get("end_angle")
            )

        case ShapeType.HYBRID:
            # Approximate graphical centroid using all edge points
            points = []
            for edge in geometry["edges"]:
                points.append(edge["start"])
                points.append(edge["end"])

            # Remove duplicates while keeping order
            seen = set()
            unique_points = []
            for pt in points:
                if pt not in seen:
                    unique_points.append(pt)
                    seen.add(pt)

            coords = _polygon(unique_points)

        case _:
            raise NotImplementedError(f"Shape '{shape}' not supported")

    return tuple(round(x, PRECISION) for x in coords)
