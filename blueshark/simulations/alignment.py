"""
Filename: alignment.py
Author: William Bowley
Version: 1.2
Date: 2025-08-03

Description:
    Functions to align the magnetic fields of the stator and armature
    for optimal Lorentz force production in linear motors.
    
    Functions:
    - phase_alignment(motor: class, number_samples: int, status: bool) -> offset: float
"""

from blueshark.configs import TWO_PI
from blueshark.output.selector import OutputSelector
from blueshark.simulations.frame import simulate_frame
from blueshark.motor.linear_interface import LinearBase
from blueshark.domain.physics.transforms import (
    inverse_clarke_transform,
    inverse_park_transform
)


def phase_alignment(
    motor: LinearBase,
    number_samples: int = 10,
    status: bool = True
) -> float:
    """
    Finds the electrical angle offset that maximizes Lorentz force
    by scanning discrete shifts across one pole pitch.

    Args:
        motor (LinearBase): The motor object to be aligned.
        number_samples (int): Number of discrete phase offsets to test.
        status (bool): If True, print intermediate alignment data.

    Returns:
        float: Electrical offset (radians) for peak Lorentz force alignment.
    """

    if number_samples <= 0:
        raise ValueError(f"Number of samples must be positive, got {number_samples}")

    best_offset = 0.0
    max_force = float("-inf")

    # Geometry
    circumference = motor.get_circumference()
    pole_count = motor.get_number_poles()
    pole_pitch = circumference / pole_count
    shift_size = pole_pitch / number_samples

    # Fixed d-q current vector
    i_d, i_q = motor.get_peak_currents()

    for index in range(number_samples + 1):
        offset = (TWO_PI * index*shift_size)/circumference * (pole_count / 2)
        selector = OutputSelector(["force_lorentz"])

        # q-b current vector -> alpha-beta -> 3-phase
        alpha, beta = inverse_park_transform(i_d, i_q, offset)
        pa, pb, pc = inverse_clarke_transform(alpha, beta)

        result = simulate_frame(
            motor=motor,
            output_selector=selector,
            groups={"group": motor.get_moving_group()},
            time=0,
            phases=(pa, pb, pc),
        )

        force = result["force_lorentz"]

        if status:
            print(f"Offset: {offset:.4f} rad | Phases: {pa:.4f}, {pb:.4f}, {pc:.4f} | Force: {force:.4f}")

        if force > max_force:
            max_force = force
            best_offset = offset

    return best_offset
