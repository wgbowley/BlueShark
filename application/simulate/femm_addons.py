"""
Filename: femm_addons.py
Author: William Bowley
Version: 1.0
Date: 29 - 06 - 2025
Description:
    This script contains addon functions for FEMM to make drawing the motor easier.
    
    Addons:
    - get_centroid_point(origin, objectLength, objectHeight)        -> (x,y)
    - draw_and_set_properties(coords, length, height, material, 
                              direction, incircuit, groups, turns)  -> None
    - origin_points(objectNum, xPitch, yPitch, xOffset, yOffset)    -> [(x,y),(x,y),...]
    - add_bounds(origin, radius, numShells, boundType, material)    -> None
    - addcoil(origin, phase, length, height, 
              innerLength, outerLength, group)                      -> None
    - addPole(origin, length, height, group, magnetizeDirection,
              magnetMaterial, backplateMaterial, backplateLength, 
              backplateHeight)                                      -> None
"""

# Libraries
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
    objectLabel = get_centroid_point(origin, length, height)
    bLVertex    = (origin[0],           origin[1])
    tRVertex    = (origin[0] + length,  origin[1] + height)
    
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

""" Adds a series of circular shells that emulate an unbounded domain"""
def add_bounds(
        origin: tuple[float, float],
        radius: float,
        numShells: int = 7,
        boundType: bool = 1, # 0 = Dirichlet & 1 = Neumann outer edges
        material: str = "Air"
    ) -> None:
    
    # Creates a series of circular shells
    femm.mi_makeABC(numShells, radius, origin[0], origin[1], boundType)
    
    # Shift block label up.
    objectLabel = (origin[0], origin[1] + 1/2*radius)
    
    # Add the label & properties 
    femm.mi_addblocklabel(objectLabel[0], objectLabel[1])
    femm.mi_selectlabel(objectLabel[0], objectLabel[1])
    femm.mi_setblockprop(material, 0, 0, "<None>", 0, 0, 0)
    femm.mi_clearselected()
    

""" Draws the negative and positive slot to the simulation space (Assumes teethLength = 0)"""
def add_coil(
        origin: tuple[float, float],
        phase: str,
        length: float,
        height: float,
        innerLength: float,
        group: int,
        teethLength: float = 0.0,
    ) -> None:
    
    # Positive Current Density Side
    positiveSlot = (origin[0]+ teethLength, origin[1])
    positiveMaterial = f'{phase}+'
    
    # Negative Current Density Side
    negativeSlot = (origin[0]+teethLength+innerLength+length, origin[1])
    negativeMaterial = f'{phase}-'
    
    draw_and_set_properties(
        origin      = positiveSlot,
        length      = length,
        height      = height,
        material    = positiveMaterial,
        direction   = 0,
        incircuit   = "<None>",
        group       = group,
        turns       = 0
    )
    
    draw_and_set_properties(
        origin      = negativeSlot,
        length      = length,
        height      = height,
        material    = negativeMaterial,
        direction   = 0,
        incircuit   = "<None>",
        group       = group,
        turns       = 0
    )


""" Draws a magnet and if defined its backplate (Assumes that the backplate isn't defined)"""
def add_pole(
        origin: tuple[float, float],
        length: float,
        height: float,
        group: int,
        magnetizeDirection: int,
        magnetMaterial: str,
        backplateMaterial: str = "Pure Iron",
        backplateLength: float = 0.0,
        backplateHeight: float = 0.0,
    ) -> None:
    
    draw_and_set_properties(
        origin      = origin,
        length      = length,
        height      = -height,
        material    = magnetMaterial,
        direction   = magnetizeDirection,
        incircuit   = "<None>",
        group       = group,
        turns       = 0 
    )
    
    # Draws backplate if its defined (x,y)
    if backplateLength > 0 and backplateHeight > 0: 
        
        # Shifts the backplate backwards so that the magnets in the center
        xBackPlateShift = 0.5*(backplateLength-length)
        backplate = (origin[0] - xBackPlateShift, origin[1] - height)
        
        draw_and_set_properties( 
            origin      =   backplate, 
            length      =   backplateLength,
            height      =   -backplateHeight,
            material    =   backplateMaterial,
            direction   =   0,
            incircuit   =   "<None>",
            group       =   group,
            turns       =   0
        )