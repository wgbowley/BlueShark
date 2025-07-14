"""
Filename: femm_force.py
Author: William Bowley
Version: 1.1
Date: 2025-07-12
Description:
    Force calculation utilities for FEMM post-processing.
    Provides separate functions for Lorentz force and weighted stress tensor force calculations.
"""

import femm
import math


def lorentz_force(group: int) -> tuple[float, float]:
    """ Calculates the Lorentz force on a given FEMM group.
    
    Parameters:
        group (int): FEMM group number.
        
    Returns:
        magnitude (float): Resultant Lorentz force magnitude.
        angle (float): Resultant Lorentz force angle in degrees (currently 0).
    """
    femm.mo_groupselectblock(group)
    fx = femm.mo_blockintegral(11)
    fy = femm.mo_blockintegral(12)
    femm.mo_clearblock()
    
    magnitude = math.sqrt(fx**2 + fy**2)
    return (magnitude, 0)


def weighted_stress_tensor_force(group: int) -> tuple[float, float]:
    """ Calculates the weighted stress tensor force on a given FEMM group.
    
    Parameters:
        group (int): FEMM group number.
        
    Returns:
        magnitude (float): Resultant weighted stress tensor force magnitude.
        angle (float): Resultant force angle in degrees (currently 0).
    """
    femm.mo_groupselectblock(group)
    fx = femm.mo_blockintegral(18)
    fy = femm.mo_blockintegral(19)
    femm.mo_clearblock()
    
    magnitude = math.sqrt(fx**2 + fy**2)
    return (magnitude, 0)
