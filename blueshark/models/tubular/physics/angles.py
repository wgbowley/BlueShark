"""
File: angles.py
Author: William Bowley
Version: 1.2
Date: 2025-07-27
Description:
    Functions to convert linear displacement to
    mechanical and electrical angles.
"""

import logging

from blueshark.domain.constants import PRECISION, TWO_PI


def mechanical_angle(circumference: float, displacement: float) -> float:
    """
    Convert linear displacement to mechanical angle in radians.

    Args:
        circumference: The circumference of the rotor path (must be > 0).
        displacement : Linear displacement along the path.

    Returns:
        float: Mechanical angle in radians, normalized to [0, 2π).

    Raises:
        ValueError: If circumference <= 0.
    """
    if circumference <= 0:
        msg = f"Circumference must be > 0, got {circumference}"
        logging.error(msg)
        raise ValueError(msg)

    angle = (TWO_PI * displacement) / circumference
    return round(angle % TWO_PI, PRECISION)


def electrical_angle(num_pole_pairs: int, mech_angle: float) -> float:
    """
    Convert mechanical angle to electrical angle.

    Args:
        num_pole_pairs: Number of pole pairs in the motor (must be > 0).
        mech_angle: Mechanical angle in radians.

    Returns:
        float: Electrical angle in radians, normalized to [0, 2π).

    Raises:
        ValueError: If num_pole_pairs <= 0.
    """
    if num_pole_pairs <= 0:
        msg = f"Number of pole pairs must be > 0, got {num_pole_pairs}"
        logging.error(msg)
        raise ValueError(msg)

    return round((mech_angle * num_pole_pairs) % TWO_PI, PRECISION)
