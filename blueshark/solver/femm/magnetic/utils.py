"""
File: utils.py
Author: William Bowley
Version: 1.4
Date: 2025-09-14
Description:
    Utility functions for FEMMagneticSolver modules.
"""

import logging
import femm


def get_circuit_properties(
    circuit_name: str
) -> tuple[float, float, float]:
    """
    Safely retrieves the properties of a specified circuit from FEMM.

    This helper function handles all error logging and exceptions.

    Args:
        circuit_name: The name of the circuit.

    Returns:
        circuit_properties:(current, voltage, flux_linkage).
    """

    if not isinstance(circuit_name, str) or not circuit_name.strip():
        msg = f"Circuit name must be a non-empty string, got '{circuit_name}'."
        logging.error(msg)
        raise ValueError(msg)

    try:
        circuit_props = femm.mo_getcircuitproperties(circuit_name)
        return circuit_props
    except Exception as e:
        msg = f"Failed to get properties from circuit '{circuit_name}': {e}"
        logging.critical(msg)
        raise RuntimeError(msg) from e


def get_block_integral(
    element_id: int,
    integral_type: int
) -> float:
    """
    Safely calculates a block integral on a specified element.

    This helper function handles all error logging and exceptions.

    Args:
        element_id: Element identifier
        integral_type: The type of integral to compute (ref. pyfemm doc).

    Returns:
        result: The result of the block integral.
    """
    if not isinstance(element_id, int) or element_id <= 0:
        msg = f"Group must be a positive integer, got {element_id}."
        logging.error(msg)
        raise ValueError(msg)

    if not isinstance(integral_type, int):
        msg = f"Integral type must be an integer, got {integral_type}."
        logging.error(msg)
        raise TypeError(msg)

    # Note: 0-30 covers all block integral types.
    # Refer to pyFEMM documentation (Page 16 - 17)
    if integral_type < 0 or integral_type > 30:
        msg = (
            f"Integral type {integral_type} is out of the expected range (0-30"
            "). Refer to pyFEMM documentation."
        )
        logging.error(msg)
        raise ValueError(msg)

    try:
        femm.mo_groupselectblock(element_id)
        result = femm.mo_blockintegral(integral_type)
        femm.mo_clearblock()
        return result
    except Exception as e:
        msg = (
            f"Failed to calculate block integral of type {integral_type} "
            f"for element id {element_id}: {e}"
        )
        logging.critical(msg)
        raise RuntimeError(msg) from e
