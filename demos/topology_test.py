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
from blueshark.addons.topology.smoothing import (
    order_points, simplify_points
)
from blueshark.addons.topology.renderer import TopologyRenderer
from blueshark.domain.constants import (
    SimulationType, Geometry, ShapeType, Units
)
from blueshark.addons.bldc.draw_armuture import (
    slot_geometry_rotated,
    coil_array
)
from blueshark.addons.bldc.draw_stator import (
    stator_geometries
)
from blueshark.renderer.femm.heat.renderer import (
    FEMMHeatflowRenderer as Femmrenderer
)

materials = {
    "Air": 0,
    # Coils 0→11
    "Coil0": 1, "Coil1": 2, "Coil2": 3, "Coil3": 4,
    "Coil4": 5, "Coil5": 6, "Coil6": 7, "Coil7": 8,
    "Coil8": 9, "Coil9": 10, "Coil10": 11, "Coil11": 12,
    # Stator
    "Stator": 13,
    "Pole": 14,
    "Backplate": 15,
    "Axial": 16
}

renderer = TopologyRenderer(1000, 1000, materials, SimulationType.PLANAR)
renderer.initalize_map("Air")

SCALE_FACTOR = 16

num_poles = 16
back_plate_outer_radius = 20 * SCALE_FACTOR
back_plate_inner_radius = 19 * SCALE_FACTOR
pole_length = 5 * SCALE_FACTOR
pole_radial_thickness = 2 * SCALE_FACTOR

num_slots = 12
sector_angle = 360 / num_slots
spacing_angle = 10
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
    "radius": r_axial
}

# # Draws objects to simulation space
renderer.draw(armuture, "Stator", tag_coords=(r_axial, r_axial))
renderer.draw(axial, "Axial")
renderer.draw(stator["back_iron"], "Backplate")

for pole in range(len(stator["poles"])):
    renderer.draw(stator["poles"][pole], "Pole")

for key in sorted(coils.keys()):
    coil_num = (key - 1) // 2
    slot = {
        "shape": ShapeType.POLYGON,
        "points": coils[key]
    }
    renderer.draw(slot, f"Coil{coil_num}")


for _ in range(0, 10):
    renderer.boundary_mutation("Stator", 0.01, 0.2)

max_radius = 20
min_dis = 5

stator_points = renderer._find_boundaries(13)
stator_points = order_points(stator_points, 20)
stator_points = simplify_points(stator_points, 4)

frender = Femmrenderer("test.feh")

frender.setup(
    SimulationType.PLANAR,
    Units.CENTIMETERS
)

test: Geometry = {
    "shape": ShapeType.POLYGON,
    "points": stator_points
}

for key in sorted(coils.keys()):
    coil_num = (key - 1) // 2
    material = materials[f"Coil{coil_num}"]
    points = renderer._find_boundaries(material)
    points = order_points(points, 20)
    points = simplify_points(points, 4)
    coil: Geometry = {
        "shape": ShapeType.POLYGON,
        "points": points
    }
    frender.draw(coil, "Air", 1)

frender.draw(test, "Air", 1)
plt.imshow(renderer.topology_map, origin='lower', cmap='tab20')
plt.title("Topology Map")
plt.colorbar(label='Material')
plt.show()
