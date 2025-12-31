"""
Valve performance and characteristics calculations.

Provides calculations for:
- Valve authority in system
- Valve rangeability analysis
- Relative flow capacity at different openings
- Valve performance verification
"""

from typing import Any


def calculate_valve_authority(
    valve_pressure_drop: float,
    system_pressure_drop: float,
) -> dict[str, Any]:
    """
    Calculate valve authority (relative pressure drop).

    Valve authority is the ratio of pressure drop across the valve to total
    system pressure drop. Higher authority (typically 0.3-0.5) provides better control.

    Authority = ΔP_valve / (ΔP_valve + ΔP_system)

    Parameters
    ----------
    valve_pressure_drop : float
        Pressure drop across valve in bar (SI) or psi (US)
    system_pressure_drop : float
        Total system pressure drop (excluding valve) in same units

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Valve authority (0-1)
        - 'assessment': Qualitative assessment of valve authority
        - 'recommendation': Advice on valve sizing
        - 'ideal_range': Typical ideal authority range
        - 'warnings': List of warnings if any
        - 'source': Reference information

    Raises
    ------
    ValueError
        If any required input is invalid
    """
    if valve_pressure_drop <= 0:
        raise ValueError("Valve pressure drop must be positive")
    if system_pressure_drop < 0:
        raise ValueError("System pressure drop cannot be negative")

    warnings = []

    total_drop = valve_pressure_drop + system_pressure_drop

    if total_drop == 0:
        raise ValueError("Total pressure drop must be positive")

    authority = valve_pressure_drop / total_drop

    # Assessment
    if authority < 0.2:
        assessment = "Low authority"
        recommendation = "Valve has poor control resolution. Consider larger valve with higher pressure drop."
    elif authority < 0.3:
        assessment = "Below optimal"
        recommendation = "Authority below typical range (0.3-0.5). May have reduced control response."
    elif authority <= 0.5:
        assessment = "Good authority"
        recommendation = "Valve authority in typical optimal range."
    elif authority <= 0.7:
        assessment = "High authority"
        recommendation = "Authority above typical range but acceptable."
    else:  # > 0.7
        assessment = "Very high authority"
        recommendation = "Valve pressure drop dominates; may overshadow system effects."

    if authority > 0.8:
        warnings.append("Very high valve authority may reduce pump efficiency significantly")

    return {
        "value": authority,
        "value_percentage": f"{authority * 100:.1f}%",
        "assessment": assessment,
        "recommendation": recommendation,
        "ideal_range": "0.3 - 0.5 (30-50%)",
        "valve_drop": valve_pressure_drop,
        "system_drop": system_pressure_drop,
        "total_drop": total_drop,
        "formula_used": "Authority = ΔP_valve / (ΔP_valve + ΔP_system)",
        "warnings": warnings,
        "source": "Valve authority calculation",
    }


def calculate_valve_rangeability(
    cv_min: float,
    cv_max: float,
    min_controllable_opening_percent: float = 5.0,
) -> dict[str, Any]:
    """
    Calculate valve rangeability (control range).

    Rangeability is the ratio of maximum to minimum controllable flow.
    Typical rangeability is 20:1 to 100:1 depending on valve type.

    Parameters
    ----------
    cv_min : float
        Cv at minimum controllable opening (typically 5%)
    cv_max : float
        Cv at maximum opening (100%)
    min_controllable_opening_percent : float, optional
        Minimum opening percentage, default 5.0

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Rangeability ratio (max:min)
        - 'assessment': Qualitative assessment
        - 'cv_min': Input minimum Cv
        - 'cv_max': Input maximum Cv
        - 'min_opening_percent': Minimum controllable opening
        - 'warnings': List of warnings if any
        - 'source': Reference information

    Raises
    ------
    ValueError
        If any required input is invalid
    """
    if cv_min <= 0:
        raise ValueError("Minimum Cv must be positive")
    if cv_max <= 0:
        raise ValueError("Maximum Cv must be positive")
    if cv_min > cv_max:
        raise ValueError("Minimum Cv cannot exceed maximum Cv")
    if min_controllable_opening_percent < 0 or min_controllable_opening_percent > 100:
        raise ValueError("Minimum opening percentage must be between 0 and 100")

    warnings = []

    rangeability = cv_max / cv_min

    # Assessment based on typical valve rangeability values
    if rangeability < 10:
        assessment = "Limited rangeability"
        recommendation = "Poor flow control range; may not be suitable for applications requiring broad turndown"
    elif rangeability < 20:
        assessment = "Moderate rangeability"
        recommendation = "Adequate for moderate flow control applications"
    elif rangeability <= 50:
        assessment = "Good rangeability"
        recommendation = "Suitable for most applications with variable flow"
    elif rangeability <= 100:
        assessment = "Excellent rangeability"
        recommendation = "Excellent for wide flow control range"
    else:
        assessment = "Outstanding rangeability"
        recommendation = "Suitable for very wide flow control applications"

    if rangeability < 20:
        warnings.append(
            "Rangeability below 20:1; may have difficulty controlling low flows"
        )

    return {
        "value": rangeability,
        "value_ratio": f"{rangeability:.1f}:1",
        "assessment": assessment,
        "recommendation": recommendation,
        "cv_min": cv_min,
        "cv_max": cv_max,
        "min_opening_percent": min_controllable_opening_percent,
        "typical_valve_types": {
            "ball_valve": "50:1 to 100:1",
            "globe_valve": "20:1 to 50:1",
            "butterfly_valve": "3:1 to 10:1",
            "needle_valve": "100:1 or higher",
        },
        "formula_used": "Rangeability = Cv_max / Cv_min",
        "warnings": warnings,
        "source": "Valve rangeability calculation",
    }


