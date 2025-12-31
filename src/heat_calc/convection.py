"""Convection heat transfer calculations.

Provides correlations for calculating convection heat transfer coefficients
for various geometries and flow regimes, including:
- Flat plate (forced convection, laminar/turbulent)
- Pipe flow (internal forced convection)
- Cylinder in crossflow (external forced convection)
- Vertical plate (natural convection)

References
----------
[1] Incropera & DeWitt: "Fundamentals of Heat and Mass Transfer"
[2] Perry's Chemical Engineers' Handbook
[3] Churchill, S.W. and Bernstein, M., "A Correlating Equation for Forced Convection"
"""

import math

from heat_calc.models.convection_input import (
    CylinderCrossflowConvection,
    FlatPlateConvection,
    PipeFlowConvection,
    VerticalPlateNaturalConvection,
)
from heat_calc.models.convection_results import ConvectionResult

# Type alias for any convection input
ConvectionInput = (
    FlatPlateConvection
    | PipeFlowConvection
    | CylinderCrossflowConvection
    | VerticalPlateNaturalConvection
)


def calculate_convection(input_data: ConvectionInput) -> ConvectionResult:
    """Calculate convection heat transfer coefficient for specified geometry.

    Dispatches to geometry-specific correlation functions based on input type.

    Parameters
    ----------
    input_data : ConvectionInput
        Geometry-specific input data (flat plate, pipe, cylinder, or natural convection).

    Returns
    -------
    ConvectionResult
        Complete results including h, dimensionless numbers, and flow regime.

    Raises
    ------
    ValueError
        If geometry type is not recognized or input data is invalid.

    Example
    -------
    >>> from heat_calc.models import FlatPlateConvection, FluidProperties
    >>>
    >>> props = FluidProperties(
    ...     density=1.2,
    ...     dynamic_viscosity=1.8e-5,
    ...     thermal_conductivity=0.026,
    ...     specific_heat=1005.0
    ... )
    >>>
    >>> flat_plate = FlatPlateConvection(
    ...     length=1.0,
    ...     flow_velocity=5.0,
    ...     surface_temperature=350.0,
    ...     bulk_fluid_temperature=300.0,
    ...     fluid_properties=props
    ... )
    >>>
    >>> result = calculate_convection(flat_plate)
    >>> print(f"h = {result.h:.2f} W/(m²·K)")
    """
    if isinstance(input_data, FlatPlateConvection):
        return _calculate_flat_plate(input_data)
    elif isinstance(input_data, PipeFlowConvection):
        return _calculate_pipe_flow(input_data)
    elif isinstance(input_data, CylinderCrossflowConvection):
        return _calculate_cylinder_crossflow(input_data)
    elif isinstance(input_data, VerticalPlateNaturalConvection):
        return _calculate_natural_convection(input_data)
    else:
        raise ValueError(f"Unknown geometry type: {type(input_data)}")


