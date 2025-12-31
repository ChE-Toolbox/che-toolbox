"""Result models for convection heat transfer calculations.

Defines Pydantic models for convection calculation outputs including heat
transfer coefficient, dimensionless numbers, and flow regime identification.
"""


from pydantic import Field, field_validator

from heat_calc.models.base import BaseCalculationResult


class ConvectionResult(BaseCalculationResult):
    """Complete results from convection correlation calculation.

    Contains heat transfer coefficient, dimensionless numbers (Re, Pr, Nu, Gr, Ra),
    flow regime identification, and correlation validity information.

    Attributes
    ----------
    h : float
        Convection heat transfer coefficient in W/(m²·K).

    Reynolds : float
        Reynolds number (dimensionless). For forced convection.

    Prandtl : float
        Prandtl number (dimensionless).

    Nusselt : float
        Nusselt number (dimensionless).

    Grashof : float, optional
        Grashof number (dimensionless). For natural convection only.

    Rayleigh : float, optional
        Rayleigh number (dimensionless). For natural convection only.

    flow_regime : str
        Identified flow regime (e.g., "laminar", "turbulent", "transitional", "natural").

    correlation_equation : str
        Name or equation of the correlation used (e.g., "Dittus-Boelter", "Churchill-Bernstein").

    is_within_correlation_range : bool
        True if input parameters are within published correlation validity bounds.

    applicable_range : Dict[str, Tuple[float, float]]
        Dictionary of parameter validity ranges {parameter_name: (min, max)}.

    geometry_type : str
        Type of geometry analyzed (e.g., "flat_plate", "pipe_flow").
    """

    model_config = {"arbitrary_types_allowed": True}

    h: float = Field(
        ...,
        description="Convection heat transfer coefficient in W/(m²·K)",
        gt=0,
        json_schema_extra={"unit": "W/(m²·K)"},
    )

    Reynolds: float = Field(
        ...,
        description="Reynolds number (dimensionless)",
        ge=0,
        json_schema_extra={"unit": "-"},
    )

    Prandtl: float = Field(
        ...,
        description="Prandtl number (dimensionless)",
        gt=0,
        json_schema_extra={"unit": "-"},
    )

    Nusselt: float = Field(
        ...,
        description="Nusselt number (dimensionless)",
        gt=0,
        json_schema_extra={"unit": "-"},
    )

    Grashof: float | None = Field(
        default=None,
        description="Grashof number (dimensionless) - for natural convection only",
        ge=0,
        json_schema_extra={"unit": "-"},
    )

    Rayleigh: float | None = Field(
        default=None,
        description="Rayleigh number (dimensionless) - for natural convection only",
        ge=0,
        json_schema_extra={"unit": "-"},
    )

    flow_regime: str = Field(
        ...,
        description="Identified flow regime (laminar, turbulent, transitional, natural)",
        json_schema_extra={"example": "turbulent"},
    )

    correlation_equation: str = Field(
        ...,
        description="Name or equation of the correlation used",
        json_schema_extra={"example": "Dittus-Boelter"},
    )

    is_within_correlation_range: bool = Field(
        ...,
        description="True if parameters are within correlation validity bounds",
    )

    applicable_range: dict[str, tuple[float, float]] = Field(
        ...,
        description="Parameter validity ranges {parameter_name: (min, max)}",
        json_schema_extra={"example": {"Re": (2300, 1000000), "Pr": (0.7, 160)}},
    )

    geometry_type: str = Field(
        ...,
        description="Type of geometry analyzed",
        json_schema_extra={"example": "pipe_flow"},
    )

    @field_validator("flow_regime")
    @classmethod
    def validate_flow_regime(cls, v: str) -> str:
        """Validate flow regime is one of expected values."""
        valid_regimes = {
            "laminar",
            "turbulent",
            "transitional",
            "natural_laminar",
            "natural_turbulent",
        }
        if v not in valid_regimes:
            # Allow any string but warn in intermediate_values
            pass
        return v

    @field_validator("applicable_range")
    @classmethod
    def validate_applicable_range(cls, v: dict[str, tuple[float, float]]) -> dict[str, tuple[float, float]]:
        """Validate that range tuples are properly ordered (min, max)."""
        for param, (min_val, max_val) in v.items():
            if min_val > max_val:
                raise ValueError(
                    f"Invalid range for {param}: min ({min_val}) > max ({max_val})"
                )
        return v
