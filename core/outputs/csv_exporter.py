"""
Filename: csv_exporter.py
Author: William Bowley
Version: 1.0
Date: 2025-07-17
Description:
    Makes it easier to export data as CSV
"""

# Libraries
import csv
import os


def flatten_results(data):
    """ 
    Flatten single-element lists in the result dicts for cleaner CSV output. 
    """
    flatData = []
    for entry in data:
        flatEntry = {
            k: (v[0] if isinstance(v, list) and len(v) == 1 else v)
            for k, v in entry.items()
        }
        flatData.append(flatEntry)
    return flatData


def save_csv(data, filename, directory="."):
    """ 
    Saves data as a CSV file to the specified directory.
    """
    
    if not filename.endswith(".csv"):
        filename += ".csv"

    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)

    # Flatten data first
    flat_data = flatten_results(data)
    
    if not flat_data:
        print("No data to save.")
        return None
    
    # Extract headers from keys of first entry
    headers = flat_data[0].keys()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(flat_data)

    print(f"Results saved to {path}")
    return path
