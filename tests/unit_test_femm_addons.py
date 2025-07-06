"""
Filename: unit_test_femm_addons.py
Author: William Bowley
Version: 1.0
Date: 27 - 06 - 2025
Description:
    This script tests the functions within application/femm_addons.py to ensure 
    they are working as expected.
    
    I would recommend entering this command before using:
    - "python -m unittest -v (this file path)" 
"""

# Libraries
import unittest
import sys
import os

# Sets the program path to the absolute path 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Modules
from application.simulate import femm_mi_addons

class TestAddons(unittest.TestCase):
    
    # Tests the get centroid point function
    def test_get_centroid_point(self):
        
        centroidAtOrigin = femm_mi_addons.get_centroid_point(
            origin          =   (0,0), 
            objectLength    =   10, 
            objectHeight    =   10
        )
        centroidOffOrigin = femm_mi_addons.get_centroid_point(
            origin          =   (100,98.2), 
            objectLength    =   10, 
            objectHeight    =   15
        )
        
        self.assertEqual(centroidAtOrigin,(5,5),'On Origin - Centeroid point failed')
        self.assertEqual(centroidOffOrigin, (105,105.7),'Off Origin - Centeroid point failed')
    
    
    # Tests the origin points function
    def test_origin_points(self):
        
        # Correct Outputs 
        originNoOffset = [(0,0), (30,0), (60,0), (90,0), (120,0)]
        originOffset = [(12,2), (32,12), (52, 22)]

        # Test functions
        originPointNoOffset = femm_mi_addons.origin_points(
            objectNum   = 5,
            xPitch      = 30,
            yPitch      = 0,
        )
        originPointOffset = femm_mi_addons.origin_points(
            objectNum   = 3,
            xPitch      = 20,
            yPitch      = 10,
            xOffset     = 12,
            yOffset     = 2
        )
        
        self.assertEqual(originPointNoOffset, originNoOffset, 'No Offset - Origin Points failed')
        self.assertEqual(originPointOffset, originOffset, 'Offset - Origin Points failed')
        
if __name__ == '__main__':
    unittest.main()