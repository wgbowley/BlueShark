"""
File: unit_physics.py
Author: William Bowley
Version: 1.0
Date: 2025-08-05

Description:
    Tests functions within domain/physics
"""

import unittest
from math import pi

from blueshark.domain.physics.commutation import displacement_commutation
from blueshark.domain.physics.angles import electrical_angle, mechanical_angle
from blueshark.domain.physics.transforms import inverse_clarke_transform
from blueshark.domain.physics.transforms import inverse_park_transform
from blueshark.domain.physics.ripple import ripple_peak_to_peak
from blueshark.domain.physics.ripple import ripple_percent
from blueshark.domain.physics.ripple import ripple_rms
from blueshark.configs import PRECISION


class TestMechanical(unittest.TestCase):
    """ Tests domain/physics/angles -> mechanical_angle"""
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
    """ Tests domain/physics/angles -> electrical_angle"""
    def test_zero_mechanical_angle(self):
        self.assertEqual(electrical_angle(10, 0), 0)

    def test_zero_poles(self):
        with self.assertRaises(ValueError) as e:
            electrical_angle(-1, 2 * pi)

        self.assertIn("Number of pole pairs must be > 0", str(e.exception))

    def test_half_mechanical_angle(self):
        self.assertEqual(electrical_angle(2, pi), 0)


class TestTransforms(unittest.TestCase):
    """ Tests domain/physics/transforms -> inverse_park_transform"""
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


class TestRippleFunctions(unittest.TestCase):
    """ Tests domain/physics/ripple -> peak-peak, rms, precent"""
    def test_peak_to_peak_basic(self):
        values = [1, 2, 3, 4, 5]
        expected = 4.0  # max-min ignoring mean shift
        result = ripple_peak_to_peak(values)
        self.assertAlmostEqual(result, expected, places=6)

    def test_rms_basic(self):
        values = [1, 2, 3, 4, 5]
        # Manual RMS calc for ripple
        mean = sum(values) / len(values)
        ripple = [(v - mean) ** 2 for v in values]
        expected = (sum(ripple) / len(values)) ** 0.5
        result = ripple_rms(values)
        self.assertAlmostEqual(result, expected, places=6)

    def test_percent_basic(self):
        values = [1, 2, 3, 4, 5]
        peak = ripple_peak_to_peak(values)
        mean = sum(values) / len(values)
        expected = (peak / mean) * 100
        result = ripple_percent(values)
        self.assertAlmostEqual(result, expected, places=6)

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            ripple_peak_to_peak([])
        with self.assertRaises(ValueError):
            ripple_rms([])
        with self.assertRaises(ValueError):
            ripple_percent([])

    def test_non_numeric_input(self):
        with self.assertRaises(TypeError):
            ripple_peak_to_peak([1, 2, 'a'])
        with self.assertRaises(TypeError):
            ripple_rms([1, 2, None])
        with self.assertRaises(TypeError):
            ripple_percent([1, 'b', 3])

    def test_zero_average_percent(self):
        values = [-1, 1]
        # average is 0, percent ripple should return 0.0 safely
        result = ripple_percent(values)
        self.assertEqual(result, 0.0)

    def test_near_zero_average_percent(self):
        values = [1e-15, -1e-15, 2e-15]
        result = ripple_percent(values)
        self.assertEqual(result, 0.0)

    def test_constant_values(self):
        values = [5, 5, 5, 5]
        self.assertEqual(ripple_peak_to_peak(values), 0.0)
        self.assertEqual(ripple_rms(values), 0.0)
        self.assertEqual(ripple_percent(values), 0.0)


class TestCommutation(unittest.TestCase):
    """ Tests domain/physics/commutation -> displacement_commutation"""
    def test_vaild_output(self):
        step_size, profile = displacement_commutation(
            displacement=1.0,
            circumference=1.0,
            pole_pairs=1,
            currents_peak=(1.0, 0.0),
            num_samples=2
        )
        self.assertEqual(len(profile), 3)
        self.assertAlmostEqual(step_size, 0.5)

    def test_zero_displacement(self):
        with self.assertRaises(ValueError):
            displacement_commutation(0.0, 1.0, 1, (1.0, 0.0), 10)

    def test_invalid_samples(self):
        with self.assertRaises(ValueError):
            displacement_commutation(1.0, 1.0, 1, (1.0, 0.0), 0)

    def test_invalid_circumference(self):
        with self.assertRaises(ValueError):
            displacement_commutation(1.0, 0.0, 1, (1.0, 0.0), 10)

    def test_invalid_currents_peak_type(self):
        with self.assertRaises(TypeError):
            # list not tuple
            displacement_commutation(1.0, 1.0, 1, [1.0, 0.0], 10)

    def test_invalid_currents_peak_length(self):
        with self.assertRaises(TypeError):
            displacement_commutation(1.0, 1.0, 1, (1.0,), 10)

    def test_invalid_currents_peak_elements(self):
        with self.assertRaises(TypeError):
            displacement_commutation(1.0, 1.0, 1, ('a', 0.0), 10)
