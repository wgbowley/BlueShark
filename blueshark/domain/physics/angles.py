"""
File: angles.py
Author: William Bowley
Version: 1.2
Date: 2025-07-27
Description:
- Functions to convert linear displacement to mechanical and electrical angles.

Functions:
- mechanical_angle(circumference, displacement) -> float
- electrical_angle(num_pole_pairs, mech_angle) -> float
"""

from blueshark.configs import PRECISION, TWO_PI

def mechanical_angle(
    circumference: float,
    displacement: float
) -> float:
    """
    Convert linear displacement to mechanical angle in radians.

    Args:
        circumference (float): The circumference of the rotor path.
        displacement (float): Linear displacement along the path.

    Returns:
        float: Mechanical angle in radians, normalized to [0, 2π).
    """
    
    if circumference <= 0:
        raise ValueError(f"Circumference must be > 0, got {circumference}")
    
    angle = (TWO_PI * displacement) / circumference
    angle %= TWO_PI 
    return round(angle, PRECISION)


def electrical_angle(
    num_pole_pairs: int,
    mech_angle: float
) -> float:
    """
    Convert mechanical angle to electrical angle.

    Args:
        num_pole_pairs (int): Number of pole pairs in the motor.
        mech_angle (float): Mechanical angle in radians.

    Returns:
        float: Electrical angle in radians, normalized to [0, 2π).
    """
    
    if num_pole_pairs <= 0:
        raise ValueError(f"Number of pole pairs must be > 0, got {num_pole_pairs}")
    
    angle = mech_angle * num_pole_pairs
    angle %= TWO_PI
    return round(angle, PRECISION)
