"""
Filename: simulate.py
Author: William Bowley
Version: 1.3
Date: 2025-09-12

Description:
    Magnetic simulation of a tubular linear motor
    using models/tubular

    References:
    - Motor.yaml & basic_tubular_diagram.png
"""

import matplotlib.pyplot as plt

from blueshark.models.tubular.motor import TubularLinearMotor
from blueshark.renderer.femm.magnetic.renderer import FEMMagneticRenderer
from blueshark.solver.femm.magnetic.solver import FEMMagneticSolver
from blueshark.simulate.quasi_transient import quasi_transient

# Motor parameter file and renderer file
param_path = "examples/tubular/motor.yaml"
file_path = "examples/tubular/tubular.fem"

renderer = FEMMagneticRenderer(file_path)
motor = TubularLinearMotor(
    renderer,
    param_path
)

# Setups simulation problem and defines the motor
motor.setup()
renderer.add_concentric_boundary(
    (0, 0),
    300,
    motor.manager.use_material("Air")
)

timeline = motor.timeline(number_samples=100)
print(timeline)

results = quasi_transient(
    motor.renderer, FEMMagneticSolver, timeline,
    requested_outputs=[
        "force_lorentz",
        "circuit_voltage",
        "circuit_inductance"
    ],
    elements=motor.SLOT_ID, circuits=motor.phases,
    status=True
)

force_magnitudes = [frame['force_lorentz'][1][0] for frame in results]
frames = list(range(len(force_magnitudes)))

# Plot
plt.figure(figsize=(8, 5))
plt.plot(frames, force_magnitudes, marker='o', linestyle='-')
plt.xlabel("Frame")
plt.ylabel("Lorentz Force [N]")
plt.title("Lorentz Force vs Frame")
plt.grid(True)
plt.tight_layout()
plt.show()