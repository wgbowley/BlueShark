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

    profile = commutation(
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

        if step != 0:
            femm.mi_selectgroup(motor.movingGroup)
            motor.step(stepSize)

        motor.set_currents(profile[step])

        femm.mi_analyse(1)
        femm.mi_loadsolution()

        stepContext = dict(baseContext)
        stepResults = outputSelector.compute(stepContext)

        stepResults["position"] = position
        results.append(stepResults)

        femm.closefemm()

        answerFile = motor.femmdocumentpath + ".ans"
        if os.path.exists(answerFile):
            os.remove(answerFile)

    return results