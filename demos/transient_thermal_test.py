"""
Filename: transient_thermal_test.py
Author: William Bowley
Version: 1.3
Date: 2025-08-16

Description:
    This project tests to see
    if blueshark can even heat flow renderer
    and solve a bldc motor from its addon "bldc"
"""
import numpy as np
import matplotlib.pyplot as plot
import matplotlib.colors as colors

import math

from blueshark.domain.elements.pole import Pole
from blueshark.domain.elements.slot import Slot
from blueshark.renderer.femm.thermal.renderer import (
    FEMMHeatflowRenderer as Femmrenderer
)
from blueshark.solver.femm.thermal.solver import (
    FEMMHeatSolver as Femmsolver
)
from blueshark.domain.constants import (
    Geometry, ShapeType, SimulationType, Units, CurrentPolarity,
    PhysicsType
)

from blueshark.addons.bldc.draw_stator import stator_geometries
from blueshark.addons.bldc.draw_armature import (
    slot_geometry_rotated,
    coil_array
)
from blueshark.addons.bldc.timelines import commutation_thermal
from blueshark.simulation.transient import transient_simulate
phases = ["phase_a", "phase_b", "phase_c"]

num_poles = 16
back_plate_outer_radius = 20
back_plate_inner_radius = 19
pole_length = 5
pole_radial_thickness = 2

num_slots = 12
sector_angle = 360 / num_slots
spacing_angle = 5
r_start = 5
r_slot = 15
r_teeth = 16


coil_height = 0.65
r_coilS = 7
r_coilE = 14
r_axial = 3


# Sets the renderer to femm magnetics
renderer = Femmrenderer(
    "test.feh",
    (
        back_plate_outer_radius*3,
        back_plate_outer_radius*3
    ),
    "Air"
)
renderer.setup(
    SimulationType.PLANAR,
    Units.CENTIMETERS,
)
renderer.create_surface_condition("AIR", "convection", 0, 0, 300, 25)

# Stator geometry (doesn't use polar coords as inbuild shapes)
stator = stator_geometries(
    num_poles,
    pole_length,
    pole_radial_thickness,
    back_plate_inner_radius,
    back_plate_outer_radius
)

# Armuture geometry (Uses polar coords)
armuture = slot_geometry_rotated(
    num_slots,
    sector_angle,
    spacing_angle,
    r_start,
    r_slot,
    r_teeth
)

# Coil geometry (Uses polar coords)
coils = coil_array(
    num_slots,
    sector_angle,
    spacing_angle,
    coil_height,
    r_start,
    r_coilS,
    r_coilE
)

axial: Geometry = {
    "shape": ShapeType.CIRCLE,
    "center": (0, 0),
    "radius": r_axial
}

# Draws objects to simulation space
renderer.draw(armuture, "Iron, Pure", 2, tag_coords=(r_axial, r_axial))
renderer.draw(axial, "Air", 0)
renderer.draw(stator["back_iron"], "Iron, Pure", 1)

for pole in range(len(stator["poles"])):
    pole_angle = 360 / num_poles
    arc_angle = pole_length / (back_plate_inner_radius - pole_radial_thickness)

    deg_arc_angle = arc_angle * math.pi / 180
    delta = ((pole_angle * pole + deg_arc_angle) - pole_angle * pole) % 360
    angle_bisector = ((pole_angle*pole) + delta / 2) % 360

    if pole % 2:
        angle_bisector += 180

    element = Pole(
        stator["poles"][pole],
        "Nickel, Pure",
        3,
        0
    )
    element.draw(renderer)

for idx, coil in enumerate(coils.values()):
    coil_geometry: Geometry = {
        "shape": ShapeType.POLYGON,
        "points": coil,
        "enclosed": True
    }
    phase = phases[idx % len(phases)]

    if idx % 2 == 0:
        polarity = CurrentPolarity.FORWARD
    else:
        polarity = CurrentPolarity.REVERSE

    element = Slot(
        phase,
        polarity,
        coil_geometry,
        "Copper, Pure",
        4,
        0.315
    )

    element.estimate_turns()
    element.draw(renderer)

tag = (
    ((back_plate_inner_radius-pole_radial_thickness)+r_teeth)/2,
    0
)
renderer.set_property(tag, 0)
renderer.add_bounds((0, 0), back_plate_outer_radius*1.5)
renderer.set_boundaries("AIR")

timeline = commutation_thermal(
    r_teeth,
    num_poles // 2,
    (0, 3),
    2,
    10,
    [4, 2, 9],
    ["phase_a", "phase_b", "phase_c"]
)

print(transient_simulate(
        PhysicsType.THERMAL,
        renderer,
        Femmsolver,
        ["average_temp"],
        {"group": 4},
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
