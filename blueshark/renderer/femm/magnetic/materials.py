"""
Filename: femm_materials.py
Author: William Bowley
Version: 0.2
Date: 2025-08-09
Description:
    Functions for getting FEMM materials or adding new materials.

    (Work in-progress not all materials in the library
     are defined for magnetics)
"""

from typing import Any

import femm


def femm_add_material(material: dict[str, Any]) -> None:
    """
    Adds a material to FEMM using mi_addmaterial,
    extracting properties from a material dict.

    Args:
        material: Material dictionary
    """
    name = material.get("name", "Unknown")

    # Relative permeability
    mu_x, mu_y = material.get("magnetic_relative_permeability", [1.0, 1.0])

    # Permanent magnet coercivity (A/m)
    Hc = material.get("coercivity", 0)

    # Applied source current density (A/mm^2)
    J = material.get("current_density", 0)

    # Electrical conductivity (MS/m)
    Cduct = material.get("electrical_conductivity", 0)

    # Lamination properties
    Lam_d = material.get("lamination_thickness", 0)  # mm
    Lam_fill = material.get("lamination_fill", 1.0)

    LamType_lookup = {
        "solid": 0,
        "lam_x": 1,
        "lam_y": 2,
        "magnet_wire": 3,
        "plain_strand": 4,
        "litz": 5,
        "square_wire": 6
    }
    LamType = LamType_lookup.get(material.get("lamination_type", "solid"), 0)

    # Hysteresis lag angles
    Phi_hmax = material.get("hysteresis_max_angle", 0)
    Phi_hx = material.get("hysteresis_angle_x", 0)
    Phi_hy = material.get("hysteresis_angle_y", 0)

    # Wire-specific properties
    nstr = material.get("number_of_strands", 1)
    dwire = material.get("wire_diameter", 0)

    # Call FEMM function
    femm.mi_addmaterial(
        name,
        mu_x,
        mu_y,
        Hc,
        J,
        Cduct,
        Lam_d,
        Phi_hmax,
        Lam_fill,
        LamType,
        Phi_hx,
        Phi_hy,
        nstr,
        dwire
    )
