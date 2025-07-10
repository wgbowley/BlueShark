"""
Filename: motor_physics.py
Author: William Bowley
Version: 1.0
Date: 10 - 06 - 2025
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
    
    - commutation(motorLength, numPairs, currentsPeak, numberSamples)         -> [(pa,pb,pc), (pa,pb,pc),...]
"""

from math import *
precision = 6

def inverted_park_transform(
        currentFlux:       float, 
        currentForce:      float, 
        electricalAngle:   float
    ) -> tuple[float, float]:
    
    """ Converts flux-force frame currents to stationary alpha-beta frame currents.
        Only works for 3 phase motors """

    # Reference: 
    # https://en.wikipedia.org/wiki/Direct-quadrature-zero_transformation
    alpha   = currentFlux * cos(electricalAngle) - currentForce * sin(electricalAngle)
    beta    = currentFlux * sin(electricalAngle) + currentForce * cos(electricalAngle)
    
    return (round(alpha, precision), round(beta, precision))


def inverted_clarke_transform(
        alpha:  float,
        beta:   float,
    ) -> tuple[float, float, float]:
    
    """ Converts alpha-beta frame currents to 3 phase step currents.
        Only works for 3 phase motors """
    
    # Reference: 
    # https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_transformation
    a = round(alpha, precision)
    b = round(1/2 * (sqrt(3)*beta - alpha), precision)
    c = round(1/2 * (-sqrt(3)*beta - alpha), precision)
    
    return (a,b,c)


def motor_rms_power(
        lineVoltage:    complex | float,
        lineCurrent:    complex | float,
        powerFactor:    float
    ) -> float:
    
    """ Calculates the power (watts) being used by the motor """
    # Reference: 
    # https://www.electricaltechnology.org/2020/10/power-formulas-ac-dc.html
    power = sqrt(3)*abs(lineVoltage)*abs(lineCurrent)*powerFactor
    
    return power


def wye_motor(
        voltagePhase: float,
        currentPhase: float,
        powerFactor:  float = 1
    ) -> float:
    
    """ Calculates the line voltages for a wye motor and returns rms power. Assumes power factor of 1"""
    
    # Reference: 
    # https://www.allaboutcircuits.com/textbook/alternating-current/chpt-10/three-phase-y-delta-configurations/
    lineVoltage = sqrt(3) / sqrt(2) *voltagePhase
    lineCurrent = currentPhase
    wyePower = motor_rms_power(lineVoltage, lineCurrent, powerFactor)
    
    return wyePower


def delta_motor(
        voltagePhase: float,
        currentPhase: float,
        powerFactor:  float = 1
    ) -> float:
    
    """ Calculates the line voltages for a delta motor and returns power used. Assumes power factor of 1"""
    
    # Reference: 
    # https://www.allaboutcircuits.com/textbook/alternating-current/chpt-10/three-phase-y-delta-configurations/
    lineVoltage = voltagePhase
    lineCurrent = sqrt(3) / sqrt(2) *currentPhase
    deltaPower = motor_rms_power(lineVoltage, lineCurrent, powerFactor)
    
    return deltaPower


def synchronous_frequency(
        targetSpeed: float,
        polePitch: float
    ) -> float:
    
    """ Calculates the synchronous frequency of the motor for a given speed (m/s)"""
    
    frequency = (targetSpeed) / (2*polePitch)
    
    return frequency


def mechanical_angle(
        motorLength: float,
        displacement: float
    ) -> float:
     
    """ Converts linear displacement to mechincal angle in radians """
     
    # motor length is the length corresponding to one full mechanical rotation
    angle = (2*pi*displacement) / motorLength
    angle = angle % (2 * pi) # Restricits domain to [0, 2pi)
    
    return round(angle, precision)


def electrical_angle(
        numPolePair: int,
        mechanicalAngle
    ):
    
    """ Converts mechincal angle (radians) to electrical angle (radians)"""
    
    angle = mechanicalAngle*numPolePair
    
    return round(angle, precision)


def commutation(
        motorLength: float,
        numPairs: int,
        currentsPeak: tuple[float, float],
        numberSamples: int
    ) -> list[tuple[float, float, float]]:

    
    """ Gets the commutation profile of the motor over one mechanical rotation.
        Only works for 3 phase motors """
        
    stepSize = motorLength / numberSamples  # Linear step per sample
    
    profile = []
    for step in range(numberSamples + 1):
        # Displacement -> Mech Angle -> Elec Angle
        mechanicalAngle = mechanical_angle(motorLength, step * stepSize)
        electricalAngle = electrical_angle(numPairs, mechanicalAngle)
        
        # Alpha-beta frame currents -> Phase A, Phase B, Phase C currents
        alpha, beta = inverted_park_transform(currentsPeak[0], currentsPeak[1], electricalAngle)
        pa, pb, pc = inverted_clarke_transform(alpha, beta)
        
        profile.append((pa, pb, pc))
        
    return profile