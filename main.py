# Libraries
import time
import json
import os
import sys 

import matplotlib.pyplot as plt 
# Modules
from models.prototype_v0 import *

# Example usage
motor = prototype_v0("data/params.yaml")
motor.generate_model()

data = motor.analysis(10)

# Separate into x and y lists
x_vals = [point[0] for point in data]
y_vals = [point[1] for point in data]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals)  # No markers
plt.title("Plot of [x, y] Data Points")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True)
plt.tight_layout()
plt.show()

# Save to JSON
with open("data.json", "w") as f:
    json.dump(data, f, indent=4)