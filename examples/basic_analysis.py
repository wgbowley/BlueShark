"""
Filename: basic_analysis.py
Author: William Bowley
Version: 1.1
Date: 2025-07-14

Description:
    Runs a rotational analysis on a tubular motor to find the
    mechanical position that optimizes force output in sync with
    the electrical cycle. Outputs results and plots Lorentz force vs displacement.
"""

import os
import sys
import matplotlib.pyplot as plt

# Dynamically apply project root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from blueshark.simulations.alignment import phase_alignment
from blueshark.simulations.rotational_analysis import rotational_analysis
from blueshark.output.selector import OutputSelector
from blueshark.output.writer import write_output_json
from models.basic_flat.motor import BasicFlat

# Simulation Parameters
alignment_samples = 20
rotational_samples = 100
motor_config = "models/basic_flat/motor.yaml"
output_file = "rotational_analysis_results.json"
requested_outputs = ["force_lorentz"]

motor = BasicFlat(motor_config)
motor.setup()

# Find phase offset to align magnetic flux for maximum force
phase_offset = phase_alignment(motor, alignment_samples)

# Processes the required outputs from user and the target for them 
output_selector = OutputSelector(requested_outputs)
subjects = {"group": motor.get_moving_group(), "phaseName": motor.phases}

# Simulate one mechanical cycle
results = rotational_analysis(motor, output_selector, subjects, rotational_samples, phase_offset)

# Logs simulation data
write_output_json(results, output_file)

# Splits raw results into displacement for x-axis and force for y-axis
positions = [res["displacement"] for res in results]
forces = [res["outputs"]["force_lorentz"][0] for res in results]

plt.figure(figsize=(8, 5))
plt.ylim(0, 1.1 * max(forces))
plt.plot(positions, forces, label="Lorentz Force")
plt.xlabel("Displacement (mm)")
plt.ylabel("Lorentz Force (N)")
plt.title("Force vs Displacement at Optimal Mechanical-Electrical Alignment")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
