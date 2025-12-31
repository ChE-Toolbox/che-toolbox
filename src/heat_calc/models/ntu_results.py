"""Result models for NTU-effectiveness heat transfer calculations.

Defines Pydantic models for NTU calculation outputs including effectiveness,
outlet temperatures, and intermediate values.
"""

from typing import Any

from pydantic import Field, field_validator

from heat_calc.models.base import BaseCalculationResult


class NTUResult(BaseCalculationResult):
    """Complete results from NTU-effectiveness calculation.

    Contains primary results (effectiveness, NTU, heat transfer rate),
    outlet temperatures, heat capacity rates, and validation metrics.

    Attributes
    ----------
    NTU : float
        Number of Transfer Units [-].

    effectiveness : float
        Heat exchanger effectiveness [-]. Bounded to [0, 1].

    heat_transfer_rate : float
        Calculated heat transfer rate in Watts.

    T_hot_outlet : float
        Hot fluid outlet temperature in Kelvin.

    T_cold_outlet : float
        Cold fluid outlet temperature in Kelvin.

    C_hot : float
        Hot fluid heat capacity rate in W/K (mdot_hot × cp_hot).

    C_cold : float
        Cold fluid heat capacity rate in W/K (mdot_cold × cp_cold).

    C_min : float
        Minimum of C_hot and C_cold in W/K.

    C_max : float
        Maximum of C_hot and C_cold in W/K.

    C_ratio : float
        Heat capacity ratio C_min / C_max [-].

    Q_max : float
        Maximum possible heat transfer in Watts.

    effectiveness_theoretical_max : float
        Theoretical maximum effectiveness for the given configuration [-].

    energy_balance_error_percent : float
        Percentage error in energy balance between hot and cold sides.
    """

    model_config = {
        "arbitrary_types_allowed": True,
        "frozen": True,
    }

    NTU: float = Field(
        ...,
        description="Number of Transfer Units [-]",
        ge=0,
        json_schema_extra={"example": 1.5},
    )

    effectiveness: float = Field(
        ...,
        description="Heat exchanger effectiveness [-]",
        ge=0,
        le=1,
        json_schema_extra={"example": 0.75},
    )

    heat_transfer_rate: float = Field(
        ...,
        description="Calculated heat transfer rate in Watts",
        ge=0,
        json_schema_extra={"unit": "W", "example": 125000.0},
    )

    T_hot_outlet: float = Field(
        ...,
        description="Hot fluid outlet temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 353.15},
    )

    T_cold_outlet: float = Field(
        ...,
        description="Cold fluid outlet temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 313.15},
    )

    C_hot: float = Field(
        ...,
        description="Hot fluid heat capacity rate in W/K",
        gt=0,
        json_schema_extra={"unit": "W/K", "example": 41800.0},
    )

    C_cold: float = Field(
        ...,
        description="Cold fluid heat capacity rate in W/K",
        gt=0,
        json_schema_extra={"unit": "W/K", "example": 62700.0},
    )

    C_min: float = Field(
        ...,
        description="Minimum heat capacity rate in W/K",
        gt=0,
        json_schema_extra={"unit": "W/K", "example": 41800.0},
    )

    C_max: float = Field(
        ...,
        description="Maximum heat capacity rate in W/K",
        gt=0,
        json_schema_extra={"unit": "W/K", "example": 62700.0},
    )

    C_ratio: float = Field(
        ...,
        description="Heat capacity ratio C_min / C_max [-]",
        ge=0,
        le=1,
        json_schema_extra={"example": 0.667},
    )

    Q_max: float = Field(
        ...,
        description="Maximum possible heat transfer in Watts",
        gt=0,
        json_schema_extra={"unit": "W", "example": 166400.0},
    )

    effectiveness_theoretical_max: float = Field(
        ...,
        description="Theoretical maximum effectiveness for the configuration [-]",
        ge=0,
        le=1,
        json_schema_extra={"example": 0.95},
    )

    energy_balance_error_percent: float = Field(
        ...,
        description="Energy balance error percentage",
        ge=0,
        le=100,
        json_schema_extra={"example": 0.5},
    )

    @field_validator("effectiveness")
    @classmethod
    def validate_effectiveness_bounds(cls, v: float) -> float:
        """Validate effectiveness is within [0, 1]."""
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Effectiveness {v} must be in range [0, 1]")
        return v

    @field_validator("C_ratio")
    @classmethod
    def validate_c_ratio(cls, v: float) -> float:
        """Validate capacity ratio is in valid range [0, 1]."""
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Capacity ratio {v} must be in range [0, 1]")
        return v

    @field_validator("NTU")
    @classmethod
    def validate_ntu(cls, v: float) -> float:
        """Validate NTU is non-negative."""
        if v < 0:
            raise ValueError(f"NTU {v} must be >= 0")
        return v

    @field_validator("heat_transfer_rate")
    @classmethod
    def validate_heat_transfer_bounded(cls, v: float, info: Any) -> float:
        """Validate heat transfer is less than Q_max."""
        if "Q_max" in info.data and v > info.data["Q_max"]:
            raise ValueError(
                f"Calculated heat transfer {v} W exceeds theoretical maximum {info.data['Q_max']} W"
            )
        return v

    @field_validator("energy_balance_error_percent")
    @classmethod
    def validate_energy_balance(cls, v: float) -> float:
        """Validate energy balance error is reasonable."""
        if v > 5.0:  # Allow up to 5% energy balance error
            raise ValueError(
                f"Energy balance error {v:.2f}% exceeds 5% threshold. "
                "Check inlet/outlet temperatures and mass flow rates."
            )
        return v
