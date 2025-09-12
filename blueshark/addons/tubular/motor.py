"""
File: motor.py
Author: William Bowley
Version: 1.2
Date: 2025-07-23

Description:
    Basic model of a tubular linear motor for use in
    the motor simulation framework.

    Parameters are defined within the motor.yaml file
"""

import pathlib
import yaml
import logging

from blueshark.addons.tubular.utils import require
from blueshark.addons.tubular.number_turns import estimate_turns
from blueshark.renderer.renderer_interface import BaseRenderer
from blueshark.renderer.material_manager import MaterialManager

from blueshark.domain.constants import (
    Geometry,
    ShapeType,
    SimulationType,
    Units
)


class Tubular():
    def __init__(
        self,
        renderer: BaseRenderer,
        parameter_file: pathlib.Path,
    ) -> None:
        # Blueshark renderer
        self.renderer = renderer
        self.manager = MaterialManager()
        self.type = SimulationType.AXI_SYMMETRIC
        self.units = Units.MILLIMETER

        # FEMM groups
        self.group_boundary: int = 0
        self.group_slot: int = 1
        self.group_pole: int = 2
        self.group_tube: int = 3

        # Motor phases
        self._phases = ["phase_a", "phase_b", "phase_c"]

        # Load parameters
        self._unpack(parameter_file)

        self.slot_material = self.manager.use_material(
            self.slot_material,
            wire_diameter=self.slot_wire_diameter
        )
        self.tube_material = self.manager.use_material(
            self.tube_material
        )
        self.pole_material = self.manager.use_material(
            self.pole_material,
            grade=self.pole_grade
        )
        self.boundary_material = self.manager.use_material(
            self.boundary_material
        )

    def setup(self) -> None:
        """
        Setup femm file and draws motor geometry to simulation space
        """
        self.renderer.setup(
            self.type,
            self.units
        )

        self.compute_geometry()
        self.add_armature()
        self.add_stator()
        self.add_boundary()

        return None

    def add_armature(self) -> None:
        """
        Adds the armuture to the simulation space.
        This includes the alternating polarity slot with pattern
        """

        # Calculates the slot origins (bottom-left vertex)
        z = -self.slot_pitch + 1.5 * self.slot_axial_spacing
        slot_origins = []
        for slot in range(self.number_slots):
            # Each slot has spacing except every third one
            if slot % 3 != 0:
                z += self.slot_axial_length + self.slot_axial_spacing
            else:
                z += self.slot_axial_length

            r = self.slot_inner_radius
            slot_origins.append((r, z))

        # Calculates turns within the slot cross section
        number_turns = estimate_turns(
            self.slot_thickness,
            self.slot_axial_length,
            self.slot_wire_diameter,
            self.fill_factor
        )

        for index, origin in enumerate(slot_origins):
            # Sets phase of slot in pattern [a,b,c]
            phase = self.phases[index % len(self.phases)]

            # Alternate positive turns and negative turns for slots
            turns = number_turns if index % 2 == 0 else -number_turns

            # Draw the slot and assign its physical/material properties
            bl = (origin[0], origin[1])
            br = (origin[0] + self.slot_thickness, origin[1])
            slot: Geometry = {
                'shape': ShapeType.RECTANGLE,
                'points': [
                    bl,
                    br,
                    (br[0], br[1] + self.slot_axial_length),
                    (bl[0], bl[1] + self.slot_axial_length)
                ],
                'enclosed': True
            }

            self.renderer.draw(
                slot,
                self.slot_material,
                self.group_slot,
                phase=phase,
                turns=turns
            )

    def add_stator(self) -> None:
        """
        Adds the stator to the simulation space.
        This includes alternating magnetized poles and the structural tube.
        """

        # Generate pole origin points, shifted axially by extra pairs
        pole_origins = []
        offset = (self.extra_pairs * self.pole_pitch)
        for pole in range(self.total_number_poles):
            x = 0
            y = self.pole_pitch * pole - 2 * offset
            pole_origins.append((x, y))

        for index, origin in enumerate(pole_origins):
            # Alternate magnetization direction every pole (e.g., N-S-N-S)
            pole_magnetization = 90 if index % 2 == 0 else -90

            # Draw the poles and assign its physical/material properties
            bl = (origin[0], origin[1])
            br = (origin[0] + self.pole_thickness, origin[1])

            pole: Geometry = {
                'shape': ShapeType.RECTANGLE,
                'points': [
                    bl,
                    br,
                    (br[0], br[1] + self.pole_axial_length),
                    (bl[0], bl[1] + self.pole_axial_length)
                ],
                'enclosed': True
            }
            self.renderer.draw(
                pole,
                self.pole_material,
                self.group_pole,
                magnetization=pole_magnetization
            )

        # Compute the tube height and origin based on all poles combined
        tube_axial_length = self.pole_axial_length * self.total_number_poles
        tube_origin = (
            self.pole_outer_radius,
            - 2 * self.extra_pairs * self.pole_axial_length
        )

        bl = (tube_origin[0], tube_origin[1])
        br = (tube_origin[0] + self.tube_thickness, tube_origin[1])
        tube: Geometry = {
            'shape': ShapeType.RECTANGLE,
            'points': [
                bl,
                br,
                (br[0], br[1] + tube_axial_length),
                (bl[0], bl[1] + tube_axial_length)
            ],
            'enclosed': True
        }

        self.renderer.draw(
            tube,
            self.tube_material,
            self.group_tube
        )

    def add_boundary(self) -> None:
        """
        Adds the Neumann outer boundary with
        a safety margin to enclose all geometry.
        """
        # origin boundary midway along poles
        origin = (0, self.pole_axial_length * self.number_poles * 0.5)

        # Radial extent based on stator poles and pitch
        stator_radius = 0.5 * (self.total_number_poles) * self.pole_pitch

        # Radial extent including armature and slot height
        armature_radius = self.slot_outer_radius

        # Use larger radius and add 20% margin for safety
        radius = max(stator_radius, armature_radius) * 1.2
        self.renderer.add_bounds(
            origin,
            radius,
            self.boundary_material
        )

    def compute_geometry(self) -> None:
        """
        Compute and set key geometric parameters for this motor class,
        including slot pitch, motor circumference, pole pitch
        """

        # Calculates slot start-to-start axial distance
        self.slot_pitch = self.slot_axial_length + self.slot_axial_spacing

        # The pattern length includes air gaps not physically present.
        # Subtract to get the actual armature circumference.
        pattern_length = self.slot_pitch * self.number_slots
        air_gaps = 1 * self.slot_axial_spacing

        self._circumference = pattern_length - air_gaps

        # Calculates pole start-to-start axial distance
        self.pole_pitch = self.circumference / self.number_poles

        # Ensures that the program doesn't crash from overlapping poles/slots
        if self.pole_pitch != self.pole_axial_length:
            self.pole_axial_length = self.pole_pitch
            msg = f"Pitch > Axial length; set to {self.pole_pitch:.3f} mm"
            logging.warning(msg)

        # Calculate total number of poles
        # Extra pairs add poles symmetrically on both sides
        self.total_number_poles = (4 * self.extra_pairs) + self.number_poles

    def get_parameters(self) -> dict:
        """
        Return a dict of all public instance variables
        """
        public_vars = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                public_vars[key] = value
        public_vars["motor_class"] = self.__class__.__name__
        return public_vars

    @property
    def phases(self) -> list[str]:
        """
        Returns the phases in the motor
        """
        return self._phases

    @property
    def path(self) -> str:
        """
        Returns the full file path of the motor simulation file.
        """
        return pathlib.Path(self.folder_path) / self.file_name

    @property
    def moving_group(self) -> str:
        """
        Returns the moving group(s) within the FEMM simulation domain.
        """
        return self.group_slot

    @property
    def circumference(self) -> float:
        """
        Returns the mechanical circumference of the stator path.
        """
        return self._circumference

    @property
    def number_poles(self) -> int:
        """
        Returns the total number of magnetic poles in the motor.
        """
        return self._number_poles

    @property
    def number_slots(self) -> int:
        """
        Returns the total number of stator slots in the motor.
        """
        return self._number_slots

    @property
    def peak_currents(self) -> tuple[float, float]:
        """
        Returns the peak d-axis and q-axis currents for simulation.
        """
        return (self.d_currents, self.q_currents)

    def _unpack(self, parameter_file: str) -> None:
        """
        Loads parameters from .yaml file into variables within the class
        """
        param_file = pathlib.Path(parameter_file)

        # Existence check
        if not param_file.exists():
            msg = f"Parameter file '{param_file}' was not found."
            raise FileNotFoundError(msg)

        # Type check
        if param_file.suffix.lower() != ".yaml":
            msg = f"File '{param_file}' has wrong extension; expected '.yaml'"
            raise ValueError(msg)

        # Attempts to read the parameter file
        try:
            with open(param_file, "r", encoding="utf-8") as file:
                parameters = yaml.safe_load(file)
        except yaml.YAMLError as e:
            msg = f"Failed to parse YAML file '{param_file}' : {e}"
            raise ValueError(msg) from e

        # Check for required sections in the parameter file
        required_sections = ["model", "slot", "pole", "tube", "output"]

        for section in required_sections:
            # Existence check for required sections
            if section not in parameters:
                msg = f"Missing required key '{section}' in {param_file}"
                raise KeyError(msg)

        # Yaml Sections
        model = parameters["model"]
        slot = parameters["slot"]
        pole = parameters["pole"]
        tube = parameters["tube"]
        output = parameters["output"]

        # Assign model parameters
        self._number_slots = require("number_slots", model)
        self._number_poles = require("number_poles", model)
        self.extra_pairs = require("extra_pairs", model)

        self.d_currents = require("d_currents", model)
        self.q_currents = require("q_currents", model)

        self.fill_factor = require("fill_factor", model)
        self.boundary_material = require("boundary_material", model)

        # Assign slot parameters
        self.slot_inner_radius = require("inner_radius", slot)
        self.slot_outer_radius = require("outer_radius", slot)
        self.slot_axial_length = require("axial_length", slot)
        self.slot_axial_spacing = require("axial_spacing", slot)

        self.slot_material = require("material", slot)
        self.slot_wire_diameter = require("wire_diameter", slot)

        # Assign pole parameters
        self.pole_outer_radius = require("outer_radius", pole)
        self.pole_axial_length = require("axial_length", pole)

        self.pole_material = require("material", pole)
        self.pole_grade = require("grade", pole)

        # Assign tube parameters
        self.tube_inner_radius = require("inner_radius", tube)
        self.tube_outer_radius = require("outer_radius", tube)

        self.tube_material = require("material", tube)

        # Calculates radial thickness for slot, tube & poles
        self.slot_thickness = self.slot_outer_radius - self.slot_inner_radius
        self.pole_thickness = self.pole_outer_radius
        self.tube_thickness = self.tube_outer_radius - self.tube_inner_radius

        # Assign output
        self.folder_path = require("folder_path", output)
        self.file_name = require("file_name", output)
