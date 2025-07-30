
# This has not been tested***

from output.selector import OutputSelector
from simulations import rotational_analysis
from motor.linear_interface import LinearBase
from domain.physics.angles import mechanical_angle

def phase_alignment(
    motor: LinearBase,
    num_samples: int = 1,
    num_shifts: int = 10,
) -> float:
    """
    Finds the phase offset that aligns the stator and armature fields.
    """

    requested_outputs = ["force_lorentz"]
    best_offset = 0.0
    best_force = float("-inf")

    motor_circumference = motor.motor_circumference
    poles_num  = motor.number_poles
    pole_pitch = motor_circumference / poles_num
    shift_size = pole_pitch / num_samples

    for index in range(num_samples):
        offset = mechanical_angle(pole_pitch/(poles_num/2), index * shift_size) # this isn't good pratice but it might work
        output_selector = OutputSelector(requested_outputs)
        
        result = rotational_analysis(motor, 
            output_selector, 
            {"group": motor.moving_group}, 
            num_shifts, 
            offset
        )

        lorentz_forces = [m["force_lorentz"][0] for m in result]
        avg_force = sum(lorentz_forces) / len(lorentz_forces)

        if avg_force > best_force:
            best_force = avg_force
            best_offset = offset

    return best_offset
