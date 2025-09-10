"""
File: regions.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    region analysis utilities for FEMM HEAT post-processing.
"""

from blueshark.domain.constants import PRECISION
from blueshark.solver.femm.thermal import utils


def average_temp_block(
    group: int
) -> float:
    """
    Calculates the average temperature over the given FEMM group

    Args:
        group (int): FEMM group number.

    Returns:
        float: Resultant average temperature over the group.
               (rounded to configured precision)
    """
    average_temp = utils.get_block_integral(group, 0)
    return round(average_temp[0], PRECISION)


def cross_section_block(
    group: int
) -> float:
    """
    Calculates the cross sectional area of the given FEMM group

    Args:
        group (int): FEMM group number

    Returns:
        float: Resultant cross sectional area
                (rounded to configured precision)
    """
    cross_sectional = utils.get_block_integral(group, 1)
    return round(cross_sectional[0], PRECISION)


def volume_block(
    group: int
) -> float:
    """
    Calculates the volume of the given FEMM group

    Args:
        group (int): FEMM group number

    Returns:
        float: Resultant volume of the block
                (rounded to configured precision)
    """
    volume = utils.get_block_integral(group, 2)
    return round(volume[0], PRECISION)


def average_flux_over_block(
    group: int
) -> tuple[float, float]:
    """
    Calculates the average (x, y) heat flux across FEMM group

    Args:
        group (int): FEMM group number

    Returns:
        float: Resultant (x, y) heat flux across group
                (rounded to configured precision)
    """
    x, y = utils.get_block_integral(group, 3)
    return (round(x, PRECISION), round(y, PRECISION))


def average_graident_over_block(
    group: int
) -> tuple[float, float]:
    """
    Calculates the average (x, y) heat flux across FEMM group

    Args:
        group (int): FEMM group number

    Returns:
        float: Resultant (x, y) heat flux across group
                (rounded to configured precision)
    """
    x, y = utils.get_block_integral(group, 4)
    return (round(x, PRECISION), round(y, PRECISION))
