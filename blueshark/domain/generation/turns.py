"""
File: turns.py
Author: William Bowley
Version: 1.1
Date: 2025-06-24
Description:
    Functions to calculate slot/coils geometry parameters, such as the estimated
    number of turns for rectangular or square slot/coils.

Functions:
- number_turns(length, height, wire_diameter, waste_factor=0.25) -> int
""" 

from math import ceil

def number_turns(
    length: float,
    height: float,
    wire_diameter: float,
    waste_factor: float = 0.25
) -> int:
    """
    Calculate the approximate number of turns for square or rectangular slot/coils.

    Assumes a default waste factor of 0.25 to account for packing inefficiency.

    Args:
        length (float): Length of the cross-section.
        height (float): Height of the cross-section.
        wire_diameter (float): Diameter of the wire.
        waste_factor (float, optional): Fractional increase in wire diameter to
                                        account for insulation and packing waste.
                                        Defaults to 0.25.

    Returns:
        int: Estimated number of turns.
    """
    
    coil_area = length * height
    wire_area = (wire_diameter * (1 + waste_factor)) ** 2
    turns = coil_area / wire_area

    return ceil(turns)
