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

from blueshark.addons.bldc.draw_armuture import (
    slot_geometry_rotated,
)

materials = {
    "Air": 0,
    "Copper": 1,
    "Neodymium": 2,
    "Pure Iron": 3
}

renderer = TopologyRenderer(500, 500, materials)
renderer.initalize_map("Air")

SCALE_FACTOR = 10

num_slots = 12
sector_angle = 360 / num_slots
spacing_angle = 5*SCALE_FACTOR
r_start = 5*SCALE_FACTOR
r_slot = 15*SCALE_FACTOR
r_teeth = 16*SCALE_FACTOR

armuture = slot_geometry_rotated(
    num_slots,
    sector_angle,
    spacing_angle,
    r_start,
    r_slot,
    r_teeth
)

renderer.draw(armuture, "Pure Iron")

plt.imshow(renderer.topology_map, origin='lower', cmap='tab20')
plt.title("Topology Map")
plt.colorbar(label='Material')
plt.show()
