"""
File: validation.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13

Description:
    These functions are used to validate
    input primitive shapes for renderers.
"""

import logging

from blueshark.domain.definitions import Connectors, Geometry, ShapeType


def _validate_polygon(points: list[tuple[float, float]]) -> None:
    """
    Check if the inputs are valid for a polygon.

    Args:
        points: List of (x, y) coordinates defining the polygon vertices.
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
            msg = (
                f"Point at index {i} must be a tuple of 2 elements, got {pt}"
            )
            logging.error(msg)
            raise ValueError(f"{__name__}: {msg}")

        if not all(isinstance(c, (int, float)) for c in pt):
            msg = (
                f"Point coordinates at index {i} "
                f"must be int or float, got {pt}"
            )
            logging.error(msg)
            raise ValueError(f"{__name__}: {msg}")


def _validate_circle(radius: float, center: tuple[float, float]) -> None:
    """
    Check if the inputs are valid for a circle.

    Args:
        radius: Length from center to any point on circumference.
        center: Center point of the circle (x, y).
    """
    if radius is None or center is None:
        msg = "Circle radius and center must be defined"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not isinstance(radius, (float, int)):
        msg = (
            "Circle radius must be float or int, "
            f"got {type(radius).__name__}"
        )
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not isinstance(center, tuple):
        msg = f"Circle center must be a tuple, got {type(center).__name__}"
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


def _validate_annulus_circle(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float
) -> None:
    """
    Check if the inputs are valid for an annulus circle.

    Args:
        center: Center point of the circle (x, y).
        r_outer: Outer radius.
        r_inner: Inner radius.
    """
    _validate_circle(r_outer, center)
    _validate_circle(r_inner, center)

    if r_outer <= r_inner:
        msg = f"r_outer must be > r_inner, got {r_outer}, {r_inner}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")


def _validate_annulus_sector(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float
) -> None:
    """
    Check if the inputs are valid for an annulus sector.

    Args:
        center: Center point of the circle (x, y).
        r_outer: Outer radius.
        r_inner: Inner radius.
        start_angle: Starting angle with respect to horizontal (degrees).
        end_angle: Ending angle with respect to horizontal (degrees).
    """

    _validate_circle(r_outer, center)
    _validate_circle(r_inner, center)

    if start_angle is None or end_angle is None:
        msg = "Annulus sector start and end angles must be defined"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not isinstance(start_angle, (float, int)):
        msg = (
            "Sector start angle must be float or int, got: "
            f"{type(start_angle).__name__}"
        )
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if not isinstance(end_angle, (float, int)):
        msg = (
            "Sector end angle must be float or int, got: "
            f"{type(end_angle).__name__}"
        )
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if r_outer <= r_inner:
        msg = f"r_outer must be > r_inner, got {r_outer}, {r_inner}"
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")

    if end_angle <= start_angle:
        msg = (
            "end_angle must be > start_angle, got "
            f"{end_angle}, {start_angle}"
        )
        logging.error(msg)
        raise ValueError(f"{__name__}: {msg}")


def _validate_hybrid(
    edges: list[dict]
) -> None:
    """
    Only checks that the hybrid shape has an 'edges' list and
    that each edge has a valid connector type.

    Args:
        geometry (Geometry): Dict describing hybrid shape.

    Raises:
        ValueError: If structure is missing or invalid.
    """
    if edges is None:
        msg = "Hybrid shape must have 'edges' defined."
        logging.error(msg)
        raise ValueError(msg)

    if not isinstance(edges, list):
        msg = f"'edges' must be a list, got {type(edges).__name__}"
        logging.error(msg)
        raise ValueError(msg)

    for i, edge in enumerate(edges):
        edge_type = edge.get("type")
        if edge_type not in Connectors:
            msg = (
                f"Edge {i} has invalid type '{edge_type}', "
                f"must be one of {list(Connectors)}"
            )
            logging.error(msg)
            raise ValueError(msg)


def validate_shape(
    geometry: Geometry
) -> None:
    """
    Validates that the input parameters are correct for
    defining the specific shape instance.

    Args:
        geometry (Geometry):
            Dictionary describing the shape and its dimensions.

    Raises:
        NotImplementedError: If the shape is unsupported.
    """
    if not geometry or "shape" not in geometry:
        raise ValueError("Geometry dictionary must contain a 'shape' key")

    shape = geometry.get("shape")
    match shape:
        case ShapeType.POLYGON | ShapeType.RECTANGLE:
            _validate_polygon(
                geometry.get("points")
            )

        case ShapeType.CIRCLE:
            _validate_circle(
                geometry.get("radius"),
                geometry.get("center")
            )

        case ShapeType.ANNULUS_CIRCLE:
            _validate_annulus_circle(
                geometry.get("center"),
                geometry.get("radius_outer"),
                geometry.get("radius_inner")
            )

        case ShapeType.ANNULUS_SECTOR:
            _validate_annulus_sector(
                geometry.get("center"),
                geometry.get("radius_outer"),
                geometry.get("radius_inner"),
                geometry.get("start_angle"),
                geometry.get("end_angle")
            )

        case ShapeType.HYBRID:
            _validate_hybrid(
                geometry.get("edges")
            )

        case _:
            raise NotImplementedError(f"Shape '{shape}' not supported")
