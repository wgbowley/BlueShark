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
from typing import Dict, Any

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

# ------------------------
# Material Management
# ------------------------

MATERIAL_LIB_PATH = "blueshark/lib/femm_materials.json"

KEY_TO_FEMM = {
    "name": "material_name",
    "mu_x": "Mu_x",
    "mu_y": "Mu_y",
    "coercivity": "H_c",
    "j_re": "J_re",
    "conductivity": "Sigma",
    "lam_thickness": "d_lam",
    "hyst_lag_max": "Phi_h",
    "lam_fill": "LamFill",
    "lam_type": "LamType",
    "hyst_lag_x": "Phi_hx",
    "hyst_lag_y": "Phi_hy",
    "num_strands": "NStrands",
    "wire_diameter": "WireD",
}

DEFAULTS: Dict[str, Any] = {
    "name": "Unnamed",
    "mu_x": 1.0,
    "mu_y": 1.0,
    "coercivity": 0.0,
    "j_re": 0.0,
    "conductivity": 0.0,
    "lam_thickness": 0.0,
    "hyst_lag_max": 0.0,
    "lam_fill": 1.0,
    "lam_type": 0,
    "hyst_lag_x": 0.0,
    "hyst_lag_y": 0.0,
    "num_strands": 1,
    "wire_diameter": 0.0,
}

FEMM_ARG_ORDER = [
    "name",
    "mu_x",
    "mu_y",
    "coercivity",
    "j_re",
    "conductivity",
    "lam_thickness",
    "hyst_lag_max",
    "lam_fill",
    "lam_type",
    "hyst_lag_x",
    "hyst_lag_y",
    "num_strands",
    "wire_diameter",
]