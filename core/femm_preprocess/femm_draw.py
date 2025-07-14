"""
Filename: femm_draw.py
Author: William Bowley
Version: 1.0
Date: 2025-07-01
Description:
    Drawing and property-setting functions for FEMM pre-processor.
"""

import femm
from core.femm_preprocess.femm_geometry import get_centroid_point


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
    
    """ Draws square or rectangular object and sets its properties """
    
    # Calculates the label & vertex positions (bottom left, top right)
    objectLabel = get_centroid_point(origin, length, height)
    bLVertex    = (origin[0], origin[1])
    tRVertex    = (origin[0] + length, origin[1] + height)
    
    # Draw the object based on provided coordinates
    femm.mi_drawrectangle(bLVertex[0], bLVertex[1],  tRVertex[0], tRVertex[1])
    femm.mi_selectrectangle(bLVertex[0], bLVertex[1],  tRVertex[0], tRVertex[1])
    femm.mi_setgroup(group)
    femm.mi_clearselected()
    
    # Add the label & properties 
    femm.mi_addblocklabel(objectLabel[0], objectLabel[1])
    femm.mi_selectlabel(objectLabel[0], objectLabel[1])
    femm.mi_setblockprop(material, 0, 0, incircuit, direction, group, turns)
    femm.mi_clearselected()
