"""
File: force.py
Author: William Bowley
Version: 1.1
Date: 2025-07-12
Description:
    Force calculation utilities for FEMM post-processing.

Functions:
- lorentz(group) -> tuple[float, float]
- weighted_stress_tensor(group) -> tuple[float, float]
"""


import femm
import math
from configs import constants


def lorentz(group: int) -> tuple[float, float]:
    """ Calculates the Lorentz force on a given FEMM group.

    Parameters:
        group (int): FEMM group number.

    Returns:
        magnitude (float): Resultant Lorentz force magnitude, rounded to configured precision.
        angle (float): Resultant Lorentz force angle in degrees [0, 360), rounded to configured precision.
    """
    femm.mo_groupselectblock(group)
    fx = femm.mo_blockintegral(11)
    fy = femm.mo_blockintegral(12)
    femm.mo_clearblock()

    if fx is None or fy is None:
        raise RuntimeError("Lorentz force calculation failed — ensure FEMM is open and the solution is loaded.")

    magnitude = math.hypot(fx, fy)
    angle = (math.degrees(math.atan2(fy, fx)) + 360) % 360
    return round(magnitude, constants.PRECISION), round(angle, constants.PRECISION)


def weighted_stress_tensor(group: int) -> tuple[float, float]:
    """ Calculates the weighted stress tensor force on a given FEMM group.

    Parameters:
        group (int): FEMM group number.

    Returns:
        magnitude (float): Resultant weighted stress tensor force magnitude, rounded to configured precision.
        angle (float): Resultant force angle in degrees [0, 360), rounded to configured precision.
    """
    femm.mo_groupselectblock(group)
    fx = femm.mo_blockintegral(18)
    fy = femm.mo_blockintegral(19)
    femm.mo_clearblock()

    if fx is None or fy is None:
        raise RuntimeError("Weighted stress tensor force calculation failed — ensure FEMM is open and the solution is loaded.")

    magnitude = math.hypot(fx, fy)
    angle = (math.degrees(math.atan2(fy, fx)) + 360) % 360
    return round(magnitude, constants.PRECISION), round(angle, constants.PRECISION)
