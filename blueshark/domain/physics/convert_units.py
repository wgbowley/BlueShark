"""
File: convert_units.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13
Description:
    Converts units within the framework to standard form
    in meters.
"""

from blueshark.domain.definitions import Units
from blueshark.domain.constants import (
    CONVERSION_TO_METERS, PRECISION
)


def _validate_input(unit: Units, value: float | int) -> None:
    """
    Validate that the unit is supported and value is a positive number.

    Args:
        unit: unit type from Units enum
        value: numeric value to validate

    Raises:
        TypeError: if unit is not of type Units or value is not float/int
        ValueError: if value is <= 0 or unit is unsupported
    """
    if not isinstance(unit, Units):
        msg = f"Unit must be an instance of Units enum, got {type(unit)}"
        raise TypeError(msg)

    if not isinstance(value, (float, int)):
        msg = f"Value must be float or int, got {type(value)}"
        raise TypeError(msg)

    if value <= 0:
        msg = f"Value must be greater than 0, got {value}"
        raise ValueError(msg)

    if unit not in CONVERSION_TO_METERS:
        raise ValueError(f"Unsupported Unit: {unit}")


def convert_to_meters(unit: Units, value: float) -> float:
    """
    Convert a length from the given unit to meters.

    Args:
        value: The numeric value to convert.
    """
    _validate_input(unit, value)
    factor = CONVERSION_TO_METERS[unit]
    return round(value * factor, PRECISION)


def convert_from_meters(unit: Units, value_in_meters: float) -> float:
    """
    Convert a length from meters back to the given unit.

    Args:
        value_in_meters: The numeric value in meters to convert.
    """
    _validate_input(unit, value_in_meters)
    factor = CONVERSION_TO_METERS[unit]
    return round(value_in_meters / factor, PRECISION)


def convert_to_square_meters(unit: Units, value: float) -> float:
    """
    Convert an area from the given unit to square meters.

    Args:
        value: The numeric area value to convert.
    """
    _validate_input(unit, value)
    factor = CONVERSION_TO_METERS[unit]
    return round(value * (factor ** 2), PRECISION)


def convert_from_square_meters(
    unit: Units,
    value_in_square_meters: float
) -> float:
    """
    Convert an area from square meters back to the given unit.

    Args:
        value_in_square_meters: The numeric area value in square meters.
    """
    _validate_input(unit, value_in_square_meters)
    factor = CONVERSION_TO_METERS[unit]
    return round(value_in_square_meters / (factor ** 2), PRECISION)
