"""
Filename: commutation.py
Author: William Bowley
Version: 1.1
Date: 2025-07-18
Description:
    Functions to generate commutation current profiles for 3-phase motors.

Functions:
- rotational_commutation(circumference, num_pairs, currents_peak, number_samples) -> list of (pa, pb, pc)
"""

import math

from blueshark.domain.physics.transforms import inverse_clarke_transform, inverse_park_transform
from blueshark.domain.physics.angles import mechanical_angle, electrical_angle

def rotational_commutation(
        circumference: float,
        num_pairs: int,
        currents_peak: tuple[float, float],
        number_samples: int
    ) -> list[tuple[float, float, float]]:
    """
    Generates the commutation current profile over one full mechanical rotation.

    Args:
        circumference (float): Circumference of the rotor path.
        num_pairs (int): Number of pole pairs in the motor.
        currents_peak (tuple[float, float]): Peak currents in the d and q axes.
        number_samples (int): Number of discrete samples in the profile.

    Returns:
        list[tuple[float, float, float]]: List of three-phase current tuples (pa, pb, pc) for each sample point.
    """
    step_size = circumference / number_samples  # Linear step per sample
    profile = []

    for step in range(number_samples + 1):
        mech_angle_val = mechanical_angle(circumference, step * step_size)
        elec_angle_val = electrical_angle(num_pairs, mech_angle_val)

        alpha, beta = inverse_park_transform(currents_peak[0], currents_peak[1], elec_angle_val)
        pa, pb, pc = inverse_clarke_transform(alpha, beta)

        profile.append((pa, pb, pc))

    return profile
