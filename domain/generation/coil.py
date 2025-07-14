"""
Filename: coil.py
Author: William Bowley
Version: 1.0
Date: 2025-06-24
Description:
    This module contains functions used to calculate coil geometry parameters
    such as number of turns for rectangular coils.
    
Functions:
- number_turns(coilLength, coilHeight, wireDiameter, wasteFactor)    -> (numberTurns)
"""

def number_turns(
        coilLength:     float, 
        coilHeight:     float, 
        wireDiameter:   float,   
        wasteFactor:     float = 0.25
    ) -> int:
    
    """ Calculates the number of turns for only square or rectangular coils.
        Assumes 0.25 waste factor by default. """

    # Number of turns = (Cross-sectional Area of Coil) / (Cross-sectional area of wire * wasted space factor)
    coilArea = coilLength * coilHeight
    wireArea = pow((wireDiameter * (1+wasteFactor)), 2)
    numberTurns = coilArea / wireArea
    
    return round(numberTurns)
