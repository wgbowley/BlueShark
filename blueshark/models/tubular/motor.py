"""
File: motor.py
Author: William Bowley
Version: 1.2
Date: 2025-09-15

Description:
    Basic model of a tubular linear motor for use in
    the simulation framework.

    Parameters are defined within the motor.yaml file
"""

import logging

from yaml import safe_load, YAMLError
from pathlib import Path
from blueshark.models.tubular.utils import require
from blueshark.domain.constants import PI
from blueshark.models.tubular.physics.number_types import estimate_turns
from blueshark.renderer.renderer_interface import MagneticRenderer
from blueshark.domain.material_manager.manager import MaterialManager
from blueshark.models.tubular.physics.commutation import commutation
from blueshark.simulate.quasi_transient import (
    Frame, LinearMotion, Currents
)
from blueshark.domain.definitions import (
    CoordinateSystem,
    Units,
    Geometry,
    ShapeType,
    CircuitType,
    CurrentPolarity
)


class TubularLinearMotor:
    """
    Generic model of a tubular linear motor
    """
    SLOT_ID = 1
    POLE_ID = 2
    TUBE_ID = 3

    def __init__(
        self,
        renderer: MagneticRenderer,
        parameter_file: Path
    ) -> None:
        self.renderer = renderer
        self.manager = MaterialManager()
        self.type = CoordinateSystem.AXI_SYMMETRIC
        self.units = Units.MILLIMETER

        # Motor parameters
        self.parameter_path = Path(parameter_file)
        self.phases = ["a", "b", "c"]

        # Load parameters, materials, compute geometry
        self._unpack(self.parameter_path)
        self._load_material()
        self._compute_geometry()

        # Choose physics strategy based on renderer type
        if isinstance(renderer, MagneticRenderer):
            self.physics_impl = MagneticPhysics(self)
        else:
            raise TypeError(f"Unsupported renderer type: {type(renderer)}")

    def setup(self):
        """
        Setup renderer problem, draw motor and sets its properties.
        """
        # Setup renderer
        self.renderer.setup(self.type, self.units)
        # Delegate to physics-specific implementation
        self.physics_impl.setup()

    def timeline(
        self,
        number_samples: int,
    ):
        """"
        quasi_transient timeline for the motor
        """
        return self.physics_impl.timeline(number_samples)

    def _rectangle_geometry(
        self,
        bottom_left: tuple[float, float],
        width: float,
        height: float
    ) -> Geometry:
        """
        Returns a rectangular geometry dictionary from bottom-left vertex.
        """
        x, y = bottom_left
        return {
            "shape": ShapeType.RECTANGLE,
            "points": [
                (x, y),
                (x + width, y),
                (x + width, y + height),
                (x, y + height)
            ],
            "enclosed": True
        }

    def _compute_geometry(self) -> None:
        """
        Computes key geometric parameters including slot pitch,
        motor circumference, and pole pitch.
        """
        self.slot_pitch = self.slot_axial_length + self.slot_axial_spacing
        self.circumference = self.slot_pitch * self.number_slots
        self.pole_pitch = self.circumference / self.number_poles

        if self.pole_pitch != self.pole_axial_length:
            self.pole_axial_length = self.pole_pitch
            logging.warning(f"Pole pitch adjusted to {self.pole_pitch:.3f} mm")

        self.total_number_poles = 4 * self.extra_pairs + self.number_poles

    def _load_material(self) -> None:
        """
        Loads materials into class variables.
        """
        self.slot_material = self.manager.use_material(
            self.slot_material, wire_diameter=self.slot_wire_diameter
        )
        self.tube_material = self.manager.use_material(
            self.tube_material
        )
        self.pole_material = self.manager.use_material(
            self.pole_material, grade=self.pole_grade
        )

    def _unpack(self, param_file: Path) -> None:
        """
        Loads parameters from a YAML file into class variables.
        """
        if not param_file.exists():
            msg = f"Parameter file '{param_file}' was not found."
            raise FileNotFoundError(msg)
        if param_file.suffix.lower() != ".yaml":
            msg = f"File '{param_file}' must have a '.yaml' extension."
            raise ValueError(msg)

        try:
            with open(param_file, "r", encoding="utf-8") as file:
                parameters = safe_load(file)
        except YAMLError as e:
            msg = f"Failed to parse YAML file '{param_file}': {e}"
            raise ValueError(msg) from e

        for section in ["model", "slot", "pole", "tube", "output"]:
            if section not in parameters:
                msg = f"Missing required key '{section}' in {param_file}"

                raise KeyError(msg)

        model, slot, pole, tube, output = (
            parameters["model"], parameters["slot"], parameters["pole"],
            parameters["tube"], parameters["output"]
        )

        # Model parameters
        self.number_slots = require("number_slots", model)
        self.number_poles = require("number_poles", model)
        self.extra_pairs = require("extra_pairs", model)
        self.d_currents = require("d_currents", model)
        self.q_currents = require("q_currents", model)
        self.fill_factor = require("fill_factor", model)

        # Slot parameters
        self.slot_inner_radius = require("inner_radius", slot)
        self.slot_outer_radius = require("outer_radius", slot)
        self.slot_axial_length = require("axial_length", slot)
        self.slot_axial_spacing = require("axial_spacing", slot)
        self.slot_material = require("material", slot)
        self.slot_wire_diameter = require("wire_diameter", slot)

        # Pole parameters
        self.pole_outer_radius = require("outer_radius", pole)
        self.pole_axial_length = require("axial_length", pole)
        self.pole_material = require("material", pole)
        self.pole_grade = require("grade", pole)

        # Tube parameters
        self.tube_inner_radius = require("inner_radius", tube)
        self.tube_outer_radius = require("outer_radius", tube)
        self.tube_material = require("material", tube)

        # Compute thicknesses
        self.slot_thickness = self.slot_outer_radius - self.slot_inner_radius
        self.tube_thickness = self.tube_outer_radius - self.tube_inner_radius
        self.pole_thickness = self.pole_outer_radius

        # Output
        self.folder_path = require("folder_path", output)
        self.file_name = require("file_name", output)


