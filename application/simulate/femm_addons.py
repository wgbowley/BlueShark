"""
Filename: femm_addons.py
Author: William Bowley
Version: 1.0
Date: 26 - 06 - 2025
Description:
    This script contains addon functions for FEMM to make drawing the motor easier.
    
    Addons:
    - get_centroid_point(origin, objectLength, objectHeight)        -> (x,y)
    - draw_and_set_properties(coords, length, height, material, 
                              direction, incircuit, groups, turns)  -> None
    - origin_points(objectNum, xPitch, yPitch, xOffset, yOffset)    -> [(x,y),(x,y),...]
"""

# Libraries
import math
import femm 

""" Gets the center point of a square or rectangular object """
def get_centroid_point(
        origin: tuple[float, float], 
        objectLength: float, 
        objectHeight: float
    ) -> dict[str, float]:
    
    # Origin[x,y] is the bottom left corner of the object 
    x = origin[0] + objectLength / 2
    y = origin[1] + objectHeight / 2
    
    return (x,y)


""" Gets the origin points for a series of objects"""
def origin_points(
        objectNum: int,
        xPitch: float, 
        yPitch: float, 
        xOffset: float = 0.0,
        yOffset: float = 0.0
    ) -> list[tuple[float, float]]:
    
    objectOrigins = []
    
    for i in range(0, objectNum):
        # xPitch & yPitch is the spacing between object origins
        # xOffset & yOffset shifts the whole series
        origin = (xOffset + i * xPitch, yOffset + i * yPitch)
        objectOrigins.append(origin)
    return objectOrigins
    

""" Draws square or rectangular object and sets its properties """
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
    
    # Calculates the label & vertex positions (bottom left, top right)
    object_label = get_centroid_point(origin, length, height)
    bLVertex    = (origin[0],           origin[1])
    tRVertex    = (origin[0] + length,  origin[1] + height)
    
    # Draw the object based on provided coordinates
    femm.mi_drawrectangle(bLVertex[0], bLVertex[1],  tRVertex[0], tRVertex[1])
    femm.mi_selectrectangle(bLVertex[0], bLVertex[1],  tRVertex[0], tRVertex[1])
    femm.mi_setgroup(group)
    femm.mi_clearselected()
    
    # Add the label & properties 
    femm.mi_addblocklabel(object_label['x'], object_label['y'])
    femm.mi_selectlabel(object_label['x'], object_label['y'])
    femm.mi_setblockprop(material, 0, 0, incircuit, direction, group, turns)
    femm.mi_clearselected()
