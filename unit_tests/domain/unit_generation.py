"""
File: unit_generation.py
Author: William Bowley
Version: 1.3
Date: 2025-08-12

Description:
    Tests functions within domain/generation
"""

import unittest

from math import pi
from blueshark.domain.constants import (
    ShapeType, Geometry, PRECISION
)
from blueshark.domain.generation.geometry import (
    calculate_area
)


class ShapeArea(unittest.TestCase):
    """
    Tests the calculate area function under geometry module
    """
    def test_standard_circle(self) -> None:
        """
        Tests standard use case of a circle
        """
        geometry: Geometry = {
            "shape": ShapeType.CIRCLE,
            "radius": 5.0
        }
        expected = round(25 * pi, PRECISION)
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_standard_polygon(self) -> None:
        """
        Tests standard use case of a polygon but off-axis
        """
        geometry: Geometry = {
            "shape": ShapeType.POLYGON,
            "points": [(5, 5), (3, 4), (7, 3)]
        }
        expected = round(3, PRECISION)
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_standard_annulus_circle(self) -> None:
        """
        Tests standard use case of a annulus circle
        """
        geometry: Geometry = {
            "shape": ShapeType.ANNULUS_CIRCLE,
            "radius_outer": 10.0,
            "radius_inner": 2.0
        }
        expected = round(96*pi, PRECISION)
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_standard_annulus_sector(self) -> None:
        """
        Tests standard use case of a annulus sector
        """
        geometry: Geometry = {
            "shape": ShapeType.ANNULUS_SECTOR,
            "radius_outer": 25.0,
            "radius_inner": 10.0,
            "start_angle": 20,
            "end_angle": 50
        }
        expected = round(525 * pi / 12, PRECISION)
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_non_supported_shape(self) -> None:
        """
        Invaild shape as input to test resilience of the function
        """
        geometry: Geometry = {
            "shape": "Heptagon",
            "radius": 10
        }

        with self.assertRaises(NotImplementedError):
            calculate_area(geometry)

    def test_2_point_polygon(self) -> None:
        """
        Invalid shape as a line doesn't have area
        """
        geometry: Geometry = {
            "shape": ShapeType.POLYGON,
            "points": [(5, 5), (3, 4)]
        }
        expected = 0.0
        result = calculate_area(geometry)
        self.assertEqual(result, expected)

    def test_no_shape(self) -> None:
        """
        Invalid geometry as it doesn't state its shape
        """
        geometry: Geometry = {
            "points": [(5, 5), (3, 4), (7, 3)]
        }

        with self.assertRaises(NotImplementedError):
            calculate_area(geometry)
