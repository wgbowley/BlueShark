"""
Filename: force_random_search.py
Author: William Bowley
Version: 1.1
Date: 2025-07-17

Description:
    Performs a simple random search optimization to maximize average Lorentz force
    in a tubular linear motor using the modular FEMM simulation framework.

    Demonstrates a basic optimization strategy without external dependencies.
    Serves as a starting example before moving to more advanced optimization methods.
"""

# --- Imports and setup ---
import os
import random
import sys

# Applies project root directory dynamically 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from blueshark.output.selector import OutputSelector
from blueshark.simulations.rotational_analysis import rotational_analysis
from models.basic_tubular.motor import BasicTubular


# --- Helper functions ---
def random_value():
    """
    Generate a random float between -1 and 1.
    Used to randomly perturb motor geometry parameters.
    """
    return random.random() * 2 - 1


def generate_geometry(step_size: float, slot_height: float, slot_radius: float) -> tuple[float, float]:
    """
    Generate a new coil height and radius by randomly perturbing
    the current values within +/- step_size.
    Ensures values are positive using abs().
    """
    height = abs(slot_height + step_size * random_value())
    radius = abs(slot_radius + step_size * random_value())
    return height, radius


# --- Optimization parameters ---
SIMULATION_NUM = 10000         # Max number of random samples to evaluate
STEP_SIZE = 20                 # Initial step size for parameter perturbation
MIN_STEP_SIZE = 0.315          # Minimum step size (convergence criterion)
STALL_MAX = 300                # Max iterations without improvement before reducing step size

POWER_LIMIT = 200             # Max allowable power to filter invalid designs

# Variables to track best found geometry
best_force = 0.0
best_height = 0.0
best_radius = 0.0
stall = 0  # Counter for iterations without improvement

# Motor config and requested outputs
motor_config_path = "models/basic_tubular/motor.yaml"
requested_outputs = ["force_lorentz", "phase_power"]
samples = 10                  # Number of simulation steps per evaluation
phase_offset = 2.073451       # Phase offset for the specific basic tubular

# Store all evaluated results for analysis or plotting
optimization_results = []

# --- Main optimization loop ---
for index in range(SIMULATION_NUM):
    motor = BasicTubular(motor_config_path)
    coil_height = motor.slot_height
    coil_radius = motor.slot_radius

    height, radius = generate_geometry(STEP_SIZE, coil_height, coil_radius)

    motor.slot_height = height
    motor.slot_radius = radius

    motor.setup()
    output_selector = OutputSelector(requested_outputs)
    subjects = {"group": motor.get_moving_group(), "phaseName": motor.phases}

    results = rotational_analysis(motor, output_selector, subjects, samples, phase_offset, False) 

    total_force = 0.0
    total_power = 0.0
    count = 0

    for step in results:
        outputs = step["outputs"]

        if outputs is None:
            print("Warning: Missing outputs for a simulation step, skipping")
            continue  
        
        force_vals = outputs.get("force_lorentz")
        power_vals = outputs.get("phase_power")

        if force_vals is None or power_vals is None:
            print("Warning: Missing required output keys, skipping step")
            continue

        total_force += force_vals[0]
        total_power += sum(power_vals)
        count += 1

    if count > 0:
        avg_force = total_force / count
        avg_power = total_power / count
    else:
        avg_force = 0
        avg_power = 0
        print("Warning: No valid simulation steps found")

    if avg_power > POWER_LIMIT:
        print(
            f"Iteration {index}: Rejected candidate "
            f"(power {avg_power:.2f} W > limit {POWER_LIMIT} W)"
        )
        stall += 1
    elif avg_force > best_force:
        best_force = avg_force
        best_height = height
        best_radius = radius
        stall = 0
        print(
            f"Iteration {index}: New best candidate! "
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

print(f"Best geometry found after {index + 1} iterations:")
print(f"Coil radius: {best_radius}")
print(f"Coil height: {best_height}")
print(f"Average force: {best_force}")
