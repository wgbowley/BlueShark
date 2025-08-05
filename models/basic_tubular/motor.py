"""
File: motor.py
Author: William Bowley
Version: 1.2
Date: 2025-07-23

Description:
    Basic model of a tubular linear motor for use in the motor simulation framework.
    Parameters are defined within the motor.yaml file

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

import pathlib
import typing
import yaml
import femm

from blueshark.motor.linear_interface import LinearBase
from blueshark.femm_utils.preprocesses.draw import draw_and_set_properties
from blueshark.femm_utils.preprocesses.boundary import add_bounds
from blueshark.domain.generation.geometry import origin_points
from blueshark.domain.generation.number_turns import estimate_turns
from blueshark.motor.utils import require


class BasicTubular(LinearBase):
    """
    Basic model of a tubular linear motor for use in the motor simulation framework
    """
    def __init__(self, parameter_file: str) -> None:
        self._unpack(parameter_file)

        # FEMM groups
        self.group_boundary: int = 0
        self.group_slot: int = 1
        self.group_pole: int = 2

        # Motor phase labels
        self.phases = ['pa', 'pb', 'pc']

    def setup(self):
        """ Setup femm file and draws motor geometry to simulation space"""
        try:
            femm.openfemm(1) # Opens femm in hide window
            femm.newdocument(0) # Magnetic problem

            # Problem Defined as a Magnetostatic simulation
            femm.mi_probdef(0, "millimeters", "axi", 1e-8) 
            
            for phase in self.phases:
                femm.mi_addcircprop(phase, 0, 1)
        
            femm.mi_getmaterial(self.pole_material)
            femm.mi_getmaterial(self.slot_material)
            femm.mi_getmaterial(self.boundary_material)
            
            # Computes geometry and than adds components
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
            # Get the moving group(s)
            group_data = self.get_moving_group()
            if isinstance(group_data, int):
                moving_groups = [group_data]
            else:
                moving_groups = group_data

            # Select and move each group
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
        
        # Calculates the number of turns with the slot cross section
        self.number_turns = estimate_turns(
            length=self.slot_thickness,
            height=self.slot_axial_length,
            wire_diameter=self.slot_wire_diameter,
            fill_factor=self.fill_factor
        )
        
        for slot_index in range(len(self.slot_origins)):
            # Sets slots phases in this pattern [pa, pb, pc]
            slot_phase = self.phases[slot_index % len(self.phases)]
            
            # Alternate turns positive and negative slot index parity
            turns = self.number_turns if slot_index % 2 == 0 else -self.number_turns

            # Draw the slot and assign its physical/material properties
            draw_and_set_properties(
                origin=self.slot_origins[slot_index],
                length=self.slot_thickness,
                height=self.slot_axial_length,
                material=self.slot_material,
                direction=0,
                incircuit=slot_phase,
                group=self.group_slot,
                turns=turns
            )
    
    def _add_stator(self) -> None:
        """
        Adds the stator to the simulation space
        """

         # Loop through all stator poles and place them with alternating magnetization
        for pole in range(self.total_number_poles):
            # Alternate magnetization direction every pole (e.g., N-S-N-S)
            pole_magnetization = 90 if pole % 2 == 0 else -90

            # Draw the magnetic pole and assign its physical/material properties
            draw_and_set_properties(
                origin=self.pole_origins[pole],
                length=self.pole_thickness,
                height=self.pole_axial_length,
                group=self.group_pole,
                direction=pole_magnetization,
                incircuit="<none>",
                material=self.pole_material,
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

        # Calculate the motor circumference based on slot pitch and number of slots
        self.circumference = self.slot_pitch * self.number_slots

        # Calculate pole pitch based on motor circumference and number of poles
        self.pole_pitch = self.circumference / self.number_poles

        # Calculate total number of poles in simulation space
        # Extra pairs add poles symmetrically on both sides
        self.total_number_poles = (4 * self.extra_pairs) + self.number_poles

        # Ensure pole height fits within pole pitch, scale down if necessary
        if self.pole_pitch < self.pole_axial_length:
            self.pole_axial_length = self.pole_pitch
            print(
                f"Warning: Pole height scaled down to fit pole pitch: new axial length = {self.slot_axial_length}"
            )

        # Generate slot origin points along y-axis, shifted by radius + gap on x-axis
        self.slot_origins = origin_points(
            self.number_slots,
            x_pitch=0,
            y_pitch=self.slot_pitch,
            x_offset=self.slot_inner_radius,
        )

        # Generate pole origin points, shifted vertically by extra pairs
        self.pole_origins = origin_points(
            self.total_number_poles,
            x_pitch=0,
            y_pitch=self.pole_pitch,
            x_offset=0,
            y_offset=-2 * (self.extra_pairs * self.pole_pitch),
        )

    def _unpack(self, parameter_file: str) -> None:

        """ Loads parameters from .YAML file into variables within this class"""
        
        param_file = pathlib.Path(parameter_file)

        if not param_file.exists():
            raise FileNotFoundError(f"Parameter file '{parameter_file}' was not found.")

        try:
            with param_file.open("r") as file:
                params = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file '{param_file}': {e}")

        for section in ["model", "slot", "pole", "output"]:
            if section not in params:
                raise KeyError(f"Missing required section '{section}' in parameter file.")

        # YAML Fields
        model = params['model']
        slot = params['slot']
        pole = params['pole']
        output = params['output']

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

        # Assign output
        self.folder_path = require("folder_path", output)
        self.file_name = require("file_name", output)

        # Optimization Parameters
        self.slot_thickness = self.slot_outer_radius - self.slot_inner_radius
        self.pole_thickness = self.pole_outer_radius

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
