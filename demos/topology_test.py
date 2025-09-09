"""
Filename: Topology_test.py
Author: William Bowley
Version: 0.2
Data: 2025-08-29

Description:
    This demo tests to see if the topology
    optimizer addon works to optimize a bldc
    motor using the femm magnetic solver.
th
Note:
    Somewhat works very very slow ~3m 30s to run
"""

import numpy as np
import matplotlib.pyplot as plot
import matplotlib.colors as colors

# Topology renderer -> Voxel setup, draw and mutation
from blueshark.addons.topology.renderer import TopologyRenderer
from blueshark.addons.topology.extraction import (
    _materials_boundaries,
    _material_perimeters,
)
from blueshark.addons.topology.interfaces import (
    interfaced_geometry
)
# Femm Renderer -> Draw, set properties, phases
from blueshark.renderer.femm.magnetic.renderer import FEMMMagneticsRenderer

# Domain Items
from blueshark.domain.constants import (
    SimulationType, Geometry, ShapeType, Units
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
    "Coil": 5,
    "Pole": 6,
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
    slot = {
        "shape": ShapeType.POLYGON,
        "points": coils[key],
        "enclosed": True
    }
    topology_renderer.draw(slot, "Coil")

# Drawing poles to voxel grid
for pole in range(len(stator["poles"])):
    topology_renderer.draw(stator["poles"][pole], "Pole")

num_materials = np.max(topology_renderer.voxel_map) + 1  # 0..N

for i in range(0, 5):
    topology_renderer.mutation("Coil", 0.1)

boundaries = _materials_boundaries(topology_renderer)
par1 = _material_perimeters(boundaries["Armature"])
par2 = _material_perimeters(boundaries["Coil"], 5)
par3 = _material_perimeters(boundaries["Backplate"])
par4 = _material_perimeters(boundaries["Pole"])

femm_renderer = FEMMMagneticsRenderer("test.fem")
femm_renderer.setup(
    SimulationType.PLANAR,
    Units.CENTIMETERS,
    40
)

for i in par1:
    armuture: Geometry = {
        "shape": ShapeType.POLYGON,
        "points": i,
        "enclosed": True
    }
    femm_renderer.draw(armuture, "Pure Iron", 2, (0, 0))

for i in par2:
    points = interfaced_geometry(i, par1[0])
    coil: Geometry = {
        "shape": ShapeType.POLYGON,
        "points": points,
        "enclosed": False
    }
    femm_renderer.draw(coil, "0.2mm", 2)

for i in par3:
    armuture: Geometry = {
        "shape": ShapeType.POLYGON,
        "points": i,
        "enclosed": True
    }
    femm_renderer.draw(armuture, "Pure Iron", 2, (0, 0))

for i in par4:
    points = interfaced_geometry(i, par3[1])
    coil: Geometry = {
        "shape": ShapeType.POLYGON,
        "points": points,
        "enclosed": False
    }
    femm_renderer.draw(coil, "N52", 2)


hues = np.linspace(0, 1, num_materials, endpoint=False)  # evenly spaced hues
saturation = 0.8
value = 0.9
distinct_colors = np.array([plot.cm.hsv(h)[:3] for h in hues])  # RGB from HSV

cmap = colors.ListedColormap(distinct_colors)

plot.imshow(topology_renderer.voxel_map, origin='lower', cmap=cmap)
plot.title("Topology Map")
plot.colorbar(label='Material')
plot.show()
