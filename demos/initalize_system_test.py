"""
Initalize system test
"""

from math import pi
from blueshark.domain.elements.pole import Pole
from blueshark.domain.elements.slot import Slot
from blueshark.domain.constants import (
    Geometry, ShapeType, SimulationType, Units, CurrentPolarity
)
from blueshark.renderer.femm.magnetic import renderer as Femmrenderer
from blueshark.solver.femm.magnetic import solver as Femmsolver
from blueshark.addons.draw_bldc import stator_geometries

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
stator = stator_geometries(
    number_poles=num_poles,
    pole_height=pole_height,
    pole_length=pole_length,
    radius_inner=radius_inner,
    radius_outer=radius_outer
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
