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

import os
import sys
import matplotlib.pyplot as plt


# Framework imports
from core.simulation.output_selector import OutputSelector
from core.simulation.rotational_analysis import rotational_analysis
from core.outputs.output_writer import *
from motors.tubular.tubular_motor import TubularMotor


# --- Configuration ---
numSamples = 1
motorConfigPath = "data/flat/flat.yaml"
outputPath = "rotational_analysis_results"
requestedOutputs = ["lorentz_force", "circuit_voltage"]

# --- Initialize and simulate ---
motor = TubularMotor(motorConfigPath)
motor.generate()

outputSelector = OutputSelector(requestedOutputs)
subjects = {"group": motor.movingGroup, "circuitName": motor.phases}

results = rotational_analysis(motor, outputSelector, subjects, numSamples)
print(results)

# --- Save results ---
save = OutputWriter(outputPath)
save.add(results)
save.write_json()


# --- Plotting ---
positions = [result["position"] for result in results]
lorentzForces = [result.get("lorentz_force", [0])[0] for result in results]

plt.figure(figsize=(8, 5))
plt.ylim(0, 1.1 * max(lorentzForces))
plt.plot(positions, lorentzForces, label="Lorentz Force", color='blue')
plt.xlabel("Displacement (mm)")
plt.ylabel("Force via Lorentz (N)")
plt.title("Tubular Motor Force vs Displacement @ 3A RMS")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
