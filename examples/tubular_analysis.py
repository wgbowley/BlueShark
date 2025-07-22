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
    motor configuration as needed. 
    
    (data/tubular/tubular.yml & blueshark/motors/tubular/tubular.py)
"""

import matplotlib.pyplot as plt

# Framework imports
from motors import TubularMotor
from outputs import OutputSelector, output_writers
from simulation import rotational_analysis

# --- Configuration ---
NUM_SAMPLES = 50
MOTOR_CONFIG_PATH = "data/tubular/tubular.yaml"
REQUESTED_OUTPUTS = ["force_lorentz", "phase_voltage"]

# --- Initialize and simulate ---
motor = TubularMotor(MOTOR_CONFIG_PATH)
motor.generate()

output_selector = OutputSelector(REQUESTED_OUTPUTS)
subjects = {"group": motor.movingGroup, "phaseName": motor.phases}

results = rotational_analysis(motor, output_selector, subjects, NUM_SAMPLES)

# --- Save results ---
output_path = motor.path
output_writers.write_json(results, motor.path)

# --- Plotting ---
positions = []
lorentz_forces = []
for result in results: 
    positions.append(result["position"])
    lorentz_forces.append(result.get("force_lorentz", [0])[0])

# --- Graphing --- 
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
