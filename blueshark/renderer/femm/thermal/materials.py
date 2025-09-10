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
                "femm_heat_materials.json"
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
        femm.hi_getmaterial(material_name)
    except Exception as e:
        msg = f"FEMM failed to load material '{material_name}': {e}"
        logging.critical(msg)
        raise RuntimeError(msg) from e
