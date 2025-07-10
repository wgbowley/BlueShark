"""
Filename: femm_addons.py
Author: William Bowley
Version: 1.0
Date: 01 - 07 - 2025
Description:
    This script contains addon functions for the FEMM post processor
    
    addons:
    - resultantForce(group, method)                 -> (magnitude, angle)
    - circuitAnalysis(circuitName)                  -> (peakVoltage, inductance)
    - densityPlotFrame(origin, length, height, path)-> None
"""

# Libraries
import femm
import math


def resulstantForce(
        group: int,
        method: int = 0
    ) -> tuple[float, float]:
    
    """ Calculates the force experienced by an object """
    
    femm.mo_groupselectblock(group)
    
    # Method 1: Steady-state lorentz force
    if method == 1:
        fx = femm.mo_blockintegral(11)
        fy = femm.mo_blockintegral(12)
    # Else: Steady-state weighted stress tensor force 
    else: 
        fx = femm.mo_blockintegral(18)
        fy = femm.mo_blockintegral(19)
    
    femm.mo_clearblock()
    
    # Gets resulstant force vector & angle to the horizontal 
    magnitude = math.sqrt(fx**2+fy**2)
    #angle = math.degrees(math.atan(fy/fx)) Was causing problems 
    
    return (magnitude, 0) #,angle)


def circuitAnalysis(circuitName: str) -> tuple[float, float]:
    peakVoltage     = 0
    inductance      = 0

    " Calculates the inductance and peak voltage in the circuit element"
    
    # Gets circuit properties from FEMM post processor
    circuitProps    = femm.mo_getcircuitproperties(circuitName)
    current         = circuitProps[0]
    peakVoltage     = circuitProps[1]
    fluxLinkage     = circuitProps[2]
    
    # Inductance = (Flux Linkage) / current 
    if current != 0:
        inductance = fluxLinkage / current
    else:
        inductance = 0
    
    return (peakVoltage, inductance)


def densityPlotFrame(
        origin: tuple[float, float],
        length: float, 
        height: float,
        path: str
    ) -> None:
    
    """ Takes a density plot of a frame """
    
    # Calculates the vertex positions for the frame
    bLVertex = (origin[0], origin[1])
    tRVertex = (origin[0] + length, origin[1] + height)
    
    # Makes the frame size very large.
    femm.mo_resize(4000, 4000)
    
    # Zooms in, enables density plot sets range (0.5T, 0T) & Saves image
    femm.mo_zoom(bLVertex[0], bLVertex[1], tRVertex[0], tRVertex[1])
    femm.mo_showdensityplot(1,0,0.5,0,"bmag")
    femm.mo_savebitmap(path)