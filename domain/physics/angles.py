"""
Filename: angles.py
Author: William Bowley
Version: 1.0
Date: 2025-06-10
Description:
    Functions to convert linear displacement to mechanical and electrical angles.
    
Functions:
- mechanical_angle(circumference, displacement)         -> float
- electrical_angle(numPolePair, mechanicalAngle)        -> float
"""

from math import pi

precision = 6

def mechanical_angle(
        circumference: float,
        displacement: float
    ) -> float: 
    
    """ Converts linear displacement to mechanical angle in radians """
    
    angle = (2 * pi * displacement) / circumference
    angle = angle % (2 * pi)  # Restrict domain to [0, 2pi)
    return round(angle, precision)


def electrical_angle(
        numPolePair: int,
        mechanicalAngle: float
    ) -> float:
    
    """ Converts mechanical angle (radians) to electrical angle (radians) """
    
    angle = mechanicalAngle * numPolePair
    return round(angle, precision)
