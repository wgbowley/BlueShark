"""
File: angles.py
Author: William Bowley
Version: 1.1
Date: 2025-06-10
Description:
    Functions to convert linear displacement to mechanical and electrical angles.

Functions:
- mechanical_angle(circumference, displacement) -> float
- electrical_angle(num_pole_pairs, mech_angle) -> float
"""

from math import pi
from configs import constants


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
    angle = (2 * pi * displacement) / circumference
    angle %= 2 * pi  # Normalize to [0, 2pi)
    return round(angle, constants.PRECISION)


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
        float: Electrical angle in radians.
    """
    angle = mech_angle * num_pole_pairs
    return round(angle, constants.PRECISION)
