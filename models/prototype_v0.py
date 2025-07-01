"""
Filename: prototype_v0
Author: William Bowley
Version: 1.1
Date: 29 - 06 - 2025
Description:
    This script describes the POC motor or prototype V0 which was made on 22-04-2025.
    It models the same configuration of motor but with your different params.
    
    Class prototype_v0:
        functions:
            _init_(param_file)      -> None
            generate_model()        -> None
            draw_armuture()         -> None
            draw_stator()           -> None
            _unpack_params(params)  -> None
            
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
        
        # Femm object groups 
        # Bounds is group 0 
        self.coreGroup = 1
        self.coilGroup = 2
        self.poleGroup = 3
        
        # Phases
        self.phases = ['a','b','c']
        
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
            0, #self.frequency,
            "millimeters",
            "planar",
            1e-8,
            self.axialLength
        )
        
        currentDensity = motor_physics.applied_current_density(0.2, 0.2, 1)
        # Adds materials to simulation
        femm.mi_getmaterial(self.backIronMaterial)
        femm.mi_getmaterial(self.armatureMaterial)
        femm.mi_getmaterial(self.poleMaterial)
        femm.mi_getmaterial("Air")
        
        # Add Coil 'Materials'
        # femm.mi_addmaterial("a+", 1, 1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 100, 0.2)
        # femm.mi_addmaterial("a-", 1, 1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 100, 0.2)
        # femm.mi_addmaterial("b+", 1, 1, 0, -currentDensity, 0, 0, 0, 0, 3, 0, 0, 100, 0.2)
        # femm.mi_addmaterial("b-", 1, 1, 0, currentDensity, 0, 0, 0, 0, 3, 0, 0, 100, 0.2)
        # femm.mi_addmaterial("c+", 1, 1, 0, currentDensity, 0, 0, 0, 0, 3, 0, 0, 100, 0.2)
        # femm.mi_addmaterial("c-", 1, 1, 0, -currentDensity, 0, 0, 0, 0, 3, 0, 0, 100, 0.2)
        
        femm.mi_addmaterial("a+", 1, 1, 0, 0)
        femm.mi_addmaterial("a-", 1, 1, 0, 0)
        femm.mi_addmaterial("b+", 1, 1, 0, -currentDensity)
        femm.mi_addmaterial("b-", 1, 1, 0, currentDensity)
        femm.mi_addmaterial("c+", 1, 1, 0, currentDensity)
        femm.mi_addmaterial("c-", 1, 1, 0, -currentDensity)
        
        self.draw_armuture()
        self.draw_stator()
        
        
        femm_addons.add_bounds(
            origin  = [(self.coilPitch*self.numCoils*1/2), 0],
            radius  = self.coilPitch*self.numCoils,   
        )
        
        femm.mi_saveas("motor.fem")
    
    
    """ Draws the armuture to the simulation space"""
    def draw_armuture(self) -> None:
        # Prototype V0 has no metal core in its armuture
        
        # Draws coils to simulation
        for i in range(0,len(self.coilOrigins)):
            phase = self.phases[i % len(self.phases)]
            
            femm_addons.add_coil(
                origin      = self.coilOrigins[i],
                phase       = phase,
                length      = self.coilLength,
                height      = self.coilHeight,
                innerLength = self.innerLength,
                group       = self.coilGroup
            )
    
    
    """ Draws the stator to the simulation space"""
    def draw_stator(self) -> None:
        # Prototype V0 has no backplate
        
        pole_magnetization = 0
        for i in range(0, self.numPoles):
            if i % 2 == 0:
                pole_magnetization = 90
            else: 
                pole_magnetization = -90
            
            femm_addons.add_pole(
                origin  = self.poleOrigin[i],
                length  = self.poleLength,
                height  = self.poleHeight,
                group   = self.poleGroup,
                magnetizeDirection = pole_magnetization,
                magnetMaterial     = self.poleMaterial
            )
                
        
    """ Takes values from params file and adds them to the class """
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
