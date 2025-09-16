"""
File: unit_physics.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13

Description:
    Tests functions within modules/tubular/physics
"""

import unittest
from math import pi, ceil
from blueshark.domain.constants import PRECISION
from blueshark.models.tubular.physics.number_turns import (
    estimate_turns
)
from blueshark.models.tubular.physics.angles import (
    electrical_angle, mechanical_angle
)
from blueshark.models.tubular.physics.transforms import (
    inverse_clarke_transform,
    inverse_park_transform
)
from blueshark.models.tubular.physics.commutation import (
    commutation
)


class TestMechanical(unittest.TestCase):
    """ Tests tubular/physics/angles -> mechanical_angle"""
    def test_zero_displacement(self):
        self.assertEqual(mechanical_angle(10, 0), 0.0)

    def test_full_circumference(self):
        # Full circle -> 0 radians
        self.assertEqual(mechanical_angle(10, 10), 0.0)

    def test_half_circumference(self):
        expected = round(pi, PRECISION)
        self.assertEqual(mechanical_angle(10, 5), expected)

    def test_displacement_greater_than_circumference(self):
        # displacement 15 with circumference 10 -> same as displacement 5
        expected = round(pi, PRECISION)
        self.assertEqual(mechanical_angle(10, 15), expected)

    def test_fractional_displacement(self):
        circumference = 20
        displacement = 2.5
        expected = round(pi / 4, PRECISION)
        actual = mechanical_angle(circumference, displacement)
        self.assertEqual(actual, expected)


class TestElectrical(unittest.TestCase):
    """ Tests tubular/physics/angles -> electrical_angle"""
    def test_zero_mechanical_angle(self):
        self.assertEqual(electrical_angle(10, 0), 0)

    def test_zero_poles(self):
        with self.assertRaises(ValueError) as e:
            electrical_angle(-1, 2 * pi)

        self.assertIn("Number of pole pairs must be > 0", str(e.exception))

    def test_half_mechanical_angle(self):
        self.assertEqual(electrical_angle(2, pi), 0)


class TestTransforms(unittest.TestCase):
    """ Tests tubular/physics/transforms -> inverse_park_transform"""
    def test_inverse_park_transform_basic(self):
        # d=1, q=0, angle=0 => alpha=1, beta=0
        alpha, beta = inverse_park_transform(1.0, 0.0, 0.0)
        self.assertAlmostEqual(alpha, 1.0, places=PRECISION)
        self.assertAlmostEqual(beta, 0.0, places=PRECISION)

    def test_inverse_park_transform_90deg(self):
        # d=0, q=1, angle=pi/2 => alpha=-1, beta=0 (approx)
        alpha, beta = inverse_park_transform(0.0, 1.0, pi / 2)
        self.assertAlmostEqual(alpha, -1.0, places=PRECISION)
        self.assertAlmostEqual(beta, 0.0, places=PRECISION)

    def test_inverse_clarke_transform_basic(self):
        # alpha=1, beta=0 => phase_a=1, phase_b=-0.5, phase_c=-0.5
        a, b, c = inverse_clarke_transform(1.0, 0.0)
        self.assertAlmostEqual(a, 1.0, places=PRECISION)
        self.assertAlmostEqual(b, -0.5, places=PRECISION)
        self.assertAlmostEqual(c, -0.5, places=PRECISION)


class TestCommutation(unittest.TestCase):
    """ Tests tubular/physics/commutation -> commutation"""
    def test_valid_output(self):
        step_size, profile = commutation(
            circumference=1.0,
            pole_pairs=1,
            currents_peak=(1.0, 0.0),
            num_samples=2
        )
        self.assertEqual(len(profile), 3)
        self.assertAlmostEqual(step_size, 0.5)

    def test_invalid_samples(self):
        with self.assertRaises(ValueError):
            commutation(1.0, 1, (1.0, 0.0), 0)

    def test_invalid_circumference(self):
        with self.assertRaises(ValueError):
            commutation(0.0, 1, (1.0, 0.0), 10)

    def test_invalid_currents_peak_type(self):
        with self.assertRaises(TypeError):
            # list not tuple
            commutation(1.0, 1, [1.0, 0.0], 10)

    def test_invalid_currents_peak_length(self):
        with self.assertRaises(TypeError):
            commutation(1.0, 1, (1.0,), 10)

    def test_invalid_currents_peak_elements(self):
        with self.assertRaises(TypeError):
            commutation(1.0, 1, ('a', 0.0), 10)


class TestNumberTurns(unittest.TestCase):
    """ Tests tubular/physics/number_turns -> estimate_turns"""
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
