"""
Filename: force_random_search.py
Author: William Bowley
Version: 1.1
Date: 2025-07-17

Description:
    Performs a simple random search optimization to maximize average
    Lorentz force in a tubular linear motor using the simulation framework.

    This script only supports motors that expose `slot_thickness` and
    `slot_axial_length` attributes directly—such as
    'basic_tubular' or the 'CmoreTubular' model.

    Demonstrates a basic optimization strategy without external dependencies.
    Serves as a starting example before moving to more advanced methods.
"""

import os
import random
import sys

# Dynamically apply project root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blueshark.output.selector import OutputSelector
from blueshark.output.writer import write_output_json
from blueshark.simulations.rotational_analysis import rotational_analysis
from blueshark.simulations.alignment import phase_alignment
from models.cmore839.motor import CmoreTubular


def random_value() -> float:
    """
    Generates a random value in the range [-1, 1].
    """
    return random.random() * 2 - 1


def generate_geometry(
    step: float,
    length: float,
    thickness: float
) -> tuple[float, float]:
    """
    Applies a small random step variation to the length and thickness,
    ensuring both remain positive.

    Args:
        step: The maximum variation to apply.
        length: Original slot axial length.
        thickness: Original slot thickness.

    Returns:
        Tuple of (new_length, new_thickness)
    """
    gen_length = abs(length + step * random_value())
    gen_thickness = abs(thickness + step * random_value())
    return gen_length, gen_thickness


# Optimization Constants
ITERATION_NUMBER = 1000
STEP_SIZE = 20             # +/- range for slot dimension mutation
MIN_STEP_SIZE = 0.315      # Minimum step size before stopping
STALL_MAX = 50             # Max iterations with no improvement -> Halving step

POWER_MAX = 250            # Max average power (W)

# Optimization State
stall = 0
best_force = 0.0
best_axial_length = 0.0
best_thickness = 0.0

# Simulation Parameters
ALIGNMENT_SAMPLES = 10
ROTATIONAL_SAMPLES = 10

motor_parameter_path = "models/cmore839/motor.yaml"
requested_outputs = ["force_lorentz", "phase_power"]
output_path = "models/cmore839/force_random_search_results.json"

optimization_results = []

# Main Optimization Loop
for index in range(ITERATION_NUMBER):
    motor = CmoreTubular(motor_parameter_path)

    # Retrieve current parameters
    thickness = motor.slot_thickness
    axial_length = motor.slot_axial_length

    # Mutate slot dimensions
    axial_length, thickness = generate_geometry(
        STEP_SIZE,
        axial_length,
        thickness
    )

    # Initialize run log
    test_log = {
        "iteration": index,
        "slot_thickness": thickness,
        "slot_axial_length": axial_length,
        "status": "started",
    }

    optimization_results.append(test_log)
    write_output_json(optimization_results, output_path, False)

    try:
        # Sets parameters to the mutate ones
        motor.slot_thickness = thickness
        motor.slot_axial_length = axial_length
        motor.setup()

        output_selector = OutputSelector(requested_outputs)
        subjects = {"group": motor.moving_group, "phaseName": motor.phases}

        # Aligns stator and armature to maximize force output
        phase_offset = phase_alignment(motor, ALIGNMENT_SAMPLES, False)

        # Simulate one mechanical cycle
        results = rotational_analysis(
            motor,
            output_selector,
            subjects,
            ROTATIONAL_SAMPLES,
            phase_offset,
            False
        )

        total_force = 0.0
        total_power = 0.0
        count = 0

        for step in results:
            outputs = step["outputs"]
            if not outputs:
                continue
            force_vals = outputs.get("force_lorentz")
            power_vals = outputs.get("phase_power")
            if force_vals is None or power_vals is None:
                continue
            total_force += force_vals[0]
            total_power += sum(power_vals)
            count += 1

        avg_force = total_force / count if count else 0.0
        avg_power = total_power / count if count else 0.0

        # Update and log results
        optimization_results[-1].update({
            "avg_force": avg_force,
            "avg_power": avg_power,
            "accepted": avg_power <= POWER_MAX,
            "status": "completed",
        })
        write_output_json(optimization_results, output_path, False)

        # Decision logic
        if avg_power > POWER_MAX:
            print(f"Iter {index}: Power {avg_power:.2f} W exceeds limit")
            stall += 1
        elif avg_force > best_force:
            best_force = avg_force
            best_thickness = thickness
            best_axial_length = axial_length
            stall = 0
            print(
                f"Iteration {index}: New best! "
                f"Force={best_force:.3f} N, Power={avg_power:.2f} W"
            )
        else:
            stall += 1
            print(f"Iteration {index}: No improvement. Stall count: {stall}")

        if stall >= STALL_MAX:
            STEP_SIZE /= 2
            stall = 0
            print(f"Step size reduced to {STEP_SIZE} due to stagnation.")

        if STEP_SIZE < MIN_STEP_SIZE:
            print("Minimum step size reached. Ending optimization.")
            break

    except Exception as e:
        optimization_results[-1].update({"status": "crashed", "error": str(e)})
        write_output_json(optimization_results, output_path, False)
        print(f"Iteration {index}: Crashed with error: {e}")
        break

# Final Report
print(f"Best geometry found after {index + 1} iterations:")
print(f"Slot thickness: {best_thickness}")
print(f"Slot axial length: {best_axial_length}")
print(f"Average force: {best_force}")
