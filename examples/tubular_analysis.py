"""
Filename: run_example.py
Author: William Bowley
Version: 1.0
Date: 2025-07-14

Description:
    Runs a rotational analysis on a tubular motor using a configuration file.
    Outputs selected results to JSON and plots Lorentz forces versus displacement.

Usage:
    Ensure FEMM and dependencies are installed. Modify requested outputs or
    motor configuration as needed. (config/tubular.yaml & motors/tubular_motor.py)
"""

import matplotlib.pyplot as plt

# Framework imports
from motors import TubularMotor
from outputs import OutputSelector, OutputWriter
from simulation import rotational_analysis

# --- Configuration ---
NUM_SAMPLES = 10000
MOTOR_CONFIG_PATH = "blueshark/motors/tubular/tubular.yaml"
REQUESTED_OUTPUTS = ["force_lorentz", "phase_voltage"]

# --- Initialize and simulate ---
motor = TubularMotor(MOTOR_CONFIG_PATH)
motor.generate()

output_selector = OutputSelector(REQUESTED_OUTPUTS)
subjects = {"group": motor.movingGroup, "phaseName": motor.phases}

results = rotational_analysis(motor, output_selector, subjects, NUM_SAMPLES)

# --- Save results ---
output_path = motor.femmdocumentpath
writer = OutputWriter(output_path)
writer.add(results)
writer.write_json()

# --- Plotting ---
positions = [result["position"] for result in results]
lorentz_forces = [result.get("lorentz_force", [0])[0] for result in results]

plt.figure(figsize=(8, 5))
plt.ylim(0, 1.1 * max(lorentz_forces))
plt.plot(positions, lorentz_forces, label="Lorentz Force", color="blue")
plt.xlabel("Displacement (mm)")
plt.ylabel("Force via Lorentz (N)")
plt.title("Tubular Motor Force vs Displacement @ 3A RMS")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
