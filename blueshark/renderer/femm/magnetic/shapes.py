"""
File: shapes.py
Author: William Bowley
Version: 1.1
Date: 2025-08-09
Description:
    Draws shapes to the magnetic simulation
    space for femm.

    Includes all shapes in ShapeType
"""

from typing import List, Tuple

import math
import femm


def draw_polygon(points: List[Tuple[float, float]]) -> None:
    """
    Draws a polygon to the simulation space.
    """
    pairs = len(points) - 1

    # Connects vertex pairs together
    for i in range(pairs):
        femm.mi_drawline(
            points[i][0],
            points[i][1],
            points[i+1][0],
            points[i+1][1]
        )

    # Connects first and last vertex
    femm.mi_drawline(
        points[-1][0],
        points[-1][1],
        points[0][0],
        points[0][1]
    )


def draw_circle(
    radius: float, 
    center: tuple[float, float],
    maxseg: int = 1
) -> None:
    """
    Draws a circle to the simulation space
    """
    cx, cy = center
    r = radius
    femm.mi_drawarc(cx + r, cy, cx, cy + r, 90, maxseg)
    femm.mi_drawarc(cx, cy + r, cx - r, cy, 90, maxseg)
    femm.mi_drawarc(cx - r, cy, cx, cy - r, 90, maxseg)
    femm.mi_drawarc(cx, cy - r, cx + r, cy, 90, maxseg)


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
    cx, cy = center

    # Outer circle (clockwise)
    femm.mi_drawarc(cx + r_outer, cy, cx, cy + r_outer, 90, maxseg)
    femm.mi_drawarc(cx, cy + r_outer, cx - r_outer, cy, 90, maxseg)
    femm.mi_drawarc(cx - r_outer, cy, cx, cy - r_outer, 90, maxseg)
    femm.mi_drawarc(cx, cy - r_outer, cx + r_outer, cy, 90, maxseg)

    # Inner circle (counter-clockwise to create hole)
    femm.mi_drawarc(cx + r_inner, cy, cx, cy + r_inner, 90, maxseg)
    femm.mi_drawarc(cx, cy + r_inner, cx - r_inner, cy, 90, maxseg)
    femm.mi_drawarc(cx - r_inner, cy, cx, cy - r_inner, 90, maxseg)
    femm.mi_drawarc(cx, cy - r_inner, cx + r_inner, cy, 90, maxseg)


def draw_annulus_sector(
    center: tuple[float, float],
    r_outer: float,
    r_inner: float,
    start_angle_deg: float,
    end_angle_deg: float,
    maxseg: int = 1
) -> None:
    """
    Draw an annulus sector in FEMM.
    """

    cx, cy = center

    # Convert angles to radians for math trig
    start_rad = math.radians(start_angle_deg)
    end_rad = math.radians(end_angle_deg)

    # Calculate points on outer arc
    outer_start_x = cx + r_outer * math.cos(start_rad)
    outer_start_y = cy + r_outer * math.sin(start_rad)
    outer_end_x = cx + r_outer * math.cos(end_rad)
    outer_end_y = cy + r_outer * math.sin(end_rad)

    # Calculate points on inner arc
    inner_start_x = cx + r_inner * math.cos(start_rad)
    inner_start_y = cy + r_inner * math.sin(start_rad)
    inner_end_x = cx + r_inner * math.cos(end_rad)
    inner_end_y = cy + r_inner * math.sin(end_rad)

    # Outer arc (clockwise)
    arc_angle = end_angle_deg - start_angle_deg
    femm.mi_drawarc(
        outer_start_x,
        outer_start_y,
        outer_end_x,
        outer_end_y,
        arc_angle,
        maxseg
    )

    # Inner arc (counter-clockwise)
    arc_angle = end_angle_deg - start_angle_deg
    femm.mi_drawarc(
        inner_start_x,
        inner_start_y,
        inner_end_x,
        inner_end_y,
        arc_angle,
        maxseg
    )

    # Connect outer end to inner end
    femm.mi_drawline(
        outer_end_x,
        outer_end_y,
        inner_end_x,
        inner_end_y
    )

    # Connect inner start back to outer start
    femm.mi_drawline(
        inner_start_x,
        inner_start_y,
        outer_start_x,
        outer_start_y
    )