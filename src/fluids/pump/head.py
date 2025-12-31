"""
Pump head calculations.

Provides calculations for pump head requirements including:
- Static head (elevation changes)
- Dynamic head (velocity head)
- Pressure head (system pressure differences)
- Total head (sum of all head components)
"""

from typing import Dict, Any, Optional


def calculate_total_head(
    elevation_change: float,
    pressure_drop: float,
    velocity: float,
    fluid_density: float = 1000.0,
    g: float = 9.81,
    unit_system: str = "SI",
) -> Dict[str, Any]:
    """
    Calculate total head required by pump.

    The total head is the sum of static head (elevation), dynamic head (velocity),
    and pressure head (system resistance).

    Parameters
    ----------
    elevation_change : float
        Elevation difference between discharge and suction (m in SI, ft in US)
    pressure_drop : float
        System pressure drop in Pa (SI) or psi (US customary)
    velocity : float
        Fluid velocity in pipe (m/s in SI, ft/s in US)
    fluid_density : float, optional
        Fluid density in kg/m³ (SI) or lb/ft³ (US), default 1000.0
    g : float, optional
        Gravitational acceleration, default 9.81 m/s²
    unit_system : str, optional
        Unit system: 'SI' or 'US', default 'SI'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Total head in meters (SI) or feet (US)
        - 'unit': Unit of head measurement
        - 'static_head': Elevation head component
        - 'dynamic_head': Velocity head component
        - 'pressure_head': Pressure drop converted to head
        - 'formula_used': Description of calculation method
        - 'warnings': List of warnings if any
        - 'intermediate_values': Dict of intermediate calculation values

    Raises
    ------
    ValueError
        If any required input is invalid or unphysical
    """
    from fluids.core.validators import validate_pipe_geometry, validate_unit_system

    # Validate inputs
    is_valid, error_msg = validate_unit_system(unit_system)
    if not is_valid:
        raise ValueError(error_msg)

    if elevation_change < 0:
        raise ValueError("Elevation change cannot be negative")
    if pressure_drop < 0:
        raise ValueError("Pressure drop cannot be negative")
    if velocity < 0:
        raise ValueError("Velocity cannot be negative")
    if fluid_density <= 0:
        raise ValueError("Fluid density must be positive")

    warnings = []

    # Calculate static head (elevation)
    static_head = elevation_change

    # Calculate dynamic head (velocity head): h_v = V²/(2g)
    if velocity > 0:
        dynamic_head = (velocity ** 2) / (2 * g)
    else:
        dynamic_head = 0.0
        warnings.append("Zero velocity: dynamic head component is zero")

    # Convert pressure drop to head
    # ΔH = ΔP / (ρg)
    if unit_system == "SI":
        # pressure_drop in Pa, result in m
        pressure_head = pressure_drop / (fluid_density * g)
        unit = "m"
    else:  # US customary
        # pressure_drop in psi, convert to pressure head in ft
        # 1 psi = 2.3066 ft of water for density ~62.4 lb/ft³
        # More general: ΔH = ΔP / (ρ * g) where ρ is in lb/ft³ and g conversion is built in
        # For US: ΔH(ft) = ΔP(psi) * 144 / ρ(lb/ft³) / 32.174
        pressure_head = pressure_drop * 144.0 / (fluid_density * 32.174)
        unit = "ft"

    # Total head
    total_head = static_head + dynamic_head + pressure_head

    return {
        "value": total_head,
        "unit": unit,
        "static_head": static_head,
        "dynamic_head": dynamic_head,
        "pressure_head": pressure_head,
        "formula_used": "H_total = H_static + H_dynamic + H_pressure",
        "warnings": warnings,
        "intermediate_values": {
            "elevation_change": elevation_change,
            "pressure_drop": pressure_drop,
            "velocity": velocity,
            "fluid_density": fluid_density,
            "gravitational_acceleration": g,
            "velocity_head_formula": "V²/(2g)",
            "pressure_head_formula": "ΔP/(ρg)" if unit_system == "SI" else "ΔP*144/(ρ*32.174)",
        },
        "source": "Pump head calculation (3-component method)",
    }


def calculate_static_head(
    elevation_change: float,
    unit_system: str = "SI",
) -> Dict[str, Any]:
    """
    Calculate static head (elevation change).

    Static head is the vertical height difference between discharge and suction points.

    Parameters
    ----------
    elevation_change : float
        Elevation difference in meters (SI) or feet (US)
    unit_system : str, optional
        Unit system: 'SI' or 'US', default 'SI'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Static head
        - 'unit': Unit of measurement
        - 'formula_used': Description of calculation
        - 'warnings': List of warnings if any
        - 'source': Reference information
    """
    from fluids.core.validators import validate_unit_system

    is_valid, error_msg = validate_unit_system(unit_system)
    if not is_valid:
        raise ValueError(error_msg)

    if elevation_change < 0:
        raise ValueError("Elevation change cannot be negative")

    warnings = []
    unit = "m" if unit_system == "SI" else "ft"

    if elevation_change == 0:
        warnings.append("Zero elevation change: static head is zero")

    return {
        "value": elevation_change,
        "unit": unit,
        "formula_used": "H_static = Δz (elevation change)",
        "warnings": warnings,
        "source": "Static head calculation",
    }


def calculate_dynamic_head(
    velocity: float,
    g: float = 9.81,
    unit_system: str = "SI",
) -> Dict[str, Any]:
    """
    Calculate dynamic head (velocity head).

    Dynamic head is the kinetic energy of the fluid expressed as head.
    H_velocity = V²/(2g)

    Parameters
    ----------
    velocity : float
        Fluid velocity in m/s (SI) or ft/s (US)
    g : float, optional
        Gravitational acceleration, default 9.81 m/s² (SI) or 32.174 ft/s² (US)
    unit_system : str, optional
        Unit system: 'SI' or 'US', default 'SI'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Dynamic head
        - 'unit': Unit of measurement
        - 'formula_used': Description of calculation
        - 'warnings': List of warnings if any
        - 'source': Reference information
    """
    from fluids.core.validators import validate_unit_system

    is_valid, error_msg = validate_unit_system(unit_system)
    if not is_valid:
        raise ValueError(error_msg)

    if velocity < 0:
        raise ValueError("Velocity cannot be negative")

    warnings = []
    unit = "m" if unit_system == "SI" else "ft"

    # Adjust g for US customary if needed
    if unit_system == "US" and g == 9.81:
        g = 32.174

    # Calculate dynamic head
    if velocity > 0:
        dynamic_head = (velocity ** 2) / (2 * g)
    else:
        dynamic_head = 0.0
        warnings.append("Zero velocity: dynamic head is zero")

    return {
        "value": dynamic_head,
        "unit": unit,
        "formula_used": "H_dynamic = V²/(2g)",
        "warnings": warnings,
        "intermediate_values": {
            "velocity": velocity,
            "gravitational_acceleration": g,
        },
        "source": "Dynamic head calculation (velocity head)",
    }
