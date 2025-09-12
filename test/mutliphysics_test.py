"""
Filename: multiphysics_test.py
Author: William Bowley
Version: 1.3
Date: 2025-08-16

Description:
    This project tests to see
    if blueshark can even renderer and
    solve a bldc motor from its addon
    "bldc"
"""

import math

from blueshark.domain.elements.pole import Pole
from blueshark.domain.elements.slot import Slot
from blueshark.renderer.femm.magnetic.renderer import (
    FEMMMagneticsRenderer as femmmagneticrenderer
)
from blueshark.solver.femm.magnetic.solver import (
    FEMMMagneticsSolver as femmmagneticsolver
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
from blueshark.renderer.femm.thermal.renderer import (
    FEMMthermalRenderer as femmheatrenderer
)
from blueshark.solver.femm.thermal.solver import (
    FEMMthermalSolver as femmheatsolver
)
from blueshark.renderer.material_manager import MaterialManager
from blueshark.addons.bldc.timelines import commutation_magnetic
from blueshark.addons.bldc.timelines import commutation_thermal
from blueshark.simulation.transient import transient_simulate

manager = MaterialManager()
wire = manager.use_material("Copper Wire", wire_diameter=0.35)
magnet = manager.use_material("Neodymium", grade="N52")
iron = manager.use_material("Pure Iron")
air = manager.use_material("Air")

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


def generate_geometry(
    renderer: femmmagneticrenderer | femmheatrenderer,
) -> None:
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
    renderer.draw(armuture, iron, 2, tag_coords=(r_axial, r_axial))
    renderer.draw(axial, air, 0)
    renderer.draw(stator["back_iron"], iron, 1)

    for pole in range(len(stator["poles"])):
        pole_angle = 360 / num_poles
        arc_angle = pole_length / (
            back_plate_inner_radius - pole_radial_thickness
        )

        deg_arc_angle = arc_angle * math.pi / 180
        delta = ((pole_angle * pole + deg_arc_angle) - pole_angle * pole) % 360
        angle_bisector = ((pole_angle*pole) + delta / 2) % 360

        if pole % 2:
            angle_bisector += 180

        element = Pole(
            stator["poles"][pole],
            magnet,
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

        # Use integer division to repeat each phase twice
        phase = phases[(idx // 2) % len(phases)]

        if idx % 2 == 0:
            polarity = CurrentPolarity.FORWARD
        else:
            polarity = CurrentPolarity.REVERSE

        element = Slot(
            phase,
            polarity,
            coil_geometry,
            wire,
            4,
            0.315
        )

        element.estimate_turns()
        element.draw(renderer)


def magnetic_sim():
    renderer = femmmagneticrenderer("test/test.fem")
    renderer.setup(
        SimulationType.PLANAR,
        Units.CENTIMETERS
    )
    generate_geometry(renderer)

    r_tag = (r_teeth+back_plate_inner_radius-pole_radial_thickness) / 2
    renderer.set_property([r_tag, 0], 10, air)

    timeline = commutation_magnetic(
        r_teeth,
        num_poles // 2,
        (5, 10),
        10,
        [4, 2, 9],
        ["phase_a", "phase_b", "phase_c"]
    )
    print(transient_simulate(
            PhysicsType.MAGNETIC,
            renderer,
            femmmagneticsolver,
            ["torque_lorentz"],
            {"group": 4},
            timeline
        )
    )


def thermal_sim():
    renderer = femmheatrenderer(
        "test/test.feh",
        SimulationType.PLANAR,
        (
            back_plate_outer_radius*3,
            back_plate_outer_radius*3
        ),
        air
    )
    renderer.setup(
        SimulationType.PLANAR,
        Units.CENTIMETERS
    )

    tag = (
        ((back_plate_inner_radius-pole_radial_thickness)+r_teeth)/2,
        0
    )

    generate_geometry(renderer)
    renderer.create_surface_condition("AIR", "convection", 0, 0, 300, 30)
    renderer.set_property(tag, 0, air)
    renderer.add_bounds((0, 0), back_plate_outer_radius*1.5, air)
    renderer.set_boundaries("AIR")

    timeline = commutation_thermal(
        Units.CENTIMETERS,
        r_teeth,
        num_poles // 2,
        (0, 3),
        2,
        5,
        10,
        [4, 2, 9],
        wire
    )

    print(
        transient_simulate(
            PhysicsType.THERMAL,
            renderer,
            femmheatsolver,
            ["average_temp"],
            {"group": 4},
            timeline
        )
    )


# magnetic_sim()
thermal_sim()
