"""
Filename: force_random_search.py
Author: William Bowley
Version: 1.0
Date: 2025-07-17

Description:
    Performs a simple random search optimization to maximize average Lorentz force
    in a tubular linear motor using the modular FEMM simulation framework.

    Demonstrates a basic optimization strategy without external dependencies.
    Serves as a starting example before moving to more advanced optimization methods.
"""

# --- Imports and setup ---
import random
import os
import sys

# Add project root to sys.path for importing framework modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from outputs.output_selector import OutputSelector
from simulation.rotational_analysis import rotational_analysis
from motors import TubularMotor

# --- Helper functions ---
def random_value() -> float:
    """
    Generates a random float between -1 and 1.
    Used to randomly perturb motor geometry parameters.
    """
    return random.random() * 2 - 1


def generate_geometry(step_size: float, coil_height: float, coil_radius: float) -> tuple[float, float]:
    """
    Randomly perturbs coil height and radius within +/- step_size.

    Returns:
        tuple: New (height, radius) values, always positive.
    """
    height = abs(coil_height + step_size * random_value())
    radius = abs(coil_radius + step_size * random_value())
    return height, radius


# --- Optimization parameters ---
simulation_num = 100         # Max number of random samples
step_size = 10               # Initial perturbation step
min_step_size = 0.315        # Stop if step falls below this
stall_max = 10               # Max iterations with no improvement
stall = 0                    # Consecutive non-improvements
power_limit = 200            # Reject candidates above this power

# Track best result
best_force = 0
best_height = 0
best_radius = 0

# Motor config and outputs
motor_config_path = "data/tublar/tubular.yaml"
requested_outputs = ["lorentz_force", "circuit_power"]
num_samples = 10

# Store results (for optional plotting later)
optimization_results = []

# --- Optimization loop ---
for index in range(simulation_num):
    motor = TubularMotor(motor_config_path)

    # Perturb current geometry
    coil_height = motor.slot_height
    coil_radius = motor.slot_radius
    height, radius = generate_geometry(step_size, coil_height, coil_radius)

    motor.slot_height = height
    motor.slot_radius = radius
    motor.generate()

    output_selector = OutputSelector(requested_outputs)
    subjects = {"group": motor.movingGroup, "circuitName": motor.phases}
    results = rotational_analysis(motor, output_selector, subjects, num_samples)

    # Compute average force and power
    total_force = sum(step["lorentz_force"][0] for step in results)
    total_power = sum(sum(step["circuit_power"]) for step in results)
    count = len(results)

    avg_force = total_force / count
    avg_power = total_power / count

    # Apply power constraint
    if avg_power > power_limit:
        print(f"Iteration {index}: Rejected (Power = {avg_power:.2f} W > limit {power_limit} W)")
        stall += 1

    # Accept if better
    elif avg_force > best_force:
        best_force = avg_force
        best_height = height
        best_radius = radius
        stall = 0
        print(f"Iteration {index}: New best! Force = {best_force:.3f} N, Power = {avg_power:.2f} W")

    else:
        stall += 1
        print(f"Iteration {index}: No improvement. Stall count = {stall}")

    # Handle stagnation
    if stall >= stall_max:
        step_size /= 2
        stall = 0
        print(f"Step size reduced to {step_size:.3f} due to stagnation.")

    # Stop condition
    if step_size < min_step_size:
        print("Minimum step size reached. Ending optimization.")
        break

# --- Final Result ---
print("\nBest geometry found:")
print(f"Coil radius:  {best_radius:.3f}")
print(f"Coil height:  {best_height:.3f}")
print(f"Average force: {best_force:.3f} N")
