"""
File: draw.py
Author: William Bowley
Version: 1.1
Date: 2025-07-01
Description:
    Functions for drawing axis-aligned rectangular geometry in FEMM and assigning block properties.

Functions:
- draw_and_set_properties(origin, length, height, material, direction, incircuit, group, turns) -> None
"""


import femm
from blueshark.femm.preprocess.geometry import get_centroid_point

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

    Raises:
        RuntimeError: If FEMM is not running or not connected.
    """
    # Check FEMM connection
    try:
        femm.mi_showgrid(True)  
        femm.mi_showgrid(False)  
    except Exception as e:
        raise RuntimeError(
            "FEMM is not running or not connected. Please open FEMM before calling this function."
        ) from e

    objectLabel = get_centroid_point(origin, length, height)
    bLVertex    = (origin[0], origin[1])
    tRVertex    = (origin[0] + length, origin[1] + height)
    
    femm.mi_drawrectangle(bLVertex[0], bLVertex[1], tRVertex[0], tRVertex[1])
    femm.mi_selectrectangle(bLVertex[0], bLVertex[1], tRVertex[0], tRVertex[1])
    femm.mi_setgroup(group)
    femm.mi_clearselected()
    
    femm.mi_addblocklabel(objectLabel[0], objectLabel[1])
    femm.mi_selectlabel(objectLabel[0], objectLabel[1])
    femm.mi_setblockprop(material, 0, 0, incircuit, direction, group, turns)
    femm.mi_clearselected()