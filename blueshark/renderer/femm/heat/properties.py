"""
File: properties.py
Author: William Bowley
Version: 1.3
Date: 2025-08-13
Description:
    Sets the properties of shapes within
    heat flow simulation space for femm.
"""

from typing import Tuple
import femm


def set_properties(
    tag_coords: Tuple[float, float],
    group_id: int,
    material: str,
) -> None:
    """
    Add block label to simulation space and sets properties of the label.

    Args:
        tag_coords (tuple): x and y coordinates of the blocklabel
        material (str): Material of the element.
        group_id (int): Group identifier.
    """

    femm.hi_addblocklabel(tag_coords[0], tag_coords[1])
    femm.hi_selectlabel(tag_coords[0], tag_coords[1])
    femm.hi_setblockprop(
        material,   # 'blockname' material
        1,          # Mesher automatically chooses the mesh density
        0,          # Size constraint on the mesh in the block
        group_id    # Member of group 'number group'
    )

    femm.hi_clearselected()


def add_conductor(
    phase: str,
    inital_heat_flux: float = 0.0
) -> None:
    """
    Adds a conductor to the simulation space with
    inital heat flux of 0 Watts
    """

    femm.hi_addconductorprop(phase, 0, inital_heat_flux, 0)