def _calculate_flat_plate(input_data: FlatPlateConvection) -> ConvectionResult:
    """Calculate convection coefficient for forced flow over a flat plate.

    Uses standard correlations:
    - Laminar (Re < 5e5): Nu = 0.664 × Re^0.5 × Pr^(1/3)
    - Turbulent (Re >= 5e5): Nu = 0.037 × Re^0.8 × Pr^(1/3)
    - Mixed regime: Combined correlation

    Parameters
    ----------
    input_data : FlatPlateConvection
        Flat plate geometry and flow conditions.

    Returns
    -------
    ConvectionResult
        Results with h, Re, Pr, Nu, and flow regime.
    """
    props = input_data.fluid_properties
    L = input_data.length
    U = input_data.flow_velocity
    k = props.thermal_conductivity
    mu = props.dynamic_viscosity
    rho = props.density
    cp = props.specific_heat

    # Calculate dimensionless numbers
    Re = rho * U * L / mu
    Pr = cp * mu / k

    # Determine flow regime and calculate Nusselt number
    Re_crit = 5e5

    if Re < Re_crit:
        # Laminar flow
        Nu = 0.664 * Re**0.5 * Pr ** (1 / 3)
        flow_regime = "laminar"
        correlation = "Blasius laminar flat plate"
        applicable_range = {
            "Re": (1e3, 5e5),
            "Pr": (0.6, 50),
        }
    else:
        # Turbulent flow
        Nu = 0.037 * Re**0.8 * Pr ** (1 / 3)
        flow_regime = "turbulent"
        correlation = "Turbulent flat plate (0.037 Re^0.8)"
        applicable_range = {
            "Re": (5e5, 1e8),
            "Pr": (0.6, 60),
        }

    # Calculate heat transfer coefficient
    h = Nu * k / L

    # Check if within correlation range
    is_within_range = _check_correlation_range({"Re": Re, "Pr": Pr}, applicable_range)

    return ConvectionResult(
        primary_value=h,
        calculation_method=f"Flat plate {flow_regime} convection",
        success=True,
        error_message="",
        intermediate_values={
            "characteristic_length_m": L,
            "flow_velocity_m_s": U,
            "fluid_density_kg_m3": rho,
            "dynamic_viscosity_Pa_s": mu,
            "thermal_conductivity_W_mK": k,
            "specific_heat_J_kgK": cp,
        },
        version="1.0.0",
        h=h,
        Reynolds=Re,
        Prandtl=Pr,
        Nusselt=Nu,
        Grashof=None,
        Rayleigh=None,
        flow_regime=flow_regime,
        correlation_equation=correlation,
        is_within_correlation_range=is_within_range,
        applicable_range=applicable_range,
        geometry_type="flat_plate",
    )


def _calculate_pipe_flow(input_data: PipeFlowConvection) -> ConvectionResult:
    """Calculate convection coefficient for internal pipe flow.

    Uses standard correlations:
    - Laminar (Re < 2300): Nu = 3.66 (fully developed)
    - Turbulent (Re >= 10000): Dittus-Boelter or Gnielinski
    - Transitional (2300 <= Re < 10000): Linear interpolation

    Parameters
    ----------
    input_data : PipeFlowConvection
        Pipe geometry and flow conditions.

    Returns
    -------
    ConvectionResult
        Results with h, Re, Pr, Nu, and flow regime.
    """
    props = input_data.fluid_properties
    D = input_data.diameter
    L = input_data.length
    U = input_data.flow_velocity
    k = props.thermal_conductivity
    mu = props.dynamic_viscosity
    rho = props.density
    cp = props.specific_heat

    # Calculate dimensionless numbers
    Re = rho * U * D / mu
    Pr = cp * mu / k

    # Determine flow regime and calculate Nusselt number
    if Re < 2300:
        # Laminar flow (fully developed, constant wall temperature)
        Nu = 3.66
        flow_regime = "laminar"
        correlation = "Fully developed laminar pipe flow"
        applicable_range = {
            "Re": (0, 2300),
            "Pr": (0.1, 1000),
        }
    elif Re >= 10000:
        # Turbulent flow - use Gnielinski correlation
        # Valid for 0.5 < Pr < 2000 and 3000 < Re < 5e6
        if 3000 <= Re <= 5e6 and 0.5 <= Pr <= 2000:
            f = (0.790 * math.log(Re) - 1.64) ** (-2)  # Petukhov friction factor
            Nu = (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * (f / 8) ** 0.5 * (Pr ** (2 / 3) - 1))
            correlation = "Gnielinski"
        else:
            # Fallback to Dittus-Boelter
            Nu = 0.023 * Re**0.8 * Pr**0.4
            correlation = "Dittus-Boelter"

        flow_regime = "turbulent"
        applicable_range = {
            "Re": (10000, 5e6),
            "Pr": (0.5, 2000),
        }
    else:
        # Transitional regime (2300 <= Re < 10000)
        # Linear interpolation between laminar and turbulent
        Nu_lam = 3.66
        Nu_turb = 0.023 * 10000**0.8 * Pr**0.4
        Nu = Nu_lam + (Nu_turb - Nu_lam) * (Re - 2300) / (10000 - 2300)
        flow_regime = "transitional"
        correlation = "Transitional (interpolated)"
        applicable_range = {
            "Re": (2300, 10000),
            "Pr": (0.5, 100),
        }

    # Calculate heat transfer coefficient
    h = Nu * k / D

    # Check if within correlation range
    is_within_range = _check_correlation_range({"Re": Re, "Pr": Pr}, applicable_range)

    return ConvectionResult(
        primary_value=h,
        calculation_method=f"Pipe flow {flow_regime} convection",
        success=True,
        error_message="",
        intermediate_values={
            "pipe_diameter_m": D,
            "pipe_length_m": L,
            "flow_velocity_m_s": U,
            "fluid_density_kg_m3": rho,
            "dynamic_viscosity_Pa_s": mu,
            "thermal_conductivity_W_mK": k,
            "specific_heat_J_kgK": cp,
        },
        version="1.0.0",
        h=h,
        Reynolds=Re,
        Prandtl=Pr,
        Nusselt=Nu,
        Grashof=None,
        Rayleigh=None,
        flow_regime=flow_regime,
        correlation_equation=correlation,
        is_within_correlation_range=is_within_range,
        applicable_range=applicable_range,
        geometry_type="pipe_flow",
    )


