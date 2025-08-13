"""
Filename: geometric_area.py
Author: William Bowley
Version: 1.3
Date: 2025-08-12

Description:
    These functions are used to calculate
    the area of shapes for analysis.
"""

from typing import List, Tuple
from math import radians, pi
from blueshark.domain.constants import (
    ShapeType,
    Geometry,
    PRECISION
)


def _area_polygon(points: List[Tuple[float, float]]) -> float:
    """
    Calculates the area of a polygon of n points

    Args:
        points: Array of points that define the polygon

    Returns: area of the polygon
    """
    # https://en.wikipedia.org/wiki/Shoelace_formula
    area = 0.0
    number_points = len(points)
    for i in range(number_points):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % number_points]
        area += x1 * y2 - x2 * y1

    return abs(area) / 2


def _area_circle(radius: float) -> float:
    """
    Calculate the area of a circle

    Args:
        Radius: Length from center to any point on circumference

    Returns: area of the circle
    """

    return pi * radius ** 2


def _area_annulus_sector(
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float
) -> float:
    """
    Calculate the area of a annulus sector

    Args:
        r_outer: outer radius
        r_inner: inner radius
        start_angle: Angle of the first line
        end_angle: Angle of the second line
    """
    # https://en.wikipedia.org/wiki/Annulus_(mathematics)
    angle_rad = radians(abs(end_angle - start_angle))
    area = 0.5 * angle_rad * (r_outer ** 2 - r_inner ** 2)
    return area


def _area_annulus_circle(
    r_outer: float,
    r_inner: float
) -> float:
    """
    Calculate the area of a annulus circle

    Args:
        r_outer: outer radius
        r_inner: inner radius
    """
    # https://en.wikipedia.org/wiki/Annulus_(mathematics)
    return pi * (r_outer ** 2 - r_inner ** 2)


def calculate_area(geometry: Geometry) -> float:
    """
    Calculate the area of a geometric element from its parameters.

    Args:
        geometry (Geometry): Dict describing shape and dimensions.

    Returns:
        float: Area of the element.

    Raises:
        ValueError, NotImplementedError: For invalid or unsupported shapes.
    """
    shape = geometry.get("shape")
    points = geometry.get("points", [])

    match shape:
        case ShapeType.POLYGON | ShapeType.RECTANGLE:
            area = _area_polygon(points)

        case ShapeType.CIRCLE:
            area = _area_circle(
                geometry.get("radius")
            )

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

        case _:
            raise NotImplementedError(f"Shape '{shape}' not supported")

    return round(area, PRECISION)
