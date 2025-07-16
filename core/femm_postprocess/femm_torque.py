"""
Filename: femm_force.py
Author: William Bowley
Version: 1.1
Date: 2025-07-12
Description:
    Torque calculation utilities for FEMM post-processing.
    Provides separate functions for Lorentz and weighted stress tensor torque calculations.
"""

import femm


def lorentz_torque(group: int) -> float:
    """ 
    Calculates the lorentz torque on a group. (Only works for planar sims)
    """
    femm.mo_groupselectblock(group)
    result = femm.mo_blockintegral(15)
    femm.mo_clearblock()
    
    return result


def weighted_stress_tensor_torque(group: int) -> float:
    """ 
    Calculates the weighted stress tensor torque on a group. (Only works for planar sims)
    """
    femm.mo_groupselectblock(group)
    result = femm.mo_blockintegral(22)
    femm.mo_clearblock()
    
    return result