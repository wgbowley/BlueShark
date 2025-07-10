"""
Filename: prototype_v0
Author: William Bowley
Version: 1.1
Date: 01 - 07 - 2025
Description:
    This script describes the POC motor or prototype V0 which was made on 22-04-2025.
    It models the same configuration of motor but with your different params.
    
Class prototype_v0:
    functions:
        _init_(paramFile)       -> None
        generate_model()        -> None
        draw_armature()         -> None
        draw_stator()           -> None
        analysis(numberSamples) -> (displacement, force)
        _unpack_params(params)  -> None
            
"""

# Libraries
import yaml
import femm
import os

# Modules 
from application.simulate import femm_mi_addons
from application.simulate import femm_mo_addons
from domain import motor_generation
from domain import motor_physics

class prototype_v0:
    
    def __init__(self, paramFile: str) -> None:
        
        # Loads in the yaml file and unpacks it
        with open(paramFile, "r") as file:
            params = yaml.safe_load(file)
        self._unpack_params(params)
        
        self.simFolder = "data/"
        self.fileName  = "prototypeV0"
        
        # Femm object groups 
        # Bounds is group 0 
        self.coreGroup = 1
        self.coilGroup = 2
        self.poleGroup = 3
        
        # Phases
        self.phases = ['pa','pb','pc']
        
        self.turns  = motor_generation.number_turns(
            coilLength = self.coilLength,
            coilHeight = self.coilHeight,
            wireDiameter= self.coilMaterial,
            wasteFactor= self.wasteFactor
        )
        
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
            targetSpeed = self.velocity,
            polePitch   = self.polePitch
        )
        
        # Coil & Pole Origins (x,y)
        self.coilOrigins = femm_mi_addons.origin_points(
            objectNum   = self.numCoils,
            xPitch      = self.coilPitch,
            yPitch      = 0
        )
        
        self.poleOrigin = femm_mi_addons.origin_points(
            objectNum   = self.numPoles + 9,
            xPitch      = self.polePitch,
            yPitch      = 0,
            yOffset     = -self.magneticGap
        )
    
    
    def generate_model(self) -> None:
        
        """ Defines problem & add motor to simulation under self.fileName """
        
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
        
        # add phase circuits to simulation
        femm.mi_addcircprop(self.phases[0], 0, 1)
        femm.mi_addcircprop(self.phases[1], 0, 1)
        femm.mi_addcircprop(self.phases[2], 0, 1)
        
        # Adds materials to simulation
        femm.mi_getmaterial(self.backIronMaterial)
        femm.mi_getmaterial(self.armatureMaterial)
        femm.mi_getmaterial(self.poleMaterial)
        femm.mi_getmaterial(str(self.coilMaterial) + "mm")
        femm.mi_getmaterial("Air")
        
        # Creates the motor
        self.draw_armature()
        self.draw_stator()
        
        # Add Neumann outer edges with air as the medium 
        femm_mi_addons.add_bounds(
            origin  = [(self.coilPitch*self.numCoils*1/2), 0],
            radius  = 2*self.coilPitch*self.numCoils,   
        )
        
        # Saves the file to "self.simFolder/self.fileName.fem"
        femm.mi_saveas(self.simFolder + self.fileName + ".fem")
    
    
    def draw_armature(self) -> None:
        # Prototype V0 has no metal core in its armature
        
        """ Draws the armature to the simulation space"""
        
        # Draws coils to simulation
        for i in range(0,len(self.coilOrigins)):
            phase = self.phases[i % len(self.phases)]
            
            femm_mi_addons.add_coil(
                origin      = self.coilOrigins[i],
                phase       = phase,
                length      = self.coilLength,
                height      = self.coilHeight,
                turns       = self.turns,
                material    = (str(self.coilMaterial) + 'mm'),
                innerLength = self.innerLength,
                group       = self.coilGroup
            )
    
    
    def draw_stator(self) -> None:
        # Prototype V0 has no backplate
        
        """ Draws the stator to the simulation space"""
        
        pole_magnetization = 0
        
        for i in range(0, self.numPoles+9):
            if i % 2 == 0:
                pole_magnetization = 90
            else: 
                pole_magnetization = -90
            
            femm_mi_addons.add_pole(
                origin  = self.poleOrigin[i],
                length  = self.poleLength,
                height  = self.poleHeight,
                group   = self.poleGroup,
                magnetizeDirection = pole_magnetization,
                magnetMaterial     = self.poleMaterial
            )
                
    
    def analysis(self, numberSamples) -> list:
        
        """ Moves armature to understand the field dynamics & solves """
        
        motorLength =   self.coilPitch*self.numCoils
        stepSize    =   motorLength / numberSamples
        numPairs    =   self.numPoles /  2
        
        profile = motor_physics.commutation(motorLength, numPairs, (0, self.currentPeak), numberSamples)
        
        data = []
        for step in range(0, len(profile)):
            
            # Opens the femm document in background
            femm.openfemm(1)
            femm.opendocument(self.simFolder + self.fileName + ".fem")
            
            # Prevents the armuture from moving from origin on first loop
            if step != 0:
                femm.mi_selectgroup(self.coilGroup)
                femm.mi_movetranslate(stepSize, 0)
            
            # Changes the set current in the coils
            femm.mi_setcurrent(self.phases[0], float(profile[step][0]))
            femm.mi_setcurrent(self.phases[1], float(profile[step][1]))
            femm.mi_setcurrent(self.phases[2], float(profile[step][2]))
            
            # femm post-processor
            femm.mi_analyse(1)
            femm.mi_loadsolution()
            
            force = femm_mo_addons.resulstantForce(self.coilGroup)[0]
            femm.closefemm()
            
            # Checks and than removes the result file
            answerFile = os.path.join(self.simFolder + self.fileName + ".ans")
            if os.path.exists(answerFile):
                os.remove(answerFile)
                
            data.append([step*stepSize,  force])
            
        return data
     
        
    def _unpack_params(self, params: dict) -> None:
        
        """Unpack parameters from YAML config matching this model."""

        # Motor Model & Simulation Parameters
        model = params.get('model', {})
        self.numCoils       = model.get('numCoils', 0)
        self.numPoles       = model.get('numPoles', 0) 
        self.currentPeak    = model.get('currentPeak', 0.0)
        self.axialLength    = model.get('axialLength', 0.0)
        self.wasteFactor    = model.get('wasteFactor', 0.0)
        self.velocity       = model.get('operatingSpeed', 0.0)

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

