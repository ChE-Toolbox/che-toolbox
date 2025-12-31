"""IAPWS-IF97 region implementations.

Each region covers different ranges of pressure and temperature.
- Region 1: Compressed liquid (low T, high P)
- Region 2: Superheated steam (low P, high T)
- Region 3: Supercritical fluid (high P, high T, near critical point)
- Saturation: Two-phase region boundaries
"""

from . import region1, region2, region3

__all__ = ["region1", "region2", "region3"]
