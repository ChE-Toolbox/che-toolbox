"""Result models for insulation sizing and economic optimization calculations.

Defines Pydantic models for insulation calculation results with comprehensive
economic analysis, heat loss reduction metrics, and validation.
"""

from typing import Any, Literal

from pydantic import Field, field_validator

from heat_calc.models.base import BaseCalculationResult


class InsulationResult(BaseCalculationResult):
    """Complete results from insulation sizing and economic optimization.

    Contains optimal insulation thickness, heat loss comparison, economic
    analysis (payback period, cost savings), and temperature profile.

    Attributes
    ----------
    optimal_insulation_thickness : float
        Calculated optimal insulation thickness in meters (m).

    optimization_mode : str
        Optimization strategy used: 'economic_payback' or 'temperature_constraint'.

    Q_uninsulated : float
        Heat loss from uninsulated pipe in W.

    Q_insulated : float
        Heat loss from insulated pipe at optimal thickness in W.

    heat_loss_reduction_percent : float
        Percentage reduction in heat loss: (Q_un - Q_ins) / Q_un × 100 in %.

    annual_energy_savings : float
        Energy saved per year in MWh.

    annual_cost_savings : float
        Cost savings per year in $.

    annual_insulation_cost : float
        Annualized insulation cost (capital cost / analysis period) in $.

    net_annual_savings : float
        Net annual savings: annual_cost_savings - annual_insulation_cost in $.

    payback_period_years : float
        Simple payback period in years (only for economic_payback mode).

    T_surface_insulated : float
        Surface temperature with optimal insulation in K.

    T_surface_required : float, optional
        Required surface temperature constraint in K (only for temperature_constraint mode).

    insulation_volume : float
        Volume of insulation material required in m³.

    insulation_mass : float
        Mass of insulation material required in kg.

    total_insulation_cost : float
        Total upfront cost of insulation (material + installation) in $.

    sensitivity : dict, optional
        Sensitivity analysis results for key parameters (energy cost, insulation cost).

    Example
    -------
    >>> result = InsulationResult(
    ...     primary_value=0.075,  # 75 mm optimal thickness
    ...     optimal_insulation_thickness=0.075,
    ...     optimization_mode="economic_payback",
    ...     Q_uninsulated=13500.0,
    ...     Q_insulated=1200.0,
    ...     heat_loss_reduction_percent=91.1,
    ...     annual_energy_savings=105.2,
    ...     annual_cost_savings=1262.40,
    ...     annual_insulation_cost=237.50,
    ...     net_annual_savings=1024.90,
    ...     payback_period_years=2.9,
    ...     T_surface_insulated=308.15,
    ...     insulation_volume=2.36,
    ...     insulation_mass=236.0,
    ...     total_insulation_cost=2375.0
    ... )
    """

    # Optimal thickness (primary result)
    optimal_insulation_thickness: float = Field(
        ...,
        description="Optimal insulation thickness (m)",
        gt=0,
        json_schema_extra={"unit": "m"},
    )

    optimization_mode: Literal["economic_payback", "temperature_constraint"] = Field(
        ...,
        description="Optimization strategy used",
    )

    # Heat loss comparison
    Q_uninsulated: float = Field(
        ...,
        description="Heat loss from uninsulated pipe (W)",
        gt=0,
        json_schema_extra={"unit": "W"},
    )

    Q_insulated: float = Field(
        ...,
        description="Heat loss from insulated pipe (W)",
        gt=0,
        json_schema_extra={"unit": "W"},
    )

    heat_loss_reduction_percent: float = Field(
        ...,
        description="Percentage reduction in heat loss (%)",
        ge=0,
        le=100,
        json_schema_extra={"unit": "%"},
    )

    # Economic analysis
    annual_energy_savings: float = Field(
        ...,
        description="Energy saved per year (MWh)",
        ge=0,
        json_schema_extra={"unit": "MWh"},
    )

    annual_cost_savings: float = Field(
        ...,
        description="Cost savings per year ($)",
        ge=0,
        json_schema_extra={"unit": "$"},
    )

    annual_insulation_cost: float = Field(
        ...,
        description="Annualized insulation cost ($)",
        ge=0,
        json_schema_extra={"unit": "$"},
    )

    net_annual_savings: float = Field(
        ...,
        description="Net annual savings: cost_savings - insulation_cost ($)",
        json_schema_extra={"unit": "$"},
    )

    payback_period_years: float = Field(
        default=0.0,
        description="Simple payback period (years). 0 for temperature_constraint mode.",
        ge=0,
        json_schema_extra={"unit": "years"},
    )

    # Temperature profile
    T_surface_insulated: float = Field(
        ...,
        description="Surface temperature with optimal insulation (K)",
        gt=0,
        json_schema_extra={"unit": "K"},
    )

    T_surface_required: float | None = Field(
        default=None,
        description="Required surface temperature constraint (K) - only for temperature_constraint mode",
        gt=0,
        json_schema_extra={"unit": "K"},
    )

    # Material quantities
    insulation_volume: float = Field(
        ...,
        description="Volume of insulation material required (m³)",
        gt=0,
        json_schema_extra={"unit": "m³"},
    )

    insulation_mass: float = Field(
        ...,
        description="Mass of insulation material required (kg)",
        gt=0,
        json_schema_extra={"unit": "kg"},
    )

    total_insulation_cost: float = Field(
        ...,
        description="Total upfront cost of insulation ($)",
        gt=0,
        json_schema_extra={"unit": "$"},
    )

    # Optional sensitivity analysis
    sensitivity: dict[str, Any] | None = Field(
        default=None,
        description="Sensitivity analysis results for key parameters",
    )

    @field_validator("Q_insulated")
    @classmethod
    def validate_heat_loss(cls, v: float, info: Any) -> float:
        """Validate that insulated heat loss is less than uninsulated.

        Heat loss with insulation should always be less than without insulation.
        """
        if "Q_uninsulated" in info.data:
            Q_un = info.data["Q_uninsulated"]
            if v > Q_un * 1.01:  # Allow 1% tolerance
                raise ValueError(
                    f"Q_insulated ({v:.1f} W) cannot exceed Q_uninsulated ({Q_un:.1f} W)"
                )
        return v

    @field_validator("heat_loss_reduction_percent")
    @classmethod
    def validate_heat_loss_reduction(cls, v: float, info: Any) -> float:
        """Validate heat loss reduction percentage calculation.

        Heat loss reduction should match: (Q_un - Q_ins) / Q_un × 100
        """
        if "Q_uninsulated" in info.data and "Q_insulated" in info.data:
            Q_un = info.data["Q_uninsulated"]
            Q_ins = info.data["Q_insulated"]
            expected = (Q_un - Q_ins) / Q_un * 100
            if abs(v - expected) > 0.1:  # 0.1% tolerance
                raise ValueError(
                    f"heat_loss_reduction_percent ({v:.1f}%) does not match "
                    f"calculated value ({expected:.1f}%)"
                )
        return v

    @field_validator("T_surface_insulated")
    @classmethod
    def validate_surface_temp_reduction(cls, v: float, info: Any) -> float:
        """Validate that insulated surface temperature meets constraints.

        For temperature_constraint mode, surface temp should be at or below limit.
        For economic mode, surface temp should be reduced from uninsulated.
        """
        if "optimization_mode" in info.data:
            mode = info.data["optimization_mode"]
            if mode == "temperature_constraint" and "T_surface_required" in info.data:
                T_req = info.data["T_surface_required"]
                if T_req is not None and v > T_req * 1.01:  # 1% tolerance
                    raise ValueError(
                        f"T_surface_insulated ({v:.1f} K) exceeds required limit ({T_req:.1f} K)"
                    )
        return v

    @field_validator("payback_period_years")
    @classmethod
    def validate_payback_period(cls, v: float, info: Any) -> float:
        """Validate payback period calculation.

        Payback = total_insulation_cost / annual_cost_savings
        Only applies to economic_payback mode.
        """
        if v > 0 and "optimization_mode" in info.data:
            mode = info.data["optimization_mode"]
            if mode == "economic_payback":
                if "total_insulation_cost" in info.data and "annual_cost_savings" in info.data:
                    cost = info.data["total_insulation_cost"]
                    savings = info.data["annual_cost_savings"]
                    if savings > 0:
                        expected = cost / savings
                        if abs(v - expected) > 0.1:  # 0.1 year tolerance
                            raise ValueError(
                                f"payback_period_years ({v:.2f}) does not match "
                                f"calculated value ({expected:.2f})"
                            )
        return v

    @field_validator("net_annual_savings")
    @classmethod
    def validate_net_savings(cls, v: float, info: Any) -> float:
        """Validate net annual savings calculation.

        Net savings = annual_cost_savings - annual_insulation_cost
        """
        if "annual_cost_savings" in info.data and "annual_insulation_cost" in info.data:
            cost_savings = info.data["annual_cost_savings"]
            insulation_cost = info.data["annual_insulation_cost"]
            expected = cost_savings - insulation_cost
            if abs(v - expected) > 0.01:  # $0.01 tolerance
                raise ValueError(
                    f"net_annual_savings (${v:.2f}) does not match "
                    f"calculated value (${expected:.2f})"
                )
        return v
