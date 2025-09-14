"""
File: test_material_manager.py
Author: William Bowley
Version: 1.4
Date: 2025-09-13

Description:
    Tests material manager class within domain/material_manager
"""

import unittest
import copy

from blueshark.domain.material_manager.manager import (
    MaterialManager
)

CUSTOM_LIBRARY = "unit_tests/domain/test_library.toml"

unit_test_material = {
    'name': 'UNIT_TEST_MATERIAL',
    'tag': '',
    'physical': {
        'lamination': 'solid',
        'lamination_fill': 1.0,
        'number_of_strands': 1,
        'wire_diameter': 0
    }
}


class ManagerTest(unittest.TestCase):
    """
    Tests the functions within the material manager
    """
    def test_use_material(self) -> None:
        """
        Tests use_material by requesting "UNIT_TEST_MATERIAL"
        """
        manager = MaterialManager()

        # Adds the unit test material to runtime memory
        manager.materials["material"].append(unit_test_material)

        expected = unit_test_material
        result = manager.use_material(
            "UNIT_TEST_MATERIAL",
        )

        self.assertEqual(expected, result)

    def test_custom_library(self) -> None:
        """
        Tests custom library path using "UNIT_TEST_MATERIAL"
        """
        manager = MaterialManager(CUSTOM_LIBRARY)
        expected = unit_test_material
        result = manager.use_material(
            "UNIT_TEST_MATERIAL"
        )

        self.assertEqual(expected, result)

    def test_case_insensitive_lookup(self) -> None:
        """
        Tests use_material and _lookup_material by entering
        low case version of the material name
        """
        manager = MaterialManager(CUSTOM_LIBRARY)
        expected = unit_test_material
        result = manager.use_material(
            "unit_test_material"
        )
        self.assertEqual(expected, result)

    def test_apply_parameter_wire(self) -> None:
        """
        Tests that a wire material correctly applies
        the wire diameter parameter and updates physical
        properties.
        """

        test_material = copy.deepcopy(unit_test_material)

        # Adds the unit test material to runtime memory
        test_material['tag'] = "wire"
        test_material['physical']['wire_diameter'] = 0.6
        manager = MaterialManager()

        manager.materials["material"].append(test_material)

        expected = test_material
        result = manager.use_material(
            "UNIT_TEST_MATERIAL",
            wire_diameter=0.6
        )

        self.assertEqual(expected, result)

    def test_apply_parameter_magnet(self) -> None:
        """
        Tests that a magnetic material correctly applies a grade parameter
        and updates magnetic properties.
        """
        manager = MaterialManager()

        test_magnet = copy.deepcopy(unit_test_material)
        test_magnet['name'] = "UNIT_TEST_MAGNET"
        test_magnet['tag'] = "magnet"
        test_magnet['magnetic'] = {
            'relative_permeability': [1.05, 1.05],
            'coercivity': 0,
            'Remanence': 0,
            'current_density': 0
        }
        test_magnet['grades'] = {
            "N35": {'coercivity': 905659, 'Remanence': 1.104},
            "N42": {'coercivity': 994529, 'Remanence': 1.104}
        }

        manager.materials["material"].append(test_magnet)

        # Apply grade N35
        result = manager.use_material(
            "UNIT_TEST_MAGNET",
            grade="N35"
        )

        self.assertEqual(result['magnetic']['coercivity'], 905659)
        self.assertEqual(result['magnetic']['Remanence'], 1.104)

    def test_invalid_tag(self) -> None:
        """
        Tests _apply_parameter by using a tag that doesn't exist
        """
        manager = MaterialManager()

        # Adds the unit test material to runtime memory
        test_material = copy.deepcopy(unit_test_material)
        test_material['tag'] = "i don't exist"
        manager.materials["material"].append(test_material)

        with self.assertRaises(ValueError):
            manager.use_material(
                "UNIT_TEST_MATERIAL"
            )

    def test_missing_param(self) -> None:
        """
        Tests _apply_parameter function by
        not using the required param for the tag
        """
        test_material = copy.deepcopy(unit_test_material)

        # Adds the unit test material to runtime memory
        test_material['tag'] = "magnet"
        manager = MaterialManager()

        manager.materials["material"].append(test_material)

        with self.assertRaises(ValueError):
            manager.use_material(
                "UNIT_TEST_MATERIAL"
            )

    def test_invalid_parameter(self) -> None:
        """
        Tests _apply_parameter function by
        using a param that isn't correct for the tag
        """

        test_material = copy.deepcopy(unit_test_material)

        # Adds the unit test material to runtime memory
        test_material['tag'] = "wire"
        manager = MaterialManager()

        manager.materials["material"].append(test_material)

        with self.assertRaises(ValueError):
            manager.use_material(
                "UNIT_TEST_MATERIAL",
                exist=0.6
            )

    def test_invalid_material(self) -> None:
        """
        Tests use_material by requesting a material
        that doesn't exist
        """

        manager = MaterialManager()
        with self.assertRaises(KeyError):
            manager.use_material(
                "Too be or not to be! That is.."
            )
