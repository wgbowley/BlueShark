"""
File: phase_shift.py
Author: William Bowley
Version: 1.4
Date: 2025-09-14
Description:
    Simple script to do analysis of
    a series of different RL circuits using
    FEM: Magnetic Renderer & Solver

    Independent:
        - Number of turns within the coil
        - In series resistor

    Dependent:
        - Phase shift

    Control:
        - 50 Hz : AC signal # Magnitude doesn't matter
        - Same core geometry
        - Assumed same coil geometry

    Assumptions:
        - Magnetic permeability of the core: u(x, y) = [100, 100]
        - Coil geometry is the same; Wire diameter changes.
"""

from math import sqrt, atan, pi, degrees

from blueshark.domain.material_manager.manager import MaterialManager
from blueshark.renderer.femm.magnetic.renderer import FEMMagneticRenderer
from blueshark.solver.femm.magnetic.solver import FEMMagneticSolver
from blueshark.simulate.static import static_simulation
from blueshark.domain.definitions import (
    Geometry, ShapeType, Units, CoordinateSystem, CircuitType,
    CurrentPolarity, BoundaryType
)


def wire_dia(area, fill, turns):
    """ Calculates the wire diameter needed to fill the coil"""
    return sqrt((area * fill) / turns)


# Parameters
frequency = 50
cross_area = 5 * 20
fill_factor = 0.9
series_resistors = [100, 200, 300, 310]
series_turns = [300, 600, 1200]
file_location = "examples/phase_shift_study/phase_shift.fem"


# Gets materials from static material manager
manager = MaterialManager()
copper = manager.use_material("Copper Wire", wire_diameter=0)
iron = manager.use_material("Pure Iron")
iron["magnetic"]["relative_permeability"] = [100, 100]
air = manager.use_material("Air")

# Defines the "u-core", coil and boundary geometry
domain: Geometry = {
    "shape": ShapeType.CIRCLE,
    "center": (115 / 2, 101 / 2),
    "radius": 200
}

inner_core: Geometry = {
    "shape": ShapeType.RECTANGLE, "enclosed": True,
    "points": [(15.0, 20.0), (15.0, 80), (100, 80), (100, 20.0)]
}

outer_core: Geometry = {
    "shape": ShapeType.RECTANGLE, "enclosed": True,
    "points": [(0, 0), (0, 100), (115, 100), (115, 0)]
}

positive: Geometry = {
    "shape": ShapeType.RECTANGLE, "enclosed": True,
    "points": [(77.5, 40), (77.5, 60), (85, 60), (85, 40)]
}

negative: Geometry = {
    "shape": ShapeType.RECTANGLE, "enclosed": True,
    "points": [(137.5, 40), (137.5, 60), (130, 60), (130, 40)]
}


# Draws the shapes to the renderer
for turns in series_turns:
    # Initializes renderer, defines problems and circuit
    renderer = FEMMagneticRenderer(file_location)
    renderer.setup(CoordinateSystem.PLANAR, Units.MILLIMETER, depth=20)
    renderer.create_circuit("circuit", CircuitType.SERIES, 1)

    renderer.draw(inner_core, air, 2)
    renderer.draw(outer_core, iron, 3, (5, 5))

    copper["physical"]["wire_diameter"] = wire_dia(cross_area, 0.8, turns)
    renderer.draw(
        positive, copper, 1,
        circuit="circuit",
        polarity=CurrentPolarity.FORWARD, turns=turns
    )

    renderer.draw(
        negative, copper, 1,
        circuit="circuit",
        polarity=CurrentPolarity.REVERSE, turns=turns
    )

    # Adds a neumann boundary condition
    renderer.draw_domain_boundary(domain, boundary_type=BoundaryType.NEUMANN)
    renderer.define_environment_region(-1, (132, 0), air)

    # Solves the magnetic problem and returns; all parameters from selector
    result = static_simulation(
        renderer, FEMMagneticSolver,
        ["circuit_inductance", "circuit_resistance"],
        [], "circuit"
    )

    res = result["circuit_resistance"]["circuit"]
    ind = result["circuit_inductance"]["circuit"]

    for R_series in series_resistors:
        r_total = R_series + res
        shift = atan((2*pi*frequency*ind) / r_total)
        msg = (
            f"R_series={R_series}, Turns={turns}, Phase shift={degrees(shift)}"
        )
        print(msg)
