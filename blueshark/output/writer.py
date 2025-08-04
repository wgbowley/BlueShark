"""
Filename: output_writer.py
Author: William Bowley
Version: 1.0 (Experimental)
Date: 2025-08-03

Description:
    Standalone utility functions for exporting simulation output data
    to JSON and CSV formats. Designed for easy integration and modular
    postprocessing of FEMM-based motor simulation results.

Functions:
    - write_output_json(data: List[Dict], filename: str = "output.json", status: bool = true) -> None
    - write_output_csv(data: List[Dict], filename: str = "output.csv",  status: bool = true) -> None
"""

import os
import json
import csv
from typing import List, Dict, Union

def write_output_json(data: List[Dict], filename: str = "output.json", status: bool = True) -> None:
    """
    Write a list of dictionaries to a JSON file.

    Args:
        data (List[Dict]): List of dicts to write.
        filename (str): Output filename (default: "output.json").
    """
    dir_path = os.path.dirname(filename)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    if status == True:
        print(f"Saved output to {filename}")


def write_output_csv(data: List[Dict], filename: str = "output.csv", status: bool = True) -> None:
    """
    Write a list of dictionaries to a CSV file.
    Tuple or list values are flattened with '|' separator.

    Args:
        data (List[Dict]): List of dicts to write.
        filename (str): Output filename (default: "output.csv").
    """
    if not data:
        print("No data to write.")
        return

    dir_path = os.path.dirname(filename)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    # Collect all keys across all dict entries for CSV columns
    keys = set()
    for entry in data:
        keys.update(entry.keys())
    keys = list(keys)

    rows = []
    for entry in data:
        row = {}
        for k in keys:
            v = entry.get(k, "")
            if isinstance(v, (list, tuple)):
                v = "|".join(str(i) for i in v)
            row[k] = v
        rows.append(row)

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)

    if status == True:
        print(f"Saved CSV output to {filename}")
