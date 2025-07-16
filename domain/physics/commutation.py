"""
Filename: commutation.py
Author: William Bowley
Version: 1.0
Date: 2025-06-10
Description:
    Functions to generate commutation current profiles for 3-phase motors.
    
Functions:
- commutation(circumference, numPairs, currentsPeak, numberSamples) -> list of (pa, pb, pc)
"""
import math 

from domain.physics.transforms import inverted_park_transform, inverted_clarke_transform
from domain.physics.angles import mechanical_angle, electrical_angle

def rotational_commutation(
        circumference: float,
        numPairs: int,
        currentsPeak: tuple[float, float],
        numberSamples: int
    ) -> list[tuple[float, float, float]]:
    
    """ Gets the commutation profile of the motor over one mechanical rotation.
        Only works for 3 phase motors """
    
    stepSize = circumference / numberSamples  # Linear step per sample
    profile = []
    
    for step in range(numberSamples + 1):
        mech_angle = mechanical_angle(circumference, step * stepSize)
        elec_angle = electrical_angle(numPairs, mech_angle)

        alpha, beta = inverted_park_transform(currentsPeak[0], currentsPeak[1], elec_angle)
        pa, pb, pc = inverted_clarke_transform(alpha, beta)
        
        profile.append((pa, pb, pc))
    
    return profile
