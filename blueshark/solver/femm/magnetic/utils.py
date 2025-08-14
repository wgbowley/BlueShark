"""
File: utils.py
Author: William Bowley
Version: 1.0
Date: 2025-08-09
Description:
    ulility functions for FEMM postprocessor
    modules.

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
        circuit_name (str): The name of the circuit.

    Returns:
        Tuple[float, float, float]: A tuple containing
            (current, voltage, flux_linkage).
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
    group: int,
    integral_type: int
) -> float:
    """
    Safely calculates a block integral on a specified FEMM group.

    This helper function handles all error logging and exceptions.

    Args:
        group (int): The FEMM group number.
        integral_type (int): The type of integral to compute (ref. pyfemm doc).

    Returns:
        float: The result of the block integral.
    """
    if not isinstance(group, int) or group <= 0:
        msg = f"Group must be a positive integer, got {group}."
        logging.error(msg)
        raise ValueError(msg)

    if not isinstance(integral_type, int):
        msg = f"Integral type must be an integer, got {integral_type}."
        logging.error(msg)
        raise TypeError(msg)

    # Note: 0-30 covers all block integral types. Refer to pyFEMM documentation
    if integral_type < 0 or integral_type > 30:
        msg = (
            f"Integral type {integral_type} is out of the expected range (0-30"
            "). Refer to pyFEMM documentation."
        )
        logging.error(msg)
        raise ValueError(msg)

    try:
        femm.mo_groupselectblock(group)
        result = femm.mo_blockintegral(integral_type)
        femm.mo_clearblock()
        return result
    except Exception as e:
        msg = (
            f"Failed to calculate block integral of type {integral_type} "
            f"for group {group}: {e}"
        )
        logging.critical(msg)
        raise RuntimeError(msg) from e
