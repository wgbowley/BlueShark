"""
File: run_tests.py
Author: William Bowley
Version: 1.3
Date: 2025-08-12

Description:
    Runs tests:
    - domain/unit_generation
"""

import unittest
import domain.unit_generation as unit_gen

loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Domain/unit_generation Tests
suite.addTests(loader.loadTestsFromTestCase(unit_gen.ShapeArea))


runner = unittest.TextTestRunner(verbosity=2)

if __name__ == "__main__":
    result = runner.run(suite)
