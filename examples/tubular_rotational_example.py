"""
Filename: tubular_rotational_example.py
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

# Add project root to sys.path to enable imports
projectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if projectRoot not in sys.path:
    sys.path.insert(0, projectRoot)

# Framework imports
from core.simulation.output_selector import OutputSelector
from core.simulation.rotational_analysis import rotational_analysis
from core.outputs.json_exporter import save_json, flatten_results
from motors.tubular_motor import TubularMotor


# --- Configuration ---
numSamples = 100
motorConfigPath = "configs/tubular.yaml"
jsonFilename = "rotational_analysis_results.json"
requestedOutputs = ["lorentz_force"]

# --- Initialize and simulate ---
motor = TubularMotor(motorConfigPath)
motor.generate()
# motor.iForcePeak = 4.2
outputSelector = OutputSelector(requestedOutputs)
subjects = {"group": motor.movingGroup}

results = rotational_analysis(motor, outputSelector, subjects, numSamples)

# --- Save results ---
save_json(flatten_results(results), jsonFilename)


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
