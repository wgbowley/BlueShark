"""
Filename: prototype_v0
Author: William Bowley
Version: 1.1
Date: 27 - 06 - 2025
Description:
    This script describes the POC motor or prototype V0 which was made on 22-04-2025.
    It models the same configuration of motor but with your different params.
    
    Class prototype_v0:
        functions:
            _init_(self, param_file)    -> None
            generate_model              -> None
            _unpack_params(params)      -> None
"""

# Libraries
import yaml
import sys
import os
import femm

# Sets the program path to the absolute path 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Modules 
from application.simulate import femm_addons
from domain import motor_generation
from domain import motor_physics

class prototype_v0:
    
    def __init__(self, param_file: str) -> None:
        
        # Loads in the yaml file and unpacks it
        with open(param_file, "r") as file:
            params = yaml.safe_load(file)
        self._unpack_params(params)
        
        # xPitch for coil and pole series
        self.coilPitch = motor_generation.coil_pitch(
            coilLength      = self.coilLength,
            slotInterLength = self.innerLength,
            slotOuterLength = self.outerLength
        )

        self.polePitch = motor_generation.pole_pitch(
            coilNumber  = self.numCoils,
            poleNumber  = self.numPoles,
            coilPitch   = self.coilPitch
        )
        
        self.frequency = motor_physics.synchronous_frequency(
            targetSpeed = 500, # Magic Numbers Yay
            polePitch   = self.polePitch
        )
        
        # Coil & Pole Origins (x,y)
        self.coilOrigins = femm_addons.origin_points(
            objectNum   = self.numCoils,
            xPitch      = self.coilPitch,
            yPitch      = 0
        )
        
        self.poleOrigin = femm_addons.origin_points(
            objectNum   = self.numPoles,
            xPitch      = self.polePitch,
            yPitch      = 0,
            yOffset     = -self.magneticGap
        )
    
    def generate_model(self) -> None:
        # Opens femm in hiden window and selects magnetic problem
        femm.openfemm(1)
        femm.newdocument(0) 
        
        # Defines the magnetic problem 
        femm.mi_probdef(
            self.frequency,
            "millimeters",
            "planar",
            1e-8,
            self.axialLength
        )
        
        # Adds materials to simulation
        femm.mi_getmaterial(self.backIronMaterial)
        femm.mi_getmaterial(self.armatureMaterial)
        femm.mi_getmaterial(self.poleMaterial)
        femm.mi_getmaterial("Air")
        
        # Add Coil 'Materials'
        # femm.mi_getmaterial(str(str(self.coilMaterial) + 'mm'))
        """
            J -> Current Density for each coil
            Each coil has a negative and positive current density region
        """
        
    # takes values from params file and adds them to the class
    def _unpack_params(self, params: dict) -> None:
        # Motor Model & Simulation Parameters
        model = params.get('model', {})
        self.numCoils       = model.get('numCoils', 0)
        self.numPoles       = model.get('numPoles', 0)
        self.currentRMS     = model.get('currentRMS', 0.0)
        self.axialLength    = model.get('axialLength', 0.0)
        self.wasteFactor    = model.get('wasteFactor', 0.0)

        # Coil Parameters
        coil = params.get('coil', {})
        self.coilLength     = coil.get('length', 0.0)
        self.coilHeight     = coil.get('height', 0.0)
        self.innerLength    = coil.get('innerLength', 0.0)
        self.outerLength    = coil.get('outerLength', 0.0)
        self.coilMaterial   = coil.get('material', '')

        # Pole Parameters
        pole = params.get('pole', {})
        self.poleLength     = pole.get('length', 0.0)
        self.poleHeight     = pole.get('height', 0.0)
        self.poleMaterial   = pole.get('material', '')

        # Back Iron Parameters 
        backIron = params.get('backIron', {})
        self.backIronLength = backIron.get('length', 0.0)
        self.backIronHeight = backIron.get('height', 0.0)
        self.backIronMaterial = backIron.get('material', '')

        # Armature Parameters
        armature = params.get('armature', {})
        self.backHeight     = armature.get('backHeight', 0.0)
        self.magneticGap    = armature.get('magneticGap', 0.0)
        self.teethLength    = armature.get('teethLength', 0.0)
        self.teethHeight    = armature.get('teethHeight', 0.0)
        self.armatureMaterial = armature.get('material', '')
    
# Example usage
motor = prototype_v0("data/params.yaml")
motor.generate_model()
