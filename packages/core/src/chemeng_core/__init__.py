"""ChemEng Toolbox Core Library.

Core utilities for chemical engineering calculations including:
- Chemical compound database with NIST-validated thermophysical properties
- Unit handling and validation with Pint
- Common utility functions
"""

from chemeng_core import compounds, units

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "compounds",
    "units",
]
