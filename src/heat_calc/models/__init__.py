"""Pydantic data models for heat exchanger calculations.

This module contains input/output models for each calculation domain:
- LMTD models (LMTDInput, LMTDResult)
- NTU models (NTUInput, NTUResult)
- Convection models (ConvectionGeometry, ConvectionResult)
- Insulation models (InsulationInput, InsulationResult)

All models are Pydantic v2 with Pint unit validation.
"""

from heat_calc.models.base import BaseCalculationInput, BaseCalculationResult
from heat_calc.models.lmtd_input import (
    FluidState,
    HeatExchangerConfiguration,
    LMTDInput,
)
from heat_calc.models.lmtd_results import LMTDResult

__all__ = [
    # Base classes
    "BaseCalculationInput",
    "BaseCalculationResult",
    # LMTD models (Phase 3)
    "FluidState",
    "HeatExchangerConfiguration",
    "LMTDInput",
    "LMTDResult",
    # Story-specific models to be added:
    # NTU: NTUInput, NTUResult
    # Convection: ConvectionGeometry, ConvectionResult
    # Insulation: InsulationInput, InsulationResult
]
