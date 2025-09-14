"""
File: thermal.py
Author: William Bowley
Version: 1.3
Date: 2025-07-27
Description:
    Calculates values related to thermal
    simulations
"""

import logging

from blueshark.domain.constants import PRECISION, EPSILON


def calculate_volumetric_heating(
    current: float,
    resistance: float,
    volume: float
) -> float:
    """
    Calculates volumetric heat generation for a coil.

    Args:
        current (float): Current through the coil (A)
        resistance (float): Electrical resistance of the coil (Ohms)
        volume (float): Volume of the coil block (m³)

    Returns:
        float: Volumetric heat generation in W/m³
    """
    if volume < EPSILON:
        msg = (
            f"volume < EPSILON {abs(volume)} < {EPSILON}, "
            "failed to calculate heating"
        )
        logging.warning(msg)
        raise ValueError(msg)

    qv = (current ** 2) * resistance / volume
    return round(qv, PRECISION)
