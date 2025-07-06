"""
Filename: unit_test_domain.py
Author: William Bowley
Version: 1.0
Date: 06 - 07 - 2025
Description:
    This script tests the functions within domain/(motor_generation & motor_physics) 
    to ensure they are working as expected.
    
    I would recommend entering this command before using:
    - "python -m unittest -v (this file path)" 
"""

# Libraries
import unittest
import sys
import os
import math

# Sets the program path to the absolute path 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Modules
from domain import motor_physics 
from domain import motor_generation 

""" Tests the motor physics module """
class motorPhysics(unittest.TestCase):
    
    # Tests the inverted park transform function
    def test_inverted_park_transform(self):
        
        test1 = motor_physics.inverted_park_transform(
            currentFlux     = 0,
            currentForce    = 1,
            electricalAngle = math.pi/2
        )
        
        test2 = motor_physics.inverted_park_transform(
            currentFlux     = 1,
            currentForce    = 0,
            electricalAngle = (2*math.pi)/3
        )
        
        test3 = motor_physics.inverted_park_transform(
            currentFlux     = 1.2,
            currentForce    = 10.32,
            electricalAngle = -math.pi/4
        )

        self.assertAlmostEqual(test1[0], -1, places=6, msg='IPT incorrect Test1 alpha')
        self.assertAlmostEqual(test1[1], 0, places=6, msg='IPT incorrect Test1 beta')

        self.assertAlmostEqual(test2[0], -0.5, places=6, msg='IPT incorrect Test2 alpha')
        self.assertAlmostEqual(test2[1], math.sqrt(3)/2, places=6, msg='IPT incorrect Test2 beta')

        # Expected Results for test 3
        expected_alpha = 1.2 * math.cos(-math.pi/4) - 10.32 * math.sin(-math.pi/4)
        expected_beta  = 1.2 * math.sin(-math.pi/4) + 10.32 * math.cos(-math.pi/4)

        self.assertAlmostEqual(test3[0], expected_alpha, places=6, msg='IPT incorrect Test3 alpha')
        self.assertAlmostEqual(test3[1], expected_beta, places=6, msg='IPT incorrect Test3 beta')
    
    
    # Tests the inverted clarke transform function
    def test_inverted_clarke_transform(self):
        
        test1 = motor_physics.inverted_clarke_transform(
            alpha   = 0.5,
            beta    = 0.25
        )
        
        test2 = motor_physics.inverted_clarke_transform(
            alpha   = -0.7,
            beta    = 0.3
        )
        
        # Test 1
        self.assertAlmostEqual(test1[0], 1/2, places=6, msg="ICT incorrect Test1 Phase A")
        self.assertAlmostEqual(test1[1], (math.sqrt(3)/8-1/4), places=6, msg="ICT incorrect Test1 Phase B")
        self.assertAlmostEqual(test1[2], (-1/4-math.sqrt(3)/8), places=6, msg="ICT incorrect Test1 Phase C")
        
        # Test 2
        self.assertAlmostEqual(test2[0], -0.7, places=6, msg="ICT incorrect Test2 Phase A")
        self.assertAlmostEqual(test2[1], (3*math.sqrt(3)+7)/20, places=6, msg="ICT incorrect Test 2 Phase B")
        self.assertAlmostEqual(test2[2], (7-3*math.sqrt(3))/20, places=6, msg="ICT incorrect Test 2 Phase C")
    
if __name__ == '__main__':
    unittest.main()