def _calculate_cylinder_crossflow(input_data: CylinderCrossflowConvection) -> ConvectionResult:
    """Calculate convection coefficient for flow over a cylinder.

    Uses Churchill-Bernstein correlation:
    Nu = 0.3 + [0.62 Re^0.5 Pr^(1/3)] / [1 + (0.4/Pr)^(2/3)]^0.25
         × [1 + (Re/282000)^(5/8)]^(4/5)

    Valid for Re×Pr > 0.2

    Parameters
    ----------
    input_data : CylinderCrossflowConvection
        Cylinder geometry and flow conditions.

    Returns
    -------
    ConvectionResult
        Results with h, Re, Pr, Nu, and flow regime.
    """
    props = input_data.fluid_properties
    D = input_data.diameter
    U = input_data.flow_velocity
    k = props.thermal_conductivity
    mu = props.dynamic_viscosity
    rho = props.density
    cp = props.specific_heat

    # Calculate dimensionless numbers
    Re = rho * U * D / mu
    Pr = cp * mu / k

    # Churchill-Bernstein correlation
    if Re * Pr > 0.2:
        Nu = 0.3 + (0.62 * Re**0.5 * Pr ** (1 / 3)) / (1 + (0.4 / Pr) ** (2 / 3)) ** 0.25 * (
            1 + (Re / 282000) ** (5 / 8)
        ) ** (4 / 5)
        correlation = "Churchill-Bernstein"
    else:
        # Fallback for very low Re×Pr
        Nu = 0.3 + 0.62 * Re**0.5 * Pr ** (1 / 3)
        correlation = "Churchill-Bernstein (simplified)"

    # Determine flow regime based on Reynolds number
    if Re < 1:
        flow_regime = "creeping"
    elif Re < 2000:
        flow_regime = "laminar"
    else:
        flow_regime = "turbulent"

    # Calculate heat transfer coefficient
    h = Nu * k / D

    applicable_range = {
        "Re": (0.1, 1e7),
        "Pr": (0.2, 1000),
        "Re×Pr": (0.2, 1e8),
    }

    # Check if within correlation range
    is_within_range = _check_correlation_range(
        {"Re": Re, "Pr": Pr, "Re×Pr": Re * Pr}, applicable_range
    )

    return ConvectionResult(
        primary_value=h,
        calculation_method=f"Cylinder crossflow {flow_regime} convection",
        success=True,
        error_message="",
        intermediate_values={
            "cylinder_diameter_m": D,
            "flow_velocity_m_s": U,
            "fluid_density_kg_m3": rho,
            "dynamic_viscosity_Pa_s": mu,
            "thermal_conductivity_W_mK": k,
            "specific_heat_J_kgK": cp,
        },
        version="1.0.0",
        h=h,
        Reynolds=Re,
        Prandtl=Pr,
        Nusselt=Nu,
        Grashof=None,
        Rayleigh=None,
        flow_regime=flow_regime,
        correlation_equation=correlation,
        is_within_correlation_range=is_within_range,
        applicable_range=applicable_range,
        geometry_type="cylinder_crossflow",
    )


