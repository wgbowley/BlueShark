"""
File: unit_generation.py
Author: William Bowley
Version: 1.0
Date: 2025-08-05

Description:
    Tests functions within domain/generation
"""

import unittest
from math import ceil

from blueshark.domain.generation.number_turns import estimate_turns
from blueshark.domain.generation.geometry import get_centroid_point
from blueshark.domain.generation.geometry import origin_points


class NumberTurns(unittest.TestCase):
    """ Tests domain/generation/number_turns -> estimate_turns"""
    def test_standard_case(self):
        num = 40000 / 189
        self.assertEqual(estimate_turns(5, 6, 0.315), ceil(num))

    def test_zero_area(self):
        with self.assertRaises(ValueError):
            estimate_turns(0, 10, 1)
        with self.assertRaises(ValueError):
            estimate_turns(10, 0, 1)

    def test_invalid_fill_factor(self):
        with self.assertRaises(ValueError):
            estimate_turns(10, 10, 1, fill_factor=0)
        with self.assertRaises(ValueError):
            estimate_turns(10, 10, 1, fill_factor=-1)
        with self.assertRaises(ValueError):
            estimate_turns(10, 10, 1, fill_factor=1.1)

    def test_small_wire(self):
        self.assertGreater(estimate_turns(10, 10, 0.1), 6000)

    def test_fill_factor(self):
        maximum = 100
        minimum = 10

        self.assertEqual(estimate_turns(10, 10, 1, 1), maximum)
        self.assertEqual(estimate_turns(10, 10, 1, 0.1), minimum)


class GetCenteroid(unittest.TestCase):
    """ Tests domain/generation/geometry -> get_centroid_point"""
    def test_standard_case(self):
        centeroid_point = (12.5, 12.5)
        self.assertEqual(get_centroid_point((10, 10), 5, 5), centeroid_point)

    def test_invalid_origins(self):
        with self.assertRaises(TypeError):
            get_centroid_point([0, 0], 2, 3)  # List instead of tuple
        with self.assertRaises(TypeError):
            get_centroid_point((0,), 2, 3)  # tuple length 1 instead of 2

    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            get_centroid_point((0, 0), 0, 5)  # Zero length
        with self.assertRaises(ValueError):
            get_centroid_point((0, 0), -1, 5)  # Negative length

    def test_invalid_height(self):
        with self.assertRaises(ValueError):
            get_centroid_point((0, 0), 5, 0)  # Zero Height
        with self.assertRaises(ValueError):
            get_centroid_point((0, 0), 5, -1)  # Negative Height


class TestOriginPoints(unittest.TestCase):
    """ Tests domain/generation/geometry -> origin_points"""
    def test_basic_linear_points(self):
        result = origin_points(3, 1.0, 2.0)
        expected = [(0.0, 0.0), (1.0, 2.0), (2.0, 4.0)]
        self.assertEqual(result, expected)

    def test_with_offsets(self):
        result = origin_points(3, 1.0, 2.0, x_offset=5.0, y_offset=10.0)
        expected = [(5.0, 10.0), (6.0, 12.0), (7.0, 14.0)]
        self.assertEqual(result, expected)

    def test_single_object(self):
        result = origin_points(1, 5.0, 5.0)
        expected = [(0.0, 0.0)]
        self.assertEqual(result, expected)

    def test_zero_object_number_raises(self):
        with self.assertRaises(ValueError):
            origin_points(0, 1.0, 1.0)

    def test_zero_pitches_raises(self):
        with self.assertRaises(ValueError):
            origin_points(3, 0.0, 0.0)
