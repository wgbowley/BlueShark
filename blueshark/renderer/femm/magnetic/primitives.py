"""
File: primitives.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Draws shapes to the magnetic simulation
    space for femm.

    Includes all shapes in ShapeType
"""

from typing import List, Tuple
from math import cos, sin, radians

import femm
from blueshark.domain.constants import Connection, Connectors
from blueshark.domain.generation.geometric_validation import (
    validate_annulus_circle,
    validate_annulus_sector,
    validate_polygon,
    validate_circle
)


def draw_polygon(
    points: List[Tuple[float, float]],
    enclosed: bool = True
) -> None:
    """
    Draws a polygon to the simulation space.

    Args:
        Points: Lists of points to draw to simulation space
                Must be more than 2 points
    """

    validate_polygon(points)

    pairs = len(points) - 1

    # Connects vertex pairs together
    for i in range(pairs):
        femm.mi_drawline(
            points[i][0],
            points[i][1],
            points[i+1][0],
            points[i+1][1]
        )

    if enclosed:
        # Connects first and last vertex
        femm.mi_drawline(
            points[-1][0],  # Last element in the point list
            points[-1][1],
            points[0][0],   # First element in the point list
            points[0][1]
        )


def draw_circle(
    radius: float,
    center: tuple[float, float],
    maxseg: int = 1
) -> None:
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

    # left to top arc
    femm.mi_drawarc(
        points[1][0], points[1][1],
        points[0][0], points[0][1],
        90,
        maxseg
    )

    # Right to top arc
    femm.mi_drawarc(
        points[2][0], points[2][1],
        points[1][0], points[1][1],
        90,
        maxseg
    )

    # bottom to Right arc
    femm.mi_drawarc(
        points[3][0], points[3][1],
        points[2][0], points[2][1],
        90,
        maxseg
    )

    # Left to bottom arc
    femm.mi_drawarc(
        points[0][0], points[0][1],
        points[3][0], points[3][1],
        90,
        maxseg
    )


def draw_annulus_circle(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    maxseg: int = 1
) -> None:
    """
    Draws an annulus (ring) by drawing two concentric circles:
    outer circle and inner circle (holes).
    """

    validate_annulus_circle(center, r_outer, r_inner)

    # Outer circle (clockwise)
    draw_circle(r_outer, center, maxseg)

    # Inner circle (clockwise to create hole)
    draw_circle(r_inner, center, maxseg)


def draw_annulus_sector(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float,
    maxseg: int = 1
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

    # Outer arc
    femm.mi_drawarc(
        outer_points[0][0],
        outer_points[0][1],
        outer_points[1][0],
        outer_points[1][1],
        arc_angle,
        maxseg
    )

    # Inner arc
    femm.mi_drawarc(
        inner_points[0][0],
        inner_points[0][1],
        inner_points[1][0],
        inner_points[1][1],
        arc_angle,
        maxseg
    )

    # Connect outer end to inner end
    femm.mi_drawline(
        outer_points[1][0],
        outer_points[1][1],
        inner_points[1][0],
        inner_points[1][1],
    )

    # # Connect inner start back to outer start
    femm.mi_drawline(
        inner_points[0][0],
        inner_points[0][1],
        outer_points[0][0],
        outer_points[0][1],
    )


def draw_hybrid(edges: List[Connection]) -> None:
    """
    Draws a hybrid geometry to FEMM, using only lines and arcs.

    Args:
        edges: List of connections describing the shape in order
    """
    if not edges:
        raise ValueError("No edges provided for hybrid geometry")

    for edge in edges:
        edge_type = edge["type"]

        if edge_type == Connectors.LINE:
            femm.mi_drawline(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1]
            )

        elif edge_type == Connectors.ARC:
            femm.mi_drawarc(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1],
                edge["angle"],
                1  # maxseg: can be increased for smoother arcs
            )

        else:
            raise ValueError(f"Unknown edge type: {edge_type}")
