"""
Filename: tubular_sim.py
Author: William Bowley
Version: 1.3
Date: 2025-09-12

Description:
    Magnetic and thermal simulation
    of a tubular linear motor.

    References:
    - Motor.yaml & basic_tubular_diagram.png
"""

import numpy as np
import matplotlib.pyplot as plot
import matplotlib.colors as colors

from blueshark.domain.constants import PhysicsType, SimulationType
from blueshark.addons.tubular.motor import Tubular
from blueshark.renderer.material_manager import MaterialManager
from blueshark.renderer.femm.magnetic.renderer import FEMMMagneticsRenderer
from blueshark.renderer.femm.thermal.renderer import FEMMthermalRenderer
from blueshark.solver.femm.magnetic.solver import FEMMMagneticsSolver
from blueshark.solver.femm.thermal.solver import FEMMthermalSolver
from blueshark.simulation.transient import transient_simulate
from blueshark.addons.tubular.timelines import (
    commutation_magnetic, commutation_thermal
)

file_location = "demos/tubular.fem"
parameter_location = "demos/motor.yaml"
renderer = FEMMMagneticsRenderer(file_location)
motor = Tubular(
    renderer,
    parameter_location
)

motor.setup()

timeline = commutation_magnetic(
    motor.circumference,
    motor.number_poles // 2,
    motor.peak_currents,
    1,
    motor.moving_group,
    motor.phases
)

results = transient_simulate(
    PhysicsType.MAGNETIC,
    renderer,
    FEMMMagneticsSolver,
    ["force_lorentz", "phase_voltage", "phase_current"],
    {"group": motor.group_slot, "phaseName": motor.phases},
    timeline
)
valid_resistances = []

# Iterate through each dictionary in the list
for data_point in results:
    phase_voltages = data_point.get('phase_voltage', [])
    phase_currents = data_point.get('phase_current', [])

    # Use zip to get pairs of voltage and current
    for voltage, current in zip(phase_voltages, phase_currents):
        if abs(current) > 1:
            try:
                resistance = voltage / current

                if abs(resistance) >= 0.1:
                    valid_resistances.append(resistance)
            except ZeroDivisionError:
                continue

if valid_resistances:
    average_resistance = sum(valid_resistances) / len(valid_resistances)


manager = MaterialManager()
air = manager.use_material("Air")
file_location2 = "demos/tubular.feh"
renderer = FEMMthermalRenderer(
    file_location2,
    SimulationType.AXI_SYMMETRIC,
    (50, 500),
    air,
    300
)

motor = Tubular(
    renderer,
    parameter_location
)

motor.setup()
renderer.create_surface_condition("AIR", "convection", 0, 0, 300, 25)
renderer.set_boundaries("AIR")

timeline = commutation_thermal(
    motor.units,
    motor.circumference,
    motor.number_poles // 2,
    motor.peak_currents,
    resistance,
    motor.slot_axial_length * motor.slot_thickness,
    10,
    motor.moving_group,
    motor.slot_material
)

print(
    transient_simulate(
        PhysicsType.THERMAL,
        renderer,
        FEMMthermalSolver,
        ["average_temp"],
        {"group": motor.moving_group},
        timeline
    )
)

num_materials = np.max(renderer.grid.voxel_map) + 1  # 0..N

hues = np.linspace(0, 1, num_materials, endpoint=False)  # evenly spaced hues
saturation = 0.8
value = 0.9
distinct_colors = np.array([plot.cm.hsv(h)[:3] for h in hues])  # RGB from HSV

cmap = colors.ListedColormap(distinct_colors)

plot.imshow(renderer.grid.voxel_map, origin='lower', cmap=cmap)
plot.title("Map")
plot.colorbar(label='Material')
plot.show()
