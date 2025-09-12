"""
File: thermal.py
Author: William Bowley
Version: 1.3
Date: 2025-07-27
Description:
    Coordinate transformation functions for motor reference frames.

Functions:
- calculate_volumetric_heating(current, resistance, volume)
    return volumetric heat generation in W/m^3
"""

from blueshark.domain.constants import PRECISION


def calulate_volumetric_heating(
    current: float,
    resistance: float,
    volume: float
) -> None:
    """
    Calculates volumetric heat generation for a coil.

    Args:
        block_name: Name of the block/material in FEMM
        current: Current through the coil (A)
        resistance: Electrical resistance of the coil (Ohms)
        volume: Volume of the coil block (m³)
    """

    # Compute volumetric heat generation in W/m³
    qv = (current ** 2) * resistance / volume

    return round(qv, PRECISION)
