"""
Filename: operators.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all solvers

    This module adds basic operators for the
    topology map
"""

import math

from typing import Tuple


def draw_line(
    start: Tuple[float, float],
    end: Tuple[float, float],
    material: int
) -> list[list[tuple, int]]:
    """
    Draws a line to the topology map using Bresenham's line algorithm.
    """
    points = []

    # Convert to integers
    x0, y0 = map(int, start)
    x1, y1 = map(int, end)

    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1

    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1

    err = dx + dy

    while True:
        points.append([(x0, y0), material])
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

    return points


def draw_arc(
    start: Tuple[float, float],
    end: Tuple[float, float],
    sweep_angle: float,
    material: int,
    segments: int = 500
) -> list[tuple[int, int]]:
    """
    Draws an arc onto a topology map and returns the list of points.
    Corrected to ensure the center is always on the right side of the chord
    based on the sweep angle sign.
    """
    x0, y0 = start
    x1, y1 = end

    dx = x1 - x0
    dy = y1 - y0
    chord_len = math.hypot(dx, dy)

    theta_rad = math.radians(abs(sweep_angle))
    if theta_rad == 0:
        return []

    # Circle radius
    radius = chord_len / (2 * math.sin(theta_rad / 2))

    # Midpoint of chord
    mx, my = (x0 + x1)/2, (y0 + y1)/2

    # Distance from midpoint to center along perpendicular
    h = math.sqrt(radius**2 - (chord_len/2)**2)

    # Unit perpendicular vector
    perp_dx = -dy / chord_len
    perp_dy = dx / chord_len

    # Determine which side to place center on
    # Positive sweep_angle -> CCW, negative -> CW
    ccw = 1 if sweep_angle >= 0 else -1
    cx = mx + ccw * h * perp_dx
    cy = my + ccw * h * perp_dy

    # Start and end angles
    start_angle = math.atan2(y0 - cy, x0 - cx)
    end_angle = start_angle + math.copysign(theta_rad, sweep_angle)

    points = []
    for i in range(segments + 1):
        t = i / segments
        angle = start_angle + t * (end_angle - start_angle)
        x = int(round(cx + radius * math.cos(angle)))
        y = int(round(cy + radius * math.sin(angle)))
        points.append([(x, y), material])

    return points
