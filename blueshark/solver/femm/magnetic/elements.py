"""
File: elements.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Magnetic properties calculation
    utilities for FEMMagnaticSolver
"""

from blueshark.domain.constants import PRECISION
from blueshark.solver.femm.magnetic import utils


def field_energy(element_id: int) -> float:
    """
    Calculates the magnetic field energy of a block elements
    under the element_id

    args:
        element_id: element identifier
    """
    return round(utils.get_block_integral(element_id, 2), PRECISION)


def aj_interaction(element_id: int) -> float:
    """
    Calculates the aj interaction through a block element
    under  the element_id

    args:
        element_id: element identifier
    """
    return round(utils.get_block_integral(element_id, 0), PRECISION)


def vector_potential(element_id: int) -> float:
    """
    Calculates the vector potential through a block element
    under the element_id

    args:
        element_id: element identifier
    """
    return round(utils.get_block_integral(element_id, 1), PRECISION)


def element_volume(element_id: int) -> float:
    """
    Calculates the volume of the block elements
    under the element_id

    args:
        element_id: element identifier
    """
    return round(utils.get_block_integral(element_id, 10), PRECISION)
