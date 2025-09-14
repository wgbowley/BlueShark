"""
File: magnetic_coil.py
Author: William Bowley
Version: 1.4
Date: 2025-09-14
Description:
    Simple script to do analysis of
    a solenoid coil in FEMM: Magnetic
"""

from blueshark.domain.material_manager.manager import MaterialManager
from blueshark.renderer.femm.magnetic.renderer import FEMMagneticRenderer
from blueshark.solver.femm.magnetic.solver import FEMMagneticSolver
from blueshark.simulate.static import static_simulation

from blueshark.domain.definitions import (
    Geometry, ShapeType, Units, CoordinateSystem, CircuitType,
    CurrentPolarity
)

# Gets materials from static material manager
manager = MaterialManager()
copper = manager.use_material("Copper Wire", wire_diameter=0.1)
iron = manager.use_material("Pure Iron")
air = manager.use_material("Air")

# Initializes renderer, defines problems and circuit
file_location = "examples/test.fem"
renderer = FEMMagneticRenderer(file_location)
renderer.setup(CoordinateSystem.PLANAR, Units.CENTIMETERS, depth=10)
renderer.create_circuit("phase_1", CircuitType.SERIES, 1)


core: Geometry = {
    "shape": ShapeType.RECTANGLE,
    "points": [(1, -2.5), (1, 2.5), (-1, 2.5), (-1, -2.5)],
    "enclosed": True
}

positive: Geometry = {
    "shape": ShapeType.RECTANGLE,
    "points": [(1, -2.5), (1, 2.5), (3.5, 2.5), (3.5, -2.5)],
    "enclosed": True
}

negative: Geometry = {
    "shape": ShapeType.RECTANGLE,
    "points": [(-1, -2.5), (-1, 2.5), (-3.5, 2.5), (-3.5, -2.5)],
    "enclosed": True
}

renderer.draw(core, iron, 2)

renderer.draw(
    positive, copper, 1,
    circuit="phase_1", polarity=CurrentPolarity.FORWARD, turns=100
)

renderer.draw(
    negative, copper, 1,
    circuit="phase_1", polarity=CurrentPolarity.REVERSE, turns=100
)

# Adds a neumann boundary condition
renderer.add_concentric_boundary((0, 0), 20, air)

# Solves the magnetic problem and returns
# all parameters from the output selector
result = static_simulation(renderer, FEMMagneticSolver, "all", 1, "phase_1")
print(result)
