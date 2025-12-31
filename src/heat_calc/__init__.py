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
    CylinderCrossflowConvection,
    FlatPlateConvection,
    FluidProperties,
    FluidState,
    HeatExchangerConfiguration,
    InsulationInput,
    InsulationResult,
    LMTDInput,
    LMTDResult,
    NTUInput,
    NTUResult,
    PipeFlowConvection,
    VerticalPlateNaturalConvection,
    ConvectionResult,
)
from heat_calc.ntu import calculate_ntu
from heat_calc.convection import calculate_convection
from heat_calc.insulation import calculate_insulation

__version__ = "1.0.0"
__author__ = "ChemEng Toolbox Contributors"
__all__ = [
    # LMTD calculations (Phase 3 - MVP)
    "calculate_lmtd",
    "LMTDInput",
    "LMTDResult",
    "FluidState",
    "HeatExchangerConfiguration",
    # NTU calculations (Phase 4)
    "calculate_ntu",
    "NTUInput",
    "NTUResult",
    # Convection calculations (Phase 5)
    "calculate_convection",
    "FluidProperties",
    "FlatPlateConvection",
    "PipeFlowConvection",
    "CylinderCrossflowConvection",
    "VerticalPlateNaturalConvection",
    "ConvectionResult",
    # Insulation calculations (Phase 6)
    "calculate_insulation",
    "InsulationInput",
    "InsulationResult",
]
