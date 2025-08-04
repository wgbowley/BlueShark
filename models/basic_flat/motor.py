"""
File: tubular_motor.py
Author: William Bowley
Version: 1.0
Date: 2025-08-05

Description:
    Basic model of a ironless flat linear motor for use in the motor simulation framework.
    Parameters are defined within the motor.yaml file.

Units and Conventions:
    - All dimensions are in millimeters (mm).
    - Angular measurements (e.g., magnetization direction) are in degrees.
    - Coordinate system:
        * The simulation uses a planar 2D FEMM model.
        * The x-axis corresponds to the linear motion direction (motor travel axis).
        * The y-axis corresponds to the motor's vertical cross-section (thickness direction).
    - Currents are in Amperes (A).
    - Time-dependent stepping is represented as linear displacement along the x-axis.
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

class BasicFlat(LinearBase):

    def __init__(self, parameter_file: str) -> None:
        self._unpack(parameter_file)

        # FEMM groups
        self.group_boundary: int = 0
        self.group_slot: int = 1
        self.group_pole: int = 2

        # Phases
        self.phases = ['pa', 'pb', 'pc']


    def setup(self):
        """ Setup femm file and draws motor geometry to simulation space"""
        try:
            femm.openfemm(1)
            femm.newdocument(0)
            femm.mi_probdef(0, "millimeters", "planar", 1e-8)
            
            for phase in self.phases:
                femm.mi_addcircprop(phase, 0, 1)
        
            femm.mi_getmaterial(self.pole_material)
            femm.mi_getmaterial(self.slot_material)
            femm.mi_getmaterial(self.boundary_material)
            
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

            femm.mi_movetranslate(step, 0)
            femm.mi_clearselected()

        except Exception as e:
            raise RuntimeError(f"Failed to move motor in FEMM: {e}") from e
       
        
    def _add_armature(self) -> None:
        """
        Adds the armature to the simulation space
        """
        
        self.number_turns = estimate_turns(
            length = self.slot_width,
            height = self.slot_height,
            wire_diameter = self.slot_wire_diameter, 
            fill_factor = self.fill_factor
        )

        for slot_idx in range(len(self.slot_origins)):
            # Repeat each phase twice before switching
            phase = self.phases[(slot_idx // 2) % len(self.phases)]
            
            # Alternate turn direction every slot
            turn = self.number_turns if slot_idx % 2 == 0 else -self.number_turns

            draw_and_set_properties(
                origin      = self.slot_origins[slot_idx],
                length      = self.slot_width,
                height      = self.slot_height,
                material    = self.slot_material,
                direction   = 0,
                incircuit   = phase,
                group       = self.group_slot,
                turns       = turn
            )


    
    def _add_stator(self) -> None:
        """
        Adds the stator to the simulation space
        """
        for pole in range(self.total_number_poles):
            pole_magnetization = 90 if pole % 2 == 0 else -90

            draw_and_set_properties(
                origin=self.pole_origins[pole],
                length=self.pole_width,
                height=self.pole_height,
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
        boundary_center = (0, 0)

        # Radial extent based on stator poles and pitch
        stator_radius = 0.5 * (self.total_number_poles + 1) * self.pole_pitch

        # Radial extent including armature and slot height
        armature_radius = self.pole_height + self.armature_stator_gap + self.slot_height

        # Use larger radius and add 10% margin for safety
        boundary_radius = max(stator_radius, armature_radius) * 1.1

        add_bounds(boundary_center, boundary_radius, material=self.boundary_material)


    def _compute_geometry(self) -> None:
        """
        Compute and set key geometric parameters for the tubular motor,
        including slot pitch, motor circumference, pole pitch, and origin points.
        """

        # Calculate the pitch of each slot (height + spacing)
        self.slot_pitch = self.slot_width + self.slot_spacing

        # Calculate the motor circumference based on slot pitch and number of slots
        self.circumference = self.slot_pitch * self.number_slots

        # Calculate pole pitch based on motor circumference and number of poles
        self.pole_pitch = self.circumference / self.number_poles

        # Calculate total number of poles in simulation space
        # Extra pairs add poles symmetrically on both sides
        self.total_number_poles = (4 * self.extra_pairs) + self.number_poles

        # Ensure pole height fits within pole pitch, scale down if necessary
        if self.pole_pitch < self.pole_width:
            self.pole_width = self.pole_pitch
            print(
                f"Warning: Pole width scaled down to fit pole pitch: new width = {self.pole_width}"
            )

        # Generate slot origin points along y-axis, shifted by width + gap on y-axis
        self.slot_origins = origin_points(
            self.number_slots,
            x_pitch=self.slot_pitch,
            y_pitch=0,
            y_offset=self.armature_stator_gap,
            x_offset=-1/2*(self.circumference)
        )

        # Generate pole origin points, shifted horizontally by extra pairs
        self.pole_origins = origin_points(
            self.total_number_poles,
            x_pitch=self.pole_pitch,
            y_pitch=0,
            y_offset=-self.pole_height,
            x_offset=-1/2*(self.total_number_poles * self.pole_pitch)
        )


    def _unpack(self, parameter_file) -> None:

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
        self.slot_width = require("width", slot)
        self.slot_height = require("height", slot)
        self.slot_spacing = require("spacing", slot)
        self.slot_material = require("material", slot)
        self.slot_wire_diameter = require("wire_diameter", slot)
        self.armature_stator_gap = require("armature_stator_gap", slot)

        # Assign pole geometry
        self.pole_width = require("width", pole)
        self.pole_height = require("height", pole)
        self.pole_material = require("material", pole)

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
