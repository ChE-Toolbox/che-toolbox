"""
Darcy-Weisbach pressure drop calculation for pipe flow.
"""

from typing import Any

from fluids.core.validators import validate_pressure_drop_inputs
from fluids.output.formatter import create_result


def calculate_pressure_drop(
    friction_factor: float,
    length: float,
    diameter: float,
    velocity: float,
    density: float,
    unit_system: str = "SI",
) -> dict[str, Any]:
    """
    Calculate pressure drop using Darcy-Weisbach equation.

    ΔP = f × (L/D) × (ρV²/2)

    Args:
        friction_factor: Dimensionless friction factor
        length: Pipe length in m (SI) or ft (US)
        diameter: Pipe diameter in m (SI) or ft (US)
        velocity: Average flow velocity in m/s (SI) or ft/s (US)
        density: Fluid density in kg/m³ (SI) or lb/ft³ (US)
        unit_system: 'SI' or 'US'

    Returns:
        Dictionary with:
        - pressure_drop: Calculated pressure drop in Pa (SI) or psi (US)
        - intermediate_values: Components of calculation
        - formula_used: Darcy-Weisbach equation

    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs
    is_valid, error_msg = validate_pressure_drop_inputs(
        friction_factor, length, diameter, velocity, density
    )
    if not is_valid:
        raise ValueError(error_msg)

    # Handle zero velocity
    if velocity == 0:
        return create_result(
            value=0.0,
            unit="Pa" if unit_system == "SI" else "psi",
            formula_used="ΔP = f × (L/D) × (ρV²/2)",
            intermediate_values={
                "friction_factor": friction_factor,
                "length": length,
                "diameter": diameter,
                "velocity": velocity,
                "dynamic_pressure": 0.0,
            },
            warnings=["Zero velocity indicates zero flow and zero pressure drop"],
            source="Darcy-Weisbach equation",
        )

    # Calculate components
    length_diameter_ratio = length / diameter
    dynamic_pressure = (density * velocity**2) / 2

    # Calculate pressure drop (Pa for SI, or needs conversion for US)
    pressure_drop = friction_factor * length_diameter_ratio * dynamic_pressure

    # Convert if needed
    if unit_system == "US":
        # Convert Pa to psi (1 psi = 6894.76 Pa)
        pressure_drop = pressure_drop / 6894.76

    result = create_result(
        value=pressure_drop,
        unit="Pa" if unit_system == "SI" else "psi",
        formula_used="ΔP = f × (L/D) × (ρV²/2)",
        intermediate_values={
            "friction_factor": friction_factor,
            "length_diameter_ratio": length_diameter_ratio,
            "dynamic_pressure": dynamic_pressure,
            "velocity": velocity,
            "diameter": diameter,
            "length": length,
            "density": density,
        },
        source="Darcy-Weisbach equation",
        reference_data="Crane TP-410",
    )

    return result
