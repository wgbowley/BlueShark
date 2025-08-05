"""
File: constants.py
Author: William Bowley
Version: 1.0
Date: 2025-08-05

Description:
    Global constants for simulation precision, numerical tolerance, and
    failure thresholds. These values are rarely changed and are meant to
    remain consistent across the framework.
"""

from math import pi

# ------------------------
# Fundamental Math Constants
# ------------------------

TWO_PI: float = 2 * pi
# 2π, useful for physics calculations (e.g., electrical phase)

# ------------------------
# Simulation Control Constants
# ------------------------

EPSILON: float = 1e-10
# Minimum threshold to treat floating-point values as effectively zero.
# Prevents division-by-zero errors or instability due to numerical noise.

PRECISION: int = 6
# Default number of decimal places for rounding or formatting output.

MAXIMUM_FAILS: int = 5
# Maximum allowed consecutive simulation failures (e.g., FEMM not converging)
# before aborting a run or skipping a parameter set.
