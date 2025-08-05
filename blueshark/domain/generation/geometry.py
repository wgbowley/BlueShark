"""
File: geometry.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Functions to calculate the centroid of a rectangular object
    and generate placement patterns.

Functions:
- get_centroid_point(origin, object_length, object_height):
    Returns the centroid point as (x, y).

- origin_points(object_number, x_pitch, y_pitch, x_offset, y_offset):
    Returns a list of origin points [(x, y), ..., (xn, yn)].
"""


def get_centroid_point(
    origin: tuple[float, float],
    object_length: float,
    object_height: float
) -> tuple[float, float]:
    """
    Calculate the centroid (center point) of a rectangular object.

    Args:
        origin (Tuple[float, float]): (x, y) coordinates of the bottom-left corner.
        object_length (float): Length of the object along the x-axis.
        object_height (float): Height of the object along the y-axis.

    Returns:
        Tuple[float, float]: (x, y) coordinates of the centroid.
    """

    if not isinstance(origin, tuple) or len(origin) != 2:
        raise TypeError("Origin must be a tuple of length 2")
    if object_length <= 0:
        raise ValueError(f"Object length must be > 0, got {object_length}")
    if object_height <= 0:
        raise ValueError(f"Object height must be > 0, got {object_height}")

    x = origin[0] + object_length / 2
    y = origin[1] + object_height / 2
    return x, y


def origin_points(
    object_number: int,
    x_pitch: float,
    y_pitch: float,
    x_offset: float = 0.0,
    y_offset: float = 0.0
) -> list[tuple[float, float]]:
    """
    Generate origin points for a linear sequence of objects.

    Args:
        object_number (int): Number of objects; must be > 0.
        x_pitch (float): Distance between objects on the x-axis.
        y_pitch (float): Distance between objects on the y-axis.
        x_offset (float): Starting x-coordinate offset. Default is 0.0.
        y_offset (float): Starting y-coordinate offset. Default is 0.0.

    Returns:
        List[Tuple[float, float]]: List of (x, y) coordinates.
    """

    if object_number <= 0:
        raise ValueError(f"object_number must be positive; got {object_number}")
    if x_pitch == 0 and y_pitch == 0:
        raise ValueError("x_pitch and y_pitch cannot both be zero.")

    points = []
    for i in range(object_number):
        x = x_offset + i * x_pitch
        y = y_offset + i * y_pitch
        points.append((x, y))

    return points
