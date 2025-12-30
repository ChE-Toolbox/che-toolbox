"""Heat Exchanger Calculations Library.

This module provides a comprehensive library for heat exchanger calculations including:
- LMTD method (Log Mean Temperature Difference)
- NTU method (Number of Transfer Units - Effectiveness)
- Convection correlations (heat transfer coefficients)
- Insulation sizing (economic thickness optimization)

All calculations are validated against published references (Incropera, NIST).
"""

from heat_calc.lmtd import calculate_lmtd
from heat_calc.models import (
    FluidState,
    HeatExchangerConfiguration,
    LMTDInput,
    LMTDResult,
)

__version__ = "1.0.0"
__author__ = "ChemEng Toolbox Contributors"
__all__ = [
    # LMTD calculations (Phase 3 - MVP)
    "calculate_lmtd",
    "LMTDInput",
    "LMTDResult",
    "FluidState",
    "HeatExchangerConfiguration",
    # To be added:
    # - calculate_ntu, NTUInput, NTUResult (Phase 4)
    # - calculate_convection, ConvectionGeometry, ConvectionResult (Phase 5)
    # - calculate_insulation, InsulationInput, InsulationResult (Phase 6)
]
