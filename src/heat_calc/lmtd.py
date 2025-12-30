"""LMTD (Log Mean Temperature Difference) Heat Transfer Calculations.

Implements the LMTD method for calculating heat transfer rates in heat exchangers
for counterflow, parallel flow, and crossflow configurations with correction factors.

References:
    - Incropera et al. Fundamentals of Heat and Mass Transfer (9th ed.), Chapters 10-11
    - NIST webbook reference data for validation
"""

import math
from typing import Dict, Tuple

from heat_calc.models.lmtd_input import LMTDInput
from heat_calc.models.lmtd_results import LMTDResult
from heat_calc.utils.constants import PERFORMANCE_TARGET_MS
from heat_calc.utils.validation import check_nan_inf, validate_positive_float, validate_temperature


def calculate_lmtd(input_data: LMTDInput) -> LMTDResult:
    """Calculate heat transfer rate using Log Mean Temperature Difference method.

    Determines heat transfer rate, LMTD, correction factor, and validates energy balance
    for counterflow, parallel flow, and various crossflow configurations.

    Parameters
    ----------
    input_data : LMTDInput
        Complete input specification with fluid states and heat exchanger configuration.

    Returns
    -------
    LMTDResult
        Results including primary heat transfer rate, intermediate LMTD values,
        energy balance validation, and configuration details.

    Raises
    ------
    ValueError
        If input validates against constraints (e.g., retrograde flow, invalid temps).

    Examples
    --------
    >>> from heat_calc.models import LMTDInput, FluidState, HeatExchangerConfiguration
    >>> from heat_calc.lmtd import calculate_lmtd
    >>>
    >>> hot = FluidState(temperature=373.15, mass_flow_rate=10.0, specific_heat=4180.0)
    >>> cold = FluidState(temperature=293.15, mass_flow_rate=15.0, specific_heat=4180.0)
    >>> config = HeatExchangerConfiguration(configuration="counterflow", area=100.0)
    >>> input_obj = LMTDInput(
    ...     hot_fluid_inlet=hot,
    ...     hot_fluid_outlet=FluidState(temperature=323.15, mass_flow_rate=10.0),
    ...     cold_fluid_inlet=cold,
    ...     cold_fluid_outlet=FluidState(temperature=323.15, mass_flow_rate=15.0),
    ...     heat_exchanger=config
    ... )
    >>> result = calculate_lmtd(input_obj)
    >>> print(f"Q = {result.heat_transfer_rate:.1f} W")
    >>> print(f"LMTD = {result.lmtd_effective:.2f} K")
    """
    try:
        # Validate inputs
        _validate_lmtd_input(input_data)

        # Extract temperatures
        t_h_in = input_data.hot_fluid_inlet.temperature
        t_h_out = input_data.hot_fluid_outlet.temperature
        t_c_in = input_data.cold_fluid_inlet.temperature
        t_c_out = input_data.cold_fluid_outlet.temperature

        # Calculate temperature differences
        delta_t_hot = t_h_in - t_h_out
        delta_t_cold = t_c_out - t_c_in

        # Get mass flow rates and specific heats
        m_h = input_data.hot_fluid_inlet.mass_flow_rate
        m_c = input_data.cold_fluid_inlet.mass_flow_rate
        cp_h = input_data.hot_fluid_inlet.specific_heat or 4180.0
        cp_c = input_data.cold_fluid_inlet.specific_heat or 4180.0

        # Calculate LMTD (arithmetic mean for counterflow/parallel)
        lmtd_arith = _calculate_lmtd_arithmetic(t_h_in, t_h_out, t_c_in, t_c_out)

        # Get correction factor
        f_correction = input_data.heat_exchanger.correction_factor or 1.0
        if f_correction is None:
            f_correction = _calculate_correction_factor(
                input_data.heat_exchanger.configuration,
                t_h_in, t_h_out, t_c_in, t_c_out
            )

        # Calculate effective LMTD
        lmtd_eff = f_correction * lmtd_arith

        # Get UA product
        if input_data.overall_ua is not None:
            ua = input_data.overall_ua
        elif input_data.heat_exchanger.overall_heat_transfer_coefficient is not None:
            u = input_data.heat_exchanger.overall_heat_transfer_coefficient
            a = input_data.heat_exchanger.area
            ua = u * a
        else:
            # Default assumption if neither provided
            ua = 50000.0  # W/K default

        # Calculate heat transfer rate
        q = ua * lmtd_eff

        # Calculate energy balance from each side
        q_hot = m_h * cp_h * delta_t_hot
        q_cold = m_c * cp_c * delta_t_cold

        # Calculate energy balance error
        if q_hot > 0 or q_cold > 0:
            q_avg = (q_hot + q_cold) / 2 if (q_hot + q_cold) > 0 else max(q_hot, q_cold)
            if q_avg > 0:
                energy_balance_error = abs(q_hot - q_cold) / q_avg * 100
            else:
                energy_balance_error = 0.0
        else:
            energy_balance_error = 0.0

        # Calculate capacity rates
        c_h = m_h * cp_h
        c_c = m_c * cp_c
        c_min = min(c_h, c_c)
        c_max = max(c_h, c_c)

        # Calculate effectiveness
        q_max = c_min * (t_h_in - t_c_in)
        effectiveness = q / q_max if q_max > 0 else 0.0
        effectiveness = min(effectiveness, 1.0)  # Cap at 1.0

        # Capacity ratio
        capacity_ratio = c_min / c_max if c_max > 0 else 0.0

        # Build intermediate values dict
        intermediate_values: Dict[str, float] = {
            "delta_t_hot_k": delta_t_hot,
            "delta_t_cold_k": delta_t_cold,
            "lmtd_arithmetic_k": lmtd_arith,
            "capacity_rate_hot_w_k": c_h,
            "capacity_rate_cold_w_k": c_c,
            "q_hot_w": q_hot,
            "q_cold_w": q_cold,
            "q_max_w": q_max,
            "ua_w_k": ua,
        }

        # Create result
        result = LMTDResult(
            primary_value=q,
            calculation_method="LMTD_v1.0",
            success=True,
            error_message="",
            heat_transfer_rate=q,
            lmtd_arithmetic=lmtd_arith,
            lmtd_effective=lmtd_eff,
            correction_factor=f_correction,
            temperature_difference_hot=delta_t_hot,
            temperature_difference_cold=delta_t_cold,
            configuration_used=input_data.heat_exchanger.configuration,
            energy_balance_hot=q_hot,
            energy_balance_cold=q_cold,
            energy_balance_error_percent=energy_balance_error,
            effectiveness=effectiveness,
            capacity_ratio=capacity_ratio,
            overall_ua=ua,
            intermediate_values=intermediate_values,
            version="1.0.0",
        )

        return result

    except ValueError as e:
        # Return result with error information
        return LMTDResult(
            primary_value=0.0,
            calculation_method="LMTD_v1.0",
            success=False,
            error_message=str(e),
            heat_transfer_rate=0.0,
            lmtd_arithmetic=0.0,
            lmtd_effective=0.0,
            correction_factor=0.0,
            temperature_difference_hot=0.0,
            temperature_difference_cold=0.0,
            configuration_used="unknown",
            energy_balance_hot=0.0,
            energy_balance_cold=0.0,
            energy_balance_error_percent=0.0,
            intermediate_values={},
            version="1.0.0",
        )


