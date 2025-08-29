
"""
Filename: interfaces.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all solvers

    This module breaks geometric shapes into
    an shared interface between them.
"""

import math
from typing import List, Tuple

from blueshark.addons.topology.extraction import (
    order_points
)


def _min_point_to_geometry(
    point_1: Tuple[int, int],
    geometry_2: List[Tuple[int, int]]
) -> Tuple[int, int]:
    """
    Finds the point on geometry_2 that is closest to point_1.
    """
    min_distance = float('inf')
    closest_point = None
    x, y = point_1

    for x1, y1 in geometry_2:
        distance = math.hypot(x - x1, y - y1)
        if distance < min_distance:
            min_distance = distance  
            closest_point = (x1, y1)

    return closest_point


def _shared_points(
    geometry_1: List[Tuple[int, int]],
    geometry_2: List[Tuple[int, int]],
    threshold: int
) -> List[Tuple[int, int]]:
    """
    Removes points in geometry_1 that are
    within 'threshold' distance of any
    point in reference_points.
    """

    filtered_points = []
    for tx, ty in geometry_1:
        too_close = False
        for rx, ry in geometry_2:
            dist = math.hypot(rx - tx, ry - ty)
            if dist <= threshold:
                too_close = True
                break
        if not too_close:
            filtered_points.append((tx, ty))

    return filtered_points


def interfaced_geometry(
    geometry_1: List[Tuple[int, int]],
    geometry_2: List[Tuple[int, int]],
    threshold: int = 5
) -> List[Tuple[int, int]]:
    """"
    Removes shared points and than finds points on
    geometry 2 to connect to.
    """
    geometry_1 = _shared_points(
        geometry_1,
        geometry_2,
        threshold
    )
    geometry_1 = order_points(geometry_1, threshold)
    start = _min_point_to_geometry(
        geometry_1[0],
        geometry_2
    )
    end = _min_point_to_geometry(
        geometry_1[-1],
        geometry_2
    )

    return [start] + geometry_1 + [end]
