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

import logging
import pathlib
import json
from typing import Any, List, Dict
from importlib import resources

import femm

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


def _extract_material_names(
    materials: list[dict[str, Any]]
) -> list[str]:
    """
    Extracts unique material names from a list of material dictionaries.

    Args:
        materials: A list of dictionaries defining materials.

    Returns:
        A list of unique material names.
    """
    names = set()
    for m in materials:
        for key in ("BlockName", "material_name", "name"):
            val = m.get(key)
            if isinstance(val, str) and val:
                names.add(val)
                break
    return list(names)


def _normalize_material_input(
    material: dict[str, Any]
) -> dict[str, Any]:
    """
    Normalizes a material dictionary by mapping keys and filling defaults.

    Args:
        material: A dictionary defining the material's properties.

    Returns:
        A new dictionary with normalized keys and filled defaults.

    Raises:
        ValueError: If the input is not a dictionary or
                    contains an invalid key.
    """
    if not isinstance(material, dict):
        raise ValueError("Material must be a dictionary or mapping.")

    normalized = {}

    for key, value in material.items():
        key_lower = key.lower()
        if key_lower in KEY_TO_FEMM:
            normalized[key_lower] = value
        else:
            for friendly, femm_key in KEY_TO_FEMM.items():
                if key == femm_key:
                    normalized[friendly] = value
                    break
            else:
                if key_lower in {"material_name", "blockname"}:
                    normalized["name"] = value
                else:
                    valid_keys = sorted(
                        list(KEY_TO_FEMM.keys()) + list(KEY_TO_FEMM.values())
                    )
                    msg = (
                        f"Invalid material key '{key}'. "
                        f"Valid keys: {valid_keys}"
                    )
                    logging.critical(msg)
                    raise ValueError(msg)

    for k, default in DEFAULTS.items():
        normalized.setdefault(k, default)

    return normalized


def load_materials(path: str | None = None) -> List[Dict[str, any]]:
    """
    Loads all materials from a json file and performs validation


    Args:
        path: Optional file path to the material library. If None,
              loads from package resources.

    Returns:
        A list of material dictionaries.
    """

    if path is None:
        try:
            with resources.open_text(
                "blueshark.lib",
                "femm_magnetic_materials.json"
            ) as f:
                data = json.load(f)
        except Exception as e:
            msg = (
                f"Failed to load material library from package resources: {e}"
            )
            logging.critical(msg)
            raise RuntimeError(msg) from e
    else:
        lib_path = pathlib.Path(path)
        if not lib_path.exists():
            msg = f"Material library not found: {lib_path}"
            logging.error(msg)
            raise RuntimeError(msg)
        try:
            with lib_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            msg = f"Failed to load material library {lib_path}: {e}"
            logging.critical(msg)
            raise RuntimeError(msg) from e

    if not isinstance(data, list):
        msg = "Material library JSON must be a list."
        logging.critical(msg)
        raise ValueError(msg)

    return data


def add_femm_material(
    materials: list[dict[str, Any]],
    material_name: str,
) -> None:
    """
    Loads a material from FEMM's internal library after validating the name.

    Args:
        materials: A list of all available materials.
        material_name: The name of the material to be added.

    Raises:
        ValueError: If the material_name is not found in the library.
        RuntimeError: If FEMM's API fails to load the material.
    """
    available = _extract_material_names(materials)

    if material_name not in available:
        msg = (
            f"Material '{material_name}' not found in library."
            f"Available: {sorted(available)}"
        )
        logging.error(msg)
        raise ValueError(msg)

    try:
        femm.mi_getmaterial(material_name)
    except Exception as e:
        msg = f"FEMM failed to load material '{material_name}': {e}"
        logging.critical(msg)
        raise RuntimeError(msg) from e


def add_custom_material(
    material: dict[str, Any]
) -> None:
    """
    Adds a custom material to the FEMM simulation
    space after normalizing the input.

    Args:
        material: A dictionary defining the material to be added.

    Raises:
        ValueError: If the input dictionary is invalid.
        RuntimeError: If FEMM's API fails to add the material.
    """
    norm = _normalize_material_input(material)

    args = [norm[k] for k in FEMM_ARG_ORDER]
    material_name = str(norm.get("name", "unnamed"))

    try:
        femm.mi_addmaterial(*args)
    except Exception as e:
        msg = f"FEMM Failed to add material '{material_name}': {e}"
        logging.critical(msg)
