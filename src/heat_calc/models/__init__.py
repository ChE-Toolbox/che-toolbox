"""Pydantic data models for heat exchanger calculations.

This module contains input/output models for each calculation domain:
- LMTD models (LMTDInput, LMTDResult)
- NTU models (NTUInput, NTUResult)
- Convection models (ConvectionGeometry, ConvectionResult)
- Insulation models (InsulationInput, InsulationResult)

All models are Pydantic v2 with Pint unit validation.
"""

from heat_calc.models.base import BaseCalculationInput, BaseCalculationResult
from heat_calc.models.convection_input import (
    CylinderCrossflowConvection,
    FlatPlateConvection,
    FluidProperties,
    PipeFlowConvection,
    VerticalPlateNaturalConvection,
)
from heat_calc.models.convection_results import ConvectionResult
from heat_calc.models.insulation_input import InsulationInput
from heat_calc.models.insulation_results import InsulationResult
from heat_calc.models.lmtd_input import (
    FluidState,
    HeatExchangerConfiguration,
    LMTDInput,
)
from heat_calc.models.lmtd_results import LMTDResult
from heat_calc.models.ntu_input import NTUInput
from heat_calc.models.ntu_results import NTUResult

__all__ = [
    # Base classes
    "BaseCalculationInput",
    "BaseCalculationResult",
    # LMTD models (Phase 3)
    "FluidState",
    "HeatExchangerConfiguration",
    "LMTDInput",
    "LMTDResult",
    # NTU models (Phase 4)
    "NTUInput",
    "NTUResult",
    # Convection models (Phase 5)
    "FluidProperties",
    "FlatPlateConvection",
    "PipeFlowConvection",
    "CylinderCrossflowConvection",
    "VerticalPlateNaturalConvection",
    "ConvectionResult",
    # Insulation models (Phase 6)
    "InsulationInput",
    "InsulationResult",
]