# Physics specific implementations
class MagneticPhysics:
    """
    Magnetic implementation of the tubular linear motor
    """
    def __init__(self, motor: TubularLinearMotor):
        self.motor = motor
        self.renderer = motor.renderer

    def setup(self):
        """
        Called by TubularLinearMotor.setup()
        """
        self._create_circuits()
        self._add_stator()
        self._add_armature()

    def timeline(
        self,
        number_samples: int,
        phase_offset: float = 0.0
    ):
        """"
        quasi_transient timeline for the motor magnetic
        """
        step_size, current_profile = commutation(
            self.motor.circumference,
            self.motor.number_poles // 2,
            (self.motor.d_currents, self.motor.q_currents),
            number_samples,
            phase_offset
        )

        motion = LinearMotion(
            step_size,
            (PI / 2, 0, 0)
        )

        timeline = []
        for profile in current_profile:
            currents = Currents(
                profile,
                self.motor.phases
            )

            frame = Frame(
                elements=self.motor.SLOT_ID
            )

            frame.motion = motion
            frame.currents = currents

            timeline.append(frame)

        return timeline

    def _add_armature(self) -> None:
        """
        Adds the armature to the simulation space.
        This includes the alternating polarity slot with pattern
        """

        # Calculates the slot origins (bottom-left vertex)
        z = -self.motor.slot_pitch
        slot_origins = []
        for slot in range(self.motor.number_slots):
            # Each slot has spacing except every third one
            if slot % 3 != 0:
                z += (
                    self.motor.slot_axial_length +
                    self.motor.slot_axial_spacing
                )
            else:
                z += self.motor.slot_axial_length

            r = self.motor.slot_inner_radius
            slot_origins.append((r, z))

        # Calculates turns within the slot cross section
        number_turns = estimate_turns(
            self.motor.slot_thickness,
            self.motor.slot_axial_length,
            self.motor.slot_wire_diameter,
            self.motor.fill_factor
        )

        for index, origin in enumerate(slot_origins):
            # Sets phase of slot in pattern [a,b,c]
            phase = self.motor.phases[index % len(self.motor.phases)]

            # Alternate polarity slot with pattern
            if index % 2 == 0:
                polarity = CurrentPolarity.FORWARD
            else:
                polarity = CurrentPolarity.REVERSE

            # Draw the slot and assign its physical/material properties
            slot = self.motor._rectangle_geometry(
                origin,
                self.motor.slot_thickness,
                self.motor.slot_axial_length
            )

            self.renderer.draw(
                slot,
                self.motor.slot_material,
                self.motor.SLOT_ID,
                circuit=phase,
                turns=number_turns,
                polarity=polarity
            )

    def _add_stator(self) -> None:
        """
        Adds the stator to the simulation space.
        This includes alternating magnetized poles and the structural tube.
        """

        # Generate pole origin points, shifted axially by extra pairs
        pole_origins = []
        offset = (self.motor.extra_pairs * self.motor.pole_pitch)
        for pole in range(self.motor.total_number_poles):
            x = 0
            y = self.motor.pole_pitch * pole - 2 * offset
            pole_origins.append((x, y))

        for index, origin in enumerate(pole_origins):
            # Alternate magnetization direction every pole (e.g., N-S-N-S)
            pole_magnetization = 90 if index % 2 == 0 else -90

            # Draw the poles and assign its physical/material properties
            pole = self.motor._rectangle_geometry(
                origin,
                self.motor.pole_thickness,
                self.motor.pole_axial_length
            )

            self.renderer.draw(
                pole,
                self.motor.pole_material,
                self.motor.POLE_ID,
                magnetization=pole_magnetization
            )

        # Compute the tube height and origin based on all poles combined
        tube_axial_length = (
            self.motor.pole_axial_length * self.motor.total_number_poles
        )
        tube_origin = (
            self.motor.pole_outer_radius,
            - 2 * self.motor.extra_pairs * self.motor.pole_axial_length
        )

        tube = self.motor._rectangle_geometry(
            tube_origin,
            self.motor.tube_thickness,
            tube_axial_length
        )
        self.renderer.draw(
            tube,
            self.motor.tube_material,
            self.motor.TUBE_ID
        )

    def _create_circuits(self) -> None:
        """
        Creates circuits for each phase of the motor.
        """
        for phase in self.motor.phases:
            self.renderer.create_circuit(
                phase,
                CircuitType.SERIES
            )


class ThermalPhysics:
    """
    Thermal implementation of the tubular linear motor
    """
    def __init__(self, motor):
        self.motor = motor

    def setup(self):
        self._add_heating_elements()
        self._add_cooling_channels()

    def _add_heating_elements(self):
        # Thermal-specific logic
        pass

    def _add_cooling_channels(self):
        # Thermal-specific logic
        pass
