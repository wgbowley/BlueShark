"""
Filename: commutation.py
Author: William Bowley
Version: 1.2
Date: 2025-07-28
Description:
    Functions to generate commutation current profiles
    for 3-phase tubular linear motor.
"""

from blueshark.models.tubular.physics.transforms import (
    inverse_clarke_transform, inverse_park_transform
)
from blueshark.models.tubular.physics.angles import (
    electrical_angle, mechanical_angle
)


def commutation(
    circumference: float,
    pole_pairs: int,
    currents_peak: tuple[float, float],
    num_samples: int,
    phase_offset: float = 0.0
) -> tuple[float, list[tuple[float, float, float]]]:
    """
    Generates the commutation current profile

    Args:
        circumference: Circumference of the motor
        pole_pairs: Number of magnetic pole pairs
        current_peak: Peak values for components (id, iq)
        numb_samples: Number of sampling points.
        phase_offset: Electrical angle offset (in radians)
                      Default is 0.0
    """
    if not isinstance(circumference, (int, float)) or circumference <= 0:
        msg = f"Circumference must be a positive number, got '{circumference}'"
        raise ValueError(msg)

    if not isinstance(pole_pairs, int) or pole_pairs <= 0:
        msg = f"Pole pairs must be a positive integer, got '{pole_pairs}'"
        raise ValueError(msg)

    if (
        not isinstance(currents_peak, tuple)
        or len(currents_peak) != 2
        or not all(isinstance(i, (int, float)) for i in currents_peak)
    ):
        raise TypeError(
            "Currents peak must be a tuple of two numbers, "
            f"got '{currents_peak}'"
        )

    if not isinstance(num_samples, int) or num_samples <= 0:
        raise ValueError(
            "Number of samples must be a positive integer, "
            f"got '{num_samples}'"
        )

    step_size = circumference / num_samples
    profile: list[tuple[float, float, float]] = []

    for step in range(num_samples + 1):
        mech_angle = mechanical_angle(circumference, step * step_size)
        elec_angle = electrical_angle(pole_pairs, mech_angle) + phase_offset

        alpha, beta = inverse_park_transform(
            currents_peak[0], currents_peak[1], elec_angle
        )
        pa, pb, pc = inverse_clarke_transform(alpha, beta)

        profile.append((pa, pb, pc))

    return step_size, profile
