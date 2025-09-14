"""
File: unit_physics.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13

Description:
    Tests functions within domain/physics
"""

import unittest

from blueshark.domain.constants import Units, PRECISION
from blueshark.domain.physics.thermal import calculate_volumetric_heating
from blueshark.domain.physics.convert_units import (
    convert_to_meters,
    convert_from_meters,
    convert_to_square_meters,
    convert_from_square_meters
)
from blueshark.domain.physics.ripple import (
    ripple_peak_to_peak,
    ripple_percent,
    ripple_rms
)


test_series = [55, 10, 52, 18, 58, 77, 64, 16, 72, 45]


class RippleSeries(unittest.TestCase):
    """
    Tests the different ripple series
    """
    def test_peak_to_peak(self) -> None:
        """
        Tests peak to peak ripple analysis using the test
        series
        """
        expected = 77 - 10
        result = ripple_peak_to_peak(test_series)
        self.assertEqual(expected, result)

    def test_percent(self) -> None:
        """
        Tests percent ripple analysis using the test series
        """
        expected = round(((77 - 10) / 46.7) * 100, PRECISION)
        result = ripple_percent(test_series)
        self.assertEqual(expected, result)

    def test_rms(self) -> None:
        """
        Tests rms ripple analysis using the test series
        """
        expected = 22.799342095771
        result = ripple_rms(test_series)
        self.assertEqual(expected, result)

    def invalid_peak_to_peak(self) -> None:
        """
        No series input to test error handling
        """
        with self.assertRaises(ValueError):
            ripple_peak_to_peak([])

    def invalid_rms(self) -> None:
        """
        Series of strings to test error handling
        """
        series = ["I", "d", "e", "k"]

        with self.assertRaises(ValueError):
            ripple_peak_to_peak(series)


class ConvertSquareMeters(unittest.TestCase):
    """
    Tests the conversion from Units to square meters
    and back
    """
    def test_square_micrometer_to_square_meter(self) -> None:
        """
        Tests conversion from square micrometer to square
        meters
        """
        unit = Units.MICROMETERS
        value = 1000

        expected = 1e-9
        result = convert_to_square_meters(unit, value)
        self.assertEqual(result, expected)

    def test_square_millimeter_to_square_meters(self) -> None:
        """
        Tests conversion from square millimeter to square
        meters
        """
        unit = Units.MILLIMETER
        value = 33.57

        expected = round(3.357e-5, PRECISION)
        result = convert_to_square_meters(unit, value)
        self.assertAlmostEqual(result, expected)

    def test_square_centimeters_to_square_meters(self) -> None:
        """
        Tests conversion from square centimeters to square
        meters
        """
        unit = Units.CENTIMETERS
        value = 1000

        expected = 0.1
        result = convert_to_square_meters(unit, value)
        self.assertEqual(result, expected)

    def test_square_meters_to_square_millimeters(self) -> None:
        """
        Tests conversion from square meters to square millimeters
        """
        unit = Units.MILLIMETER
        value = 100

        expected = 1e+8
        result = convert_from_square_meters(unit, value)
        self.assertAlmostEqual(result, expected)


class ConvertMeters(unittest.TestCase):
    """
    Tests the conversion from Units to meters
    and back
    """
    def test_micrometers_to_meters(self) -> None:
        """
        Tests conversion from micrometers  to meters
        """
        unit = Units.MICROMETERS
        value = 100000

        expected = 0.1
        result = convert_to_meters(unit, value)
        self.assertEqual(result, expected)

    def test_millimeters_to_meters(self) -> None:
        """
        Tests conversion from millimeters to meters
        """
        unit = Units.MILLIMETER
        value = 0.001

        expected = 1e-6
        result = convert_to_meters(unit, value)
        self.assertEqual(result, expected)

    def test_centimeters_to_meters(self) -> None:
        """
        Test conversion from centimeters to meters
        """
        unit = Units.CENTIMETERS
        value = 1000

        expected = 10
        result = convert_to_meters(unit, value)
        self.assertEqual(result, expected)

    def test_meters_to_meters(self) -> None:
        """
        Test conversion from meters to meters
        """
        unit = Units.METER
        value = 1.0

        expected = 1.0
        result = convert_to_meters(unit, value)
        self.assertEqual(result, expected)

    def test_meters_to_centimeters(self) -> None:
        """
        Test conversion from meters to centimeters
        """
        unit = Units.CENTIMETERS
        value = 1

        expected = 100
        result = convert_from_meters(unit, value)
        self.assertEqual(result, expected)

    def test_invalid_unit(self) -> None:
        """
        Inputted unit that isn't in Units
        """
        unit = "I don't exist! Though if I don't exist, how can I say that?"
        value = 100

        with self.assertRaises(TypeError):
            convert_to_meters(unit, value)

    def test_invalid_value(self) -> None:
        """
        Inputted value that isn't a float or int
        """
        unit = Units.CENTIMETERS
        value = "Like I was saying..."

        with self.assertRaises(TypeError):
            convert_to_meters(unit, value)

    def test_invalid_range(self) -> None:
        """
        Inputted value that is less than 0
        """
        unit = Units.CENTIMETERS
        value = -100

        with self.assertRaises(ValueError):
            convert_to_meters(unit, value)


class VolumetricHeating(unittest.TestCase):
    """
    Test volumetric heating function
    """
    def test_standard_heating_problem(self) -> None:
        """
        Tests with standard in range values
        """
        current = 10
        resistance = 2
        volume = 10

        expected = (100*2) / 10
        result = calculate_volumetric_heating(
            current,
            resistance,
            volume
        )
        self.assertEqual(expected, result)

    def test_zero_case(self) -> None:
        """
        Test for zero case when current is zero
        """
        current = 0
        resistance = 2
        volume = 10

        expected = 0
        result = calculate_volumetric_heating(
            current,
            resistance,
            volume
        )
        self.assertEqual(expected, result)

    def test_invalid_volume(self) -> None:
        """
        Test with negative volume
        """
        current = 10
        resistance = 2
        volume = -10

        with self.assertRaises(ValueError):
            calculate_volumetric_heating(
                current,
                resistance,
                volume
            )