def calculate_relative_flow_capacity(
    opening_percent: float,
    valve_type: str = "linear",
) -> dict[str, Any]:
    """
    Calculate relative flow capacity at a given opening.

    Valve flow characteristic (how Cv changes with position):
    - Linear: Flow proportional to opening (Cv = Cv_max × opening)
    - Parabolic/Quadratic: More aggressive opening (Cv = Cv_max × opening²)
    - Equal percentage: Logarithmic relationship

    Parameters
    ----------
    opening_percent : float
        Valve opening position as percentage (0-100)
    valve_type : str, optional
        Valve characteristic type: 'linear', 'parabolic', 'equal_percentage'
        Default 'linear'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Relative flow capacity (0-1)
        - 'flow_percent': Flow as percentage of maximum
        - 'valve_type': Input valve type
        - 'description': Explanation of flow characteristic
        - 'formula_used': Mathematical formula for this characteristic
        - 'source': Reference information

    Raises
    ------
    ValueError
        If opening_percent or valve_type are invalid
    """
    if opening_percent < 0 or opening_percent > 100:
        raise ValueError("Opening percentage must be between 0 and 100")

    valve_type = valve_type.lower().strip()
    if valve_type not in ["linear", "parabolic", "equal_percentage"]:
        raise ValueError(
            "Valve type must be 'linear', 'parabolic', or 'equal_percentage'"
        )

    # Convert percentage to fraction
    x = opening_percent / 100.0

    # Calculate relative flow based on characteristic
    if valve_type == "linear":
        # Cv ∝ opening
        relative_flow = x
        description = "Linear flow characteristic: flow proportional to opening"
        formula = "Relative flow = opening%/100"
    elif valve_type == "parabolic":
        # Cv ∝ opening²
        relative_flow = x ** 2
        description = "Parabolic flow characteristic: flow proportional to opening squared"
        formula = "Relative flow = (opening%/100)²"
    else:  # equal_percentage
        # Logarithmic: Cv = Cv_max × R^(x-1)
        # Where R is rangeability (typically 50 for equal percentage)
        R = 50  # Typical rangeability parameter
        relative_flow = R ** (x - 1)
        # Normalize to 0-1 range
        relative_flow = min(relative_flow, 1.0)
        description = "Equal percentage characteristic: same percentage change in flow for each % opening change"
        formula = f"Relative flow = R^(opening%/100 - 1) where R={R}"

    return {
        "value": relative_flow,
        "flow_percent": relative_flow * 100,
        "valve_type": valve_type,
        "opening_percent": opening_percent,
        "description": description,
        "formula_used": formula,
        "characteristics": {
            "linear": "Fast response near closed, slow near open",
            "parabolic": "Good balance of control throughout range",
            "equal_percentage": "Slow response near closed, fast near open",
        },
        "source": "Valve flow characteristic calculation",
    }


def assess_valve_performance(
    cv_at_design: float,
    cv_max: float,
    pressure_drop_design: float,
    system_pressure_drop: float,
) -> dict[str, Any]:
    """
    Assess overall valve performance characteristics.

    Provides comprehensive assessment of valve performance including
    authority, opening percentage, and recommendations.

    Parameters
    ----------
    cv_at_design : float
        Valve Cv at design flow conditions
    cv_max : float
        Valve Cv at full opening
    pressure_drop_design : float
        Pressure drop at design conditions
    system_pressure_drop : float
        System pressure drop (pipe, fittings, etc.)

    Returns
    -------
    dict
        Result dictionary with comprehensive performance assessment
    """
    if cv_at_design <= 0 or cv_max <= 0:
        raise ValueError("Cv values must be positive")
    if cv_at_design > cv_max:
        raise ValueError("Design Cv cannot exceed maximum Cv")
    if pressure_drop_design <= 0:
        raise ValueError("Pressure drop must be positive")
    if system_pressure_drop < 0:
        raise ValueError("System pressure drop cannot be negative")

    # Calculate opening percentage
    opening_percent = (cv_at_design / cv_max) * 100

    # Calculate authority
    authority_result = calculate_valve_authority(
        pressure_drop_design, system_pressure_drop
    )

    # Check opening percentage
    if opening_percent < 10:
        opening_assessment = "Severely throttled"
        opening_warning = "Valve operating in very tight control range; poor resolution"
    elif opening_percent < 25:
        opening_assessment = "Heavily throttled"
        opening_warning = "Valve tight; consider larger valve for better control"
    elif opening_percent <= 75:
        opening_assessment = "Good operating range"
        opening_warning = None
    else:
        opening_assessment = "Nearly wide open"
        opening_warning = "Valve near full opening; limited control range remains"

    warnings = []
    if opening_warning:
        warnings.append(opening_warning)
    warnings.extend(authority_result["warnings"])

    return {
        "opening_percent": opening_percent,
        "opening_assessment": opening_assessment,
        "valve_authority": authority_result["value"],
        "authority_percentage": authority_result["value_percentage"],
        "authority_assessment": authority_result["assessment"],
        "cv_at_design": cv_at_design,
        "cv_max": cv_max,
        "pressure_drop_design": pressure_drop_design,
        "system_pressure_drop": system_pressure_drop,
        "total_pressure_drop": authority_result["total_drop"],
        "overall_assessment": f"{opening_assessment} with {authority_result['assessment']} authority",
        "recommendations": [
            authority_result["recommendation"],
            f"Valve operates at {opening_percent:.1f}% opening",
        ],
        "warnings": warnings,
        "source": "Comprehensive valve performance assessment",
    }
