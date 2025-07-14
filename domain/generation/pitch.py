"""
Filename: pitch.py
Author: William Bowley
Version: 1.0
Date: 2025-06-24
Description:
    This module contains functions used to calculate mechanical pitch parameters
    for linear motors.
    
Functions:
- coil_pitch(coilLength, slotOuterLength, slotInterLength)          -> (mechanicalPitch)
- pole_pitch(coilNumber, poleNumber, coilPitch)                     -> (mechanicalPitch)
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
    
    # Pole pitch = (Armature length) / (length of pole)
    mechanicalPitch = (coilPitch * coilNumber) / poleNumber
    
    return mechanicalPitch
