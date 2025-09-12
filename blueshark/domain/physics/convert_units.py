"""
File: convert_units.py
Author: William Bowley
Version: 1.3
Date: 2025-07-27
Description:
    Converts units within the framework to standard form
    in meters.
"""

from blueshark.domain.constants import Units


class UnitConverter:
    """
    Converts values from different units to meters.
    """

    # conversion factors to meters
    _to_meters = {
        Units.MICROMETERS: 1e-6,
        Units.MILLIMETER: 1e-3,
        Units.CENTIMETERS: 1e-2,
        Units.METER: 1.0,
        Units.INCH: 0.0254,
        Units.MILS: 0.0000254,  # 1 mil = 0.001 inch
    }

    @staticmethod
    def to_meters(value: float, unit: Units) -> float:
        """
        Convert a value from the specified unit to meters.

        Args:
            value: numeric value to convert
            unit: unit type from Units enum

        Returns:
            float: value in meters
        """
        factor = UnitConverter._to_meters.get(unit)
        if factor is None:
            raise ValueError(f"Unsupported unit: {unit}")
        return value * factor

    @staticmethod
    def to_square_meters(value: float, unit: Units) -> float:
        """
        Convert an area value from the specified unit to square meters.

        Args:
            value: numeric area value to convert
            unit: unit type from Units enum

        Returns:
            float: value in square meters
        """
        factor = UnitConverter._to_meters.get(unit)
        if factor is None:
            raise ValueError(f"Unsupported unit: {unit}")
        return value * (factor ** 2)
