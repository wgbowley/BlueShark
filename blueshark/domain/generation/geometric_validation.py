"""
File: geometric_validation.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Validation for all primitives within the framework
    that use the abstract base class for renderer
"""

from typing import List, Tuple

import logging


def validate_polygon(points: List[Tuple[float, float]]) -> None:
    """
    Checks if the inputs are correct for a polygon

    Args:
        Points: List of point that make up the shape from
                clockwise placement
    """

    if points is None:
        msg = "Points must be defined to draw a polygon"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not isinstance(points, list):
        msg = f"Points must be a list, got {type(points).__name__}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if len(points) < 3:
        msg = "At least 3 points required for a polygon"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    for i, pt in enumerate(points):
        if not isinstance(pt, tuple) or len(pt) != 2:
            msg = f"Point at index {i} must be a tuple of 2 elements, got {pt}"
            logging.error(msg)
            raise ValueError(f"{__name__}: {msg}")

        if not all(isinstance(c, (int, float)) for c in pt):
            msg = f"Point coords at index {i} must be int or float, got {pt}"
            logging.error(msg)
            raise ValueError(f"{__name__}: {msg}")


def validate_circle(
    radius: float,
    center: tuple[float, float]
) -> None:
    """
    Checks if the inputs are correct for a circle

    Args:
        Radius: Length from center to any point on circumference
        Center: Center point of the circle (x,y)
    """

    if radius is None or center is None:
        msg = "Circle radius and center must be defined"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not isinstance(radius, (float, int)):
        type_name = type(radius).__name__
        msg = f"Circle radius must be type: float, int, got {type_name}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not isinstance(center, tuple):
        type_name = type(center).__name__
        msg = f"Circle center must be type: tuple, got {type_name}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if len(center) != 2:
        msg = f"Circle center tuple must have 2 elements, got {len(center)}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not all(isinstance(c, (float, int)) for c in center):
        msg = f"Circle center coordinates must be float or int, got {center}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if radius <= 0:
        msg = f"Circle must have a radius > 0, got {radius}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")


def validate_annulus_circle(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
) -> None:
    """
    Checks if the inputs are correct for a
    annulus circle

    Args:
        Center: Center point of the circle (x,y)
        r_outer: Length from center to any point on outer circumference
        r_inner: Length from center to any point on inner circumference

    * (Center, r_outer & r_inner are checked by validate_circle)
    """

    validate_circle(r_outer, center)
    validate_circle(r_inner, center)

    if r_outer <= r_inner:
        msg = f"r_outer > r_inner required, got {r_outer}, {r_inner}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")


def validate_annulus_sector(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float,
) -> None:
    """
    Checks if the inputs are correct for a
    annulus sector

    Args:
        Center: Center point of the circle (x,y)
        r_outer: Length from center to any point on outer circumference
        r_inner: Length from center to any point on inner circumference
        start_angle: Starting angle with respect to horizontal
        end_angle: Ending angle with respect to horizontal

    * (Center, r_outer & r_inner are checked by validate_circle)
    """

    validate_circle(r_outer, center)
    validate_circle(r_inner, center)

    if start_angle is None or end_angle is None:
        msg = "Annulus Sector start and end angle must be defined"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not isinstance(start_angle, (float, int)):
        type_name = type(start_angle).__name__
        msg = f"Sector start angle must be type: float, int, got {type_name}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not isinstance(end_angle, (float, int)):
        type_name = type(end_angle).__name__
        msg = f"Sector end angle must be type: float, int, got {type_name}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if r_outer <= r_inner:
        msg = f"r_outer > r_inner required, got {r_outer}, {r_inner}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if end_angle <= start_angle:
        msg = f"end > start anlge required, got {end_angle}, {start_angle}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")
