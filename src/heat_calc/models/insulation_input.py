"""Input models for insulation sizing and economic optimization calculations.

Defines Pydantic models for insulation sizing inputs, including pipe geometry,
thermal conditions, material properties, and economic parameters.
"""

from typing import Literal, Optional

from pydantic import Field, field_validator

from heat_calc.models.base import BaseCalculationInput


class InsulationInput(BaseCalculationInput):
    """Complete input for insulation sizing and economic optimization.

    Calculates optimal insulation thickness for cylindrical pipes based on
    economic payback or temperature constraint optimization. Supports both
    economic mode (minimize total cost) and temperature-constrained mode
    (meet surface temperature requirement).

    Attributes
    ----------
    pipe_diameter : float
        Outside diameter of uninsulated pipe in meters (m).

    pipe_length : float
        Total length of pipe to be insulated in meters (m).

    T_surface_uninsulated : float
        Surface temperature of uninsulated pipe in Kelvin (K).

    T_ambient : float
        Ambient air temperature in Kelvin (K). Default: 298 K (25°C).

    h_ambient : float
        Natural convection heat transfer coefficient to ambient in W/(m²·K).
        Typical range: 5-25 W/(m²·K) for natural convection in air.

    insulation_material : str
        Name of insulation material (e.g., 'fiberglass', 'mineral_wool', 'polyurethane').

    thermal_conductivity_insulation : float
        Thermal conductivity of insulation material in W/(m·K).
        Typical values: 0.03-0.05 W/(m·K) for common insulations.

    density_insulation : float
        Density of insulation material in kg/m³ (used for cost estimation).

    energy_cost : float
        Cost of energy in $/MWh or $/GJ. Used for economic optimization.

    energy_annual_operating_hours : int
        Hours per year the system operates. Default: 8760 (continuous).

    insulation_cost_per_thickness : float
        Cost of insulation per unit area per unit thickness in $/(m²·m).
        Represents installed cost including material and labor.

    surface_temp_limit : float, optional
        Maximum allowable surface temperature in Kelvin (K) for safety or
        operational requirements. If provided, overrides economic optimization
        to meet this constraint.

    insulation_thickness_min : float
        Minimum insulation thickness in meters (m). Default: 0.01 m (10 mm).

    insulation_thickness_max : float
        Maximum insulation thickness in meters (m). Default: 0.15 m (150 mm).

    analysis_period_years : int
        Number of years for economic analysis and cost amortization. Default: 10 years.

    optimization_mode : str, optional
        Optimization strategy: 'economic_payback' (default) or 'temperature_constraint'.
        Auto-detected based on whether surface_temp_limit is provided.

    Example
    -------
    >>> from heat_calc.models import InsulationInput
    >>>
    >>> # Economic optimization example
    >>> input_data = InsulationInput(
    ...     pipe_diameter=0.1,  # 100 mm OD
    ...     pipe_length=100.0,
    ...     T_surface_uninsulated=423.15,  # 150°C
    ...     T_ambient=298.15,  # 25°C
    ...     h_ambient=15.0,
    ...     insulation_material="mineral_wool",
    ...     thermal_conductivity_insulation=0.04,
    ...     density_insulation=100.0,
    ...     energy_cost=12.0,  # $/GJ
    ...     insulation_cost_per_thickness=50.0
    ... )
    >>>
    >>> # Temperature-constrained optimization
    >>> input_constrained = InsulationInput(
    ...     pipe_diameter=0.1,
    ...     pipe_length=100.0,
    ...     T_surface_uninsulated=423.15,
    ...     T_ambient=298.15,
    ...     h_ambient=15.0,
    ...     insulation_material="fiberglass",
    ...     thermal_conductivity_insulation=0.035,
    ...     density_insulation=64.0,
    ...     energy_cost=12.0,
    ...     insulation_cost_per_thickness=45.0,
    ...     surface_temp_limit=333.15  # 60°C max surface temp
    ... )
    """

    # Pipe geometry
    pipe_diameter: float = Field(
        ...,
        description="Outside diameter of uninsulated pipe (m)",
        gt=0,
        json_schema_extra={"unit": "m", "example": 0.1},
    )

    pipe_length: float = Field(
        ...,
        description="Total length of pipe to be insulated (m)",
        gt=0,
        json_schema_extra={"unit": "m", "example": 100.0},
    )

    # Thermal conditions
    T_surface_uninsulated: float = Field(
        ...,
        description="Surface temperature of uninsulated pipe (K)",
        gt=0,
        json_schema_extra={"unit": "K", "example": 423.15},
    )

    T_ambient: float = Field(
        default=298.15,
        description="Ambient air temperature (K)",
        gt=0,
        json_schema_extra={"unit": "K", "example": 298.15},
    )

    h_ambient: float = Field(
        ...,
        description="Natural convection heat transfer coefficient to ambient (W/(m²·K))",
        gt=0,
        json_schema_extra={"unit": "W/(m²·K)", "example": 15.0},
    )

    # Insulation material properties
    insulation_material: str = Field(
        ...,
        description="Name of insulation material",
        json_schema_extra={"example": "mineral_wool"},
    )

    thermal_conductivity_insulation: float = Field(
        ...,
        description="Thermal conductivity of insulation material (W/(m·K))",
        gt=0,
        json_schema_extra={"unit": "W/(m·K)", "example": 0.04},
    )

    density_insulation: float = Field(
        ...,
        description="Density of insulation material (kg/m³)",
        gt=0,
        json_schema_extra={"unit": "kg/m³", "example": 100.0},
    )

    # Economic parameters
    energy_cost: float = Field(
        ...,
        description="Cost of energy ($/MWh or $/GJ)",
        gt=0,
        json_schema_extra={"unit": "$/MWh", "example": 12.0},
    )

    energy_annual_operating_hours: int = Field(
        default=8760,
        description="Hours per year the system operates",
        gt=0,
        le=8760,
        json_schema_extra={"example": 8760},
    )

    insulation_cost_per_thickness: float = Field(
        ...,
        description="Cost of insulation per unit area per unit thickness ($/(m²·m))",
        gt=0,
        json_schema_extra={"unit": "$/(m²·m)", "example": 50.0},
    )

    # Constraints
    surface_temp_limit: Optional[float] = Field(
        default=None,
        description="Maximum allowable surface temperature (K). Overrides economic optimization if provided.",
        gt=0,
        json_schema_extra={"unit": "K", "example": 333.15},
    )

    insulation_thickness_min: float = Field(
        default=0.01,
        description="Minimum insulation thickness (m)",
        gt=0,
        json_schema_extra={"unit": "m", "example": 0.01},
    )

    insulation_thickness_max: float = Field(
        default=0.15,
        description="Maximum insulation thickness (m)",
        gt=0,
        json_schema_extra={"unit": "m", "example": 0.15},
    )

    # Analysis period
    analysis_period_years: int = Field(
        default=10,
        description="Number of years for economic analysis",
        gt=0,
        json_schema_extra={"example": 10},
    )

    optimization_mode: Optional[Literal["economic_payback", "temperature_constraint"]] = Field(
        default=None,
        description="Optimization strategy. Auto-detected from surface_temp_limit if not specified.",
    )

    @field_validator("insulation_thickness_max")
    @classmethod
    def validate_thickness_range(cls, v: float, info) -> float:
        """Ensure max thickness is greater than min thickness."""
        if "insulation_thickness_min" in info.data:
            min_thickness = info.data["insulation_thickness_min"]
            if v <= min_thickness:
                raise ValueError(
                    f"insulation_thickness_max ({v} m) must be greater than "
                    f"insulation_thickness_min ({min_thickness} m)"
                )
        return v

    @field_validator("T_surface_uninsulated")
    @classmethod
    def validate_surface_temp(cls, v: float, info) -> float:
        """Ensure surface temperature is physically reasonable."""
        if "T_ambient" in info.data:
            T_amb = info.data["T_ambient"]
            if v <= T_amb:
                raise ValueError(
                    f"T_surface_uninsulated ({v} K) must be greater than "
                    f"T_ambient ({T_amb} K) for heat loss to occur"
                )
        return v

    @field_validator("surface_temp_limit")
    @classmethod
    def validate_temp_limit(cls, v: Optional[float], info) -> Optional[float]:
        """Ensure temperature limit is between ambient and uninsulated surface temp."""
        if v is not None:
            if "T_ambient" in info.data and v <= info.data["T_ambient"]:
                raise ValueError(
                    f"surface_temp_limit ({v} K) must be greater than T_ambient "
                    f"({info.data['T_ambient']} K)"
                )
            if "T_surface_uninsulated" in info.data and v >= info.data["T_surface_uninsulated"]:
                raise ValueError(
                    f"surface_temp_limit ({v} K) must be less than T_surface_uninsulated "
                    f"({info.data['T_surface_uninsulated']} K) - otherwise no insulation is needed"
                )
        return v
