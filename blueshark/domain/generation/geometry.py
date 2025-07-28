"""
File: geometry.py
Author: William Bowley
Version: 1.0
Date: 2025-07-01
Description:
    Helper functions for geometric calculations

Functions:
- get_centroid_point(origin, object_length, object_height) -> tuple[float, float]

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
    
    if not isinstance(origin, tuple) or len(origin) !=2:
        raise TypeError("Origin must be a tuple of length 2")
    if object_length <= 0:
        raise ValueError(f"Object length must be > 0, got {object_length}")
    if object_height <= 0:
        raise ValueError(f"Object height must be > 0, got {object_height}")
    
    x = origin[0] + object_length / 2
    y = origin[1] + object_height / 2
    return x, y
