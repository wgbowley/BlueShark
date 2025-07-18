"""
Filename: femm_materials.py
Author: William Bowley
Version: 1.0
Date: 2025-07-01
Description:
    Geometry helper functions for FEMM modeling.
"""

import femm
import json

def get_material (materialName: str) -> None:
    femm.mi_getmaterial(materialName)
    

def add_custom_materials(json_file_path: str):

    with open(json_file_path, 'r') as file:
        materials = json.load(file)

    for mat in materials:
        name = mat.get("BlockName", "UnnamedMaterial")
        mu_x = mat.get("Mu_x", 1.0)
        mu_y = mat.get("Mu_y", 1.0)
        coercivity = mat.get("H_c", 0.0)
        current_density = mat.get("J_re", 0.0)
        conductivity = mat.get("Sigma", 0.0)
        lam_thickness = mat.get("d_lam", 0.0)
        hysteresis_lag = mat.get("Phi_h", 0.0)
        lam_fill = mat.get("LamFill", 1.0)
        lam_type = mat.get("LamType", 0)
        hysteresis_lag_x = mat.get("Phi_hx", 0.0)
        hysteresis_lag_y = mat.get("Phi_hy", 0.0)
        num_strands = mat.get("NStrands", 1)
        wire_diameter = mat.get("WireD", 0.0)

        femm.mi_addmaterial(
            name,
            mu_x,
            mu_y,
            coercivity,
            current_density,
            conductivity,
            lam_thickness,
            hysteresis_lag,
            lam_fill,
            lam_type,
            hysteresis_lag_x,
            hysteresis_lag_y,
            num_strands,
            wire_diameter
        )

        print(f"Material '{name}' added successfully.")
