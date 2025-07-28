import unittest
from math import ceil

from domain.generation.number_turns import estimate_turns
from domain.generation.geometry import get_centroid_point

class NumberTurns(unittest.TestCase):
    """Unit tests for the estimate_turns function."""

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
    def test_standard_case(self):
        centeroid_point = (12.5, 12.5)
        self.assertEqual(get_centroid_point((10,10), 5, 5), centeroid_point)
        
    def test_invalid_origins(self):
        with self.assertRaises(TypeError):
            get_centroid_point([0,0], 2, 3) # List instead of tuple
        with self.assertRaises(TypeError):
            get_centroid_point((0,), 2, 3) # tuple length 1 instead of 2
    
    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            get_centroid_point((0,0), 0, 5) # Zero length
        with self.assertRaises(ValueError):
            get_centroid_point((0,0), -1, 5) # Negative length 
            
    def test_invalid_height(self):
        with self.assertRaises(ValueError):
            get_centroid_point((0,0), 5, 0) # Zero Height
        with self.assertRaises(ValueError):
            get_centroid_point((0,0), 5, -1) # Negative Height 
            