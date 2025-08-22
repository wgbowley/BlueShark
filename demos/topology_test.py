"""
Filename: topology_test.py
Author: William Bowley
Version: 1.3
Date: 2025-08-16

Description:
    This demo tests to see if the topology addon
    ever works to add simple geometries
"""
import matplotlib.pyplot as plt

from blueshark.addons.topology.renderer import TopologyRenderer
from blueshark.domain.constants import SimulationType, Geometry, ShapeType
from blueshark.addons.bldc.draw_armuture import (
    slot_geometry_rotated,
    coil_array
)
from blueshark.addons.bldc.draw_stator import (
    stator_geometries
)

materials = {
    "Air": 0,
    "Copper": 1,
    "Neodymium": 2,
    "Pure Iron": 3
}

renderer = TopologyRenderer(1000, 1000, materials, SimulationType.PLANAR)
renderer.initalize_map("Air")

SCALE_FACTOR = 10

num_poles = 16
back_plate_outer_radius = 20 * SCALE_FACTOR
back_plate_inner_radius = 19 * SCALE_FACTOR
pole_length = 5 * SCALE_FACTOR
pole_radial_thickness = 2 * SCALE_FACTOR

num_slots = 12
sector_angle = 360 / num_slots
spacing_angle = 5
r_start = 5 * SCALE_FACTOR
r_slot = 15 * SCALE_FACTOR
r_teeth = 16 * SCALE_FACTOR

coil_height = 0.65 * SCALE_FACTOR
r_coilS = 7 * SCALE_FACTOR
r_coilE = 14 * SCALE_FACTOR
r_axial = 3 * SCALE_FACTOR


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
    "radius": r_axial * SCALE_FACTOR
}

# Draws objects to simulation space
renderer.draw(armuture, "Pure Iron", tag_coords=(r_axial, r_axial))
renderer.draw(axial, "Air")
renderer.draw(stator["back_iron"], "Pure Iron")

for pole in range(len(stator["poles"])):
    renderer.draw(stator["poles"][pole], "Neodymium")

for idx, coil in enumerate(coils.values()):
    coil_geometry: Geometry = {
        "shape": ShapeType.POLYGON,
        "points": coil
    }
    renderer.draw(coil_geometry, "Copper")


plt.imshow(renderer.topology_map, origin='lower', cmap='tab20')
plt.title("Topology Map")
plt.colorbar(label='Material')
plt.show()
