"""
Filename: femm_geometry.py
Author: William Bowley
Version: 1.0
Date: 2025-07-01
Description:
    Geometry helper functions for FEMM modeling.
"""

def get_centroid_point(
        origin: tuple[float, float], 
        objectLength: float, 
        objectHeight: float
    ) -> tuple[float, float]:

    """ Gets the center point of a square or rectangular object """
    
    # Origin[x,y] is the bottom left corner of the object 
    x = origin[0] + objectLength / 2
    y = origin[1] + objectHeight / 2
    
    return (x, y)


def origin_points(
        objectNum: int,
        xPitch: float, 
        yPitch: float, 
        xOffset: float = 0.0,
        yOffset: float = 0.0
    ) -> list[tuple[float, float]]:
    
    """ Gets the origin points for a series of objects """
    
    objectOrigins = []
    
    for i in range(objectNum):
        # xPitch & yPitch is the spacing between object origins
        # xOffset & yOffset shifts the whole series
        origin = (xOffset + i * xPitch, yOffset + i * yPitch)
        objectOrigins.append(origin)
        
    return objectOrigins
