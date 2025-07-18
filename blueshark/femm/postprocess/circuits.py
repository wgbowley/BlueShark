"""
File: circuits.py
Author: William Bowley
Version: 1.1
Date: 2025-07-18
Description:
    Circuit analysis utilities for FEMM post-processing.

Functions:
- circuit_voltage(circuit_name) -> float
- circuit_current(circuit_name) -> float
- circuit_inductance(circuit_name) -> float
- circuit_flux_linkage(circuit_name) -> float
- circuit_power(circuit_name) -> float
"""

import femm
from blueshark.configs import constants


def circuit_voltage(circuit_name: str) -> float:
    """
    Get the voltage drop across the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Voltage drop in volts, rounded to configured PRECISION.
    """
    circuit_props = femm.mo_getcircuitproperties(circuit_name)
    voltage = circuit_props[1]
    return round(voltage, constants.PRECISION)


def circuit_current(circuit_name: str) -> float:
    """
    Get the instantaneous current of the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Current in amperes, rounded to configured PRECISION.
    """
    circuit_props = femm.mo_getcircuitproperties(circuit_name)
    current = circuit_props[0]
    return round(current, constants.PRECISION)


def circuit_inductance(circuit_name: str) -> float:
    """
    Calculate the inductance of the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Inductance in henrys (always positive), rounded to configured PRECISION.
    """
    circuit_props = femm.mo_getcircuitproperties(circuit_name)
    current = circuit_props[0]
    flux_linkage = circuit_props[2]

    if abs(current) > constants.EPSILON:
        inductance = flux_linkage / current
    else:
        inductance = 0.0

    return round(abs(inductance), constants.PRECISION)


def circuit_flux_linkage(circuit_name: str) -> float:
    """
    Get the flux linkage of the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Flux linkage in webers-turns, rounded to configured PRECISION.
    """
    circuit_props = femm.mo_getcircuitproperties(circuit_name)
    flux_linkage = circuit_props[2]
    return round(flux_linkage, constants.PRECISION)


def circuit_power(circuit_name: str) -> float:
    """
    Calculate the instantaneous power of the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Power in watts, rounded to configured PRECISION.
    """
    circuit_props = femm.mo_getcircuitproperties(circuit_name)
    current = circuit_props[0]
    voltage = circuit_props[1]

    power = current * voltage
    return round(power, constants.PRECISION)
