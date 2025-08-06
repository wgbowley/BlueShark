"""
File: draw.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Functions for drawing axis-aligned rectangular geometry in FEMM
    and assigning block properties.

Functions:
- draw_and_set_properties(origin, length, height, material,
                          direction, incircuit, group, turns)
    Adds a square or rectangular object with specified properties.
    Returns None.
"""

import femm
from blueshark.domain.generation.geometry import get_centroid_point


def draw_and_set_properties(
    origin: tuple[float, float],
    length: float,
    height: float,
    material: str,
    direction: int,
    incircuit: str,
    group: int,
    turns: int
) -> None:
    """
    Draw and assign FEMM properties to a square or rectangular object.

    This function only supports axis-aligned rectangular or square shapes. It
    draws the object based on the provided origin (bottom-left corner), length,
    and height, then sets material and coil-related FEMM properties.

    Args:
        origin (tuple[float, float]): Bottom-left corner of the object.
        length (float): Width of the rectangle along the X-axis.
        height (float): Height of the rectangle along the Y-axis.
        material (str): Name of the material in the FEMM library.
        direction (int): Magnetization direction (degrees).
        incircuit (str): Circuit name assigned to this block.
        group (int): FEMM group number for object organization.
        turns (int): Number of turns for electromagnetic simulation.

    Note:
        This does not support angled, curved, or irregular geometries.
    """

    if not isinstance(origin, tuple) or len(origin) != 2:
        raise TypeError("Origin must be a tuple of length 2")
    if length <= 0:
        raise ValueError(f"Region length must be > 0, got {length}")
    if height <= 0:
        raise ValueError(f"Region height must be > 0, got {height}")

    if not isinstance(group, int) or not isinstance(turns, int):
        raise TypeError("Group and Turns must be integer values")
    if not isinstance(incircuit, str):
        raise TypeError("Circuit name & material must be a string")

    object_label = get_centroid_point(origin, length, height)

    # Vertexs (bottom left and top right)
    bl = (origin[0], origin[1])
    tr = (origin[0] + length, origin[1] + height)

    femm.mi_drawrectangle(bl[0], bl[1], tr[0], tr[1])
    femm.mi_selectrectangle(bl[0], bl[1], tr[0], tr[1])
    femm.mi_setgroup(group)
    femm.mi_clearselected()

    femm.mi_addblocklabel(object_label[0], object_label[1])
    femm.mi_selectlabel(object_label[0], object_label[1])
    femm.mi_setblockprop(material, 0, 0, incircuit, direction, group, turns)
    femm.mi_clearselected()
