"""
Testing first renderer
"""

from blueshark.domain.elements.pole import Pole
from blueshark.domain.constants import (
    Geometry, ShapeType, SimulationType, Units
)
from blueshark.renderer.femm.magnetic import renderer as Femmrenderer

renderer = Femmrenderer.FEMMMagneticsRenderer("test.fem")
renderer.setup(
    SimulationType.PLANAR,
    Units.CENTIMETERS,
)

slot_geometry: Geometry = {
    "shape": ShapeType.ANNULUS_SECTOR,
    "center": (0, 0),
    "radius_inner": 8,
    "radius_outer": 10,
    "start_angle": 120,
    "end_angle": 280
}

pole_geometry: Geometry = {
    "shape": ShapeType.POLYGON,
    "points": [(10, 10), (0, 10), (-10, 0), (10, -10)]
}

first_pole = Pole(
    geometry=pole_geometry,
    material="",
    group_id=4,
    magnetization_angle=20
)

first_pole.draw(renderer)
