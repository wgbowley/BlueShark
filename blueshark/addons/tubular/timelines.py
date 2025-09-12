"""
File: timelines.py
Author: William Bowley
Version: 0.1
Date: 2025-07-28
Description:
    This is an addon for timelines for tubular motor
    magnetic & heat transisent simulations
"""

import math
from typing import Any

from blueshark.domain.constants import Units
from blueshark.domain.physics.convert_units import UnitConverter
from blueshark.domain.physics.thermal import (
    calulate_volumetric_heating
)

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
    for _, current_set in enumerate(currents):
        # cumulative rotation angle for this step

        # rotational motion dictionary
        motion = {
            "step": step_size,
            "angle": math.pi/2
        }

        entry = {
            "motion": motion,  # or motion_rot
            "groups": groups,
            "currents": [current_set, phases]
        }
        timeline.append(entry)

    return timeline


def commutation_thermal(
    units: Units,
    circumference: float,
    pole_pairs: int,
    currents_peak: tuple[float, float],
    resistance: float,
    slot_volume: float,
    num_samples: int,
    groups: list[int],
    material: str
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

    area = UnitConverter.to_square_meters(slot_volume, units)
    material = material.get("name", "unknown")
    timeline = []
    for _, current_set in enumerate(currents):
        # cumulative rotation angle for this step

        # rotational motion dictionary
        motion = {
            "step": step_size,
            "angle": math.pi/2
        }

        heat = calulate_volumetric_heating(
            max(current_set),
            resistance,
            area
        )

        entry = {
            "motion": motion,
            "groups": groups,
            "heat_flux": (heat, material)
        }
        timeline.append(entry)

    return timeline
