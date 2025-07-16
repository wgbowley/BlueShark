"""
Filename: rotational_analysis.py
Author: William Bowley
Version: 1.0
Date: 2025-07-14

Description:
    Performs a single mechanical rotation analysis of a motor by:
    - Computing a full 3-phase commutation profile
    - Stepping through each sample
    - Applying phase currents
    - Gathering selected outputs via OutputSelector
"""

import femm
import os
import time
from typing import Any

# Modules
from core.simulation.motor_interface import MotorBase
from core.simulation.output_selector import OutputSelector
from domain.physics.commutation import *


def rotational_analysis(
        motor: MotorBase, 
        outputSelector: OutputSelector, 
        baseContext: dict[str, Any],
        numSamples: int
    ) -> list[dict]:

    motorCir = motor.motorCircumference
    stepSize = motorCir / numSamples
    
    profile = rotational_commutation(
        circumference   = motorCir,
        numPairs        = motor.numberPoles // 2,
        currentsPeak    = motor.peakCurrents,
        numberSamples   = numSamples
    )

    results = []

    for step in range(numSamples):
        position = step * stepSize

        femm.openfemm(1)
        femm.opendocument(motor.femmdocumentpath + ".fem")

        # Prevents the armuture from moving on the first step
        if step != 0:
            femm.mi_selectgroup(motor.movingGroup)
            motor.step(stepSize)

        motor.set_currents(profile[step])

        # Was having a werid error with femm thats why I added this
        for attempt in range(5):
            try:
                femm.mi_analyse(1)
                femm.mi_loadsolution()
                break 
            except Exception as e:
                print(f"Attempt {attempt+1} failed with error: {e}")
                if attempt == 1:
                    raise  
                time.sleep(0.5)  

        stepContext = dict(baseContext)
        stepResults = outputSelector.compute(stepContext)

        stepResults["position"] = position
        results.append(stepResults)

        femm.closefemm()

        answerFile = motor.femmdocumentpath + ".ans"
        if os.path.exists(answerFile):
            os.remove(answerFile)

    return results