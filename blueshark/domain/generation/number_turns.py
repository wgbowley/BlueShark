"""
File: number_turns.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Functions to calculate slot/coils geometry parameters, such
    as the estimatednumber of turns for rectangular or square slot/coils.

Functions:
- estimate_turns(length, height, wire_diameter, fill_factor=0.7)
    Estimates the number of turns within the slot/coil cross section.
"""

from math import ceil


def estimate_turns(
    length: float,
    height: float,
    wire_diameter: float,
    fill_factor: float = 0.7
) -> int:
    """
    Calculate the approximate number of turns for
    square or rectangular slot/coils.

    Args:
        length (float): Slot length in mm.
        height (float): Slot height in mm.
        wire_diameter (float): Diameter of the wire in mm
                               (including insulation).
        fill_factor (float): Fraction of slot area filled by copper (0->1).
                             Default 0.7.

    Returns:
        int: Estimated number of turns.
    """

    if length <= 0 or height <= 0 or wire_diameter <= 0:
        raise ValueError("All dimensions must be positive and non-zero.")
    if fill_factor <= 0 or fill_factor >= 1:
        raise ValueError("Fill factor must be between 0 and 1.")

    slot_area = length * height
    wire_area = wire_diameter ** 2
    effective_area = slot_area * fill_factor
    turns = effective_area / wire_area

    return ceil(turns)
