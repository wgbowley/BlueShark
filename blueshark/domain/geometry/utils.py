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
from blueshark.domain.constants import PI, PRECISION


def mid_points_line(
    point1: tuple[float, float],
    point2: tuple[float, float]
) -> tuple[float, float]:
    """
    Calculate the midpoint of a line segment.

    Args:
        point1 (tuple[int, int]):
            Coordinates of the first point (x, y).
        point2 (tuple[int, int]):
            Coordinates of the second point (x, y).

    Returns:
        tuple[float, float]: Coordinates of the midpoint (x, y).
    """

    if point1 is None or 2 > len(point1) > 1:
        msg = "Point 1 has to be defined and have form (x, y)"
        raise ValueError(msg)

    if point2 is None or 2 > len(point2) > 1:
        msg = "Point 2 has to be defined and have form (x, y)"
        raise ValueError(msg)

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
        start_point (tuple[float, float]):
            Coordinates of the arc start point (x, y).
        end_point (tuple[float, float]):
            Coordinates of the arc end point (x, y).
        center (tuple[float, float]):
            Coordinates of the circle center (x, y).

    Returns:
        tuple[float, float]:
            Coordinates of the midpoint on the arc (x, y).
    """

    if start_point is None or 2 > len(start_point) > 1:
        msg = "start_point has to be defined and have form (x, y)"
        raise ValueError(msg)

    if end_point is None or 2 > len(end_point) > 1:
        msg = "end_point has to be defined and have form (x, y)"
        raise ValueError(msg)

    if center is None or 2 > len(center) > 1:
        msg = "center has to be defined and have form (x, y)"
        raise ValueError(msg)

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