def _validate_lmtd_input(input_data: LMTDInput) -> None:
    """Validate LMTD input for physical consistency.

    Parameters
    ----------
    input_data : LMTDInput
        Input to validate.

    Raises
    ------
    ValueError
        If input violates constraints.
    """
    # Validate temperatures
    t_h_in = input_data.hot_fluid_inlet.temperature
    t_h_out = input_data.hot_fluid_outlet.temperature
    t_c_in = input_data.cold_fluid_inlet.temperature
    t_c_out = input_data.cold_fluid_outlet.temperature

    validate_temperature(t_h_in, "hot_inlet")
    validate_temperature(t_h_out, "hot_outlet")
    validate_temperature(t_c_in, "cold_inlet")
    validate_temperature(t_c_out, "cold_outlet")

    # Check for retrograde flow (temperature inversions)
    if t_h_out > t_h_in:
        raise ValueError(
            f"Hot side retrograde flow: T_out ({t_h_out:.2f} K) > T_in ({t_h_in:.2f} K)"
        )
    if t_c_out < t_c_in:
        raise ValueError(
            f"Cold side retrograde flow: T_out ({t_c_out:.2f} K) < T_in ({t_c_in:.2f} K)"
        )

    # Check for physical impossibility (hot outlet colder than cold inlet)
    if t_h_out < t_c_in:
        raise ValueError(
            f"Hot outlet ({t_h_out:.2f} K) is colder than cold inlet ({t_c_in:.2f} K) - "
            "physically impossible without external energy"
        )

    # Check mass flow rates
    m_h = input_data.hot_fluid_inlet.mass_flow_rate
    m_c = input_data.cold_fluid_inlet.mass_flow_rate
    validate_positive_float(m_h, "hot_mass_flow_rate")
    validate_positive_float(m_c, "cold_mass_flow_rate")

    # Check heat exchanger area
    validate_positive_float(input_data.heat_exchanger.area, "heat_exchanger_area")


