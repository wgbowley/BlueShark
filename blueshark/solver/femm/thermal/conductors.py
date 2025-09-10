"""
File: conductor.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Conductor analysis utilities for FEMM HEAT post-processing.
"""

from blueshark.domain.constants import PRECISION
from blueshark.solver.femm.thermal import utils


def conductor_heat_flux(
    conductor_name: str
) -> float:
    """
    Gets the total heat flux through the conductor

    Args:
        conductor_name (str): Name of the conductor

    Returns:
        float: (Watts) total heat flux in the motor,
                round to configured PRECISION
    """
    conductor = utils.get_conductor_properties(
        conductor_name
    )
    return round(conductor[1], PRECISION)


def conductor_temperature(
    conductor_name: str
) -> float:
    """
    Gets the temperature of the conductor

    Args:
        conductor_name (str): Name of the conductor

    Returns:
        float: (Kelvin) temperature of the conductor
    """
    conductor = utils.get_conductor_properties(
        conductor_name
    )
    return round(conductor[0], PRECISION)
