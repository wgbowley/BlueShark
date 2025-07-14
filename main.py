"""
Filename: main.py
Author: William Bowley
Version: 1.0
Date: 2025-07-14
"""


import matplotlib.pyplot as plt

from core.simulation.output_selector import OutputSelector
from core.simulation.rotational_analysis import rotational_analysis
from motors.tubular_motor import TubularMotor


motorConfigPath = "configs/tubular.yaml"
requestedOutputs = ["lorentz_force", "force_via_stress_tensor", "circuit_analysis"]  
numSamples = 10000

# Set up motor
motor = TubularMotor(motorConfigPath)
motor.draw()

# Output Selector
outputSelector = OutputSelector(requestedOutputs)

# Output context
baseContext = {
    "group": motor.movingGroup,         
    "circuitName": motor.phases         
}

# --- Run Rotation Analysis ---
results = rotational_analysis(
    motor=motor,
    outputSelector=outputSelector,
    baseContext=baseContext,
    numSamples=numSamples
)

# Map position to force (assumes "position" and "lorentz_force" exist in results)
positions = [result["position"] for result in results]

lorentz_forces = [result.get("lorentz_force", [0])[0] for result in results]
stress_tensor_forces = [result.get("force_via_stress_tensor", [0])[0] for result in results]

plt.plot(positions, lorentz_forces, color='b', label="Lorentz Force")
plt.plot(positions, stress_tensor_forces, color='r', label="Stress Tensor Force")

plt.xlabel("Displacement (mm)")
plt.ylabel("Force (N)")
plt.title("Tubular Motor Force vs Displacement @ 3A RMS")
plt.legend()
plt.grid(True)
plt.show()
