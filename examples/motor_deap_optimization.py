"""
Filename: motor_deap_optimization.py
Author: William Bowley
Version: 1.0
Date: 2025-07-17

Description:
    Example of using the motor simulation framework with the DEAP evolutionary optimizer.
    Optimizes coil geometry (height and radius) for force output while considering
    power, voltage, and inductance constraints.
"""

# === Standard libraries ===
import os
import sys
import random
import json
from deap import base, creator, tools, algorithms

# === Add project root to sys.path for framework imports ===
projectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if projectRoot not in sys.path:
    sys.path.insert(0, projectRoot)

# === Framework imports ===
from core.simulation.output_selector import OutputSelector
from core.simulation.rotational_analysis import rotational_analysis
from motors.tubular.tubular_motor import TubularMotor

# === Optimization Setup ===
individuals = 20
generations = 20

maxPower = 250
maxInductance = 0.1
maxVoltage = 56
maxCoilHeight = 7.5
maxCoilRadius = 7.5

# === Simulation Configuration ===
numberSamples = 10
motorConfigPath = "data/tublar/tubular.yaml"
requestedOutputs = ["lorentz_force", "circuit_power", "circuit_voltage", "circuit_inductance"]

# === Input Generation ===
def input_generation(lowerBound: float, upperBound: float) -> float:
    """Generates a random float within bounds."""
    return random.uniform(lowerBound, upperBound)

# === Simulation Runner ===
def simulate(radius, height) -> dict:
    """Runs a motor simulation with given coil radius and height."""
    motor = TubularMotor(motorConfigPath)
    motor.coilRadius = abs(radius)
    motor.coilHeight = abs(height)
    motor.generate()

    selector = OutputSelector(requestedOutputs)
    subjects = {"group": motor.movingGroup, "circuitName": motor.phases}
    results = rotational_analysis(motor, selector, subjects, numberSamples)
    return results

# === Evaluation Function ===
def evaluateMotor(individual):
    total_force = 0
    total_power = 0
    total_inductance = 0
    samples = 0

    results = simulate(individual[0], individual[1])
    print(f"Evaluating individual: height={individual[0]:.3f}, radius={individual[1]:.3f}")
    print("Simulation first step sample:", results[0])

    for step in results:
        print("Voltages:", step["circuit_voltage"])
        for phaseVoltage in step["circuit_voltage"]:
            if abs(phaseVoltage) > maxVoltage:
                print('failed voltage:', phaseVoltage)
                return (0.0, 0.0, 0.0)

        total_force += step['lorentz_force'][0]
        total_power += sum(step['circuit_power'])
        total_inductance += sum(step["circuit_inductance"])
        samples += 1

    avg_force = total_force / samples
    avg_power = total_power / samples
    avg_inductance = total_inductance / samples

    print(f"Avg Power: {avg_power}, Avg Force: {avg_force}, Avg Inductance: {avg_inductance}")

    if avg_power >= maxPower or avg_inductance > maxInductance:
        print('failed power or inductance constraints')
        return (0.0, 0.0, 0.0)

    return (avg_power, avg_force, avg_inductance)


# === DEAP Setup ===
creator.create("FitnessMulti", base.Fitness, weights=(-1, 4.0, -1))
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()
toolbox.register("inputHeight", input_generation, 0.35, maxCoilHeight)
toolbox.register("inputRadius", input_generation, 0.35, maxCoilRadius)
toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.inputHeight, toolbox.inputRadius), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluateMotor)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1.0, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# === Main Optimization Loop ===
population = toolbox.population(n=individuals)
crossoverPB = 0.7
mutationPB = 0.5

output_data = []  # To save all results

for generation in range(generations):
    offspring = algorithms.varAnd(population, toolbox, cxpb=crossoverPB, mutpb=mutationPB)
    fits = list(map(toolbox.evaluate, offspring))

    generation_data = {
        "generation": generation,
        "individuals": []
    }

    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
        generation_data["individuals"].append({
            "coil_height": ind[0],
            "coil_radius": ind[1],
            "fitness": {
                "avg_power": fit[0],
                "avg_force": fit[1],
                "avg_inductance": fit[2]
            }
        })

    output_data.append(generation_data)

    population = toolbox.select(offspring, len(population))
    best_individual = tools.selBest(population, 1)[0]
    print(f"Generation {generation}: Fitness = {best_individual.fitness.values}")

# === Save JSON Output ===
with open("deap_optimization_results.json", "w") as f:
    json.dump(output_data, f, indent=2)

# === Final Best Solution ===
final_best = tools.selBest(population, 1)[0]
print("\nBest Individual Found:")
print(f"  Coil Height: {final_best[0]:.3f}")
print(f"  Coil Radius: {final_best[1]:.3f}")
print(f"  Fitness (Power, Force, Inductance): {final_best.fitness.values}")
