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
import warnings

import yaml
import femm

from blueshark.motor.linear_interface import LinearBase

from blueshark.femm_utils.preprocesses.draw import draw_and_set_properties
from blueshark.domain.generation.number_turns import estimate_turns
from blueshark.femm_utils.preprocesses.boundary import add_bounds
from blueshark.domain.generation.geometry import origin_points
from blueshark.motor.utils import require


class BasicTubular(LinearBase):
    """
    Basic model of a tubular linear motor

    Units and conventions:
        - All dimensions are in millimeters (mm)
        - Angular measurements are in radians expect for FEMM inputs
        - Coordinate system:
            * Uses an axial (axi) 2D FEMM Model
            * r-axis corresponds to the radial direction
            * z-axis corresponds to the linear/axial direction
        - Currents are in amperes (A)
        - Stepping is represented as linear displacement along the x-axis
    """

    def __init__(self, parameter_file) -> None:
        # FEMM groups
        self.group_boundary: int = 0
        self.group_slot: int = 1
        self.group_pole: int = 2
        self.group_tube: int = 3

        # Motor phases
        self.phases = ["phase_a", "phase_b", "phase_c"]

        # Load parameters
        self._unpack(parameter_file)

    def setup(self) -> None:
        """
        Setup femm file and draws motor geometry to simulation space
        """
        try:
            femm.openfemm(1)  # Opens femm in a hiden window
            femm.newdocument(0)  # Magnetic problem

            # Problem Defined as a Magnetostatic simulation
            femm.mi_probdef(0, "millimeters", "axi", 1e-8)

            for phase in self.phases:
                femm.mi_addcircprop(phase, 0, 1)

            femm.mi_getmaterial(self.pole_material)
            femm.mi_getmaterial(self.slot_material)
            femm.mi_getmaterial(self.boundary_material)

            # Computes geometry and than adds components
            # Re-calculates encase user changed any parameters
            self._compute_geometry()
            self._add_armature()
            self._add_stator()
            self._add_boundary()

            path = pathlib.Path(self.folder_path) / f"{self.file_name}.fem"
            femm.mi_saveas(str(path))
        except Exception as e:
            raise RuntimeError(f"Femm setup failed: {e}") from e
        finally:
            femm.closefemm()

    def set_currents(self, currents: tuple[float, float, float]) -> None:
        """Set 3-phase currents for the simulation step."""
        try:
            for phase, current in zip(self.phases, currents):
                femm.mi_setcurrent(phase, float(current))
        except Exception as e:
            raise RuntimeError(f"Failed to set currents in FEMM: {e}") from e

    def step(self, step: float) -> None:
        """
        Move the motor by a specified linear step.
        """
        try:
            femm.mi_selectgroup(self.moving_group)
            femm.mi_movetranslate(0, step)
            femm.mi_clearselected()

        except Exception as e:
            raise RuntimeError(f"Failed to move motor in FEMM: {e}") from e

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

    def _add_armature(self) -> None:
        """
        Adds the armature to the simulation space.
        This includes the alternating polarity slot with pattern
        """

        # Generate coil origin points, shifted axially by extra pairs
        slot_origins = origin_points(
            self.number_slots,
            0,
            self.slot_pitch,
            x_offset=self.slot_inner_radius
        )

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
            draw_and_set_properties(
                origin,
                self.slot_thickness,
                self.slot_axial_length,
                self.slot_material,
                0,  # No magnetization
                phase,
                self.group_slot,
                turns
            )

    def _add_stator(self) -> None:
        """
        Adds the stator to the simulation space.
        This includes alternating magnetized poles
        """

        # Generate pole origin points, shifted axially by extra pairs
        pole_origins = origin_points(
            self.total_number_poles,
            0,
            self.pole_pitch,
            y_offset=-2 * (self.extra_pairs * self.pole_pitch)
        )

        for index, origin in enumerate(pole_origins):
            # Alternate magnetization direction every pole (e.g., N-S-N-S)
            pole_magnetization = 90 if index % 2 == 0 else -90

            # Draw the poles and assign its physical/material properties
            draw_and_set_properties(
                origin,
                self.pole_thickness,
                self.pole_axial_length,
                self.pole_material,
                pole_magnetization,
                "<none>",
                self.group_pole,
                0
            )

    def _add_boundary(self) -> None:
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

        add_bounds(
            origin,
            radius,
            material=self.boundary_material
        )

    def _compute_geometry(self) -> None:
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
        if self.pole_pitch > self.pole_axial_length:
            self.pole_axial_length = self.pole_pitch
            msg = f"Pitch > Axial length; set to {self.pole_pitch:.3f} mm"
            warnings.warn(msg)

        # Calculate total number of poles
        # Extra pairs add poles symmetrically on both sides
        self.total_number_poles = (4 * self.extra_pairs) + self.number_poles

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
        required_sections = ["model", "slot", "pole", "output"]

        for section in required_sections:
            # Existence check for required sections
            if section not in parameters:
                msg = f"Missing required key '{section}' in {param_file}"
                raise KeyError(msg)

        # Yaml Sections
        model = parameters["model"]
        slot = parameters["slot"]
        pole = parameters["pole"]
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

        # Calculates radial thickness for slot, tube & poles
        self.slot_thickness = self.slot_outer_radius - self.slot_inner_radius
        self.pole_thickness = self.pole_outer_radius

        # Assign output
        self.folder_path = require("folder_path", output)
        self.file_name = require("file_name", output)
