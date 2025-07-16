"""
Filename: custom_deap.py
Author: William Bowley
Version: 1.1
Date: 21 - 05 - 2025
Description:
"""

import random 

def select_Wire(wire_sizes: list[float]) -> float:
    selectedWire = random.choice(wire_sizes)
    return selectedWire