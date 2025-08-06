"""
Filename: rotational_analysis.py
Author: William Bowley
Version: 1.2
Date: 2025-07-29

Description:
    Provides the rotational_analysis function to perform detailed
    rotational simulation of linear motors using FEMM.

    Simulation flow:
    - Retrieves the motor circumference and number of pole pairs.
    - Generates step size and three-phase current profiles.
    - Simulates frames to produce results with respect to dispalcement.
"""

from typing import Any
from blueshark.motor.linear_interface import LinearBase
from blueshark.output.selector import OutputSelector

from blueshark.domain.physics.commutation import displacement_commutation
from blueshark.simulations.frame import simulate_frame


def rotational_analysis(
    motor: LinearBase,
    output_selector: OutputSelector,
    subjects: dict[str, Any],
    number_samples: int,
    phase_offset: float = 0,
    status: bool = True,
) -> list[dict[str, Any]]:
    """
    Perform rotational analysis by simulating frames over displacement steps
    using current profiles from displacement_commutation.

    Args:
        motor (LinearBase): Motor instance to simulate.
        output_selector (OutputSelector): Defines which outputs to extract.
        subjects (dict[str, Any]): Metadata or context for the simulation.
        number_samples (int): Number of simulation steps.
        phase_offset (float): Electrical shift to align flux.
        status (bool): Whether to print progress messages.

    Returns:
        List[dict]: Simulation outputs for each displacement step.
    """

    if number_samples <= 0:
        raise ValueError("Number of samples must be a positive integer.")
    if not isinstance(status, bool):
        raise ValueError("Status must be a boolean value.")

    motor_circumference = motor.circumference
    motor_pole_pairs = motor.number_poles // 2

    step_size, profile = displacement_commutation(
        motor_circumference,
        motor_circumference,
        motor_pole_pairs,
        motor.peak_currents,
        number_samples,
        phase_offset
    )

    results = []

    for step, currents in enumerate(profile, start=1):
        displacement = step * step_size

        if status:
            print(f"[{step - 1}/{number_samples}] dx={displacement:.2f}")

        frame_results = simulate_frame(
            motor,
            output_selector,
            subjects,
            step_size,
            currents,
        )

        formatted = {"displacement": displacement, "outputs": frame_results}
        results.append(formatted)

    return results
