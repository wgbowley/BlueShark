"""
Filename: output_writer.py
Author: William Bowley
Version: 0.2 
Date: 2025-07-22

Description:
    Helper functions for exporting simulation output data
    to JSON and CSV formats.
"""

import os
import json
import csv
from typing import List, Dict, Any, Optional


def write_json(data: List[Dict[str, Any]], filename: Optional[str] = "output.json") -> None:
    if not filename.endswith(".json"):
        filename += ".json"

    dir_path = os.path.dirname(filename)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Saved JSON output to {filename}")


def write_csv(data: List[Dict[str, Any]], filename: Optional[str] = "output.csv") -> None:
    if not filename.endswith(".csv"):
        filename += ".csv"

    dir_path = os.path.dirname(filename)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    keys = sorted({key for entry in data for key in entry})

    rows = []
    for entry in data:
        row = {}
        for key in keys:
            value = entry.get(key, "")
            if isinstance(value, (list, tuple)):
                value = "|".join(str(v) for v in value)
            row[key] = value
        rows.append(row)

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved CSV output to {filename}")
