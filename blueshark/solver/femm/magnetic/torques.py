"""
File: torque.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Torque calculation utilities for FEMM post-processing.

"""

from blueshark.domain.constants import PRECISION
from blueshark.solver.femm.magnetic import utils


def lorentz(group: int) -> float:
    """
    Calculates the Lorentz torque on a given FEMM group.

    Args:
        group (int): FEMM group number.

    Returns:
        float: Resultant Lorentz torque magnitude.
               (rounded to configured precision)
    """
    torque = utils.get_block_integral(group, 15)

    return round(torque, PRECISION)


def weighted_stress_tensor(group: int) -> float:
    """
    Calculates the weighted stress tensor torque on a given FEMM group.

    Args:
        group (int): FEMM group number.

    Returns:
        float: Resultant weighted stress tensor torque magnitude.
        (rounded to configured precision)
    """

    torque = utils.get_block_integral(group, 22)

    return round(torque, PRECISION)
