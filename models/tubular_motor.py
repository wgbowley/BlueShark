"""
Filename: tubular_motor.py
Author: William Bowley
Version: 1.0
Date: 01 - 07 - 2025

Description:
    Base model of a tubular linear motor for use in the optimizer framework.
    Adapted from the "DIY-Linear-Motor" project by cmore839:
        https://github.com/cmore839/DIY-Linear-Motor

    FEMM reference by JuPrgn based on original design.

Class: tublur_motor
    Methods:
        __init__(paramFile: str)       -> None
        generate_model()                -> None
        draw_armature()                 -> None
        draw_stator()                   -> None
        analysis(numberSamples: int)    -> (displacment, force)
        _unpack_params(params: dict)    -> None
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

class tublur_motor:
    
    def __init__(self, paramFile: str) -> None:
        
        # Loads in the yaml file and unpacks it 
        with open(paramFile, 'r') as file:
            params = yaml.safe_load(file)
            
        self._unpack_params(params)
        
        self.simFolder = "data/"
        self.fileName  = "tublur_motor"
        
        # Femm object groups | Bounds is group 0
        self.coilGroup = 1
        self.poleGroup = 2
        
        # Phases 
        self.phases = ['pa','pb','pc']
        
        self.numTurns = motor_generation.number_turns(
            coilLength   = self.coilLength,
            coilHeight   = self.coilHeight,
            wireDiameter = self.coilMaterial,
            wasteFactor  = self.wasteFactor
        )
        
        
        ## CUSTOM FOR TUBLUR MOTORS
        self.coilPitch = self.coilHeight + self.outerLength
        self.polePitch = self.poleHeight
        
        self.frequency = motor_physics.synchronous_frequency(
            targetSpeed = self.velocity,
            polePitch   = self.polePitch
        )
        
        # Coil & Pole Origins (r,z)
        self.coilOrigins = femm_mi_addons.origin_points(
            objectNum   = self.numCoils,
            xPitch      = 0,
            yPitch      = self.coilPitch,
            xOffset     = self.poleLength + self.magneticGap,
            yOffset     = -self.coilPitch*self.numCoils/2
        )
        
        self.poleOrigins = femm_mi_addons.origin_points(
            objectNum   = self.numPoles + 3*self.numPoles,
            xPitch      = 0,
            yPitch      = self.polePitch,
            yOffset     = -self.numPoles*self.polePitch
        )

    
        
    def generate_model(self) -> None:
        
        """ Defines problem & add motor to simulation under self.fileName """
        
        femm.openfemm(1)
        femm.newdocument(0) 
        
        # Defines the magnetic problem 
        femm.mi_probdef(
            0, #self.frequency,
            "millimeters",
            "axi",
            1e-8,
        )
        
        # add phase circuits to simulation
        femm.mi_addcircprop(self.phases[0], 0, 1)
        femm.mi_addcircprop(self.phases[1], 0, 1)
        femm.mi_addcircprop(self.phases[2], 0, 1)
        
        # Adds materials to simulation
        femm.mi_getmaterial(self.poleMaterial)
        femm.mi_getmaterial(str(self.coilMaterial) + "mm")
        femm.mi_getmaterial("Air")
        
        # Creates the motor
        self.draw_armature()
        self.draw_stator()
        femm.mi_selectgroup(self.coilGroup)
        femm.mi_movetranslate(0, -self.poleLength)
        femm_mi_addons.add_bounds((0,0), self.polePitch*self.numPoles*3)
        femm.mi_saveas(self.simFolder + self.fileName + ".fem")
        
        
    def draw_armature(self) -> None:
        
        """ Draws the armature to the simulation space"""
        
        # Draws coils to simulation
        
        ## CUSTOM FOR TUBLUR MOTORS
        
        PATTERN = [0, 1, 0, 1, 0, 1]
        
        for i in range(0,len(self.coilOrigins)):
            phase = self.phases[i % len(self.phases)]   
            
            turn = 0
            if PATTERN[i] == 0:
                turn = self.numTurns
            elif PATTERN[i] == 1:
                turn = -self.numTurns
                
            femm_mi_addons.draw_and_set_properties(
                origin      = self.coilOrigins[i],
                length      = self.coilLength,
                height      = self.coilHeight,
                material    = (str(self.coilMaterial) + 'mm'),
                direction   = 0,
                incircuit   = phase,
                group       = self.coilGroup,
                turns       = turn
            )


    def draw_stator(self) -> None:
        
        """ Draws the stator to the simulation space"""
        
        pole_magnetization = 0
        
        for i in range(0, self.numPoles+3*self.numPoles):
            if i % 2 == 0:
                pole_magnetization = 90
            else: 
                pole_magnetization = -90
            
            femm_mi_addons.add_pole(
                origin  = self.poleOrigins[i],
                length  = self.poleLength,
                height  = self.poleHeight,
                group   = self.poleGroup,
                magnetizeDirection = pole_magnetization,
                magnetMaterial     = self.poleMaterial
            )
    
    
    def analysis(self, numberSamples) -> list:
        
        """ Moves armature to understand the field dynamics & solves """
        
        motorHeight =   self.numPoles*self.poleHeight
        stepSize    =   motorHeight / numberSamples
        numPairs    =   self.numPoles /  2
        
        profile = motor_physics.commutation(motorHeight, numPairs, (0, self.currentPeak), numberSamples)
        
        data = []
        for step in range(0, len(profile)):
            
            # Opens the femm document in background
            femm.openfemm(1)
            femm.opendocument(self.simFolder + self.fileName + ".fem")
            
            # Prevents the armuture from moving from origin on first loop
            if step != 0:
                femm.mi_selectgroup(self.coilGroup)
                femm.mi_movetranslate(0, stepSize)
            
            # Changes the set current in the coils
            femm.mi_setcurrent(self.phases[0], float(profile[step][0]))
            femm.mi_setcurrent(self.phases[1], float(profile[step][1]))
            femm.mi_setcurrent(self.phases[2], float(profile[step][2]))
            
            # femm post-processor
            femm.mi_analyse(1)
            femm.mi_loadsolution()
            
            force = femm_mo_addons.resulstantForce(self.coilGroup, 1)[0]
            femm.closefemm()
            
            # Checks and than removes the result file
            answerFile = os.path.join(self.simFolder + self.fileName + ".ans")
            if os.path.exists(answerFile):
                os.remove(answerFile)
                
            data.append([step*stepSize,  force])
            
        return data
        
        
    def _unpack_params(self, params: dict) -> None:
        """Unpack parameters from YAML config matching this model."""

        model = params.get('model', {})
        self.numCoils     = model['numCoils']
        self.numPoles     = model['numPoles']
        self.currentPeak  = model['currentPeak']
        self.axialLength  = model['axialLength']
        self.wasteFactor  = model['wasteFactor']
        self.velocity     = model['operatingSpeed']

        coil = params.get('coil', {})
        self.coilLength   = coil['length']
        self.coilHeight   = coil['height']
        self.outerLength  = coil['outerLength']
        self.coilMaterial = coil['material']
        self.magneticGap  = coil['magneticGap']

        pole = params.get('pole', {})
        self.poleLength   = pole['length']
        self.poleHeight   = pole['height']
        self.poleMaterial = pole['material']
