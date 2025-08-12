from blueshark.domain.elements.pole import Pole
from blueshark.domain.constants import (
    Geometry, ShapeType, SimulationType, Units
)
from blueshark.renderer.femm.magnetic import renderer as Femmrenderer

renderer = Femmrenderer.FEMMMagneticsRenderer()
renderer.setup(
    SimulationType.PLANAR,
    Units.CENTIMETERS,
    "test.fem"
)

pole_geometry: Geometry = {
    "shape": ShapeType.CIRCLE,
    "center": (0, 0),
    "radius": 10
} 

first_pole = Pole(
    geometry=pole_geometry,
    material="",
    group_id=1,
    magnetization_angle=100
)

first_pole.draw(renderer)