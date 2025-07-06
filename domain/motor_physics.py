"""
Filename: motor_physics.py
Author: William Bowley
Version: 1.0
Date: 07 - 06 - 2025
Description:
    This script contains functions that are used to process inputs & outputs 
    of the FEMM Program
    
    Functions:
    - inverted_park_transform(currentFlux, currentForce, electricalAngle)   -> (alpha, beta)
    - inverted_clark_transform(alpha, beta)                                 -> {a,b,c}
    
    - motor_power(lineVoltage, lineCurrent, powerFactor)                    -> (power)
    - wye_motor(voltagePhase, voltageCurrent, powerFactor)                  -> (power)
    - delta_motor(voltagePhase, voltageCurrent, powerFactor)                -> (power)
    
    - mechanical_angle(motorLength, displacement)                           -> (mAngle)
    - electrical_angle(numPolePair, mechanicalAngle)                        -> (eAngle)
    
    - commutation(motorLength, numPairs, currentRMS, numberSamples)         -> [(pa,pb,pc), (pa,pb,pc),...]
"""

from math import *
precision = 6

""" Converts flux-force frame currents to stationary alpha-beta frame currents"""
def inverted_park_transform(
        currentFlux:       float, 
        currentForce:      float, 
        electricalAngle:   float
    ) -> tuple[float, float]:
    
    # Reference: 
    # https://en.wikipedia.org/wiki/Direct-quadrature-zero_transformation
    alpha   = currentFlux * cos(electricalAngle) - currentForce * sin(electricalAngle)
    beta    = currentFlux * sin(electricalAngle) + currentForce * cos(electricalAngle)
    
    return (round(alpha, precision), round(beta, precision))


""" Converts alpha-beta frame currents to 3 phase step currents"""
def inverted_clarke_transform(
        alpha:  float,
        beta:   float,
    ) -> tuple[float, float, float]:
    
    # Reference: 
    # https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_transformation
    a = round(alpha, precision)
    b = round(1/2 * (sqrt(3)*beta - alpha), precision)
    c = round(1/2 * (-sqrt(3)*beta - alpha), precision)
    
    return (a,b,c)


""" Calculates the power (watts) being used by the motor"""
def motor_rms_power(
        lineVoltage:    complex | float,
        lineCurrent:    complex | float,
        powerFactor:    float
    ) -> float:
    
    # Reference: 
    # https://www.electricaltechnology.org/2020/10/power-formulas-ac-dc.html
    power = sqrt(3)*abs(lineVoltage)*abs(lineCurrent)*powerFactor
    
    return power


""" Calculates the line voltages for a wye motor and returns rms power. Assumes power factor of 1"""
def wye_motor(
        voltagePhase: float,
        currentPhase: float,
        powerFactor:  float = 1
    ) -> float:
    
    # Reference: 
    # https://www.allaboutcircuits.com/textbook/alternating-current/chpt-10/three-phase-y-delta-configurations/
    lineVoltage = sqrt(3) / sqrt(2) *voltagePhase
    lineCurrent = currentPhase
    wyePower = motor_rms_power(lineVoltage, lineCurrent, powerFactor)
    
    return wyePower


""" Calculates the line voltages for a delta motor and returns power used. Assumes power factor of 1"""
def delta_motor(
        voltagePhase: float,
        currentPhase: float,
        powerFactor:  float = 1
    ) -> float:
    
    # Reference: 
    # https://www.allaboutcircuits.com/textbook/alternating-current/chpt-10/three-phase-y-delta-configurations/
    lineVoltage = voltagePhase
    lineCurrent = sqrt(3) / sqrt(2) *currentPhase
    deltaPower = motor_rms_power(lineVoltage, lineCurrent, powerFactor)
    
    return deltaPower


""" Calculates the synchronous frequency of the motor for a given speed (m/s)"""
def synchronous_frequency(
        targetSpeed: float,
        polePitch: float
    ) -> float:
    
    frequency = (targetSpeed) / (2*polePitch)
    
    return frequency


""" Gets the mechanical angle of the motor from origin"""
def mechanical_angle(
        motorLength: float,
        displacement: float
    ) -> float:
    
    angle = (2*pi*displacement) / motorLength
    
    return round(angle, precision)


""" Gets the electrical angle of the motor from mechanical angle"""
def electrical_angle(
        numPolePair: int,
        mechanicalAngle
    ):
    
    angle = mechanicalAngle*numPolePair
    
    return round(angle, precision)

""" Gets the commutation profile of the motor over one mechanical rotation"""
def commutation(
        motorLength: float,
        numPairs: int,
        currentsRMS: tuple[float,float],
        numberSamples: int
    ) -> list[(float,float,float)]:
    
    stepSize = motorLength / numberSamples
    
    profile = []
    for step in range(0, numberSamples+1):
        mechanicalAngle = mechanical_angle(motorLength, step*stepSize)
        electricalAngle = electrical_angle(numPairs, mechanicalAngle) # +math.pi 
        
        alpha, beta     = inverted_park_transform(currentsRMS[0], currentsRMS[1], electricalAngle)
        pa, pb, pc      = inverted_clarke_transform(alpha, beta)
        
        profile.append([pa,pb,pc])
        
    return profile