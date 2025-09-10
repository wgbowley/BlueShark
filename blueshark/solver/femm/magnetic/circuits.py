"""
File: circuits.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Circuit analysis utilities for FEMM magentic post-processing.

"""

from blueshark.domain.constants import PRECISION, EPSILON
from blueshark.solver.femm.magnetic import utils


def phase_voltage(circuit_name: str) -> float:
    """
    Get the voltage drop across the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Voltage drop in volts, rounded to configured PRECISION.
    """

    circuit_props = utils.get_circuit_properties(circuit_name)
    voltage = circuit_props[1]
    return round(voltage, PRECISION)


def phase_current(circuit_name: str) -> float:
    """
    Get the instantaneous current of the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Current in amperes, rounded to configured PRECISION.
    """

    circuit_props = utils.get_circuit_properties(circuit_name)
    current = circuit_props[0]
    return round(current, PRECISION)


def phase_inductance(circuit_name: str) -> float:
    """
    Calculate the inductance of the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Inductance in henrys (always positive),
               rounded to configured PRECISION.
    """

    circuit_props = utils.get_circuit_properties(circuit_name)
    current = circuit_props[0]
    flux_linkage = circuit_props[2]

    if abs(current) > EPSILON:
        inductance = flux_linkage / current
    else:
        inductance = 0.0

    return round(abs(inductance), PRECISION)


def phase_flux_linkage(circuit_name: str) -> float:
    """
    Get the flux linkage of the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Flux linkage in webers-turns, rounded to configured PRECISION.
    """

    circuit_props = utils.get_circuit_properties(circuit_name)
    flux_linkage = circuit_props[2]
    return round(flux_linkage, PRECISION)


def phase_power(circuit_name: str) -> float:
    """
    Calculate the instantaneous power of the specified circuit.

    Args:
        circuit_name (str): Name of the circuit.

    Returns:
        float: Power in watts, rounded to configured PRECISION.
    """

    circuit_props = utils.get_circuit_properties(circuit_name)
    current = circuit_props[0]
    voltage = circuit_props[1]

    power = current * voltage
    return round(power, PRECISION)
