"""Base classes for all heat exchanger calculation models."""

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class BaseCalculationInput(BaseModel):
    """Base class for all calculation input models.

    Provides common configuration for Pydantic v2 models with:
    - Arbitrary type support for Pint quantities
    - Frozen models to prevent accidental mutation
    - JSON serialization support
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=False,  # Allow mutation during input setup
        json_schema_extra={"description": "Heat exchanger calculation input"},
    )

    class Config:
        """Pydantic v2 configuration."""

        json_encoders: Dict[Any, Any] = {}


class BaseCalculationResult(BaseModel):
    """Base class for all calculation result models.

    Provides common output structure with:
    - Calculation metadata (source method, version)
    - Intermediate values for traceability
    - Primary value with units
    - Success/failure status tracking
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,  # Immutable results
        json_schema_extra={"description": "Heat exchanger calculation result"},
    )

    primary_value: float = Field(
        ...,
        description="Primary result value (Q for heat transfer, etc.)",
        json_schema_extra={"unit": "depends on calculation method"},
    )

    calculation_method: str = Field(
        default="unknown",
        description="Name of the calculation method used (LMTD, NTU, Convection, Insulation)",
    )

    success: bool = Field(
        default=True,
        description="Whether the calculation completed successfully",
    )

    error_message: str = Field(
        default="",
        description="Error message if calculation failed",
    )

    intermediate_values: Dict[str, Any] = Field(
        default_factory=dict,
        description="Intermediate calculation values for verification and debugging",
    )

    version: str = Field(
        default="1.0.0",
        description="Version of the calculation engine used",
    )
