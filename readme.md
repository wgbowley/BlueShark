# An Idealized Linear Motor Design Explorer

## Overview  
This package serves to explore possible linear motor designs quickly, providing easy integration for optimizers. It targets applications such as 3D printers, pick-and-place machines, laser cutters, and other electromechanical systems.

<b>Status:</b><br>
- This version is <b>archived</b> and no longer actively maintained.<br>
- Active development continues in the <code>v1.3-dev</code> branch.<br>
<br>

<b>Limitations:</b><br>
- No support or updates for this version.<br>
- Experimental and loosely structured codebase.<br>
- Some features may be incomplete or unstable.<br>
<br>

<b>Improvements in Newer Versions:</b><br>
- More abstraction (Solver, FEMMSolver, Motor)
- Multi-Physics (Heat & Electromagnetic Sims)
- Motor models are only high level. Independent of Solver

<br>


## Installation

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
