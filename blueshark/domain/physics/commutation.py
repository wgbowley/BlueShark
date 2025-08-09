"""
Filename: commutation.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Functions to generate commutation current profiles for 3-phase motors.

Functions:
- displacement_commutation(displacement, circumference, pole_pairs,
                           currents_peak, num_samples, phase_offset=0.0)
    Generates commutation current profiles based
    on rotor displacement and motor parameters.
"""

import logging

from typing import Tuple, List
from blueshark.domain.physics.angles import electrical_angle, mechanical_angle
from blueshark.domain.physics.transforms import inverse_clarke_transform
from blueshark.domain.physics.transforms import inverse_park_transform


def displacement_commutation(
    displacement: float,
    circumference: float,
    pole_pairs: int,
    currents_peak: Tuple[float, float],
    num_samples: int,
    phase_offset: float = 0.0
) -> Tuple[float, List[Tuple[float, float, float]]]:
    """
    Generates the commutation current profile for a given displacement.

    Args:
        displacement (float): Total linear displacement for
        which the profile is generated.
        circumference (float): Circumference of the motor.
        pole_pairs (int): Number of magnetic pole pairs.
        currents_peak (Tuple[float, float]): Peak values for flux and
                                             force current components (id, iq).
        num_samples (int): Number of sampling points.
        phase_offset (float, optional): Electrical angle offset (in radians).
                                        Default is 0.0.

    Returns:
        Tuple[float, List[Tuple[float, float, float]]]:
            step_size: The distance between each sample step.
            profile: List of phase currents at each step as (pa, pb, pc).
    """

    if displacement == 0:
        msg = "Displacement cannot be set to zero."
        logging.error(msg)
        raise ValueError(msg)

    if num_samples <= 0:
        msg = f"Number of samples must be > 0, got {num_samples}"
        logging.error(msg)
        raise ValueError(msg)

    if circumference <= 0:
        msg = f"Motor circumference must be > 0, got {circumference}"
        logging.error(msg)
        raise ValueError(msg)

    if pole_pairs <= 0:
        msg = f"Number of pole pairs must be > 0, got {pole_pairs}"
        logging.error(msg)
        raise ValueError(msg)

    if not isinstance(currents_peak, tuple) or len(currents_peak) != 2:
        msg = "Current peaks must be a tuple of length 2."
        logging.error(msg)
        raise TypeError(msg)

    if any(not isinstance(i, (int, float)) for i in currents_peak):
        msg = "Each current peak must be a number."
        logging.error(msg)
        raise TypeError("Each current peak must be a number.")

    step_size = displacement / num_samples
    profile: List[Tuple[float, float, float]] = []

    for step in range(num_samples + 1):
        mech_angle = mechanical_angle(circumference, step * step_size)
        elec_angle = electrical_angle(pole_pairs, mech_angle) + phase_offset

        alpha, beta = inverse_park_transform(
            currents_peak[0], currents_peak[1], elec_angle
        )
        pa, pb, pc = inverse_clarke_transform(alpha, beta)

        profile.append((pa, pb, pc))

    return step_size, profile
