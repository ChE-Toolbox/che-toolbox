"""Pydantic data models for heat exchanger calculations.

This module contains input/output models for each calculation domain:
- LMTD models (LMTDInput, LMTDResult)
- NTU models (NTUInput, NTUResult)
- Convection models (ConvectionGeometry, ConvectionResult)
- Insulation models (InsulationInput, InsulationResult)

All models are Pydantic v2 with Pint unit validation.
"""

from heat_calc.models.base import BaseCalculationInput, BaseCalculationResult

__all__ = [
    "BaseCalculationInput",
    "BaseCalculationResult",
    # Story-specific models to be added:
    # LMTD: LMTDInput, LMTDResult, FluidState, HeatExchangerConfiguration
    # NTU: NTUInput, NTUResult
    # Convection: ConvectionGeometry, ConvectionResult
    # Insulation: InsulationInput, InsulationResult
]
