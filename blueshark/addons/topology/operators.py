"""
Filename: map.py
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
    top_map: list[list[int]],  
    start: Tuple[float, float],
    end: Tuple[float, float],
    material: int
) -> None:
    """
    Draws a line to the topology map using Bresenham's line algorithm.
    """

    # Convert to integers
    x0, y0 = map(int, start)
    x1, y1 = map(int, end)

    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1

    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1

    err = dx + dy

    while True:
        if 0 <= x0 < len(top_map[0]) and 0 <= y0 < len(top_map):
            top_map[y0][x0] = material
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def draw_arc(
    top_map: list[list[int]],
    start: Tuple[float, float],
    end: Tuple[float, float],
    sweep_angle: float,
    material: int,
    segments: int = 50
) -> None:
    """
    Draws an arc onto a topology map
    """
    x0, y0 = start
    x1, y1 = end

    # Chord vector
    dx = x1 - x0
    dy = y1 - y0
    chord_len = math.sqrt(dx*dx + dy*dy)

    # Compute radius
    theta_rad = math.radians(abs(sweep_angle))
    if theta_rad == 0:
        return  # degenerate case
    radius = chord_len / (2 * math.sin(theta_rad / 2))

    # Midpoint of chord
    mx, my = (x0 + x1)/2, (y0 + y1)/2

    # Distance from midpoint to center along perpendicular bisector
    h = math.sqrt(radius**2 - (chord_len/2)**2)

    # Unit perpendicular vector to chord (choose CCW side)
    perp_dx = -dy / chord_len
    perp_dy = dx / chord_len
    if sweep_angle < 0:  # flip for CW
        perp_dx *= -1
        perp_dy *= -1

    # Center of circle
    cx = mx + h * perp_dx
    cy = my + h * perp_dy

    # Start and end angles relative to center
    start_angle = math.atan2(y0 - cy, x0 - cx)
    end_angle = math.atan2(y1 - cy, x1 - cx)

    # Make sure angles progress in correct sweep direction
    if sweep_angle > 0:
        if end_angle < start_angle:
            end_angle += 2*math.pi
    else:
        if end_angle > start_angle:
            end_angle -= 2*math.pi

    # Draw arc points
    for i in range(segments + 1):
        t = i / segments
        theta = start_angle + t * (end_angle - start_angle)
        x = int(round(cx + radius * math.cos(theta)))
        y = int(round(cy + radius * math.sin(theta)))
        if 0 <= x < len(top_map[0]) and 0 <= y < len(top_map):
            top_map[y][x] = material
