# Libraries
import time
import json
import os
import sys

import matplotlib.pyplot as plt

# Modules
from models.tubular_motor import *

precision = 6
# Example usage
motor = tublur_motor("data/tubular.yaml")
motor.generate_model()

data = motor.analysis(1000)

# Separate into x and y lists
x_vals = [point[0] for point in data]
y_vals = [point[1] for point in data]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals)
plt.title("Cmore Motor Force Vs Displacement @ 3A RMS")
plt.xlabel("Displacement (mm)")
plt.ylabel("Force (N)")
plt.grid(True)

# Force y-axis to start at 0
plt.ylim(0, max(y_vals) * 1.1)

plt.tight_layout()
plt.show()

# Save to JSON
with open("data.json", "w") as f:
    json.dump(data, f, indent=4)
