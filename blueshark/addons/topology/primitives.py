"""
Filename: primitives.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all renderers / solvers.

    This module adds perimeters for the
    topology map
"""

from math import cos, sin, radians
from typing import List, Tuple
from blueshark.domain.constants import Connection, Connectors
from blueshark.addons.topology.operators import draw_line, draw_arc
from blueshark.domain.generation.geometric_validation import (
    validate_polygon,
    validate_annulus_circle,
    validate_annulus_sector,
    validate_circle,
)


def draw_polygon(
    points: List[Tuple[float, float]],
    material: int,
    enclosed: bool = True
) -> list[tuple[int, int]]:
    """
    Draws a polygon to the simulation space.

    Args:
        Points: Lists of points to draw to simulation space
                Must be more than 2 points
    """

    validate_polygon(points)

    pairs = len(points) - 1
    return_points = []
    # Connects vertex pairs together
    for i in range(pairs):
        return_points.extend(
            draw_line(
                points[i],
                points[i+1],
                material
            )
        )

    # Connects first and last vertex
    if enclosed:
        return_points.extend(
            draw_line(
                points[-1],  # Last element in the point list
                points[0],   # First element in the point list
                material
            )
        )

    return return_points


def draw_circle(
    radius: float,
    center: tuple[float, float],
    material: int,
    maxseg: int = 0
) -> list[tuple[int, int]]:
    """
    Draws a circle to the simulation space via
    drawarc comamnd within femm.

    Circle makes up 4 x 90 degree arcs

    Args:
        radius: Length from center to any point on circumference
        center: Center point of the circle
        maxseg: Resolution of the circle
    """

    validate_circle(radius, center)

    cx, cy = center
    r = radius
    points = [
        (cx - r, cy),  # Left
        (cx, cy + r),  # Top
        (cx + r, cy),  # Right
        (cx, cy - r)   # Bottom
    ]

    return_points = []
    # left to top arc
    return_points.extend(
        draw_arc(
            points[1],
            points[0],
            90,
            material
        )
    )

    # Right to top arc
    return_points.extend(
        draw_arc(
            points[2],
            points[1],
            90,
            material
        )
    )

    # bottom to Right arc
    return_points.extend(
        draw_arc(
            points[3],
            points[2],
            90,
            material
        )
    )

    # Left to bottom arc
    return_points.extend(
        draw_arc(
            points[0],
            points[3],
            90,
            material
        )
    )

    return return_points


def draw_annulus_circle(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    material: int,
    maxseg: int = 0
) -> list[tuple[int, int]]:
    """
    Draws an annulus (ring) by drawing two concentric circles:
    outer circle and inner circle (holes).
    """

    validate_annulus_circle(center, r_outer, r_inner)
    points = []

    # Outer circle (clockwise)
    points.extend(draw_circle(r_outer, center, material, maxseg))

    # Inner circle (clockwise to create hole)
    points.extend(draw_circle(r_inner, center, material, maxseg))

    return points


def draw_annulus_sector(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float,
    material: int,
    maxseg: int = 500
) -> None:
    """
    Draw an annulus sector in magnetic FEMM.
    """

    validate_annulus_sector(center, r_outer, r_inner, start_angle, end_angle)
    cx, cy = center

    # Convert angles to radians & calculates angle
    start_rad = radians(start_angle)
    end_rad = radians(end_angle)
    arc_angle = end_angle - start_angle

    # Calculate vertex points on outer & inner arcs
    outer_points = [
        (cx + r_outer * cos(start_rad), cy + r_outer * sin(start_rad)),
        (cx + r_outer * cos(end_rad), cy + r_outer * sin(end_rad))
    ]

    inner_points = [
        (cy + r_inner * cos(start_rad), cy + r_inner * sin(start_rad)),
        (cy + r_inner * cos(end_rad), cy + r_inner*sin(end_rad))
    ]

    return_points = []

    # Outer arc
    return_points.extend(
        draw_arc(
            outer_points[0],
            outer_points[1],
            arc_angle,
            material,
            maxseg
        )
    )

    # Inner arc
    return_points.extend(
        draw_arc(
            inner_points[0],
            inner_points[1],
            arc_angle,
            material,
            maxseg
        )
    )

    # Connect outer end to inner end
    return_points.extend(
        draw_line(
            outer_points[1],
            inner_points[1],
            material
        )
    )

    # # Connect inner start back to outer start
    return_points.extend(
        draw_line(
            inner_points[0],
            outer_points[0],
            material,
        )
    )

    return return_points


def draw_hybrid(
    material: int,
    edges: List[Connection]
) -> list[list[tuple, int]]:
    """
    Draws a hybrid geometry to topology map, using only lines and arcs.

    Args:
        edges: List of connections describing the shape in order
    """
    points = []
    if not edges:
        raise ValueError("No edges provided for hybrid geometry")

    for edge in edges:
        edge_type = edge["type"]

        if edge_type == Connectors.LINE:
            points.extend(
                draw_line(
                    edge["start"],
                    edge["end"],
                    material
                )
            )

        elif edge_type == Connectors.ARC:
            points.extend(
                draw_arc(
                    edge["start"],
                    edge["end"],
                    edge["angle"],
                    material
                )
            )
        else:
            raise ValueError(f"Unknown edge type: {edge_type}")

    return points
