"""
Filename: motor_generation.py
Author: William Bowley
Version: 1.0
Date: 24 - 06 - 2025
Description:
    This script contains functions that are used to generate the motor geometry
    
    functions:
    - coil_pitch(coilLength, slotOuterLength, slotInterLength)          -> (mechanicalPitch)
    - pole_pitch(coilNumber, poleNumber, coilPitch)                     -> (mechanicalPitch)
    - number_turns(coilLength, coilHeight, wireDiameter, fillFactor)    -> (numberTurns)
    
"""

def coil_pitch(
        coilLength:         float,
        slotOuterLength:    float,
        slotInterLength:    float
    ) -> float:
    
    """ Calculates coil mechanical pitch.
        This function only works for flat style linear motors. """
    
    slotLength = 2*coilLength + slotInterLength
    mechanicalPitch = slotLength + 2 * slotOuterLength
    return mechanicalPitch


def pole_pitch(
        coilNumber:    int,
        poleNumber:    int,
        coilPitch:     float,
    ) -> float:
    
    """ Calculates pole mechanical pitch. 
        This function only works for flat style linear motors. """
    
    # Pole pitch = (Armuture length) / (length of pole)
    mechanicalPitch = (coilPitch * coilNumber) / poleNumber
    
    return mechanicalPitch


def number_turns(
        coilLength:     float, 
        coilHeight:     float, 
        wireDiameter:   float,   
        wasteFactor:     float = 0.25
    ) -> int:
    
    
    """ Calulates the number of turns for only square or rectangular coils. Assumes 0.25 waste factor """

    # Number of turns = (Cross-sectional Area of Coil) / (Cross-sectional area of wire * wasted space factor)
    coilArea = coilLength * coilHeight
    wireArea = pow((wireDiameter * (1+wasteFactor)), 2)
    numberTurns = coilArea / wireArea
    
    return round(numberTurns)

