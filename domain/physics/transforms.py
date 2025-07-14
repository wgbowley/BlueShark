"""
Filename: transforms.py
Author: William Bowley
Version: 1.0
Date: 2025-06-10
Description:
    Functions for coordinate transforms between motor reference frames.
    
Functions:
- inverted_park_transform(currentFlux, currentForce, electricalAngle)   -> (alpha, beta)
- inverted_clarke_transform(alpha, beta)                                -> (a, b, c)
"""

from math import cos, sin, sqrt

precision = 6

def inverted_park_transform(
        currentFlux:       float, 
        currentForce:      float, 
        electricalAngle:   float
    ) -> tuple[float, float]:
    
    """ Converts flux-force frame currents to stationary alpha-beta frame currents.
        Only works for 3 phase motors """
        
    alpha   = currentFlux * cos(electricalAngle) - currentForce * sin(electricalAngle)
    beta    = currentFlux * sin(electricalAngle) + currentForce * cos(electricalAngle)
    return (round(alpha, precision), round(beta, precision))


def inverted_clarke_transform(
        alpha:  float,
        beta:   float,
    ) -> tuple[float, float, float]:
    
    """ Converts alpha-beta frame currents to 3 phase step currents.
        Only works for 3 phase motors """
        
    a = round(alpha, precision)
    b = round(0.5 * (sqrt(3)*beta - alpha), precision)
    c = round(0.5 * (-sqrt(3)*beta - alpha), precision)
    return (a, b, c)
