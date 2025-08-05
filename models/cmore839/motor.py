"""
File: motor.py
Author: William Bowley
Version: 1.1
Date: 2025-07-19

Description:
    Framework model for cmore839 tubular linear motor design 

    Adapted from the "DIY-Linear-Motor" project by cmore839:
    https://github.com/cmore839/DIY-Linear-Motor

    FEMM simulation structure partially based on contributions by JuPrgn:
    https://github.com/JuPrgn/FEMM_linear_motor_simulations

Units and Conventions:
    - All dimensions are in millimeters (mm).
    - Angular measurements (e.g., magnetization direction) are in degrees.
    - Coordinate system:
        * The simulation uses an axial (axi) 2D FEMM model.
        * The r-axis corresponds to the radial direction (outward from center).
        * The z-axis corresponds to the linear/axial direction of motor movement.
    - Currents are in Amperes (A).
    - The motor geometry is defined in the z-direction with origins spaced accordingly.
    - Stepping is represented as linear displacement along the z-axis.
"""

import yaml
import femm
import pathlib
import typing

from blueshark.motor.linear_interface import LinearBase
from blueshark.femm_utils.preprocesses.draw import draw_and_set_properties
from blueshark.femm_utils.preprocesses.boundary import add_bounds
from blueshark.domain.generation.geometry import origin_points
from blueshark.domain.generation.number_turns import estimate_turns
from blueshark.motor.utils import require

