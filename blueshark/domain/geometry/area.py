"""
Filename: area.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13

Description:
    These functions are used to calculate
    the area of geometric shapes for analysis.
"""

from typing import List, Tuple
from math import radians

from blueshark.domain.constants import PRECISION, PI
from blueshark.domain.definitions import Geometry, ShapeType


def _area_polygon(points: List[Tuple[float, float]]) -> float:
    """
    Calculate the area of a polygon with n points using the shoelace formula.

    Args:
        points: List of (x, y) coordinates defining the polygon vertices.

    Returns:
        float: Area of the polygon.
    """
    if not points or len(points) < 3:
        raise ValueError("Polygon must have at least 3 points")

    # Reference: https://en.wikipedia.org/wiki/Shoelace_formula
    area = 0.0
    number_points = len(points)
    for i in range(number_points):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % number_points]
        area += x1 * y2 - x2 * y1

    return abs(area) / 2


def _area_circle(radius: float) -> float:
    """
    Calculate the area of a circle.

    Args:
        radius: Distance from center to any point on the circumference.

    Returns:
        float: Area of the circle.
    """
    if radius is None:
        raise ValueError("Circle radius is required")
    return PI * radius ** 2


def _area_annulus_sector(
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float
) -> float:
    """
    Calculate the area of an annulus sector.

    Args:
        r_outer: Outer radius.
        r_inner: Inner radius.
        start_angle: Angle of the first boundary line (degrees).
        end_angle: Angle of the second boundary line (degrees).

    Returns:
        float: Area of the annulus sector.
    """
    for param in (r_outer, r_inner, start_angle, end_angle):
        if param is None:
            raise ValueError("All annulus sector parameters are required")

    # Reference: https://en.wikipedia.org/wiki/Annulus_(mathematics)
    angle_rad = radians(abs(end_angle - start_angle))
    area = 0.5 * angle_rad * (r_outer ** 2 - r_inner ** 2)
    return area


def _area_annulus_circle(
    r_outer: float,
    r_inner: float
) -> float:
    """
    Calculate the area of an annulus circle.

    Args:
        r_outer: Outer radius.
        r_inner: Inner radius.

    Returns:
        float: Area of the annulus.
    """
    if r_outer is None or r_inner is None:
        raise ValueError("Outer and inner radii are required for annulus")

    # Reference: https://en.wikipedia.org/wiki/Annulus_(mathematics)
    return PI * (r_outer ** 2 - r_inner ** 2)


def calculate_area(geometry: Geometry) -> float:
    """
    Calculate the area of a geometric element from its parameters.

    Args:
        geometry (Geometry): Dictionary describing shape and dimensions.

    Returns:
        float: Area of the element.

    Raises:
        ValueError, NotImplementedError: For invalid or unsupported shapes.
    """
    if not geometry or "shape" not in geometry:
        raise ValueError("Geometry dictionary must contain a 'shape' key")

    shape = geometry["shape"]

    match shape:
        case ShapeType.POLYGON | ShapeType.RECTANGLE:
            points = geometry.get("points")
            area = _area_polygon(points)

        case ShapeType.CIRCLE:
            radius = geometry.get("radius")
            area = _area_circle(radius)

        case ShapeType.ANNULUS_SECTOR:
            area = _area_annulus_sector(
                geometry.get("radius_outer"),
                geometry.get("radius_inner"),
                geometry.get("start_angle"),
                geometry.get("end_angle")
            )

        case ShapeType.ANNULUS_CIRCLE:
            area = _area_annulus_circle(
                geometry.get("radius_outer"),
                geometry.get("radius_inner")
            )

        case ShapeType.HYBRID:
            # Approximate area using all edge points
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

            area = _area_polygon(unique_points)

        case _:
            raise NotImplementedError(f"Shape '{shape}' not supported")

    return round(area, PRECISION)
