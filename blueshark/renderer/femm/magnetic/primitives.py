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

from typing import List, Tuple, Dict
from math import cos, sin, radians, atan2, pi, hypot

import femm
from blueshark.domain.constants import Connection, Connectors
from blueshark.domain.generation.geometric_validation import (
    validate_annulus_circle,
    validate_annulus_sector,
    validate_polygon,
    validate_circle
)


def _mid_points_line(
    point1: tuple[int, int],
    point2: tuple[int, int]
) -> tuple[float, float]:
    x1, y1 = point1
    x2, y2 = point2

    return ((x1 + x2) / 2, (y1 + y2) / 2)


def _mid_points_arc(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    center: tuple[float, float],
) -> tuple[float, float]:
    start_x, start_y = start_point
    end_x, end_y = end_point
    center_x, center_y = center

    # Find the angles of the start and end points relative to the center
    start_angle = atan2(start_y - center_y, start_x - center_x)
    end_angle = atan2(end_y - center_y, end_x - center_x)

    # Calculate the average angle
    mid_angle = (start_angle + end_angle) / 2

    # Handle cases where the arc crosses the 0/360-degree line
    if abs(end_angle - start_angle) > pi:
        mid_angle += pi

    # Get the radius from the start point to the center
    radius = hypot(start_x - center_x, start_y - center_y)

    # Use the mid-angle and radius to find the midpoint's coordinates
    mid_x = center_x + radius * cos(mid_angle)
    mid_y = center_y + radius * sin(mid_angle)

    return (mid_x, mid_y)


def draw_polygon(
    points: List[Tuple[float, float]],
    enclosed: bool = True
) -> Dict:
    """
    Draws a polygon to the simulation space.

    Args:
        Points: Lists of points to draw to simulation space
                Must be more than 2 points
    """
    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }
    validate_polygon(points)

    pairs = len(points) - 1

    # Connects vertex pairs together
    for i in range(pairs):
        contours[Connectors.LINE].append(
            _mid_points_line(
                points[i], points[i + 1]
            )
        )
        femm.mi_drawline(
            points[i][0],
            points[i][1],
            points[i+1][0],
            points[i+1][1]
        )

    if enclosed:
        contours[Connectors.LINE].append(
            _mid_points_line(
                points[-1], points[0]
            )
        )
        # Connects first and last vertex
        femm.mi_drawline(
            points[-1][0],  # Last element in the point list
            points[-1][1],
            points[0][0],   # First element in the point list
            points[0][1]
        )

    return contours


def draw_circle(
    radius: float,
    center: tuple[float, float],
    maxseg: int = 1
) -> Dict:
    """
    Draws a circle to the simulation space via
    drawarc comamnd within femm.

    Circle makes up 4 x 90 degree arcs

    Args:
        radius: Length from center to any point on circumference
        center: Center point of the circle
        maxseg: Resolution of the circle
    """

    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }

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
    contours[Connectors.ARC].append(
        _mid_points_arc(
            points[1], points[0], center
        )
    )
    femm.mi_drawarc(
        points[1][0], points[1][1],
        points[0][0], points[0][1],
        90,
        maxseg
    )

    # Right to top arc
    contours[Connectors.ARC].append(
        _mid_points_arc(
            points[2], points[1], center
        )
    )
    femm.mi_drawarc(
        points[2][0], points[2][1],
        points[1][0], points[1][1],
        90,
        maxseg
    )

    # bottom to Right arc
    contours[Connectors.ARC].append(
        _mid_points_arc(
            points[3], points[2], center
        )
    )
    femm.mi_drawarc(
        points[3][0], points[3][1],
        points[2][0], points[2][1],
        90,
        maxseg
    )

    # Left to bottom arc
    # Left to bottom arc
    contours[Connectors.ARC].append(
        _mid_points_arc(
            points[0], points[3], center
        )
    )
    femm.mi_drawarc(
        points[0][0], points[0][1],
        points[3][0], points[3][1],
        90,
        maxseg
    )

    return contours


def draw_annulus_circle(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    maxseg: int = 1
) -> Dict:
    """
    Draws an annulus (ring) by drawing two concentric circles:
    outer circle and inner circle (holes).
    """

    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }

    validate_annulus_circle(center, r_outer, r_inner)
    # Outer circle (clockwise)
    outer_contours = draw_circle(r_outer, center, maxseg)

    # Inner circle (clockwise to create hole)
    inner_contours = draw_circle(r_inner, center, maxseg)

    contours[Connectors.LINE].extend(outer_contours[Connectors.LINE])
    contours[Connectors.LINE].extend(inner_contours[Connectors.LINE])

    contours[Connectors.ARC].extend(outer_contours[Connectors.ARC])
    contours[Connectors.ARC].extend(inner_contours[Connectors.ARC])
    return contours


def draw_annulus_sector(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    start_angle: float,
    end_angle: float,
    maxseg: int = 1
) -> Dict:
    """
    Draw an annulus sector in magnetic FEMM.
    """
    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }
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
    contours[Connectors.ARC].append(
        _mid_points_arc(
            outer_points[0], outer_points[1], center
        )
    )
    femm.mi_drawarc(
        outer_points[0][0],
        outer_points[0][1],
        outer_points[1][0],
        outer_points[1][1],
        arc_angle,
        maxseg
    )

    # Inner arc
    contours[Connectors.ARC].append(
        _mid_points_arc(
            inner_points[0], inner_points[1], center
        )
    )
    femm.mi_drawarc(
        inner_points[0][0],
        inner_points[0][1],
        inner_points[1][0],
        inner_points[1][1],
        arc_angle,
        maxseg
    )

    # Connect outer end to inner end
    contours[Connectors.LINE].append(
        _mid_points_line(
            outer_points[1], inner_points[1]
        )
    )
    femm.mi_drawline(
        outer_points[1][0],
        outer_points[1][1],
        inner_points[1][0],
        inner_points[1][1],
    )

    # # Connect inner start back to outer start
    contours[Connectors.LINE].append(
        _mid_points_line(
            inner_points[0], outer_points[0]
        )
    )
    femm.mi_drawline(
        inner_points[0][0],
        inner_points[0][1],
        outer_points[0][0],
        outer_points[0][1],
    )

    return contours


def draw_hybrid(edges: List[Connection]) -> dict:
    """
    Draws a hybrid geometry to FEMM, using only lines and arcs.

    Args:
        edges: List of connections describing the shape in order
    """
    if not edges:
        raise ValueError("No edges provided for hybrid geometry")

    contours = {
        Connectors.LINE: [],
        Connectors.ARC: []
    }

    for edge in edges:
        edge_type = edge["type"]

        if edge_type == Connectors.LINE:
            contours[Connectors.LINE].append(
                _mid_points_line(
                    edge["start"], edge["end"]
                )
            )
            femm.mi_drawline(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1]
            )

        elif edge_type == Connectors.ARC:
            contours[Connectors.ARC].append(
                _mid_points_arc(
                    edge["start"], edge["end"], (0, 0)
                )
            )
            femm.mi_drawarc(
                edge["start"][0], edge["start"][1],
                edge["end"][0], edge["end"][1],
                edge["angle"],
                1  # maxseg: can be increased for smoother arcs
            )

        else:
            raise ValueError(f"Unknown edge type: {edge_type}")

    return contours
