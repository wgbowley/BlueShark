"""
File: torque.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Torque calculation utilities for FEMM post-processing.

Functions:
- lorentz(group) -> float
- weighted_stress_tensor(group) -> float
"""

import femm
from blueshark.configs import PRECISION

def lorentz(group: int) -> float:
    """
    Calculates the Lorentz torque on a given FEMM group.

    Args:
        group (int): FEMM group number.

    Returns:
        float: Resultant Lorentz torque magnitude, rounded to configured precision.
    """
    femm.mo_groupselectblock(group)
    torque = femm.mo_blockintegral(15)
    femm.mo_clearblock()

    return round(torque, PRECISION)


def weighted_stress_tensor(group: int) -> float:
    """
    Calculates the weighted stress tensor torque on a given FEMM group.

    Args:
        group (int): FEMM group number.

    Returns:
        float: Resultant weighted stress tensor torque magnitude, rounded to configured precision.
    """
    femm.mo_groupselectblock(group)
    torque = femm.mo_blockintegral(22)
    femm.mo_clearblock()
    
    return round(torque, PRECISION)