class CmoreTubular(LinearBase):
    """
    Framework model for cmore839 tubular linear motor design 
    """
    def __init__(self, parameter_file):
        self._unpack(parameter_file)

        # FEMM groups
        self.group_boundary: int = 0
        self.group_slot: int = 1
        self.group_pole: int = 2
        self.group_tube: int = 3

        # Phases
        self.phases = ['pa', 'pb', 'pc']

    def setup(self):
        """ Setup femm file and draws motor geometry to simulation space"""
        try:
            femm.openfemm(1)
            femm.newdocument(0)
            femm.mi_probdef(0, "millimeters", "axi", 1e-8)
            
            for phase in self.phases:
                femm.mi_addcircprop(phase, 0, 1)
        
            femm.mi_getmaterial(self.pole_material)
            femm.mi_getmaterial(self.slot_material)
            femm.mi_getmaterial(self.boundary_material)
            femm.mi_addmaterial('AluminumTube', 1, 1, 0, 0, 37, 0, 0, 1, 0, 0, 0, 1, 1)
            # femm.mi_getmaterial(self.tube_material)

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
            moving_groups = (
                [self.get_moving_group()]
                if isinstance(self.get_moving_group(), int)
                else self.get_moving_group()
            )

            for group in moving_groups:
                femm.mi_selectgroup(group)

            femm.mi_movetranslate(0, step)
            femm.mi_clearselected()

        except Exception as e:
            raise RuntimeError(f"Failed to move motor in FEMM: {e}") from e

    def _add_armature(self) -> None:
        """
        Adds the armature to the simulation space
        """

        relative_radius = self.slot_outer_radius - self.slot_inner_radius
        self.number_turns = estimate_turns(
            length=relative_radius,
            height=self.slot_axial_length,
            wire_diameter=self.slot_wire_diameter, 
            fill_factor=self.fill_factor
        )
        
        for slot_index in range(len(self.slot_origins)):
            slot_phase = self.phases[slot_index % len(self.phases)]
            
            # Alternate turns positive and negative slot index parity
            turns = self.number_turns if slot_index % 2 == 0 else -self.number_turns

            draw_and_set_properties(
                origin=self.slot_origins[slot_index],
                length=relative_radius,
                height=self.slot_axial_length,
                material=self.slot_material,
                direction=0,
                incircuit=slot_phase,
                group=self.group_slot,
                turns=turns
            )
    
    def _add_stator(self) -> None:
        """
        Adds the stator to the simulation space.
        This includes alternating magnetized poles and the outer structural tube.
        """

        pole_relative_radius = self.pole_outer_radius
        # Loop through all stator poles and place them with alternating magnetization
        for pole in range(self.total_number_poles):
            # Alternate magnetization direction every pole (e.g., N-S-N-S)
            pole_magnetization = 90 if pole % 2 == 0 else -90

            # Draw the magnetic pole and assign its physical/material properties
            draw_and_set_properties(
                origin=self.pole_origins[pole], 
                length=pole_relative_radius,
                height=self.pole_axial_length,
                group=self.group_pole,
                direction=pole_magnetization,
                incircuit="<none>",
                material=self.pole_material,
                turns=0,
            )

        # Compute the tube height and origin based on all poles combined
        tube_axial_length = self.pole_axial_length * self.total_number_poles
        tube_origin = (self.pole_outer_radius, -0.5 * tube_axial_length + 1/2*(self.pole_axial_length*self.number_poles))

        # Draw the outer tube encasing all poles, unmagnetized
        tube_relative_radius = self.tube_outer_radius - self.tube_inner_radius
        draw_and_set_properties(
            origin=tube_origin,
            length=tube_relative_radius,
            height=tube_axial_length,
            group=self.group_tube,
            direction=0,  # No magnetization
            incircuit="<none>",
            material=self.tube_material,
            turns=0,
        )
        
    def _add_boundary(self) -> None:
        """
        Adds the Neumann outer boundary with a safety margin to enclose all geometry.
        """
        # Center boundary midway along poles
        boundary_center = (0, self.pole_axial_length * self.number_poles * 0.5)

        # Radial extent based on stator poles and pitch
        stator_radius = 0.5 * (self.total_number_poles + 1) * self.pole_pitch

        # Radial extent including armature and slot height
        armature_radius = self.slot_outer_radius

        # Use larger radius and add 10% margin for safety
        boundary_radius = max(stator_radius, armature_radius) * 1.1

        add_bounds(boundary_center, boundary_radius, material=self.boundary_material)

    def _compute_geometry(self) -> None:
        """
        Compute and set key geometric parameters for the tubular motor,
        including slot pitch, motor circumference, pole pitch, and origin points.
        """

        # Calculate the pitch of each slot (height + spacing)
        self.slot_pitch = self.slot_axial_length + self.slot_axial_spacing

        # Calculate the motor circumference based on pole height and number of slots
        self.circumference = self.pole_axial_length * self.number_poles

        # Calculate pole pitch based on motor circumference and number of poles
        self.pole_pitch = self.circumference / self.number_poles

        # Calculate total number of poles in simulation space
        # Extra pairs add poles symmetrically on both sides
        self.total_number_poles = (4 * self.extra_pairs) + self.number_poles
        
        if self.pole_pitch < self.pole_axial_length:
            self.pole_axial_length = self.pole_pitch
            print(
                f"Warning: Pole height scaled down to fit pole pitch: new axial length = {self.slot_axial_length}"
            )

        # Add spacing between slots except every third one (for coil grouping pattern)
        y = 0
        self.slot_origins = []
        for slot in range(self.number_slots):
            if slot % 3 != 0:
                y += self.slot_pitch
            else:
                y += self.slot_axial_length

            x = self.slot_inner_radius
            self.slot_origins.append((x, y))

        # Generate pole origin points, shifted axially by extra pairs
        self.pole_origins = origin_points(
            self.total_number_poles,
            x_pitch=0,
            y_pitch=self.pole_pitch,
            x_offset=0,
            y_offset=-2 * (self.extra_pairs * self.pole_pitch),
        )

    def _unpack(self, parameter_file):

        """ Loads parameters from .YAML file into variables within this class"""
        
        param_file = pathlib.Path(parameter_file)

        if not param_file.exists():
            raise FileNotFoundError(f"Parameter file '{parameter_file}' was not found.")

        try:
            with param_file.open("r") as file:
                params = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file '{param_file}': {e}")

        for section in ["model", "slot", "pole", "tube", "output"]:
            if section not in params:
                raise KeyError(f"Missing required section '{section}' in parameter file.")

        model = params["model"]
        slot  = params["slot"]
        pole  = params["pole"]
        tube  = params["tube"]
        output  = params["output"]

        # Assign model parameters
        self.number_slots = require("number_slots", model)
        self.number_poles = require("number_poles", model)
        self.d_currents = require("d_currents", model)
        self.q_currents = require("q_currents", model)
        self.fill_factor = require("fill_factor", model)
        self.extra_pairs = require("extra_pairs", model)
        self.boundary_material = require("boundary_material", model)
        
        # Assign slot geometry
        self.slot_inner_radius = require("inner_radius", slot)
        self.slot_outer_radius = require("outer_radius", slot)
        self.slot_axial_length = require("axial_length", slot)
        self.slot_axial_spacing = require("axial_spacing", slot)
        self.slot_material = require("material", slot)
        self.slot_wire_diameter = require("wire_diameter", slot)

        # Assign pole geometry
        self.pole_outer_radius = require("outer_radius", pole)
        self.pole_axial_length = require("axial_length", pole)
        self.pole_material = require("material", pole)

        # Assign tube geometry
        self.tube_inner_radius = require("inner_radius", tube)
        self.tube_outer_radius = require("outer_radius", tube)
        self.tube_material = require("material", tube)

        # Assign output
        self.folder_path = require("folder_path", output)
        self.file_name = require("file_name", output)

    def get_parameters(self) -> dict:
        """
        Return a dictionary of all public instance variables for this motor object.
        """
        return {
            **{k: v for k, v in self.__dict__.items() if not k.startswith("_")},
            "motor_class": self.__class__.__name__,
        }

    def get_path(self) -> pathlib.Path:
        """
        Returns the full file path of the motor simulation file.
        """
        return pathlib.Path(self.folder_path) / self.file_name

    def get_moving_group(self) -> typing.Union[int, typing.List[int]]:
        """
        Returns the moving group(s) within the FEMM simulation domain.
        """
        return self.group_slot

    def get_circumference(self) -> float:
        """
        Returns the mechanical circumference of the stator path.
        """
        return self.circumference

    def get_number_poles(self) -> int:
        """
        Returns the total number of magnetic poles in the motor.
        """
        return self.number_poles

    def get_number_slots(self) -> int:
        """
        Returns the total number of stator slots in the motor.
        """
        return self.number_slots

    def get_peak_currents(self) -> tuple[float, float]:
        """
        Returns the peak d-axis and q-axis currents for simulation.
        """
        return (self.d_currents, self.q_currents)
    