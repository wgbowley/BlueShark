# An Idealized Linear Motor Design Explorer

## Overview  
This package serves to explore possible linear motor designs quickly, providing easy integration for optimizers. It targets applications such as 3D printers, pick-and-place machines, laser cutters, and other electromechanical systems.

## Installation
The only solver/renderer that comes with the package currently is FEMM. Others will be added in the future if the project grows past
FEMM use cases. 

1. **Install FEMM**  
   FEMM (Finite Element Method Magnetics) is a free, open-source tool for low-frequency electromagnetic simulations, ideal for motor design.

   Download and install FEMM from the official website:  
   [https://www.femm.info/wiki/HomePage](https://www.femm.info/wiki/HomePage)

   > Make sure FEMM is added to your system PATH or installed in the default location (usually `C:\femm42` on Windows) so the simulator can call it without issues.

2. **Install BlueShark**  
   Clone the repository and install the package locally:

   ```bash
   git clone https://github.com/wgbowley/blueshark.git
   cd blueshark
   python setup.py install
