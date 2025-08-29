"""
File: draw_armature.py
Author: William Bowley
Version: 0.1
Date: 2025-07-28
Description:
    This is an addon for drawing bldc
    motors armuture through the renderer interface.

    (Tests)
"""

import math

from blueshark.domain.constants import (
    ShapeType,
    Connection,
    Connectors
)


def polar_to_cartesian(r: float, angle_deg: float) -> tuple[float, float]:
    theta = math.radians(angle_deg)
    return r * math.cos(theta), r * math.sin(theta)


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
    Generate the hybrid geometry for all slots rotated around the center.
    Each slot is built from lines and arcs, then rotated.
    Returns a dict with 'shape' and 'edges'.
    """

    half_angle = 0.5 * (sector_angle - spacing_angle)

    # --- Base geometry for one slot (before rotation) ---
    # Start point inner edge
    p1 = polar_to_cartesian(r_start, -half_angle)

    # Radial line outward
    p2 = (
        p1[0] + (r_slot - r_start) * math.cos(math.radians(-half_angle)),
        p1[1]
    )

    # Outer radial edge
    p4 = polar_to_cartesian(r_teeth, -half_angle)
    p3 = (p2[0], p4[1])

    # Arc along tooth tip
    p5 = polar_to_cartesian(r_teeth, half_angle)

    # Vertical return line
    p6 = (p2[0], p5[1])
    p7 = (p2[0], -p1[1])
    p8 = (p1[0], -p1[1])

    # --- Define edges for one slot ---
    base_edges: list[Connection] = [
        {"type": Connectors.LINE, "start": p1, "end": p2},
        {"type": Connectors.LINE, "start": p2, "end": p3},
        {"type": Connectors.LINE, "start": p3, "end": p4},
        {"type": Connectors.ARC,  "start": p4, "end": p5,
         "center": (0, 0), "angle": 2 * half_angle, "radius": r_teeth},
        {"type": Connectors.LINE, "start": p5, "end": p6},
        {"type": Connectors.LINE, "start": p6, "end": p7},
        {"type": Connectors.LINE, "start": p7, "end": p8},
    ]

    all_edges: list[Connection] = []
    slot_starts, slot_ends = [], []

    # --- Replicate slots ---
    for i in range(number_slots):
        theta = sector_angle * i
        slot_edges = []
        for edge in base_edges:
            start_rot = rotate_point(edge["start"], theta)
            end_rot = rotate_point(edge["end"], theta)
            edge_rot = edge.copy()
            edge_rot["start"] = start_rot
            edge_rot["end"] = end_rot
            if edge["type"] == Connectors.ARC:
                edge_rot["center"] = (0, 0)
            slot_edges.append(edge_rot)

        all_edges.extend(slot_edges)
        slot_starts.append(slot_edges[0]["start"])
        slot_ends.append(slot_edges[-1]["end"])

    # --- Stitch with arcs along r_start ---
    arc_angle = sector_angle  # each slot sector angle
    for i in range(number_slots):
        start = slot_ends[i]
        end = slot_starts[(i + 1) % number_slots]
        all_edges.append({
            "type": Connectors.ARC,
            "start": start,
            "end": end,
            "center": (0, 0),
            "angle": arc_angle
        })

    return {
        "shape": ShapeType.HYBRID,
        "edges": all_edges
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
    """
    Gets the coordinates for the objects.
    """
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
