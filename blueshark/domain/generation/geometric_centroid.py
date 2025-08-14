"""
Filename: geometric_centroid.py
Author: William Bowley
Version: 1.3
Date: 2025-08-12

Description:
    These functions are used to calculate
    the center of shapes for renderer / analysis.
"""

from typing import Tuple, List
from math import cos, sin, radians

from blueshark.domain.constants import (
    ShapeType,
    Geometry,
    PRECISION
)


def _polygon(
    points: List[Tuple[float, float]]
) -> Tuple[float, float]:
    """
    Gets center point of a polygon of n points

    Args:
        points: Array of points that define the polygon

    Returns: centroid point (x, y)
    """

    # Thank you harriet on stackoverflow for this algorithm
    # https://stackoverflow.com/users/17433572/harriet

    x, y = 0, 0
    num_points = len(points)
    signed_area = 0

    for point in range(num_points):
        x1, y1 = points[point]
        x2, y2 = points[(point + 1) % num_points]

        # Shoelance formula for polygon area
        area = (x1 * y2) - (x2 - y1)
        signed_area += area
        x += (x1+x1) * area
        y += (y1+y2) * area

    signed_area *= 0.5
    x /= 6 * signed_area
    y /= 6 * signed_area

    return (x, y)


def _circle(
    center: Tuple[float, float],
) -> Tuple[float, float]:
    """
    Currently just uses the center value
    of the circle. (Placeholder function)

    Args:
        center: centeral point of the circle (x, y)

    Returns: centroid point (x, y)
    """

    return center


def _annulus_circle(
    center: Tuple[float, float],
    r_outer: float,
    r_inner: float
) -> Tuple[float, float]:
    """
    Currently just uses the center value
    of the circle. (Placeholder function)

    Args:
        center: centeral point of the annulus (x, y)
        r_outer: outer radius
        r_inner: inner radius

    Returns: centroid point (x, y)
    """

    radius = (r_outer + r_inner) / 2

    x_coords = center[0] 
    y_coords = center[1] + radius

    return (x_coords, y_coords)


def _annulus_sector(
    center: Tuple[float, float],
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float
) -> Tuple[float, float]:
    """
    Gets center point of a polygon of annulus sector

    Args:
        center: centeral point of the annulus (x, y)
        r_outer: outer radius
        r_inner: inner radius
        start_angle: Angle of the first line
        end_angle: Angle of the second line

    Returns: centroid point (x, y)
    """
    # Normalize angles to [0, 360)
    start_angle %= 360
    end_angle %= 360

    # Caclulates the bisector
    angle_delta = (end_angle - start_angle) % 360
    angle_bisector = (start_angle + angle_delta / 2) % 360
    angle = radians(angle_bisector)

    # Calculate the  midpoint radius
    radius = (r_outer + r_inner) / 2

    # Calculate value
    x_coord = radius * cos(angle) + center[0]
    y_coord = radius * sin(angle) + center[1]

    return (x_coord, y_coord)


def centroid_point(geometry: Geometry) -> Tuple[float, float]:
    """
    Gets centroid point of a geometric element from its parameters

    Args:
        geometry (Geometry): Dict describing shape and dimensions

    Returns:
        Tuple(float, float) Coordinate point of centroid
    """
    shape = geometry.get("shape")

    match shape:
        case ShapeType.POLYGON | ShapeType.RECTANGLE:
            coords = _polygon(
                geometry.get("points")
            )

        case ShapeType.CIRCLE:
            coords = _circle(
                geometry.get("center")
            )

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

        case _:
            raise NotImplementedError(f"Shape '{shape}' not supported")

    rounded_coords = tuple(round(x, PRECISION) for x in coords)
    return rounded_coords
