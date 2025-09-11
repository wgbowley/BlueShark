"""
File: timelines.py
Author: William Bowley
Version: 0.1
Date: 2025-07-28
Description:
    This is an addon for timelines for bldc motor
    magnetic & heat transisent simulations
"""

import math
from typing import Any

from blueshark.domain.physics.commutation import (
    displacement_commutation
)


def commutation_magnetic(
    circumference: float,
    pole_pairs: int,
    currents_peak: tuple[float, float],
    num_samples: int,
    groups: list[int],
    phases: list[str],
    axis: tuple[float, float, float] = (0, 0)
) -> list[dict[str, Any]] | None:
    """
    Magnetic Commutation (One rotation)
    """
    # Get the displacement commutation steps and currents
    step_size, currents = displacement_commutation(
        circumference,
        circumference,
        pole_pairs,
        currents_peak,
        num_samples
    )

    timeline = []
    for i, current_set in enumerate(currents):
        # cumulative rotation angle for this step
        angle = (i * step_size) / circumference * math.tau

        # rotational motion dictionary
        motion = {
            "axis": axis,
            "angle": angle
        }

        entry = {
            "motion": motion,  # or motion_rot
            "groups": groups,
            "currents": [current_set, phases]
        }
        timeline.append(entry)

    return timeline


def commutation_thermal(
    circumference: float,
    pole_pairs: int,
    currents_peak: tuple[float, float],
    resistance: float,
    num_samples: int,
    groups: list[int],
    phases: list[str],
    axis: tuple[float, float, float] = (0, 0)
) -> list[dict[str, Any]] | None:
    """
    Thermal Commutation (One rotation)
    """
    # Get the displacement commutation currents (like your magnetic version)
    step_size, currents = displacement_commutation(
        circumference,
        circumference,
        pole_pairs,
        currents_peak,
        num_samples
    )

    timeline = []
    for i, current_set in enumerate(currents):
        # cumulative rotation angle for this step
        angle = (i * step_size) / circumference * math.tau

        # compute per-phase copper losses: P = I^2 * R
        losses = [i_val**2 * resistance for i_val in current_set]

        entry = {
            "motion": {"axis": axis, "angle": angle},
            "groups": groups,
            "heat_flux": (losses, phases)
        }
        timeline.append(entry)

    return timeline
