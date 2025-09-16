"""
Filename: utils.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13

Description:
    This module contains utility / helper functions
    for renderers and solvers.
"""

from math import atan2, hypot, cos, sin
from blueshark.domain.constants import PI, PRECISION, EPSILON
from blueshark.domain.definitions import Geometry, ShapeType
from blueshark.domain.geometry.graphical_centroid import _polygon
from blueshark.domain.geometry.validation import validate_shape


def _check_point(
    name: str,
    point: tuple[float, float]
) -> None:
    """
    Check if a given tuple contains exactly two
    floating-point numbers. Raises an error if not.
    """
    # Type test
    if not isinstance(point, tuple):
        raise TypeError(f"'{name}' must be a tuple, got: {point}")

    # Range test
    if len(point) != 2:
        raise ValueError(f"'{name}' must be length two, got: {point}")

    # Type test
    if not all(isinstance(coord, (float, int)) for coord in point):
        msg = f"Tuple '{name}' must contain only float or int, got {point}"
        raise ValueError(msg)


def _scale_polygon(
    points: list[tuple[float, float]],
    factor: float
) -> list[tuple[float, float]]:
    """
    Scales (expands or shrinks) a polygon away from a given
    centroid

    Args:
        points: list of (x, y) tuple
        factor: float > 1 expands, < 1 shrinks
    """

    # Assumes that the centroid is geometric center
    x0, y0 = _polygon(points)
    print(x0, y0)

    scaled_points = []
    for x1, y1 in points:
        scaled_points.append((
            x0 + factor * (x1 - x0),
            y0 + factor * (y1 - y0)
        ))

    return scaled_points


def mid_points_line(
    point1: tuple[float, float],
    point2: tuple[float, float]
) -> tuple[float, float]:
    """
    Calculate the midpoint of a line segment.

    Args:
        point1:
            Coordinates of the first point (x, y).
        point2:
            Coordinates of the second point (x, y).

    Returns:
        tuple[float, float]: Coordinates of the midpoint (x, y).
    """
    _check_point("point1", point1)
    _check_point("point2", point2)

    x1, y1 = point1
    x2, y2 = point2

    coords = ((x1 + x2) / 2, (y1 + y2) / 2)
    return tuple(round(x, PRECISION) for x in coords)


def mid_points_arc(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    center: tuple[float, float],
) -> tuple[float, float]:
    """
    Calculate an approximate midpoint of a circular arc.

    Args:
        start_point:
            Coordinates of the arc start point (x, y).
        end_point:
            Coordinates of the arc end point (x, y).
        center:
            Coordinates of the circle center (x, y).

    Returns:
        (cx, cy) center coordinates. Values are round to configured PRECISION
    """

    _check_point("start_point", start_point)
    _check_point("end_point", end_point)
    _check_point("center", center)

    start_x, start_y = start_point
    end_x, end_y = end_point
    center_x, center_y = center

    start_angle = atan2(start_y - center_y, start_x - center_x)
    end_angle = atan2(end_y - center_y, end_x - center_x)
    mid_angle = (start_angle + end_angle) / 2

    if abs(end_angle - start_angle) > PI:
        mid_angle += PI

    radius = hypot(start_x - center_x, start_y - center_y)
    mid_x = center_x + radius * cos(mid_angle)
    mid_y = center_y + radius * sin(mid_angle)

    coords = (mid_x, mid_y)
    return tuple(round(x, PRECISION) for x in coords)


def find_arc_center(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    start_angle: float,
    end_angle: float,
) -> tuple[float, float]:
    """
    Calculate the center of a circular arc defined by start and end points
    and a sweep angle (radians).

    Args:
        start_point:
            Coordinates of the arc start point (x, y).
        end_point:
            Coordinates of the arc end point (x, y).
        start_angle:
            Angle with respect to the positive horizontal at start_point.
        start_end:
            Angle with respect to the positive horizontal at end_point.

    Returns:
        (cx, cy) center coordinates. Values are round to configured PRECISION
    """

    _check_point("start_point", start_point)
    _check_point("end_point", end_point)

    x0, y0 = start_point
    x1, y1 = end_point

    if hypot(x1 - x0, y1 - y0) < EPSILON:
        raise ValueError("Start and end points must be distinct.")

    denom_x = cos(end_angle) - cos(start_angle)
    denom_y = sin(end_angle) - sin(start_angle)

    # Identical angles or 180 degrees apart.
    if abs(denom_x) < EPSILON and abs(denom_y) < EPSILON:
        msg = "Start and end angles cannot be identical or pi radians apart."
        raise ValueError(msg)

    # Solve for radius using the x and y components
    # Both should be consistent with one other
    if abs(denom_x) > EPSILON:
        radius_from_x = (x1 - x0) / denom_x
    else:
        radius_from_x = float('inf')

    if abs(denom_y) > EPSILON:
        radius_from_y = (y1 - y0) / denom_y
    else:
        radius_from_y = float('inf')

    # Check for consistency between the two radius calculations
    if (
        radius_from_x != float('inf') and
        radius_from_y != float('inf') and
        abs(radius_from_x - radius_from_y) > EPSILON
    ):
        msg = "Angles or points do not form a consistent arc."
        raise ValueError(msg)

    radius = radius_from_x if radius_from_x != float('inf') else radius_from_y

    # Calculate center using the start point and angle
    cx = x0 - radius * cos(start_angle)
    cy = y0 - radius * sin(start_angle)

    return tuple(round(coord, PRECISION) for coord in (cx, cy))


def scale_geometry(
    shape: Geometry,
    factor: float
) -> Geometry:
    """
    Scales shape by factor

    Implementation Note:
    - Hybrid shapes are not currently supported

    Args:
        shape: Defines the boundary shape (Geometry (Enum))
        factor: scaling factor
    """
    validate_shape(shape)

    shape_type = shape.get("shape")
    match shape_type:
        case ShapeType.POLYGON | ShapeType.RECTANGLE:
            shape["points"] = _scale_polygon(
                shape["points"],
                factor
            )

        case ShapeType.CIRCLE:
            shape["radius"] = factor * shape["radius"]

        case ShapeType.ANNULUS_CIRCLE | ShapeType.ANNULUS_SECTOR:
            shape["radius_outer"] = factor * shape["radius_outer"]
            shape["radius_inner"] = factor * shape["radius_inner"]

        case _:
            msg = f"Shape '{shape_type}' not supported for scaling"
            raise NotImplementedError(msg)

    return shape
