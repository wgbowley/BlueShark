"""
File: force.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Force calculation utilities for
    FEMMagnaticSolver
"""

import math

from blueshark.domain.constants import PRECISION
from blueshark.solver.femm.magnetic import utils


def lorentz(element_id: int) -> tuple[float, float]:
    """
    Calculates the Lorentz force on a given element.

    Args:
        element_id: element identifier

    Returns:
        magnitude (float): Resultant Lorentz force magnitude.
        angle (float): Resultant Lorentz force angle in degrees [0, 360).
        (rounded to configured precision)
    """

    fx = utils.get_block_integral(element_id, 11)
    fy = utils.get_block_integral(element_id, 12)

    magnitude = math.hypot(fx, fy)
    angle = (math.degrees(math.atan2(fy, fx)) + 360) % 360

    return round(magnitude, PRECISION), round(angle, PRECISION)


def weighted_stress_tensor(element_id: int) -> tuple[float, float]:
    """
    Calculates the weighted stress tensor force on a given FEMM element.

    Args:
        element_id: element identifier

    Returns:
        magnitude (float): Resultant weighted stress tensor force magnitude.
        angle (float): Resultant force angle in degrees [0, 360).
        (rounded to configured precision)
    """

    fx = utils.get_block_integral(element_id, 18)
    fy = utils.get_block_integral(element_id, 19)

    magnitude = math.hypot(fx, fy)
    angle = (math.degrees(math.atan2(fy, fx)) + 360) % 360

    return round(magnitude, PRECISION), round(angle, PRECISION)
