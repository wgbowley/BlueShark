"""
File: run_tests.py
Author: William Bowley
Version: 1.0
Date: 2025-08-05

Description:
    Runs tests:
    - unit_generation
    - unit_physics
"""

import unittest
import unit_physics
import unit_generation

loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Domain/Physics Tests
suite.addTests(loader.loadTestsFromTestCase(unit_physics.TestMechanical))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestElectrical))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestTransforms))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestRippleFunctions))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestCommutation))

# Domain/Generation Tests
suite.addTest(loader.loadTestsFromTestCase(unit_generation.NumberTurns))
suite.addTest(loader.loadTestsFromTestCase(unit_generation.GetCenteroid))
suite.addTest(loader.loadTestsFromTestCase(unit_generation.TestOriginPoints))

runner = unittest.TextTestRunner(verbosity=2)

if __name__ == "__main__":
    result = runner.run(suite)