def _calculate_natural_convection(input_data: VerticalPlateNaturalConvection) -> ConvectionResult:
    """Calculate natural convection coefficient for a vertical plate.

    Uses Rayleigh number-based correlations:
    - Laminar (Ra < 1e9): Nu = 0.68 + 0.670 Ra^0.25 / [1 + (0.492/Pr)^(9/16)]^(4/9)
    - Turbulent (Ra >= 1e9): Nu = 0.15 Ra^(1/3)

    Parameters
    ----------
    input_data : VerticalPlateNaturalConvection
        Vertical plate geometry and temperature conditions.

    Returns
    -------
    ConvectionResult
        Results with h, Gr, Ra, Pr, Nu, and flow regime.
    """
    props = input_data.fluid_properties
    H = input_data.height
    T_s = input_data.surface_temperature
    T_inf = input_data.bulk_fluid_temperature
    k = props.thermal_conductivity
    mu = props.dynamic_viscosity
    rho = props.density
    cp = props.specific_heat

    # Thermal expansion coefficient
    if props.thermal_expansion_coefficient is not None:
        beta = props.thermal_expansion_coefficient
    else:
        # For ideal gas: beta ≈ 1/T_film
        T_film = (T_s + T_inf) / 2
        beta = 1.0 / T_film

    # Kinematic viscosity
    nu = mu / rho

    # Thermal diffusivity
    alpha = k / (rho * cp)

    # Calculate dimensionless numbers
    Pr = nu / alpha
    Gr = 9.81 * beta * abs(T_s - T_inf) * H**3 / nu**2
    Ra = Gr * Pr

    # Determine flow regime and calculate Nusselt number
    if Ra < 1e9:
        # Laminar natural convection
        Nu = 0.68 + (0.670 * Ra**0.25) / (1 + (0.492 / Pr) ** (9 / 16)) ** (4 / 9)
        flow_regime = "natural_laminar"
        correlation = "Churchill-Chu (laminar)"
        applicable_range = {
            "Ra": (1e4, 1e9),
            "Pr": (0.1, 1000),
        }
    else:
        # Turbulent natural convection
        Nu = 0.15 * Ra ** (1 / 3)
        flow_regime = "natural_turbulent"
        correlation = "Churchill-Chu (turbulent)"
        applicable_range = {
            "Ra": (1e9, 1e13),
            "Pr": (0.1, 1000),
        }

    # Calculate heat transfer coefficient
    h = Nu * k / H

    # Check if within correlation range
    is_within_range = _check_correlation_range({"Ra": Ra, "Pr": Pr}, applicable_range)

    return ConvectionResult(
        primary_value=h,
        calculation_method=f"Vertical plate {flow_regime} convection",
        success=True,
        error_message="",
        intermediate_values={
            "plate_height_m": H,
            "surface_temperature_K": T_s,
            "ambient_temperature_K": T_inf,
            "temperature_difference_K": abs(T_s - T_inf),
            "thermal_expansion_coeff_1_K": beta,
            "kinematic_viscosity_m2_s": nu,
            "thermal_diffusivity_m2_s": alpha,
        },
        version="1.0.0",
        h=h,
        Reynolds=0.0,  # Not applicable for natural convection
        Prandtl=Pr,
        Nusselt=Nu,
        Grashof=Gr,
        Rayleigh=Ra,
        flow_regime=flow_regime,
        correlation_equation=correlation,
        is_within_correlation_range=is_within_range,
        applicable_range=applicable_range,
        geometry_type="vertical_plate_natural",
    )


def _check_correlation_range(
    values: dict[str, float], ranges: dict[str, tuple[float, float]]
) -> bool:
    """Check if parameter values are within correlation validity ranges.

    Parameters
    ----------
    values : Dict[str, float]
        Dictionary of parameter values to check.
    ranges : Dict[str, Tuple[float, float]]
        Dictionary of validity ranges {parameter: (min, max)}.

    Returns
    -------
    bool
        True if all parameters are within their respective ranges.
    """
    for param, value in values.items():
        if param in ranges:
            min_val, max_val = ranges[param]
            if value < min_val or value > max_val:
                return False
    return True
