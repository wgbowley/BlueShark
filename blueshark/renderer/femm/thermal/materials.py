"""
Filename: femm_materials.py
Author: William Bowley
Version: 0.3
Date: 2025-09-12
Description:
    Functions for getting FEMM materials, adding new materials, or modifying existing ones.
    Includes hi_modifymaterial wrapper for volumetric heating and thermal properties.
"""

from typing import Any
import femm


def femm_add_material(material: dict[str, Any]) -> None:
    """
    Adds a thermal material to FEMM using hi_addmaterial,
    extracting properties from a material dict.

    Args:
        material: Material dictionary
    """
    name = material.get("name", "Unknown")

    # Thermal properties
    thermal = material.get("thermal", {})
    kx = thermal.get("thermal_conductivity_x", 0)
    ky = thermal.get("thermal_conductivity_y", 0)
    qv = thermal.get("volumetric_heat_source", 0)

    # Take temp_dependence array (TKValues) as-is
    kt = thermal.get("temp_dependence", [])

    # Call FEMM function
    femm.hi_addmaterial(name, kx, ky, qv, kt)


def femm_modify_material(
    block_name: str,
    propnum: int,
    value: Any
) -> None:
    """
    Modifies a property of an existing FEMM material 
    block without redefining the whole material.

    Args:
        block_name: Name of the block/material to modify
        propnum: Property number to change
            0 = BlockName (rename)
            1 = kx (thermal conductivity x/r)
            2 = ky (thermal conductivity y/z)
            3 = qs (volumetric heat generation)
            4 = kt (volumetric heat capacity)
        value: New value to assign
    """
    femm.hi_modifymaterial(block_name, propnum, value)
