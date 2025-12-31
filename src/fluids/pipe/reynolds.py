"""
Reynolds number calculation for pipe flow analysis.

Reynolds number determines flow regime (laminar, transitional, turbulent).
"""

from typing import Any, Dict, Optional
from fluids.core.validators import (
    validate_reynolds_components,
    validate_flow_regime,
)
from fluids.output.formatter import create_result


def calculate_reynolds(
    density: float,
    velocity: float,
    diameter: float,
    viscosity: float,
    unit_system: str = "SI",
) -> Dict[str, Any]:
    """
    Calculate Reynolds number for pipe flow.

    Reynolds number Re = ρVD/μ is used to determine flow regime:
    - Re < 2300: Laminar flow
    - 2300 ≤ Re ≤ 4000: Transitional flow
    - Re > 4000: Turbulent flow

    Args:
        density: Fluid density in kg/m³ (SI) or lb/ft³ (US)
        velocity: Flow velocity in m/s (SI) or ft/s (US)
        diameter: Pipe diameter in m (SI) or ft (US)
        viscosity: Dynamic viscosity in Pa·s (SI) or lb/(ft·s) (US)
        unit_system: 'SI' or 'US'

    Returns:
        Dictionary with:
        - reynolds_number: Calculated Reynolds number (dimensionless)
        - flow_regime: 'laminar', 'transitional', or 'turbulent'
        - warnings: List of warnings if any

    Raises:
        ValueError: If inputs are invalid or negative
    """
    # Validate inputs
    is_valid, error_msg = validate_reynolds_components(
        density, velocity, diameter, viscosity
    )
    if not is_valid:
        raise ValueError(error_msg)

    # Calculate Reynolds number (formula is independent of unit system)
    reynolds_number = (density * velocity * diameter) / viscosity

    # Determine flow regime and get warning if needed
    regime, warning = validate_flow_regime(reynolds_number)

    # Build result
    warnings = []
    if warning:
        warnings.append(warning)

    result = create_result(
        value=reynolds_number,
        unit="dimensionless",
        formula_used="Re = ρVD/μ",
        intermediate_values={
            "density": density,
            "velocity": velocity,
            "diameter": diameter,
            "viscosity": viscosity,
            "flow_regime": regime,
        },
        warnings=warnings,
        source="Standard fluid mechanics formula",
    )

    # Add calculated properties to result
    result["flow_regime"] = regime

    return result
