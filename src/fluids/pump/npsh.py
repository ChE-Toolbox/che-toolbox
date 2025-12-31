"""
Net Positive Suction Head (NPSH) calculations.

Provides calculations for:
- NPSH available (NPSHA): Suction head available in system
- NPSH required (NPSHR): Suction head required by pump
- Cavitation risk assessment
"""

from typing import Dict, Any


def calculate_npsh_available(
    atmospheric_pressure: float,
    vapor_pressure: float,
    suction_head: float,
    suction_losses: float = 0.0,
    fluid_density: float = 1000.0,
    g: float = 9.81,
    unit_system: str = "SI",
) -> Dict[str, Any]:
    """
    Calculate NPSH available in the system.

    NPSH Available (NPSHA) is the total head available at the pump suction.
    It accounts for atmospheric pressure, vapor pressure, elevation,
    and suction line losses.

    NPSHA = (P_atm - P_vapor) / (ρg) + h_suction - h_losses

    Parameters
    ----------
    atmospheric_pressure : float
        Atmospheric pressure in Pa (SI) or psi (US)
    vapor_pressure : float
        Fluid vapor pressure in Pa (SI) or psi (US) - same units as atmospheric
    suction_head : float
        Suction elevation head in meters (SI) or feet (US)
        Positive if suction source is above pump centerline (flooded suction)
        Negative if pump is above suction source (priming required)
    suction_losses : float, optional
        Pressure losses in suction line in Pa (SI) or psi (US), default 0.0
    fluid_density : float, optional
        Fluid density in kg/m³ (SI) or lb/ft³ (US), default 1000.0
    g : float, optional
        Gravitational acceleration, default 9.81 m/s² (SI)
    unit_system : str, optional
        Unit system: 'SI' or 'US', default 'SI'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': NPSH available in meters (SI) or feet (US)
        - 'unit': Unit of measurement
        - 'pressure_head': Pressure head component [(P_atm - P_vapor)/(ρg)]
        - 'suction_head': Static suction head
        - 'suction_loss_head': Suction line losses in head form
        - 'formula_used': Description of calculation
        - 'warnings': List of warnings if any
        - 'source': Reference information

    Raises
    ------
    ValueError
        If any required input is invalid
    """
    from fluids.core.validators import validate_unit_system

    is_valid, error_msg = validate_unit_system(unit_system)
    if not is_valid:
        raise ValueError(error_msg)

    if atmospheric_pressure <= 0:
        raise ValueError("Atmospheric pressure must be positive")
    if vapor_pressure < 0:
        raise ValueError("Vapor pressure cannot be negative")
    if vapor_pressure > atmospheric_pressure:
        raise ValueError("Vapor pressure cannot exceed atmospheric pressure")
    if suction_losses < 0:
        raise ValueError("Suction losses cannot be negative")
    if fluid_density <= 0:
        raise ValueError("Fluid density must be positive")

    warnings = []

    # Convert pressures to head
    if unit_system == "SI":
        # Pressure head = ΔP / (ρg) in meters
        pressure_head = (atmospheric_pressure - vapor_pressure) / (
            fluid_density * g
        )
        unit = "m"
    else:  # US customary
        # Pressure head in feet
        # 1 psi = 2.3066 ft of water (for ρ = 62.4 lb/ft³)
        # More general: head = pressure * 144 / (ρ * 32.174)
        pressure_head = (atmospheric_pressure - vapor_pressure) * 144.0 / (
            fluid_density * 32.174
        )
        unit = "ft"

    # Convert suction losses to head
    if unit_system == "SI":
        loss_head = suction_losses / (fluid_density * g)
    else:  # US customary
        loss_head = suction_losses * 144.0 / (fluid_density * 32.174)

    # Calculate NPSHA
    npsha = pressure_head + suction_head - loss_head

    # Warnings
    if suction_head < 0:
        warnings.append(
            f"Negative suction head {suction_head:.2f} {unit}: pump is above source (lift/priming required)"
        )
    if npsha < 0:
        warnings.append("NEGATIVE NPSHA: System cannot supply adequate suction head")

    return {
        "value": npsha,
        "unit": unit,
        "pressure_head": pressure_head,
        "suction_head": suction_head,
        "suction_loss_head": loss_head,
        "net_available": npsha,
        "formula_used": "NPSHA = (P_atm - P_vapor)/(ρg) + h_suction - h_losses",
        "warnings": warnings,
        "intermediate_values": {
            "atmospheric_pressure": atmospheric_pressure,
            "vapor_pressure": vapor_pressure,
            "pressure_margin": atmospheric_pressure - vapor_pressure,
            "suction_losses": suction_losses,
            "fluid_density": fluid_density,
            "gravitational_acceleration": g,
        },
        "source": "NPSH Available calculation",
    }


