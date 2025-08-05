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


from blueshark.output.selector import OutputSelector
from blueshark.simulations.frame import simulate_frame
from blueshark.motor.linear_interface import LinearBase
from blueshark.domain.physics.transforms import inverse_clarke_transform
from blueshark.domain.physics.transforms import inverse_park_transform
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
        status (bool): If True, print intermediate alignment data.

    Returns:
        float: Phase shift (radians) for peak Lorentz force alignment.
    """

    if number_samples <= 0:
        raise ValueError(f"Number samples must be > 0, got {number_samples}")
    if not isinstance(status, bool):
        raise ValueError(f"Status must be a boolean value, got {status}")

    best_offset = 0.0
    max_force = float("-inf")

    # Geometry
    circumference = motor.get_circumference()
    pole_count = motor.get_number_poles()

    if pole_count <= 0 or circumference <= 0:
        raise ValueError("pole_count and circumference must be > 0")

    pole_pitch = circumference / pole_count
    shift_size = pole_pitch / number_samples

    # Fixed d-q current vector
    i_d, i_q = motor.get_peak_currents()

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
            subjects={"group": motor.get_moving_group()},
            currents=(pa, pb, pc),
            step=0
        )

        if result is None:
            if status:
                print(f"[WARN] Simulation failed at offset {angle:.4f}")
            continue

        force = result["force_lorentz"][0]

        if status:
            print(f"Shift:{angle:.3f} rad | Force:{force:.3f}N")

        if force > max_force:
            max_force = force
            best_offset = angle

    return best_offset
