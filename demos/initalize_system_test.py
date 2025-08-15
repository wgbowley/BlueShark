"""
Initalize system test

- Will have to refactor the renderer
"""

from math import pi
from blueshark.domain.elements.pole import Pole
from blueshark.domain.elements.slot import Slot
from blueshark.domain.constants import (
    Geometry, ShapeType, SimulationType, Units, CurrentPolarity
)
from blueshark.renderer.femm.magnetic import renderer as Femmrenderer
from blueshark.addons.bldc.draw_stator import stator_geometries
from blueshark.addons.bldc.draw_armuture import (
 slot_geometry_rotated,
 coil_array
)

renderer = Femmrenderer.FEMMMagneticsRenderer("test.fem")
renderer.setup(
    SimulationType.PLANAR,
    Units.CENTIMETERS,
)


num_poles = 12
radius_inner = 12
radius_outer = 14
pole_length = 4
pole_height = 2

# this one doesn't use polar coords to do it (Uses inbuild shapes)
stator = stator_geometries(
    12,
    4,
    2,
    12,
    14
)

# this one does use polar coords to do it
armuture = slot_geometry_rotated(
    12,
    30,
    5,
    4,
    9,
    9.5
)

# this one does use polar coords to do it
coils = coil_array(
    12,
    30,
    5,
    0.25,
    4,
    6,
    8
)

renderer.draw(
    armuture,
    "Pure Iron",
    1,
    tag_coords=(2, 2)
)

axial: Geometry = {
    "shape": ShapeType.CIRCLE,
    "center": (0, 0),
    "radius": 2
}

renderer.draw(
    axial,
    "Air",
    0
)

renderer.draw(
    stator["back_iron"],
    "Pure Iron",
    1
)

for index in range(len(stator["poles"])):
    pole_angle = 360/num_poles
    arc_anlge = pole_length/(radius_inner-pole_height) * 180/pi

    angle_delta = ((pole_angle * index + arc_anlge) - pole_angle*index) % 360
    angle_bisector = ((pole_angle*index) + angle_delta / 2) % 360

    if index % 2:
        angle_bisector += 180

    renderer.draw(
        stator["poles"][index],
        "N52",
        2,
        magnetization=angle_bisector
    )

for coil in coils.values():
    element: Geometry = {
        "shape": ShapeType.POLYGON,
        "points": coil
    }

    renderer.draw(
        element,
        "0.315mm",
        3,
    )
