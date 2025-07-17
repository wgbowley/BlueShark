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
projectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if projectRoot not in sys.path:
    sys.path.insert(0, projectRoot)

from core.simulation.output_selector import OutputSelector
from core.simulation.rotational_analysis import rotational_analysis
from motors.tubular.tubular_motor import TubularMotor

# --- Helper function ---
def random_value():
    """
    Generates a random float between -1 and 1.
    Used to randomly perturb motor geometry parameters.
    """
    return random.random() * 2 - 1

def generate_geometry(stepSize: float, coilHeight: float, coilRadius: float) -> tuple[float, float]:
    """
    Generates a new coil height and radius by randomly perturbing
    the current values within +/- stepSize.
    Ensures values are positive using abs().
    """
    
    height = abs(coilHeight + stepSize * random_value())
    radius = abs(coilRadius + stepSize * random_value())
    
    return height, radius

# --- Optimization parameters ---
simulationNum = 100          # Max number of random samples to evaluate
stepSize = 10                # Initial step size for parameter perturbation
minStepSize = 0.315          # Minimum step size (convergence criterion)
stallMax = 10                # Max iterations without improvement before reducing step size
stall = 0                    # Counter for iterations without improvement

powerLimit = 200             # Max allowable power to filter invalid designs

# Variables to track best found geometry
bestForce = 0
bestHeight = 0
bestRadius = 0

# Motor config and requested outputs
motorConfigPath = "motors/tubular/tubular.yaml"
requestedOutputs = ["lorentz_force", "circuit_power"]
samples = 10                 # Number of simulation steps per evaluation

# Store all evaluated results for analysis or plotting
optimization_results = []

# --- Main optimization loop ---
for index in range(simulationNum):
    motor = TubularMotor(motorConfigPath)
    coilHeight = motor.coilHeight
    coilRadius = motor.coilRadius

    height, radius = generate_geometry(stepSize, coilHeight, coilRadius)

    motor.coilHeight = height
    motor.coilRadius = radius

    motor.generate()
    outputSelector = OutputSelector(requestedOutputs)
    subjects = {"group": motor.movingGroup, "circuitName": motor.phases}

    results = rotational_analysis(motor, outputSelector, subjects, samples)

    totalForce = 0
    totalPower = 0
    count = 0
    for step in results:
        totalForce += step['lorentz_force'][0]
        totalPower += sum(step['circuit_power'])
        count += 1

    avgForce = totalForce / count
    avgPower = totalPower / count

    if avgPower > powerLimit:
        print(f"Iteration {index}: Rejected candidate (power {avgPower:.2f} W > limit {powerLimit} W)")
        stall += 1  
        
    elif avgForce > bestForce:
        bestForce = avgForce
        bestHeight = height
        bestRadius = radius
        stall = 0
        print(f"Iteration {index}: New best candidate! Force={bestForce:.3f} N, Power={avgPower:.2f} W")
    else:
        stall += 1
        print(f"Iteration {index}: No improvement. Stall count: {stall}")

    if stall >= stallMax:
        stepSize /= 2
        stall = 0
        print(f"Step size reduced to {stepSize} due to stagnation.")
    
    if stepSize < minStepSize:
        print("Minimum step size reached. Ending optimization.")
        break

print(f"Best geometry found after {index+1} iterations:")
print(f"Coil radius: {bestRadius}")
print(f"Coil height: {bestHeight}")
print(f"Average force: {bestForce}")

