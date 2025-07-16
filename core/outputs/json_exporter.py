"""
Filename: json_exporter.py
Author: William Bowley
Version: 1.0
Date: 2025-07-14
Description:
    Makes it easier to export data as json
"""

# Libaries
import json
import os


def flatten_results(data):
    
    """ Flatten single-element lists in the result dicts for cleaner JSON output. """
    
    flatData = []
    for entry in data:
        flatEntry = {
            k: (v[0] if isinstance(v, list) and len(v) == 1 else v)
            for k, v in entry.items()
        }
        flatData.append(flatEntry)
    return flatData


def save_json(data, filename, directory="."):
    
    """ Saves data as a JSON file to the specified directory."""
    
    if not filename.endswith(".json"):
        filename += ".json"

    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Results saved to {path}")
    return path