"""
Filename: flat_motor.py
Author: William Bowley
Version: 1.0
Date: 2025-07-01

Description:
    Base model of a flat linear motor for use in the motor simulation and optimization framework.
    
    This class implements the MotorBase interface and provides core functionality such as:
    - Geometry setup from YAML config
    - FEMM-compatible drawing
    - Stepping through linear positions
    - Applying 3-phase currents
"""

# Libraries
import yaml
import femm
import os 

# Modules
from core.simulation.motor_interface import *
from core.femm_preprocess.femm_geometry import *
from core.femm_preprocess.femm_boundary import *
from core.femm_preprocess.femm_materials import *
from core.femm_preprocess.femm_draw import *
from domain.generation.coil import *
from domain.generation.pitch import *

class FlatMotor(MotorBase):
    
    def __init__(self, configFile):
        
        self.unpack(configFile)
        
        self.simFolder = "data/flat"
        self.fileName = "flat_motor"
        
        os.makedirs(self.simFolder, exist_ok=True)
        
        # Objects & circuits
        self.boundary = 0
        self.coilGroup = 1
        self.poleGroup = 2
        self.phases = ['pa', 'pb', 'pc']
        self.outerPairs = 4
    
    
    def generate(self):
        
        self.numTurns = number_turns(
            self.coilLength,
            self.coilHeight,
            self.coilMaterial,
            self.wasteFactor
        )
        
        self.slotPitch = self.coilOuterSpace + self.coilLength + 1/2*self.coilInterSpace
        self.polePitch = pole_pitch(self.numeberSlots, self.numberPoles, self.slotPitch)
        
        self.slotOrigins = origin_points(
            self.numeberSlots,
            self.slotPitch,
            0
        )

        self.poleOrigins = origin_points(
            self.numberPoles + (4*self.outerPairs),
            self.polePitch,
            0,
            xOffset = - 2* self.outerPairs * self.polePitch,
            yOffset = -(self.magneticGap+self.poleHeight)
        )
        
        femm.openfemm(1)
        femm.newdocument(0)
        
        # Defines the magnetic problem
        femm.mi_probdef(0, "millimeters", "planar", 1e-8, self.axialLength) 
        
        # Add phase circuits to simulation
        femm.mi_addcircprop(self.phases[0], 0, 1)
        femm.mi_addcircprop(self.phases[1], 0, 1)
        femm.mi_addcircprop(self.phases[2], 0, 1)
        
        # Add materials to simulation
        get_material(self.poleMaterial)
        get_material(str(self.coilMaterial) + "mm")
        get_material("Air")
        
                # Creates motor geometry 
        self.draw_armuture()
        self.draw_stator()
        
        # Boundary
        boundaryOrigin = (0,self.poleHeight)
        radius         = self.numPoles * (self.outerPairs * self.polePitch + self.polePitch)
        
        add_bounds(boundaryOrigin, radius)
        femm.mi_selectgroup(self.coilGroup)
        femm.mi_clearselected()
        
        femm.mi_saveas(self.simFolder + "/" + self.fileName + ".fem")
    
               
           
    def draw_armuture(self) -> None:
        """Draws the armature to the simulation space"""
        
        for slot_idx in range(len(self.slotOrigins)):
            # Repeat each phase twice before switching
            phase = self.phases[(slot_idx // 2) % len(self.phases)]
            
            # Alternate turn direction every slot
            turn = self.numTurns if slot_idx % 2 == 0 else -self.numTurns

            draw_and_set_properties(
                origin      = self.slotOrigins[slot_idx],
                length      = self.coilLength,
                height      = self.coilHeight,
                material    = f"{self.coilMaterial}mm",
                direction   = 0,
                incircuit   = phase,
                group       = self.coilGroup,
                turns       = turn
            )
            
        
    def draw_stator(self) -> None:
        
        """ Draws the stator to the simulation space"""
        
        pole_magnetization = 0
        
        for pole in range((4 * self.outerPairs) + self.numPoles):
            if pole % 2 == 0:
                pole_magnetization = 90
            else: 
                pole_magnetization = -90
            
            draw_and_set_properties(
                origin      =   self.poleOrigins[pole],
                length      =   self.poleLength,
                height      =   self.poleHeight,
                group       =   self.poleGroup,
                direction   =   pole_magnetization,
                incircuit   =   "<none>",
                material    =   self.poleMaterial,
                turns       =   0
            )
    

    def set_currents(self, currents):
        femm.mi_setcurrent(self.phases[0], float(currents[0]))
        femm.mi_setcurrent(self.phases[1], float(currents[1]))
        femm.mi_setcurrent(self.phases[2], float(currents[2]))
    
    
    def step(self, step):
        femm.mi_selectgroup(self.movingGroup)
        femm.mi_movetranslate(step, 0)
        femm.mi_clearselected()
    
    
    @property
    def femmdocumentpath(self) -> str:
        return self.simFolder + "/" + self.fileName


    @property
    def motorCircumference(self) -> float:
        return self.poleHeight*self.numPoles

    @property
    def movingGroup(self) -> int:
        return self.coilGroup


    @property
    def numberPoles(self) -> int:
        return self.numPoles


    @property
    def numeberSlots(self) -> int:
        return self.numSlots


    @property
    def peakCurrents(self) -> tuple[float, float]:
        return (self.iFluxPeak, self.iForcePeak)
    
    
    def unpack(self, configFile):
        with open(configFile, 'r') as file:
            params = yaml.safe_load(file)

        model = params.get('model', {})
        self.numSlots     = model['numSlots']
        self.numPoles     = model['numPoles']     
        self.iForcePeak   = model['iForcePeak']
        self.iFluxPeak    = model['iFluxPeak']
        
        self.axialLength  = model['axialLength']
        self.wasteFactor  = model['wasteFactor']


        coil = params.get('coil', {})
        self.coilLength     = coil['length']          
        self.coilHeight     = coil['height']
        self.coilInterSpace = coil['interSpacing']    
        self.coilOuterSpace = coil['outerSpacing']    
        self.coilMaterial   = coil['material']
        self.magneticGap    = coil['magneticGap']


        pole = params.get('pole', {})
        self.poleLength   = pole['length']            
        self.poleHeight   = pole['height']
        self.poleMaterial = pole['material']
