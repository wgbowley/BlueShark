"""
Filename: tubular_motor.py
Author: William Bowley
Version: 1.4
Date: 2025-09-15

Description:
    Run a rotational analysis on a tubular linear motor
    to find the force it produces vs displacement
"""

import matplotlib.pyplot as plt

from blueshark.models.tubular.motor import TubularLinearMotor
from blueshark.renderer.femm.magnetic.renderer import FEMMagneticRenderer
from blueshark.solver.femm.magnetic.solver import FEMMagneticSolver
from blueshark.simulate.quasi_transient import quasi_transient

# Motor parameter file and renderer file
param_path = "examples/tubular_motor_params.yaml"
file_path = "examples/tubular.fem"

renderer = FEMMagneticRenderer(file_path)
motor = TubularLinearMotor(
    renderer,
    param_path
)

# Setups simulation problem and defines the motor
motor.setup()

# Femm cannot automatically fill domain
tag = (100, 100)
renderer.define_environment_region(
    motor.BOUNDARY, tag, motor.boundary_material
)

results = quasi_transient(
    motor.renderer,
    FEMMagneticSolver,
    motor.timeline(number_samples=100),
    requested_outputs=["force_lorentz"],
    elements=motor.SLOT_ID,
    circuits=motor.phases,
    status=True
)

force_magnitudes = [frame['force_lorentz'][1][0] for frame in results]
displacement = [f * motor.step_size for f in range(len(force_magnitudes))]

if not force_magnitudes:
    raise RuntimeError("No force results returned from simulation")

# Plot
plt.figure(figsize=(8, 5))
plt.plot(displacement, force_magnitudes)
plt.xlabel(f"Displacement [{motor.units}]")
plt.ylim(0, 1.1 * max(force_magnitudes))
plt.ylabel("Lorentz Force [N]")
plt.title("Lorentz Force vs Displacement")
plt.grid(True)
plt.tight_layout()
plt.show()
