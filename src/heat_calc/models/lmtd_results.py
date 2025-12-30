"""Result models for LMTD heat transfer calculations.

Defines Pydantic models for LMTD calculation results with comprehensive
validation and traceability.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator

from heat_calc.models.base import BaseCalculationResult


class LMTDResult(BaseCalculationResult):
    """Complete results from LMTD heat transfer calculation.

    Contains primary heat transfer rate, intermediate LMTD values,
    energy balance validation, and configuration details.

    Attributes
    ----------
    heat_transfer_rate : float
        Calculated heat transfer rate in W.

    lmtd_arithmetic : float
        Log mean temperature difference in K (before correction factor).

    lmtd_effective : float
        Corrected LMTD after applying correction factor in K.

    correction_factor : float
        F correction factor applied [0, 1].

    temperature_difference_hot : float
        Hot side temperature change ΔT_h = T_inlet - T_outlet in K.

    temperature_difference_cold : float
        Cold side temperature change ΔT_c = T_outlet - T_inlet in K.

    configuration_used : str
        Configuration type used (counterflow, parallel_flow, etc).

    energy_balance_hot : float
        Heat transfer from hot side: mdot_h × cp_h × ΔT_h in W.

    energy_balance_cold : float
        Heat transfer from cold side: mdot_c × cp_c × ΔT_c in W.

    energy_balance_error_percent : float
        Relative energy balance error: |(Q_hot - Q_cold)| / Q_avg × 100 in %.

    effectiveness : float
        Heat exchanger effectiveness: actual Q / max possible Q.

    capacity_ratio : float
        Capacity rate ratio: min(C_h, C_c) / max(C_h, C_c).

    overall_ua : float, optional
        Overall heat transfer coefficient times area in W/K.

    intermediate_values : dict
        Additional intermediate calculations for debugging.
    """

    heat_transfer_rate: float = Field(
        ...,
        description="Heat transfer rate in W",
        json_schema_extra={"unit": "W"},
    )

    lmtd_arithmetic: float = Field(
        ...,
        description="Log mean temperature difference (arithmetic) in K",
        json_schema_extra={"unit": "K"},
    )

    lmtd_effective: float = Field(
        ...,
        description="Effective LMTD after correction factor in K",
        json_schema_extra={"unit": "K"},
    )

    correction_factor: float = Field(
        ...,
        description="LMTD correction factor F",
        ge=0.0,
        le=1.0,
    )

    temperature_difference_hot: float = Field(
        ...,
        description="Hot side temperature change in K",
        json_schema_extra={"unit": "K"},
    )

    temperature_difference_cold: float = Field(
        ...,
        description="Cold side temperature change in K",
        json_schema_extra={"unit": "K"},
    )

    configuration_used: str = Field(
        ...,
        description="Heat exchanger configuration used",
        json_schema_extra={"example": "counterflow"},
    )

    energy_balance_hot: float = Field(
        ...,
        description="Heat transfer calculated from hot side in W",
        json_schema_extra={"unit": "W"},
    )

    energy_balance_cold: float = Field(
        ...,
        description="Heat transfer calculated from cold side in W",
        json_schema_extra={"unit": "W"},
    )

    energy_balance_error_percent: float = Field(
        ...,
        description="Energy balance error as percentage",
        json_schema_extra={"unit": "%"},
    )

    effectiveness: float = Field(
        default=0.0,
        description="Heat exchanger effectiveness (Q/Q_max)",
        ge=0.0,
        le=1.0,
    )

    capacity_ratio: float = Field(
        default=0.0,
        description="Capacity rate ratio (min/max)",
        ge=0.0,
        le=1.0,
    )

    overall_ua: float = Field(
        default=0.0,
        description="Overall heat transfer coefficient times area in W/K",
        ge=0.0,
        json_schema_extra={"unit": "W/K"},
    )

    @field_validator("lmtd_effective")
    @classmethod
    def validate_lmtd_effective(cls, v: float, info: Any) -> float:
        """Validate that effective LMTD ≤ arithmetic LMTD.

        The correction factor should reduce the effective LMTD, so:
        LMTD_effective = F × LMTD_arithmetic, where 0 ≤ F ≤ 1.
        """
        if "lmtd_arithmetic" in info.data:
            lmtd_arith = info.data["lmtd_arithmetic"]
            if v > lmtd_arith * 1.01:  # Allow 1% tolerance for floating point
                raise ValueError(
                    f"LMTD_effective ({v:.2f}) cannot exceed LMTD_arithmetic ({lmtd_arith:.2f})"
                )
        return v

    @field_validator("energy_balance_error_percent")
    @classmethod
    def validate_energy_balance(cls, v: float) -> float:
        """Validate that energy balance error is less than 1%.

        This is a sanity check that hot and cold side calculations agree.
        """
        if v > 1.0:
            raise ValueError(
                f"Energy balance error {v:.3f}% exceeds 1% threshold. "
                "Check inlet/outlet temperatures and mass flow rates."
            )
        return v

    @field_validator("correction_factor")
    @classmethod
    def validate_correction_factor(cls, v: float) -> float:
        """Validate correction factor is in valid range [0, 1]."""
        if not (0.0 <= v <= 1.0):
            raise ValueError(
                f"Correction factor {v} must be in range [0, 1]"
            )
        return v

    class Config:
        """Pydantic configuration."""

        json_encoders = {}
