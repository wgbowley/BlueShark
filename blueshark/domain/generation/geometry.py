"""
Filename: geometry.py
Author: William Bowley
Version: 1.3
Date: 2025-08-12

Description:
    These functions are used to calculate
    properties of geometric areas.
"""

import logging
import warnings

from typing import List, Tuple
from math import radians, pi
from blueshark.domain.constants import (
    ShapeType,
    Geometry,
    PRECISION
)


def _area_polygon(points: List[Tuple[float, float]]) -> float:
    area = 0.0
    number_points = len(points)
    for i in range(number_points):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % number_points]
        area += x1 * y2 - x2 * y1

    return abs(area) / 2


def _area_circle(radius: float) -> float:
    if radius <= 0:
        msg = f"Circle must have a positive radius, got {radius}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    return pi * radius ** 2


def _area_annulus_sector(
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float
) -> float:
    if r_outer <= 0 or r_inner < 0 or r_inner >= r_outer:
        msg = "Annulus Sector radii invalid (r_outer > r_inner >= 0 required)"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    angle_rad = radians(abs(end_angle - start_angle))
    return 0.5 * angle_rad * (r_outer ** 2 - r_inner ** 2)


def _area_annulus_circle(
    r_outer: float,
    r_inner: float
) -> float:
    if r_outer <= 0 or r_inner < 0 or r_inner >= r_outer:
        msg = "Annulus Circle radii invalid (r_outer > r_inner >= 0 required)"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

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
            if not points or len(points) < 3:
                msg = "At least 3 points required for polygon/rectangle area"
                logging.error(msg)
                warnings.warn(f"{__name__}: {msg}")
                return 0.0
            area = _area_polygon(points)

        case ShapeType.CIRCLE:
            radius = geometry.get("radius")
            if radius is None:
                msg = "Circle radius must be defined"
                logging.error(msg)
                raise ValueError(f"{__name__}: {msg}")
            area = _area_circle(radius)

        case ShapeType.ANNULUS_SECTOR:
            r_outer = geometry.get("radius_outer")
            r_inner = geometry.get("radius_inner")
            start_angle = geometry.get("start_angle")
            end_angle = geometry.get("end_angle")

            if None in (r_outer, r_inner, start_angle, end_angle):
                msg = "Annulus Sector parameters missing"
                logging.error(msg)
                raise ValueError(f"{__name__}: {msg}")

            area = _area_annulus_sector(
                r_outer,
                r_inner,
                start_angle,
                end_angle
            )

        case ShapeType.ANNULUS_CIRCLE:
            r_outer = geometry.get("radius_outer")
            r_inner = geometry.get("radius_inner", 0)
            if r_outer is None:
                msg = "Annulus Circle radius_outer missing"
                logging.error(msg)
                raise ValueError(f"{__name__}: {msg}")
            area = _area_annulus_circle(r_outer, r_inner)

        case _:
            raise NotImplementedError(f"Shape '{shape}' not supported")

    return round(area, PRECISION)
