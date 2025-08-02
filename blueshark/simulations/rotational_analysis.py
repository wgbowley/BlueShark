"""
Filename: rotational_analysis.py
Author: William Bowley
Version: 1.2
Date: 2025-07-29

Description:
    Provides the rotational_analysis function to perform detailed
    rotational simulation of linear motors using FEMM.

    This module uses displacement_commutation to generate phase
    current profiles over a full mechanical rotation and simulates
    each step via simulate_frame. It aggregates the results with
    displacement data for analysis.
"""

from blueshark.domain.physics.commutation import displacement_commutation
from blueshark.simulations.frame import simulate_frame
from blueshark.motor.linear_interface import LinearBase
from blueshark.output.selector import OutputSelector
from typing import Any


def rotational_analysis(
    motor: LinearBase,
    output_selector: OutputSelector,
    subjects: dict[str, Any],
    number_samples: int,
    phase_offset: float = 0,    
    status: bool = True,
):
    """
    Perform rotational analysis by simulating frames over displacement steps
    with current profiles from displacement_commutation.

    Args:
        motor: LinearBase motor instance.
        output_selector: OutputSelector instance to compute outputs.
        subjects: Context dict for output selector.
        number_samples: Number of samples (simulation steps).
        phase_offset: Aligns magnetic fields of stator & armuture
        status: Whether to print progress.

    Returns:
        List of dicts containing displacement and simulation outputs per step.
    """
    if number_samples <= 0:
        raise ValueError(f"Number samples must be a positive integer, got {number_samples}")
    
    motor_circumference = motor.get_circumference()
    
    step_size, profile = displacement_commutation(
        motor_circumference,
        motor_circumference,
        motor.get_number_poles() / 2,
        motor.get_peak_currents(),
        number_samples,
        phase_offset
    )

    results = []
    displacement = 0.0

    for step, currents in enumerate(profile, start=1):
        if status:
            print(f"Step {step-1}/{number_samples} | Total displacement: {displacement:.4f}")

        frame_results = simulate_frame(
            motor,
            output_selector,
            subjects,
            step_size,
            currents,
        )

        results.append({"displacement": displacement, "outputs": frame_results})
        displacement += step_size

    return results
