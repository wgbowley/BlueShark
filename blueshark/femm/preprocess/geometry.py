"""
File: geometry.py
Author: William Bowley
Version: 1.0
Date: 2025-07-01
Description:
    Helper functions for geometric calculations used in FEMM modeling.

Functions:
- get_centroid_point(origin, object_length, object_height) -> tuple[float, float]
- origin_points(object_num, x_pitch, y_pitch, x_offset=0.0, y_offset=0.0) -> list[tuple[float, float]]
"""


from typing import Tuple, List


def get_centroid_point(
    origin: Tuple[float, float],
    object_length: float,
    object_height: float
) -> Tuple[float, float]:
    """
    Calculate the centroid (center point) of a rectangular object.

    Args:
        origin (Tuple[float, float]): (x, y) coordinates of the bottom-left corner.
        object_length (float): Length of the object along the x-axis.
        object_height (float): Height of the object along the y-axis.

    Returns:
        Tuple[float, float]: (x, y) coordinates of the centroid.
    """
    x = origin[0] + object_length / 2
    y = origin[1] + object_height / 2
    return x, y


def origin_points(
    object_num: int,
    x_pitch: float,
    y_pitch: float,
    x_offset: float = 0.0,
    y_offset: float = 0.0
) -> List[Tuple[float, float]]:
    """
    Generate a list of origin points for a sequence of objects spaced linearly.

    Args:
        object_num (int): Number of objects.
        x_pitch (float): Distance between objects along the x-axis.
        y_pitch (float): Distance between objects along the y-axis.
        x_offset (float, optional): Initial x offset for the series. Defaults to 0.0.
        y_offset (float, optional): Initial y offset for the series. Defaults to 0.0.

    Returns:
        List[Tuple[float, float]]: List of (x, y) origin points for each object.
    """
    object_origins = []
    for i in range(object_num):
        origin = (x_offset + i * x_pitch, y_offset + i * y_pitch)
        object_origins.append(origin)
    return object_origins
