"""
Filename: alignment.py
Author: William Bowley
Version: 1.2
Date: 2025-08-03

Description:
    Provides the phase_alignment function to align the magnetic flux
    of the stator and armature for optimal force output.

    Simulation Flow:
    - Compute geometry
    - Simulate phase shifts
    - Return optimal alignment
"""

import logging

from blueshark.motor.interface import LinearBase
from blueshark.output.selector import OutputSelector

from blueshark.domain.physics.transforms import inverse_clarke_transform
from blueshark.domain.physics.transforms import inverse_park_transform
from blueshark.simulations.frame import simulate_frame
from blueshark.configs import TWO_PI


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
        status (bool): Whether to print progress messages

    Returns:
        float: Phase shift (radians) for peak Lorentz force alignment.
    """
    logging.info(f"Starting phase alignment for {motor}")

    if number_samples <= 0:
        msg = f"Number samples must be > 0, got {number_samples}"
        logging.error(msg)
        raise ValueError(msg)

    if not isinstance(status, bool):
        msg = f"Status must be a boolean value, got {status}"
        logging.error(msg)
        raise ValueError(msg)

    best_offset = 0.0
    max_force = float("-inf")

    # Geometry
    circumference = motor.circumference
    pole_count = motor.number_poles

    if pole_count <= 0 or not isinstance(pole_count, int):
        msg = f"Pole count must be > 0 & integer, got {pole_count}"
        logging.error(msg)
        raise ValueError(msg)

    if circumference <= 0:
        msg = f"Circumference must be > 0, got {circumference}"
        logging.error(msg)
        raise ValueError(msg)

    pole_pitch = circumference / pole_count
    shift_size = pole_pitch / number_samples

    # Fixed d-q current vector
    i_d, i_q = motor.peak_currents

    for index in range(number_samples + 1):
        real_angle = (TWO_PI * index * shift_size) / circumference
        angle = real_angle * (pole_count / 2)
        selector = OutputSelector(["force_lorentz"])

        # q-b current vector -> alpha-beta -> 3-phase
        alpha, beta = inverse_park_transform(i_d, i_q, angle)
        pa, pb, pc = inverse_clarke_transform(alpha, beta)

        result = simulate_frame(
            motor=motor,
            output_selector=selector,
            subjects={"group": motor.moving_group},
            currents=(pa, pb, pc),
            step=0
        )

        if result is None:
            msg = f"Simulation failed at offset {angle:.4f}"
            logging.warning(msg)
            continue

        force = result["force_lorentz"][0]

        if status:
            print(f"Shift:{angle:.3f} rad | Force:{force:.3f}N")

        if force > max_force:
            max_force = force
            best_offset = angle

    logging.info(f"Phase alignment completed for {motor}")
    return best_offset
