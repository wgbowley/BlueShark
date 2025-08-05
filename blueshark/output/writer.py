"""
Filename: output_writer.py
Author: William Bowley
Version: 1.0
Date: 2025-08-03

Description:
    Standalone utility functions for exporting simulation output data
    to JSON and CSV formats. Designed for easy integration and modular
    postprocessing of FEMM-based motor simulation results.

Functions:
- write_output_json(data, filename = "output.json", status = true):
    Writes the data to json file; Returns None

- write_output_csv(data, filename = "output.csv", status = true, sep = "|"):
    Writes the data to csv file; Returns None
"""

import os
import json
import csv
from typing import List, Dict, Any


def write_output_json(
    data: List[Dict[str, Any]],
    filename: str = "output.json",
    status: bool = True
) -> None:
    """
    Write a list of dictionaries to a JSON file.

    Args:
        data (List[Dict]): List of dicts to write.
        filename (str): Output filename (default: "output.json").
        status (bool): Whether to print confirmation message.

    Returns:
        None
    """
    dir_path = os.path.dirname(filename)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    if status:
        print(f"Saved output to {filename}")


def write_output_csv(
    data: List[Dict[str, Any]],
    filename: str = "output.csv",
    status: bool = True,
    sep: str = "|"
) -> None:
    """
    Write a list of dictionaries to a CSV file.
    Tuple or list values are flattened with the given separator.

    Args:
        data (List[Dict]): List of dicts to write.
        filename (str): Output filename (default: "output.csv").
        status (bool): Whether to print confirmation message.
        sep (str): Separator for flattening list/tuple values (default: "|").

    Returns:
        None
    """
    if not data:
        if status:
            print("Warning: No data given to write")
        return

    dir_path = os.path.dirname(filename)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    keys = sorted({k for entry in data for k in entry})

    rows = []
    for entry in data:
        row = {}
        for k in keys:
            v = entry.get(k, "")
            if isinstance(v, (list, tuple)):
                v = sep.join(str(i) for i in v)
            row[k] = v
        rows.append(row)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)

    if status:
        print(f"Saved CSV output to {filename}")
