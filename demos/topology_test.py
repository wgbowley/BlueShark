"""
Filename: Topology_test.py
Author: William Bowley
Version: 0.2
Data: 2025-08-29

Description:
    This demo tests to see if the topology
    optimizer addon works to optimize a bldc
    motor using the femm magnetic solver.
"""

import numpy as np
import matplotlib.pyplot as plot
import matplotlib.colors as colors

# Topology renderer -> Voxel setup, draw and mutation
from blueshark.addons.topology.renderer import TopologyRenderer

# Femm Renderer -> Draw, set properties, phases
from blueshark.renderer.femm.magnetic.renderer import FEMMMagneticsRenderer

# Extraction of data from voxel topology map
from blueshark.addons.topology.extraction import (
    order_points,
    order_remaining_points,
    smooth_points,
    simplify_points
)

# Interfaces between extraction geometry
from blueshark.addons.topology.interfaces import (
    interfaced_geometry,
)

# Domain Items
from blueshark.domain.constants import (
    SimulationType, Geometry, ShapeType, Units
)
from blueshark.domain.generation.geometric_centroid import (
    _polygon
)

# Bldc Motor addons
from blueshark.addons.bldc.draw_armature import (
    slot_geometry_rotated, coil_array
)
from blueshark.addons.bldc.draw_stator import (
    stator_geometries
)

topology_materials = {
    "Air": 0,
    "Armature": 2,
    "Backplate": 1,
    "Axial": 4,
    **{f"Coil{i}": i + 1 + 4 for i in range(24)},  # Coils 0→23
    **{f"Pole{i}": i + 1 + 24 for i in range(16)},   # Poles 24->40
}

POLY_NUM = 6

topology_renderer = TopologyRenderer(
    1000,
    1000,
    topology_materials,
    SimulationType.PLANAR
)
topology_renderer.initalize_map("Air")

SCALE_FACTOR = 16

# Pole & Stator Geometry
num_poles = 16
back_plate_outer_radius = 20 * SCALE_FACTOR
back_plate_inner_radius = 19 * SCALE_FACTOR
pole_length = 5 * SCALE_FACTOR
pole_radial_thickness = 2 * SCALE_FACTOR

# Coil & Armature Geometry
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

# Stator Geometry -> Cartesian Coordinate System
stator = stator_geometries(
    num_poles,
    pole_length,
    pole_radial_thickness,
    back_plate_inner_radius,
    back_plate_outer_radius
)

# Armature Geometry -> Polar Coordinate System
Armature = slot_geometry_rotated(
    num_slots,
    sector_angle,
    spacing_angle,
    r_start,
    r_slot,
    r_teeth
)

# Coil array geometry -> Polar Coordinate System
coils = coil_array(
    num_slots,
    sector_angle,
    spacing_angle,
    coil_height,
    r_start+1.5,
    r_coilS,
    r_coilE
)

# Topology Rendering

axial: Geometry = {
    "shape": ShapeType.CIRCLE,
    "center": (0, 0),
    "radius": r_axial
}

topology_renderer.draw(Armature, "Armature", tag_coords=(r_axial, r_axial))
topology_renderer.draw(axial, "Axial")
topology_renderer.draw(stator["back_iron"], "Backplate")

# Drawing Coils to voxel grid
for key in sorted(coils.keys()):
    coil_num = (key - 1)
    slot = {
        "shape": ShapeType.POLYGON,
        "points": coils[key]
    }
    topology_renderer.draw(slot, f"Coil{coil_num}")

# Drawing poles to voxel grid
for pole in range(len(stator["poles"])):
    topology_renderer.draw(stator["poles"][pole], f"Pole{pole}")

num_materials = np.max(topology_renderer.voxel_map) + 1  # 0..N


# Femm Renderer
femm_renderer = FEMMMagneticsRenderer("test.femm")
femm_renderer.setup(
    SimulationType.PLANAR,
    Units.CENTIMETERS,
    40
)

blackplate = topology_renderer._find_boundaries(
    topology_materials["Backplate"]
)
inner_backplate = order_points(blackplate, 10)
outer_backplate = order_remaining_points(blackplate, inner_backplate, 10)

inner: Geometry = {
    "shape": ShapeType.POLYGON,
    "points": simplify_points(smooth_points(inner_backplate, 5), POLY_NUM),
    "enclosed": True,
}

outer: Geometry = {
    "shape": ShapeType.POLYGON,
    "points": simplify_points(smooth_points(outer_backplate, 5), POLY_NUM),
    "enclosed": True,
}


Armature = topology_renderer._find_boundaries(
    topology_materials["Armature"]
)

armature = order_points(Armature, 10)
axial = order_remaining_points(Armature, armature, 20)
arm: Geometry = {
    "shape": ShapeType.POLYGON,
    "points": simplify_points(smooth_points(armature, 5), POLY_NUM),
    "enclosed": True,
}

axial: Geometry = {
    "shape": ShapeType.POLYGON,
    "points": simplify_points(smooth_points(axial, 5), POLY_NUM),
    "enclosed": True,
}


femm_renderer.draw(inner, "Pure Iron", 1)
femm_renderer.draw(outer, "Pure Iron", 1)
femm_renderer.draw(axial, "Air", 2)
femm_renderer.draw(arm, "Pure Iron", 2)


for key in sorted(coils.keys()):
    coil_num = (key - 1)
    material = topology_materials[f"Coil{coil_num}"]
    points = topology_renderer._find_boundaries(material)
    points = simplify_points(points, 10)
    points = interfaced_geometry(points, arm["points"], POLY_NUM)
    # print(key)
    coil: Geometry = {
        "shape": ShapeType.POLYGON,
        "points": points,
        "enclosed": False
    }
    femm_renderer.draw(coil, "0.2mm", 2, (0, 0))


# for key in range(len(stator["poles"])):
#     material = topology_materials[f"Pole{key}"]
#     points = topology_renderer._find_boundaries(material)
#     points = simplify_points(points, 10)
#     points = interfaced_geometry(points, inner["points"], POLY_NUM)
#     # print(key)
#     pole: Geometry = {
#         "shape": ShapeType.POLYGON,
#         "points": points,
#         "enclosed": False
#     }
#     femm_renderer.draw(pole, "N52", 2, (0, 0))


# Generate distinct colors in HSV space
hues = np.linspace(0, 1, num_materials, endpoint=False)  # evenly spaced hues
saturation = 0.8
value = 0.9
distinct_colors = np.array([plot.cm.hsv(h)[:3] for h in hues])  # RGB from HSV

cmap = colors.ListedColormap(distinct_colors)

plot.imshow(topology_renderer.voxel_map, origin='lower', cmap=cmap)
plot.title("Topology Map")
plot.colorbar(label='Material')
plot.show()
