"""Input models for NTU-effectiveness heat transfer calculations.

Defines Pydantic models for specifying NTU calculation inputs with inlet conditions,
fluid properties, and heat exchanger characteristics.
"""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from heat_calc.models.base import BaseCalculationInput


class NTUInput(BaseCalculationInput):
    """Complete input for NTU-effectiveness calculation.

    Calculates heat exchanger effectiveness and outlet temperatures using
    the Number of Transfer Units method.

    Attributes
    ----------
    T_hot_inlet : float
        Hot fluid inlet temperature in Kelvin.

    T_cold_inlet : float
        Cold fluid inlet temperature in Kelvin.

    mdot_hot : float
        Hot fluid mass flow rate in kg/s.

    mdot_cold : float
        Cold fluid mass flow rate in kg/s.

    cp_hot : float
        Hot fluid specific heat capacity in J/(kg·K).

    cp_cold : float
        Cold fluid specific heat capacity in J/(kg·K).

    UA : float
        Overall heat transfer coefficient × area product in W/K.

    configuration : str
        Heat exchanger configuration type. Options:
        - "counterflow": Counterflow heat exchanger
        - "parallel_flow": Parallel flow heat exchanger
        - "shell_and_tube_1_2": Shell-and-tube with 1 shell pass, 2 tube passes
        - "crossflow_unmixed_both": Crossflow with both fluids unmixed
        - "crossflow_mixed_one": Crossflow with one fluid mixed

    T_hot_outlet : float, optional
        Hot fluid outlet temperature (K). If provided, calculate T_cold_outlet instead.

    T_cold_outlet : float, optional
        Cold fluid outlet temperature (K). If provided, calculate T_hot_outlet instead.

    Example
    -------
    >>> from heat_calc.models import NTUInput
    >>>
    >>> input_data = NTUInput(
    ...     T_hot_inlet=373.15,  # K
    ...     T_cold_inlet=293.15,  # K
    ...     mdot_hot=10.0,  # kg/s
    ...     mdot_cold=15.0,  # kg/s
    ...     cp_hot=4180.0,  # J/(kg·K)
    ...     cp_cold=4180.0,  # J/(kg·K)
    ...     UA=50000.0,  # W/K
    ...     configuration="counterflow"
    ... )
    """

    model_config = {"arbitrary_types_allowed": True}

    T_hot_inlet: float = Field(
        ...,
        description="Hot fluid inlet temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 373.15},
    )

    T_cold_inlet: float = Field(
        ...,
        description="Cold fluid inlet temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 293.15},
    )

    mdot_hot: float = Field(
        ...,
        description="Hot fluid mass flow rate in kg/s",
        gt=0,
        json_schema_extra={"unit": "kg/s", "example": 10.0},
    )

    mdot_cold: float = Field(
        ...,
        description="Cold fluid mass flow rate in kg/s",
        gt=0,
        json_schema_extra={"unit": "kg/s", "example": 15.0},
    )

    cp_hot: float = Field(
        ...,
        description="Hot fluid specific heat capacity in J/(kg·K)",
        gt=0,
        json_schema_extra={"unit": "J/(kg·K)", "example": 4180.0},
    )

    cp_cold: float = Field(
        ...,
        description="Cold fluid specific heat capacity in J/(kg·K)",
        gt=0,
        json_schema_extra={"unit": "J/(kg·K)", "example": 4180.0},
    )

    UA: float = Field(
        ...,
        description="Overall heat transfer coefficient × area product in W/K",
        gt=0,
        json_schema_extra={"unit": "W/K", "example": 50000.0},
    )

    configuration: Literal[
        "counterflow",
        "parallel_flow",
        "shell_and_tube_1_2",
        "crossflow_unmixed_both",
        "crossflow_mixed_one",
    ] = Field(
        ...,
        description="Heat exchanger configuration type",
        json_schema_extra={"example": "counterflow"},
    )

    T_hot_outlet: Optional[float] = Field(
        default=None,
        description="Hot fluid outlet temperature (K). If provided, calculate T_cold_outlet instead.",
        gt=0,
        json_schema_extra={"unit": "K"},
    )

    T_cold_outlet: Optional[float] = Field(
        default=None,
        description="Cold fluid outlet temperature (K). If provided, calculate T_hot_outlet instead.",
        gt=0,
        json_schema_extra={"unit": "K"},
    )

    @model_validator(mode="after")
    def validate_mutually_exclusive_outlets(self) -> "NTUInput":
        """Ensure T_hot_outlet and T_cold_outlet are not both specified.

        Only one outlet temperature can be specified at a time.
        If both are provided, raise a validation error.
        """
        if self.T_hot_outlet is not None and self.T_cold_outlet is not None:
            raise ValueError(
                "Cannot specify both T_hot_outlet and T_cold_outlet. "
                "Provide one or neither to calculate the other."
            )
        return self
