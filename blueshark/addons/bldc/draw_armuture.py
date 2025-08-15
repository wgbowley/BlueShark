"""
File: draw_bldc.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    This is an addon for drawing bldc
    motors armuture through the renderer interface.

    (Tests)
"""

import math

from blueshark.domain.constants import (
    Geometry,
    ShapeType
)

# Will need to replace this with the native femm function
def points_on_arc(start_angle, end_angle, radius, num=20) -> list:
    points = []
    
    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)
    
    step = (end_rad - start_rad) / (num - 1) 
    
    for t in range(num):
        angle = start_rad + step * t
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    
    return points


def polar_to_cartesian(r, theta_deg):
    """
    Converts polar form to cartesian form
    """
    theta_rad = math.radians(theta_deg)  
    return r * math.cos(theta_rad), r * math.sin(theta_rad)


def rotate_point(
    p: tuple[float, float],
    angle_deg: float
) -> tuple[float, float]:
    """
    Rotates objects around the center
    """
    angle_rad = math.radians(angle_deg)
    x, y = p
    xr = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    yr = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    return (xr, yr)


def flip_tuple(t):
    """
    Filps tuple across axis
    """
    return tuple(-x for x in t)


def slot_geometry_rotated(
    number_slots: int,
    sector_angle: float,
    spacing_angle: float,
    r_start: float,
    r_slot: float,
    r_teeth: float
) -> dict:
    """
    Generate the geometry for all slots rotated around the center.
    Arc points go from negative to positive angles first, then rotated for each slot.
    Returns a dict with 'shape' and a flat list of points.
    """

    half_angle = 0.5 * (sector_angle - spacing_angle)

    # Base slot points
    p1 = polar_to_cartesian(r_start, -half_angle)
    p2 = (
        p1[0] + (r_slot - r_start) * math.cos(math.radians(-half_angle)), 
        p1[1]
    )
    p4 = polar_to_cartesian(r_teeth, -half_angle)
    p3 = (p2[0], p4[1])

    # Arc from negative to positive
    arc_points = points_on_arc(-half_angle, half_angle, r_teeth)

    p5 = polar_to_cartesian(r_teeth, half_angle)
    p6 = (p2[0], p5[1])
    p7 = (p2[0], -p1[1])
    p8 = (p1[0], -p1[1])

    base_slot = [p1, p2, p3, p4] + arc_points + [p5, p6, p7, p8]

    all_points: list[tuple[float, float]] = []

    # Rotate for each slot
    for i in range(number_slots):
        rotated_slot = [rotate_point(p, sector_angle * i) for p in base_slot]
        all_points.extend(rotated_slot)

    return {
        "shape": ShapeType.POLYGON,
        "points": all_points
    }


def coil_array(
    number_slots: int,
    sector_angle: float,
    spacing_angle: float,
    coil_height: float,
    r_start: float,
    r_coilS: float,
    r_coilE: float
) -> dict:
    coils = {}
    half_angle = 0.5 * (sector_angle - spacing_angle)

    # Base slot coil shape (slot 0)
    slot_coords = polar_to_cartesian(r_start, -half_angle)
    p1 = (r_coilS*math.cos(math.radians(-half_angle)), slot_coords[1])
    p2 = (
        r_coilS*math.cos(math.radians(-half_angle)),
        slot_coords[1] - coil_height
    )
    p3 = (
        r_coilE*math.cos(math.radians(-half_angle)),
        slot_coords[1] - coil_height
    )
    p4 = (r_coilE*math.cos(math.radians(-half_angle)), slot_coords[1])

    p5 = (p1[0], -p1[1])
    p6 = (p2[0], -p2[1])
    p7 = (p3[0], -p3[1])
    p8 = (p4[0], -p4[1])

    base_coil1 = [p1, p2, p3, p4]
    base_coil2 = [p5, p6, p7, p8]

    # Rotate into place for each slot
    coil_index = 1
    for slot in range(number_slots):
        slot_angle = slot * sector_angle
        rotated_coil1 = [rotate_point(pt, slot_angle) for pt in base_coil1]
        rotated_coil2 = [rotate_point(pt, slot_angle) for pt in base_coil2]
     
        coils[coil_index] = rotated_coil1
        coil_index += 1
        coils[coil_index] = rotated_coil2
        coil_index += 1

    return coils
