"""
Valve Cv (flow coefficient) calculations.

Provides calculations for:
- Cv (flow coefficient) determination
- Flow rate through valve
- Valve sizing based on required flow
"""

import math
from typing import Any


def calculate_cv_required(
    flow_rate: float,
    pressure_drop: float,
    fluid_gravity: float = 1.0,
    unit_system: str = "SI",
) -> dict[str, Any]:
    """
    Calculate Cv required for given flow and pressure drop.

    Cv is the flow coefficient that describes the flow capacity of a valve.
    For liquids: Q = Cv * sqrt(ΔP / sg)
    where Q in gpm, Cv in gpm/√psi/sg, ΔP in psi, sg is specific gravity

    For SI: Q = Cv * sqrt(ΔP)
    where Q in m³/h, Cv in (m³/h)/√bar

    Parameters
    ----------
    flow_rate : float
        Volumetric flow rate in m³/h (SI) or gpm (US)
    pressure_drop : float
        Pressure drop across valve in bar (SI) or psi (US)
    fluid_gravity : float, optional
        Specific gravity of fluid (water = 1.0), default 1.0
    unit_system : str, optional
        Unit system: 'SI' or 'US', default 'SI'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Cv coefficient required
        - 'unit': Unit of Cv
        - 'flow_rate': Input flow rate
        - 'pressure_drop': Input pressure drop
        - 'specific_gravity': Fluid specific gravity
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

    if flow_rate < 0:
        raise ValueError("Flow rate cannot be negative")
    if pressure_drop <= 0:
        raise ValueError("Pressure drop must be positive")
    if fluid_gravity <= 0:
        raise ValueError("Specific gravity must be positive")

    warnings = []

    # Calculate Cv
    if unit_system == "SI":
        # Q = Cv * sqrt(ΔP)
        # Cv = Q / sqrt(ΔP)
        if pressure_drop == 0:
            raise ValueError("Pressure drop cannot be zero")

        cv = flow_rate / math.sqrt(pressure_drop)
        unit = "(m³/h)/√bar"
    else:  # US customary
        # Q = Cv * sqrt(ΔP / sg)
        # Cv = Q / sqrt(ΔP / sg) = Q * sqrt(sg / ΔP)
        if pressure_drop == 0:
            raise ValueError("Pressure drop cannot be zero")

        cv = flow_rate / math.sqrt(pressure_drop / fluid_gravity)
        unit = "gpm/√psi/sg"

    # Warnings for very small or very large Cv
    if cv < 0.1:
        warnings.append(
            f"Cv {cv:.3f} is very small; may result in poor control resolution"
        )
    if cv > 1000:
        warnings.append(f"Cv {cv:.1f} is very large; consider multiple valves")

    return {
        "value": cv,
        "unit": unit,
        "flow_rate": flow_rate,
        "pressure_drop": pressure_drop,
        "specific_gravity": fluid_gravity,
        "formula_used": "Q = Cv × √(ΔP/sg)" if unit_system == "US" else "Q = Cv × √ΔP",
        "warnings": warnings,
        "intermediate_values": {
            "flow_rate": flow_rate,
            "pressure_drop": pressure_drop,
            "fluid_gravity": fluid_gravity,
        },
        "source": "Valve Cv calculation (IEC 60534 flow capacity)",
    }


def calculate_flow_rate_through_valve(
    cv: float,
    pressure_drop: float,
    fluid_gravity: float = 1.0,
    unit_system: str = "SI",
) -> dict[str, Any]:
    """
    Calculate flow rate through valve given Cv and pressure drop.

    Uses the valve flow equation:
    Q = Cv * sqrt(ΔP / sg) (US customary)
    Q = Cv * sqrt(ΔP) (SI)

    Parameters
    ----------
    cv : float
        Valve Cv coefficient (flow coefficient)
    pressure_drop : float
        Pressure drop across valve in bar (SI) or psi (US)
    fluid_gravity : float, optional
        Specific gravity of fluid, default 1.0
    unit_system : str, optional
        Unit system: 'SI' or 'US', default 'SI'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Flow rate through valve
        - 'unit': Unit of flow rate (m³/h for SI, gpm for US)
        - 'cv': Input Cv value
        - 'pressure_drop': Input pressure drop
        - 'specific_gravity': Fluid specific gravity
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

    if cv <= 0:
        raise ValueError("Cv must be positive")
    if pressure_drop <= 0:
        raise ValueError("Pressure drop must be positive")
    if fluid_gravity <= 0:
        raise ValueError("Specific gravity must be positive")

    warnings = []

    # Calculate flow rate
    if unit_system == "SI":
        # Q = Cv * sqrt(ΔP)
        flow_rate = cv * math.sqrt(pressure_drop)
        unit = "m³/h"
    else:  # US customary
        # Q = Cv * sqrt(ΔP / sg)
        flow_rate = cv * math.sqrt(pressure_drop / fluid_gravity)
        unit = "gpm"

    # Warning if flow rate is unusually high or low
    if flow_rate > 10000:
        warnings.append("Flow rate unusually high; verify valve specifications")
    if flow_rate < 0.01:
        warnings.append("Flow rate very low; may cause control issues")

    return {
        "value": flow_rate,
        "unit": unit,
        "cv": cv,
        "pressure_drop": pressure_drop,
        "specific_gravity": fluid_gravity,
        "formula_used": "Q = Cv × √(ΔP/sg)" if unit_system == "US" else "Q = Cv × √ΔP",
        "warnings": warnings,
        "intermediate_values": {
            "cv": cv,
            "pressure_drop": pressure_drop,
            "pressure_ratio_term": pressure_drop / fluid_gravity if unit_system == "US" else pressure_drop,
        },
        "source": "Valve flow rate calculation (IEC 60534)",
    }


