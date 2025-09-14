"""
File: torque.py
Author: William Bowley
Version: 1.4
Date: 2025-09-14
Description:
    Torque calculation utilities for
    FEMMagneticSolver

"""

from blueshark.domain.constants import PRECISION
from blueshark.solver.femm.magnetic import utils


def lorentz(element_id: int) -> float:
    """
    Calculates the Lorentz torque on a given element.

    Args:
        element_id: element identifier

    Returns:
        float: Resultant Lorentz torque magnitude.
               (rounded to configured precision)
    """
    torque = utils.get_block_integral(element_id, 15)

    return round(torque, PRECISION)


def weighted_stress_tensor(element_id: int) -> float:
    """
    Calculates the weighted stress tensor torque on a given element.

    Args:
        element_id: element identifier

    Returns:
        float: Resultant weighted stress tensor torque magnitude.
        (rounded to configured precision)
    """

    torque = utils.get_block_integral(element_id, 22)

    return round(torque, PRECISION)
