"""Input models for LMTD heat transfer calculations.

Defines Pydantic models for specifying heat exchanger configurations,
fluid stream states, and complete LMTD calculation inputs.
"""

from typing import Literal, Optional

from pint import Quantity
from pydantic import BaseModel, Field

from heat_calc.models.base import BaseCalculationInput


class FluidState(BaseModel):
    """Single fluid stream state (inlet/outlet conditions).

    Represents temperature and flow rate for one side of a heat exchanger
    at either inlet or outlet.

    Attributes
    ----------
    temperature : float
        Temperature value in Kelvin. Can also accept Pint Quantity.
    mass_flow_rate : float
        Mass flow rate in kg/s. Can also accept Pint Quantity.
    specific_heat : float, optional
        Specific heat capacity in J/(kg·K). Required for energy balance.
        Can also accept Pint Quantity.
    """

    model_config = {"arbitrary_types_allowed": True}

    temperature: float = Field(
        ...,
        description="Temperature in Kelvin (K)",
        json_schema_extra={"unit": "K", "example": 373.15},
    )

    mass_flow_rate: float = Field(
        ...,
        description="Mass flow rate in kg/s",
        json_schema_extra={"unit": "kg/s", "example": 10.0},
    )

    specific_heat: Optional[float] = Field(
        default=None,
        description="Specific heat capacity in J/(kg·K). Required for energy balance validation.",
        json_schema_extra={"unit": "J/(kg·K)", "example": 4180.0},
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {}


class HeatExchangerConfiguration(BaseModel):
    """Heat exchanger geometry and flow configuration.

    Specifies the type of heat exchanger (counterflow, parallel, crossflow)
    and surface area for heat transfer. Optional correction factor for
    non-ideal flow patterns.

    Attributes
    ----------
    configuration : str
        Type of heat exchanger arrangement: 'counterflow', 'parallel_flow',
        'crossflow_unmixed_both', 'crossflow_unmixed_hot_mixed_cold',
        'crossflow_mixed_both'.

    area : float
        Heat transfer surface area in m^2.

    correction_factor : float, optional
        F correction factor for LMTD [0, 1]. If not provided, defaults to 1.0
        for counterflow and parallel flow. For crossflow, typically 0.7-0.95
        depending on temperature ratio and capacity ratio.

    overall_heat_transfer_coefficient : float, optional
        Overall heat transfer coefficient U in W/(m^2·K). Alternative to
        providing UA separately.
    """

    model_config = {"arbitrary_types_allowed": True}

    configuration: Literal[
        "counterflow",
        "parallel_flow",
        "crossflow_unmixed_both",
        "crossflow_unmixed_hot_mixed_cold",
        "crossflow_mixed_both",
    ] = Field(
        ...,
        description="Heat exchanger configuration type",
        json_schema_extra={"example": "counterflow"},
    )

    area: float = Field(
        ...,
        description="Heat transfer surface area in m^2",
        gt=0,
        json_schema_extra={"unit": "m^2", "example": 100.0},
    )

    correction_factor: Optional[float] = Field(
        default=None,
        description="LMTD correction factor F [0, 1]. Auto-calculated if not provided.",
        ge=0.0,
        le=1.0,
        json_schema_extra={"example": 0.95},
    )

    overall_heat_transfer_coefficient: Optional[float] = Field(
        default=None,
        description="Overall heat transfer coefficient U in W/(m^2·K). Overrides area-only calculation.",
        gt=0,
        json_schema_extra={"unit": "W/(m^2·K)", "example": 500.0},
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {}


class LMTDInput(BaseCalculationInput):
    """Complete input for LMTD heat transfer calculation.

    Combines hot and cold fluid states with heat exchanger configuration
    to specify a complete LMTD calculation scenario.

    Attributes
    ----------
    hot_fluid : FluidState
        Hot side inlet and outlet temperatures and flow rate.

    cold_fluid : FluidState
        Cold side inlet and outlet temperatures and flow rate.

    heat_exchanger : HeatExchangerConfiguration
        Heat exchanger geometry and flow arrangement.

    overall_ua : float, optional
        Pre-calculated UA product in W/K. If provided, overrides calculation
        from area and overall_heat_transfer_coefficient.

    Example
    -------
    >>> from heat_calc.models import LMTDInput, FluidState, HeatExchangerConfiguration
    >>>
    >>> hot = FluidState(
    ...     temperature=373.15,
    ...     mass_flow_rate=10.0,
    ...     specific_heat=4180.0
    ... )
    >>> cold = FluidState(
    ...     temperature=293.15,
    ...     mass_flow_rate=15.0,
    ...     specific_heat=4180.0
    ... )
    >>> config = HeatExchangerConfiguration(
    ...     configuration="counterflow",
    ...     area=100.0
    ... )
    >>> input_data = LMTDInput(
    ...     hot_fluid_inlet=hot,
    ...     cold_fluid_inlet=cold,
    ...     heat_exchanger=config
    ... )
    """

    hot_fluid_inlet: FluidState = Field(
        ...,
        description="Hot fluid inlet state",
    )

    hot_fluid_outlet: FluidState = Field(
        ...,
        description="Hot fluid outlet state (used for energy balance validation)",
    )

    cold_fluid_inlet: FluidState = Field(
        ...,
        description="Cold fluid inlet state",
    )

    cold_fluid_outlet: FluidState = Field(
        ...,
        description="Cold fluid outlet state (used for energy balance validation)",
    )

    heat_exchanger: HeatExchangerConfiguration = Field(
        ...,
        description="Heat exchanger configuration and geometry",
    )

    overall_ua: Optional[float] = Field(
        default=None,
        description="Overall heat transfer coefficient × area product (W/K). Overrides area-based calculation.",
        gt=0,
        json_schema_extra={"unit": "W/K", "example": 50000.0},
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {}
