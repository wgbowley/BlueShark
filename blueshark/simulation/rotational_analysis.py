import os
import femm
from typing import Any

from motors.motor_interface import MotorBase
from outputs.output_selector import OutputSelector
from domain.physics.commutation import rotational_commutation


def rotational_analysis(
    motor: MotorBase,
    output_selector: OutputSelector,
    subjects: dict[str, Any],
    num_samples: int,
    status: bool = True
) -> list[dict]:
    """
    Performs a full rotation analysis for a motor using FEMM.

    Args:
        motor (MotorBase): The motor simulation object.
        output_selector (OutputSelector): Extracts desired outputs from FEMM simulation.
        subjects (dict): Dictionary of FEMM elements used by OutputSelector to compute outputs.
            Expected keys:
                - 'group' (int or list of ints) for group-based outputs
                - 'circuitName' (str or list of str) for circuit-based outputs
        num_samples (int): Number of discrete steps dividing one full rotation.

    Returns:
        list[dict]: List of output dictionaries, one per simulation step.
    """
    
    fem_path = motor.path + ".fem"
    ans_path = motor.path + ".ans"

    motor_circumference = motor.motorCircumference
    step_size = motor_circumference / num_samples

    profile = rotational_commutation(
        circumference=motor_circumference,
        num_pairs=motor.numberPoles // 2,
        currents_peak=motor.peakCurrents,
        number_samples=num_samples,
    )

    results = []

    for step in range(num_samples):
        position = step * step_size
        
        if status == True:
            print(f"Step {step + 1}/{num_samples} | Total displacement: {position:.4f}")

        femm.openfemm(1)
        femm.opendocument(fem_path)

        if step != 0:
            femm.mi_selectgroup(motor.movingGroup)
            motor.step(step_size)

        motor.set_currents(profile[step])

        femm.mi_analyse(1)
        femm.mi_loadsolution()

        step_context = dict(subjects)
        step_results = output_selector.compute(step_context)
        step_results["position"] = position
        results.append(step_results)

        if os.path.exists(ans_path):
            os.remove(ans_path)
        
        femm.closefemm()

    return results
