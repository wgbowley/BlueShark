"""
Filename: smoothing.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all solvers
"""

import math
from typing import List, Tuple


def _distance(
    point_1: Tuple[int, int],
    point_2: Tuple[int, int]
) -> float:
    """
    Calculates the distance between two points
    """
    x0, y0 = point_1
    x1, y1 = point_2
    return math.hypot(x0-x1, y0-y1)


def _influence_points(
    points: List[Tuple[int, int]],
    current_point: Tuple[int, int],
    radius: int,
) -> list[Tuple[int, int]]:
    """
    Finds local points to a point within a square area
    """
    influence_points = []
    x0, y0 = current_point

    for x, y in points:
        if abs(x - x0) < radius and abs(y - y0) < radius:
            influence_points.append((x, y))

    return influence_points


def simplify_points(
    points: List[Tuple[float, float]],
    min_dist: float
) -> List[Tuple[float, float]]:
    """
    Simplifies a list of 2D points by removing points that are too close
    together.
    """
    if not points:
        return []

    simplified = [points[0]]
    for pt in points[1:]:
        x0, y0 = simplified[-1]
        x1, y1 = pt
        if _distance((x0, y0), (x1, y1)) >= min_dist:
            simplified.append(pt)

    return simplified


def smooth_points(
    points: List[Tuple[float, float]],
    window_size: int = 3
) -> List[Tuple[float, float]]:
    """
    Smooths a list of 2D points using a moving average.
    """
    if not points or window_size < 2:
        return points

    n = len(points)
    smoothed = []

    for i in range(n):
        # Determine the window boundaries
        start = max(0, i - window_size // 2)
        end = min(n, i + window_size // 2 + 1)

        # Average x and y in the window
        avg_x = sum(points[j][0] for j in range(start, end)) / (end - start)
        avg_y = sum(points[j][1] for j in range(start, end)) / (end - start)

        smoothed.append((avg_x, avg_y))

    return smoothed


def order_points(
    points: list[tuple[int, int]],
    radius: int = 20
) -> List[Tuple[float, float]]:
    """
    Orders the points into a series of connected
    points perimeter
    """
    if not points:
        return []

    temp_points = points.copy()
    ordered = [temp_points.pop(0)]

    for _ in range(len(points) - 1):
        current_point = ordered[-1]
        local_points = _influence_points(temp_points, current_point, radius)

        if local_points:
            nearest_point = min(
                local_points,
                key=lambda p: _distance(p, current_point)
            )

            temp_points.remove(nearest_point)
            ordered.append(nearest_point)

    return ordered
