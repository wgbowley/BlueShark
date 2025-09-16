
"""
File: simple_coilgun.py
Author: William Bowley
Version: 1.4
Date: 2025-09-16
Description:
    Simple script to do analysis of
    a battery powered coil gun in FEMM: Magnetic

    Uses mm-g-s Units:
        - Millimeter, gram, second, ampere
"""

import matplotlib.pyplot as plt

from math import ceil, exp, radians, sin, pi

from blueshark.domain.material_manager.manager import MaterialManager
from blueshark.renderer.femm.magnetic.renderer import FEMMagneticRenderer
from blueshark.solver.femm.magnetic.solver import FEMMagneticSolver
from blueshark.simulate.static import static_simulation
from blueshark.domain.constants import EPSILON
from blueshark.domain.definitions import (
    Geometry, ShapeType, Units, CoordinateSystem, CircuitType,
    CurrentPolarity, BoundaryType
)


# Simulation Parameters
voltage = 8     # Volts
test_current = 0.001  # very small to start loop
fluid_density = 1.225  # kg/m^3
coefficient_drag = 0.82  # dimensionless
file_location = "examples/coilgun.fem"
time_step = 5e-4    # Seconds

# Coil Parameters (mm)
coil_length = 50
coil_inner_radi = 6.25
coil_outer_radi = 17.5
wire_dia = 1.25

# Projectile Parameters (mm)
projectile_radi = 4
projectile_length = 50
projectile_mass = 20  # grams


def turns(length, inner, outer, wire_dia, factor):
    """ Calculates the number of turns within section of the coil"""
    slot_area = length * (outer - inner)
    wire_area = wire_dia ** 2
    effective = slot_area * factor

    return ceil(effective / wire_area)


def projectile_drag(density, velocity, coefficient, radius):
    """
    Calculates the drag force.
    Inputs are in mm-g-s units; output is in Newtons (N).
    """
    # Convert inputs to SI units for calculation
    v_m_s = velocity * 1e-3  # mm/s -> m/s
    r_m = radius * 1e-3      # mm -> m
    area = pi * r_m**2       # m^2

    # Air density is in kg/m^3
    drag_force = 0.5 * density * v_m_s * abs(v_m_s) * area * coefficient
    return drag_force   # Force in Newtons (N)


def inst_current_charge(time, inductance, resistance, voltage):
    """Calculates the current during charging in an RL circuit"""
    if abs(inductance) < EPSILON or abs(resistance) < EPSILON:
        return 0.0

    tau = inductance / resistance
    max_i = voltage / resistance

    return max_i * (1 - exp((-time) / tau))


def inst_current_discharge(
    time, time_offset, initial_current, resistance, inductance
):
    """Calculates the current during discharging an RL circuit"""
    if abs(inductance) < EPSILON or abs(resistance) < EPSILON:
        return 0.0
    tau = inductance / resistance

    return initial_current * exp(-(time - time_offset) / tau)


# Gets materials from static material manager
manager = MaterialManager()
air = manager.use_material("Air")
copper = manager.use_material("Copper Wire", wire_diameter=wire_dia)

# Haven't implemented soft iron in blueshark library yet
iron = manager.use_material("Pure Iron")
iron["magnetic"]["relative_permeability"] = [1000, 1000]

renderer = FEMMagneticRenderer(file_location)
renderer.setup(CoordinateSystem.AXI_SYMMETRIC, Units.MILLIMETER)
renderer.create_circuit("coil", CircuitType.SERIES, test_current)

domain: Geometry = {
    "shape": ShapeType.CIRCLE, "center": (0, 0),
    "radius": projectile_length * 4
}

coil: Geometry = {
    "shape": ShapeType.RECTANGLE,
    "enclosed": True,
    "points": [
        (coil_inner_radi, 0),
        (coil_outer_radi, 0),
        (coil_outer_radi, coil_length),
        (coil_inner_radi, coil_length)
    ]
}

projectile: Geometry = {
    "shape": ShapeType.RECTANGLE,
    "enclosed": True,
    "points": [
        (0, -projectile_length),
        (projectile_radi, -projectile_length),
        (projectile_radi, 0),
        (0, 0)
    ]
}


# Draws the shapes
renderer.draw(projectile, iron, 2)

turn = turns(coil_length, coil_inner_radi, coil_outer_radi, wire_dia, 0.8)
renderer.draw(
    coil, copper, 1, circuit="coil",
    polarity=CurrentPolarity.FORWARD,
    turns=turn
)


renderer.draw_domain_boundary(domain, boundary_type=BoundaryType.NEUMANN)
renderer.define_environment_region(-1, (50, 0), air)

# Loop Vars
time = 0.0
time_offset = 0.0
position = 0.0
current = 0.0
velocity = 0.0
last_force = 0.0
switch_off = False

time_series = []
velocity_series = []
while position < 2 * coil_length:
    print(f"Projectile Path {position} : {2*coil_length}")
    time += time_step

    result = static_simulation(
        renderer, FEMMagneticSolver,
        ["circuit_inductance", "circuit_resistance"],
        circuits="coil"
    )

    inductance = result['circuit_inductance']['coil']
    resistance = result['circuit_resistance']['coil']

    if switch_off:
        i = inst_current_discharge(
            time, time_offset, current, resistance, inductance
        )
    else:
        i = inst_current_charge(time, inductance, resistance, voltage)
        current = i
        time_offset = time
    renderer.change_circuit_current("coil", i)

    result = static_simulation(
        renderer,
        FEMMagneticSolver,
        ["force_stress_tensor"], elements=2
    )

    f, theta = result["force_stress_tensor"][2]
    axial_force = f * sin(radians(theta))     # Axial force in Newtons

    # Drag force in Newtons
    drag_force = projectile_drag(
        fluid_density, velocity, coefficient_drag, projectile_radi
    )

    net_force_mm_g_s = (axial_force - drag_force) * 1e6
    acceleration = net_force_mm_g_s / projectile_mass

    # Update velocity and position in mm and mm/s
    velocity += acceleration * time_step
    dx = velocity * time_step
    position += dx

    renderer.move_element(2, dx, (pi / 2, 0, 0))

    # Switching mechanism
    if not switch_off:
        if axial_force < last_force and last_force > 0:
            switch_off = True
    last_force = axial_force

    # Saving results for output
    time_series.append(time)
    velocity_series.append(velocity)

# Plot
plt.figure(figsize=(8, 5))
plt.plot(time_series, velocity_series)
plt.xlabel("time (s)")
plt.ylim(0, 1.1 * max(velocity_series))
plt.ylabel("velocity (mm/s)")
plt.title("velocity vs time")
plt.grid(True)
plt.tight_layout()
plt.show()