def calculate_valve_sizing(
    flow_rate: float,
    pressure_drop: float,
    valve_cv_options: list,
    fluid_gravity: float = 1.0,
    unit_system: str = "SI",
) -> dict[str, Any]:
    """
    Find suitable valve Cv from available options.

    Selects valve that:
    1. Can handle the required flow at given pressure drop
    2. Stays within typical operating range (typically 10%-90% open)
    3. Minimizes oversizing

    Parameters
    ----------
    flow_rate : float
        Required flow rate in m³/h (SI) or gpm (US)
    pressure_drop : float
        Pressure drop across valve in bar (SI) or psi (US)
    valve_cv_options : list
        List of available valve Cv values (integers or floats)
    fluid_gravity : float, optional
        Specific gravity of fluid, default 1.0
    unit_system : str, optional
        Unit system: 'SI' or 'US', default 'SI'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'recommended_cv': Recommended valve Cv
        - 'recommended_percentage': Opening percentage at design flow
        - 'alternative_cvs': List of alternative suitable valves
        - 'reasons': Explanation of recommendation
        - 'warnings': List of warnings if any
        - 'source': Reference information

    Raises
    ------
    ValueError
        If no suitable valve found
    """
    from fluids.core.validators import validate_unit_system

    is_valid, error_msg = validate_unit_system(unit_system)
    if not is_valid:
        raise ValueError(error_msg)

    if flow_rate <= 0:
        raise ValueError("Flow rate must be positive")
    if pressure_drop <= 0:
        raise ValueError("Pressure drop must be positive")
    if not valve_cv_options or len(valve_cv_options) == 0:
        raise ValueError("Must provide at least one valve Cv option")

    warnings = []
    suitable_valves = []

    # Ideal Cv needed
    cv_needed = calculate_cv_required(
        flow_rate, pressure_drop, fluid_gravity, unit_system
    )["value"]

    # Evaluate each option
    for cv_option in sorted(valve_cv_options):
        # Flow at design pressure drop
        flow_at_dp = calculate_flow_rate_through_valve(
            cv_option, pressure_drop, fluid_gravity, unit_system
        )["value"]

        # Opening percentage (assuming linear relationship between Cv and opening)
        # This is a simplification; actual pump curves vary
        opening_percent = (cv_needed / cv_option) * 100

        # Check if valve operates in reasonable range
        if 10 <= opening_percent <= 90:
            suitable_valves.append(
                {
                    "cv": cv_option,
                    "opening_percent": opening_percent,
                    "flow_capacity": flow_at_dp,
                    "oversizing_ratio": cv_option / cv_needed,
                }
            )

    if not suitable_valves:
        # If no valve in typical range, find closest match
        best_valve = min(
            valve_cv_options,
            key=lambda cv: abs(cv - cv_needed),
        )
        suitable_valves = [
            {
                "cv": best_valve,
                "opening_percent": (cv_needed / best_valve) * 100,
                "flow_capacity": calculate_flow_rate_through_valve(
                    best_valve, pressure_drop, fluid_gravity, unit_system
                )["value"],
                "oversizing_ratio": best_valve / cv_needed,
            }
        ]
        warnings.append(
            f"No valve found in 10-90% opening range; selected closest match Cv={best_valve}"
        )

    # Recommend the smallest valve that meets requirements
    recommended = min(suitable_valves, key=lambda v: v["cv"])

    return {
        "recommended_cv": recommended["cv"],
        "recommended_percentage": recommended["opening_percent"],
        "oversizing_factor": recommended["oversizing_ratio"],
        "required_cv": cv_needed,
        "alternative_cvs": [v["cv"] for v in suitable_valves[1:]],
        "all_suitable_options": suitable_valves,
        "reasons": [
            f"Valve opening at design flow: {recommended['opening_percent']:.1f}%",
            f"Oversizing ratio: {recommended['oversizing_ratio']:.2f}x",
        ],
        "warnings": warnings,
        "source": "Valve sizing selection",
    }