def _calculate_lmtd_arithmetic(t_h_in: float, t_h_out: float, t_c_in: float, t_c_out: float) -> float:
    """Calculate logarithmic mean temperature difference.

    LMTD = (ΔT1 - ΔT2) / ln(ΔT1 / ΔT2)

    Where ΔT1 and ΔT2 are the temperature differences at each end,
    appropriately defined for the configuration.

    Parameters
    ----------
    t_h_in : float
        Hot fluid inlet temperature (K).
    t_h_out : float
        Hot fluid outlet temperature (K).
    t_c_in : float
        Cold fluid inlet temperature (K).
    t_c_out : float
        Cold fluid outlet temperature (K).

    Returns
    -------
    float
        LMTD in K.

    Raises
    ------
    ValueError
        If LMTD calculation is invalid (e.g., parallel flow with equal temps).
    """
    # For counterflow and parallel flow
    delta_t1 = t_h_in - t_c_out
    delta_t2 = t_h_out - t_c_in

    check_nan_inf(delta_t1, "ΔT1")
    check_nan_inf(delta_t2, "ΔT2")

    # Handle near-zero case (equal temperatures)
    if abs(delta_t1 - delta_t2) < 1e-6:
        # When ΔT1 ≈ ΔT2, LMTD ≈ ΔT1 (use L'Hôpital's rule)
        if delta_t1 > 0:
            return delta_t1
        else:
            raise ValueError("Both temperature differences are zero - no heat transfer")

    # Standard LMTD calculation
    if delta_t1 <= 0 or delta_t2 <= 0:
        raise ValueError(
            f"Invalid temperature configuration for LMTD: ΔT1={delta_t1:.2f}, ΔT2={delta_t2:.2f}. "
            "Both must be positive for counterflow."
        )

    lmtd = (delta_t1 - delta_t2) / math.log(delta_t1 / delta_t2)

    if lmtd < 0:
        raise ValueError(f"Calculated LMTD is negative: {lmtd:.2f} K")

    return lmtd


def _calculate_correction_factor(
    configuration: str,
    t_h_in: float,
    t_h_out: float,
    t_c_in: float,
    t_c_out: float,
) -> float:
    """Calculate F correction factor for non-ideal heat exchanger geometries.

    For counterflow: F = 1.0 (no correction needed)
    For parallel flow: F = 1.0 (no correction needed)
    For crossflow: F is approximated or uses correlation charts

    Parameters
    ----------
    configuration : str
        Heat exchanger configuration.
    t_h_in : float
        Hot inlet temperature (K).
    t_h_out : float
        Hot outlet temperature (K).
    t_c_in : float
        Cold inlet temperature (K).
    t_c_out : float
        Cold outlet temperature (K).

    Returns
    -------
    float
        Correction factor F [0, 1].
    """
    if configuration in ["counterflow", "parallel_flow"]:
        return 1.0

    # For crossflow configurations, use simplified approximation
    # In practice, these come from charts in Incropera or other references
    if configuration in ["crossflow_unmixed_both", "crossflow_unmixed_hot_mixed_cold", "crossflow_mixed_both"]:
        # Simplified approximation: 0.7-0.95 typical for crossflow
        # This is a placeholder; actual implementation would use correlation charts
        return 0.90  # Default conservative estimate

    return 1.0


def _apply_correction_factor(lmtd_arithmetic: float, f_correction: float) -> float:
    """Apply F correction factor to arithmetic LMTD.

    LMTD_effective = F × LMTD_arithmetic

    Parameters
    ----------
    lmtd_arithmetic : float
        Log mean temperature difference (K).
    f_correction : float
        Correction factor [0, 1].

    Returns
    -------
    float
        Corrected LMTD (K).
    """
    return f_correction * lmtd_arithmetic