def calculate_npsh_required(
    pump_design_point_flow: float,
    actual_flow: float,
    npsh_required_at_design: float = 1.0,
) -> Dict[str, Any]:
    """
    Calculate NPSH required by pump at operating conditions.

    NPSH Required varies with flow rate. This uses a square-law relationship
    commonly found in pump curves.

    NPSHR = NPSHR_design * (Q_actual / Q_design)²

    Parameters
    ----------
    pump_design_point_flow : float
        Design flow rate for pump (m³/s in SI, gpm or ft³/s in US)
    actual_flow : float
        Actual operating flow rate (same units as design)
    npsh_required_at_design : float, optional
        NPSH required at design point in meters (SI) or feet (US), default 1.0

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': NPSH required at actual flow
        - 'unit': Unit of measurement (same as input NPSH)
        - 'design_flow': Design point flow
        - 'actual_flow': Actual operating flow
        - 'design_npsh': NPSH at design point
        - 'flow_ratio': Ratio of actual to design flow
        - 'formula_used': Description of calculation
        - 'warnings': List of warnings if any
        - 'source': Reference information

    Raises
    ------
    ValueError
        If any required input is invalid
    """
    if pump_design_point_flow <= 0:
        raise ValueError("Design point flow must be positive")
    if actual_flow < 0:
        raise ValueError("Actual flow cannot be negative")
    if npsh_required_at_design <= 0:
        raise ValueError("NPSH required at design must be positive")

    warnings = []

    flow_ratio = actual_flow / pump_design_point_flow

    if flow_ratio > 1.2:
        warnings.append(
            f"Operating at {flow_ratio:.2%} of design flow: pump may be unstable or damaged"
        )
    if flow_ratio < 0.5:
        warnings.append(
            f"Operating at only {flow_ratio:.2%} of design flow: pump performance severely reduced"
        )

    # Square-law relationship for NPSH required
    npsh_required = npsh_required_at_design * (flow_ratio ** 2)

    return {
        "value": npsh_required,
        "unit": "m (SI) or ft (US) - same as design NPSH input",
        "design_flow": pump_design_point_flow,
        "actual_flow": actual_flow,
        "design_npsh": npsh_required_at_design,
        "flow_ratio": flow_ratio,
        "flow_ratio_percentage": f"{flow_ratio * 100:.1f}%",
        "formula_used": "NPSHR = NPSHR_design × (Q_actual / Q_design)²",
        "warnings": warnings,
        "intermediate_values": {
            "design_point_flow": pump_design_point_flow,
            "actual_flow": actual_flow,
            "npsh_at_design": npsh_required_at_design,
            "flow_ratio_squared": flow_ratio ** 2,
        },
        "source": "NPSH Required calculation (pump performance curve)",
    }


def check_cavitation_risk(
    npsh_available: float,
    npsh_required: float,
) -> Dict[str, Any]:
    """
    Check cavitation risk based on NPSH margin.

    Cavitation occurs when local pressure drops below vapor pressure,
    creating vapor bubbles that collapse and can damage pump components.

    Parameters
    ----------
    npsh_available : float
        NPSH available in system
    npsh_required : float
        NPSH required by pump at operating conditions

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'cavitation_risk': Risk level ('safe', 'marginal', 'danger', 'critical')
        - 'npsh_margin': Difference between available and required
        - 'margin_percentage': Margin as percentage of required
        - 'recommendation': Advice on mitigation
        - 'source': Reference information

    Raises
    ------
    ValueError
        If inputs are invalid
    """
    if npsh_available < 0 or npsh_required < 0:
        raise ValueError("NPSH values cannot be negative")

    margin = npsh_available - npsh_required
    margin_percent = (margin / npsh_required * 100) if npsh_required > 0 else 0

    # Classification based on margin
    if npsh_available < npsh_required:
        risk_level = "critical"
        recommendation = "CRITICAL: Cavitation will occur. Increase system pressure, reduce flow, or switch to lower-NPSH pump."
    elif margin_percent < 10:
        risk_level = "danger"
        recommendation = "DANGER: Very low margin. Minor system changes may cause cavitation. Review suction conditions."
    elif margin_percent < 20:
        risk_level = "marginal"
        recommendation = "MARGINAL: Acceptable but with minimal safety margin. Monitor for cavitation noise/vibration."
    else:
        risk_level = "safe"
        recommendation = "SAFE: Adequate NPSH margin. Normal operation expected."

    return {
        "cavitation_risk": risk_level,
        "npsh_available": npsh_available,
        "npsh_required": npsh_required,
        "npsh_margin": margin,
        "margin_percentage": f"{margin_percent:.1f}%",
        "recommendation": recommendation,
        "safety_threshold_percent": 20,
        "source": "Cavitation risk assessment",
    }
