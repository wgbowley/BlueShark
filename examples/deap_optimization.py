"""
Filename: deap_optimization.py
Author: William Bowley
Version: 1.0
Date: 2025-08-06

Description:
    Example of using the motor simulation framework with the
    DEAP evolutionary optimizer.

    Optimizes coil geometry (height and radius) for force output while
    considering power, voltage, and inductance constraints.
"""

import os
import sys
import random
from deap import base, creator, tools, algorithms

# Dynamically apply project root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blueshark.output.selector import OutputSelector
from models.cmore839.motor import CmoreTubular

from blueshark.simulations.rotational_analysis import rotational_analysis
from blueshark.simulations.alignment import phase_alignment
from blueshark.output.writer import write_output_json

# Optimization Setup
individuals = 50
generations = 20
weights = (1, 5, -1)  # Power, Force, Inductance
random.seed(42)  # Improves reproducibility

VOLTAGE_MAX = 56  # Max voltage (V)
POWER_MAX = 250  # Max average power (W)
INDUCTANCE_MAX = 0.05  # Max phase inductance (H)
UPPER_BOUND = 20
LOWER_BOUND = 0.2

# Motor configuration
ALIGNMENT_SAMPLES = 10
ROTATIONAL_SAMPLES = 10

motor_parameter_path = "models/cmore839/motor.yaml"
output_path = "models/cmore839/deap_optimization_results.json"

requested_outputs = [
    "force_lorentz",
    "phase_power",
    "phase_voltage",
    "phase_inductance"
]


def simulate(
    slot_thickness: float,
    slot_axial_length: float
) -> dict:
    """
    Runs a motor simulation with given slot thickness and axial length.
    """
    # 'CmoreTubular' Can be changed out for any motor in 'model'
    motor = CmoreTubular(motor_parameter_path)
    motor.slot_thickness = slot_thickness
    motor.slot_axial_length = slot_axial_length
    motor.setup()

    selector = OutputSelector(requested_outputs)
    subjects = {"group": motor.moving_group, "phaseName": motor.phases}

    # Find phase offset to align magnetic flux for maximum force
    phase_offset = phase_alignment(motor, ALIGNMENT_SAMPLES, False)

    # Simulate one mechanical cycle
    results = rotational_analysis(
        motor,
        selector,
        subjects,
        ROTATIONAL_SAMPLES,
        phase_offset,
        False
    )

    return results


def evaluate_motor(individual) -> tuple[float, float, float]:
    total_force = 0
    total_power = 0
    total_inductance = 0
    samples = 0

    results = simulate(individual[0], individual[1])
    print(
        f"Evaluating: height={individual[0]:.3f}, radius={individual[1]:.3f} "
    )

    for step in results:
        outputs = step.get("outputs")
        # Existence check
        if not outputs:
            continue

        # Range check (max voltage)
        voltages = outputs.get("phase_voltage")
        if voltages:
            for voltage in voltages:
                if abs(voltage) > VOLTAGE_MAX:
                    print(f"Design failed: Phase V {voltage} V exceeds limit")
                    return (0.0, 0.0, 0.0)

        force_values = outputs.get("force_lorentz")
        power_values = outputs.get("phase_power")
        inductance_values = outputs.get("phase_inductance")

        # Existence check
        if force_values is None or power_values is None:
            continue

        total_force += force_values[0]  # [Force, Angle]
        total_power += sum(power_values)
        total_inductance += sum(inductance_values)

        samples += 1

    if samples == 0:
        print("Design fail: No valid samples outputted")
        return (0.0, 0.0, 0.0)

    avg_force = total_force / samples
    avg_power = total_power / samples
    avg_inductance = total_inductance / samples

    # Range check  (max power)
    if avg_power > POWER_MAX:
        print(f"Design fail: Power {avg_power:.2f} W exceeds limit")
        return (0.0, 0.0, 0.0)

    # Range check  (max inductance)
    if avg_inductance > INDUCTANCE_MAX:
        print(f"Design fail: Inductance {avg_inductance:.2f} H exceeds limit")

    print(
        f"Average Force: {avg_force:.3f} "
        f"Average Power: {avg_power:.3f} "
        f"Average Inductance: {avg_inductance:.3f}"
    )

    return (avg_power, avg_force, avg_inductance)


# DEAP setup
creator.create("FitnessMulti", base.Fitness, weights=weights)
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()
toolbox.register(
    "input_thickness",
    random.uniform,
    LOWER_BOUND,
    UPPER_BOUND
)
toolbox.register(
    "input_length",
    random.uniform,
    LOWER_BOUND,
    UPPER_BOUND
)
toolbox.register(
    "individual",
    tools.initCycle,
    creator.Individual,
    (toolbox.input_thickness, toolbox.input_length),
    n=1
)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_motor)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register(
    "mutate",
    tools.mutPolynomialBounded,
    low=LOWER_BOUND,
    up=UPPER_BOUND,
    eta=20.0,
    indpb=0.2,
)
toolbox.register("select", tools.selTournament, tournsize=3)

# Optimization loop
population = toolbox.population(n=individuals)
crossoverPB = 0.7
mutationPB = 0.5

result_output = []

for generation in range(generations):
    offspring = algorithms.varAnd(
        population,
        toolbox,
        cxpb=crossoverPB,
        mutpb=mutationPB
    )

    # Clamp values to respect simulation bounds
    for ind in offspring:
        for i in range(len(ind)):
            ind[i] = min(UPPER_BOUND, max(LOWER_BOUND, ind[i]))

    fits = list(map(toolbox.evaluate, offspring))

    generation_data = {
        "generation": generation,
        "individuals": []
    }

    for fit, ind in zip(fits, offspring):
        ind.fitness.values = fit
        generation_data["individuals"].append({
            "Slot thickness": ind[0],
            "Slot axial length": ind[1],
            "fitness": {
                "average power": fit[0],
                "average force": fit[1],
                "average inductance": fit[2]
            }
        })

    result_output.append(generation_data)

    population = toolbox.select(offspring, len(population))
    best_individual = tools.selBest(population, 1)[0]
    print(
        f"Generation {generation}: Fitness = {best_individual.fitness.values}"
    )

# Save JSON Output
write_output_json(result_output, output_path)

# Final Best Solution
final_best = tools.selBest(population, 1)[0]
print(
    f"Best: thickness={final_best[0]:.2f}, "
    f"length={final_best[1]:.2f}, "
    f"fitness={final_best.fitness.values}"
)
