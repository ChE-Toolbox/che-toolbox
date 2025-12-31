"""Insulation Sizing and Economic Optimization Calculations.

Implements economic insulation thickness optimization for cylindrical pipes,
balancing capital cost (insulation material + installation) against energy
savings from reduced heat loss. Supports both economic payback optimization
and temperature-constrained design.

References:
    - Perry's Chemical Engineers' Handbook (9th ed.), Section 11: Heat Transfer Equipment
    - ASHRAE Fundamentals Handbook, Chapter 23: Insulation for Mechanical Systems
    - Economic Thickness for Industrial Insulation (NAIMA 3E Plus methodology)
"""

import math
from typing import cast

from scipy.optimize import minimize_scalar

from heat_calc.models.insulation_input import InsulationInput
from heat_calc.models.insulation_results import InsulationResult
from heat_calc.utils.validation import validate_positive_float


def calculate_insulation(input_data: InsulationInput) -> InsulationResult:
    """Calculate optimal insulation thickness for cylindrical pipes.

    Determines optimal insulation thickness by either:
    1. Economic optimization: Minimize total cost (capital + energy)
    2. Temperature constraint: Meet surface temperature requirement

    Parameters
    ----------
    input_data : InsulationInput
        Complete input specification with pipe geometry, thermal conditions,
        material properties, and economic parameters.

    Returns
    -------
    InsulationResult
        Results including optimal thickness, heat loss comparison, economic
        analysis (payback, savings), and temperature profile.

    Raises
    ------
    ValueError
        If inputs are invalid (e.g., T_surface < T_ambient, negative dimensions).

    Examples
    --------
    >>> from heat_calc.models import InsulationInput
    >>> from heat_calc.insulation import calculate_insulation
    >>>
    >>> # Economic optimization
    >>> input_data = InsulationInput(
    ...     pipe_diameter=0.1,  # 100 mm OD
    ...     pipe_length=100.0,
    ...     T_surface_uninsulated=423.15,  # 150°C
    ...     T_ambient=298.15,  # 25°C
    ...     h_ambient=15.0,
    ...     insulation_material="mineral_wool",
    ...     thermal_conductivity_insulation=0.04,
    ...     density_insulation=100.0,
    ...     energy_cost=12.0,
    ...     insulation_cost_per_thickness=50.0
    ... )
    >>> result = calculate_insulation(input_data)
    >>> print(f"Optimal thickness: {result.optimal_insulation_thickness:.3f} m")
    >>> print(f"Payback period: {result.payback_period_years:.1f} years")
    """
    try:
        # Validate inputs
        _validate_insulation_input(input_data)

        # Determine optimization mode
        if input_data.optimization_mode:
            opt_mode = input_data.optimization_mode
        elif input_data.surface_temp_limit is not None:
            opt_mode = "temperature_constraint"
        else:
            opt_mode = "economic_payback"

        # Calculate uninsulated heat loss (baseline)
        q_uninsulated = _calculate_heat_loss_uninsulated(
            input_data.pipe_diameter,
            input_data.pipe_length,
            input_data.T_surface_uninsulated,
            input_data.T_ambient,
            input_data.h_ambient,
        )

        # Find optimal insulation thickness
        if opt_mode == "economic_payback":
            optimal_thickness = _optimize_economic_thickness(input_data, q_uninsulated)
        else:  # temperature_constraint
            optimal_thickness = _optimize_temperature_constrained(input_data)

        # Calculate insulated heat loss at optimal thickness
        q_insulated = _calculate_heat_loss_insulated(
            input_data.pipe_diameter,
            input_data.pipe_length,
            input_data.T_surface_uninsulated,
            input_data.T_ambient,
            input_data.h_ambient,
            optimal_thickness,
            input_data.thermal_conductivity_insulation,
        )

        # Calculate surface temperature with insulation
        t_surface_insulated = _calculate_surface_temperature(
            input_data.pipe_diameter,
            input_data.T_surface_uninsulated,
            input_data.T_ambient,
            input_data.h_ambient,
            optimal_thickness,
            input_data.thermal_conductivity_insulation,
        )

        # Calculate material quantities
        insulation_volume, insulation_mass = _calculate_material_quantities(
            input_data.pipe_diameter,
            input_data.pipe_length,
            optimal_thickness,
            input_data.density_insulation,
        )

        # Calculate economic metrics
        economic_metrics = _calculate_economic_metrics(
            q_uninsulated,
            q_insulated,
            insulation_volume,
            input_data.pipe_length,
            optimal_thickness,
            input_data.energy_cost,
            input_data.energy_annual_operating_hours,
            input_data.insulation_cost_per_thickness,
            input_data.analysis_period_years,
        )

        # Build result object
        result = InsulationResult(
            primary_value=optimal_thickness,
            calculation_method="InsulationSizing_EconomicOptimization_v1",
            success=True,
            optimal_insulation_thickness=optimal_thickness,
            optimization_mode=opt_mode,
            Q_uninsulated=q_uninsulated,
            Q_insulated=q_insulated,
            heat_loss_reduction_percent=economic_metrics["heat_loss_reduction_percent"],
            annual_energy_savings=economic_metrics["annual_energy_savings"],
            annual_cost_savings=economic_metrics["annual_cost_savings"],
            annual_insulation_cost=economic_metrics["annual_insulation_cost"],
            net_annual_savings=economic_metrics["net_annual_savings"],
            payback_period_years=economic_metrics["payback_period_years"],
            T_surface_insulated=t_surface_insulated,
            T_surface_required=input_data.surface_temp_limit,
            insulation_volume=insulation_volume,
            insulation_mass=insulation_mass,
            total_insulation_cost=economic_metrics["total_insulation_cost"],
            intermediate_values={
                "optimization_mode": opt_mode,
                "pipe_diameter": input_data.pipe_diameter,
                "pipe_length": input_data.pipe_length,
                "k_insulation": input_data.thermal_conductivity_insulation,
            },
        )

        return result

    except Exception as e:
        # Return error result
        return InsulationResult(
            primary_value=0.0,
            calculation_method="InsulationSizing_EconomicOptimization_v1",
            success=False,
            error_message=str(e),
            optimal_insulation_thickness=0.0,
            optimization_mode="economic_payback",
            Q_uninsulated=0.0,
            Q_insulated=0.0,
            heat_loss_reduction_percent=0.0,
            annual_energy_savings=0.0,
            annual_cost_savings=0.0,
            annual_insulation_cost=0.0,
            net_annual_savings=0.0,
            payback_period_years=0.0,
            T_surface_insulated=0.0,
            insulation_volume=0.0,
            insulation_mass=0.0,
            total_insulation_cost=0.0,
        )


def _validate_insulation_input(input_data: InsulationInput) -> None:
    """Validate insulation input data for physical consistency.

    Parameters
    ----------
    input_data : InsulationInput
        Input data to validate.

    Raises
    ------
    ValueError
        If any validation check fails.
    """
    # Temperature validation
    if input_data.T_surface_uninsulated <= input_data.T_ambient:
        raise ValueError(
            f"T_surface_uninsulated ({input_data.T_surface_uninsulated:.1f} K) must be greater than "
            f"T_ambient ({input_data.T_ambient:.1f} K)"
        )

    # Geometry validation
    validate_positive_float(input_data.pipe_diameter, "pipe_diameter")
    validate_positive_float(input_data.pipe_length, "pipe_length")
    validate_positive_float(input_data.insulation_thickness_min, "insulation_thickness_min")
    validate_positive_float(input_data.insulation_thickness_max, "insulation_thickness_max")

    if input_data.insulation_thickness_max <= input_data.insulation_thickness_min:
        raise ValueError(
            f"insulation_thickness_max ({input_data.insulation_thickness_max}) must be greater than "
            f"insulation_thickness_min ({input_data.insulation_thickness_min})"
        )

    # Material properties validation
    validate_positive_float(
        input_data.thermal_conductivity_insulation, "thermal_conductivity_insulation"
    )
    validate_positive_float(input_data.density_insulation, "density_insulation")
    validate_positive_float(input_data.h_ambient, "h_ambient")

    # Economic parameters validation
    validate_positive_float(input_data.energy_cost, "energy_cost")
    validate_positive_float(
        input_data.insulation_cost_per_thickness, "insulation_cost_per_thickness"
    )

    if input_data.analysis_period_years <= 0:
        raise ValueError(
            f"analysis_period_years must be positive, got {input_data.analysis_period_years}"
        )


def _calculate_heat_loss_uninsulated(
    pipe_diameter: float, pipe_length: float, t_surface: float, t_ambient: float, h_ambient: float
) -> float:
    """Calculate heat loss from uninsulated cylindrical pipe.

    Uses Newton's law of cooling: Q = h × A × ΔT

    Parameters
    ----------
    pipe_diameter : float
        Outside diameter of pipe (m).
    pipe_length : float
        Length of pipe (m).
    t_surface : float
        Surface temperature (K).
    t_ambient : float
        Ambient temperature (K).
    h_ambient : float
        Convection coefficient to ambient (W/(m²·K)).

    Returns
    -------
    float
        Heat loss in W.
    """
    area = math.pi * pipe_diameter * pipe_length
    delta_t = t_surface - t_ambient
    q = h_ambient * area * delta_t
    return q


def _calculate_heat_loss_insulated(
    pipe_diameter: float,
    pipe_length: float,
    t_pipe_surface: float,
    t_ambient: float,
    h_ambient: float,
    insulation_thickness: float,
    k_insulation: float,
) -> float:
    """Calculate heat loss from insulated cylindrical pipe.

    Uses thermal resistance network:
    Q = ΔT / R_total
    where R_total = R_conduction (cylinder) + R_convection (outer surface)

    Parameters
    ----------
    pipe_diameter : float
        Outside diameter of bare pipe (m).
    pipe_length : float
        Length of pipe (m).
    t_pipe_surface : float
        Temperature at pipe surface (K).
    t_ambient : float
        Ambient temperature (K).
    h_ambient : float
        Convection coefficient to ambient (W/(m²·K)).
    insulation_thickness : float
        Thickness of insulation layer (m).
    k_insulation : float
        Thermal conductivity of insulation (W/(m·K)).

    Returns
    -------
    float
        Heat loss in W.
    """
    r1 = pipe_diameter / 2.0  # Inner radius (bare pipe surface)
    r2 = r1 + insulation_thickness  # Outer radius (insulation surface)

    # Thermal resistance of insulation (cylindrical conduction)
    # R_cond = ln(r2/r1) / (2 * π * L * k)
    r_conduction = math.log(r2 / r1) / (2.0 * math.pi * pipe_length * k_insulation)

    # Thermal resistance of outer surface convection
    # R_conv = 1 / (h * A_outer)
    area_outer = 2.0 * math.pi * r2 * pipe_length
    r_convection = 1.0 / (h_ambient * area_outer)

    # Total resistance
    r_total = r_conduction + r_convection

    # Heat transfer rate
    delta_t = t_pipe_surface - t_ambient
    q = delta_t / r_total

    return q


def _calculate_surface_temperature(
    pipe_diameter: float,
    t_pipe_surface: float,
    t_ambient: float,
    h_ambient: float,
    insulation_thickness: float,
    k_insulation: float,
) -> float:
    """Calculate outer surface temperature of insulated pipe.

    Uses thermal resistance to find temperature at insulation outer surface.

    Parameters
    ----------
    pipe_diameter : float
        Outside diameter of bare pipe (m).
    t_pipe_surface : float
        Temperature at pipe surface (K).
    t_ambient : float
        Ambient temperature (K).
    h_ambient : float
        Convection coefficient to ambient (W/(m²·K)).
    insulation_thickness : float
        Thickness of insulation layer (m).
    k_insulation : float
        Thermal conductivity of insulation (W/(m·K)).

    Returns
    -------
    float
        Outer surface temperature in K.
    """
    r1 = pipe_diameter / 2.0
    r2 = r1 + insulation_thickness

    # For unit length (L = 1 m)
    r_conduction = math.log(r2 / r1) / (2.0 * math.pi * k_insulation)
    area_outer = 2.0 * math.pi * r2  # per unit length
    r_convection = 1.0 / (h_ambient * area_outer)

    r_total = r_conduction + r_convection

    # Heat flux per unit length
    delta_t = t_pipe_surface - t_ambient
    q_per_length = delta_t / r_total

    # Temperature drop across convection layer
    delta_t_conv = q_per_length * r_convection

    # Surface temperature
    t_surface = t_ambient + delta_t_conv

    return t_surface


def _calculate_material_quantities(
    pipe_diameter: float, pipe_length: float, insulation_thickness: float, density_insulation: float
) -> tuple[float, float]:
    """Calculate insulation material volume and mass.

    Parameters
    ----------
    pipe_diameter : float
        Outside diameter of bare pipe (m).
    pipe_length : float
        Length of pipe (m).
    insulation_thickness : float
        Thickness of insulation layer (m).
    density_insulation : float
        Density of insulation material (kg/m³).

    Returns
    -------
    Tuple[float, float]
        (volume in m³, mass in kg)
    """
    r1 = pipe_diameter / 2.0
    r2 = r1 + insulation_thickness

    # Volume of cylindrical shell: π × L × (r2² - r1²)
    volume = math.pi * pipe_length * (r2**2 - r1**2)
    mass = volume * density_insulation

    return volume, mass


def _calculate_economic_metrics(
    q_uninsulated: float,
    q_insulated: float,
    insulation_volume: float,
    pipe_length: float,
    insulation_thickness: float,
    energy_cost: float,
    operating_hours: int,
    insulation_cost_per_thickness: float,
    analysis_period_years: int,
) -> dict[str, float]:
    """Calculate economic metrics for insulation investment.

    Parameters
    ----------
    q_uninsulated : float
        Heat loss without insulation (W).
    q_insulated : float
        Heat loss with insulation (W).
    insulation_volume : float
        Volume of insulation material (m³).
    pipe_length : float
        Length of pipe (m).
    insulation_thickness : float
        Thickness of insulation (m).
    energy_cost : float
        Cost of energy ($/MWh).
    operating_hours : int
        Annual operating hours.
    insulation_cost_per_thickness : float
        Cost of insulation per area per thickness ($/(m²·m)).
    analysis_period_years : int
        Economic analysis period (years).

    Returns
    -------
    Dict[str, float]
        Dictionary with economic metrics.
    """
    # Heat loss reduction
    heat_loss_reduction = q_uninsulated - q_insulated
    heat_loss_reduction_percent = (
        (heat_loss_reduction / q_uninsulated) * 100 if q_uninsulated > 0 else 0.0
    )

    # Annual energy savings (MWh)
    annual_energy_savings = (heat_loss_reduction * operating_hours) / 1e6  # W × h → MWh

    # Annual cost savings ($)
    annual_cost_savings = annual_energy_savings * energy_cost

    # Total insulation cost (material + installation)
    # Cost per unit area per unit thickness × area × thickness
    pipe_diameter = (
        2.0 * (insulation_volume / (math.pi * pipe_length)) ** 0.5 - 2.0 * insulation_thickness
    )
    area = math.pi * (pipe_diameter + 2.0 * insulation_thickness) * pipe_length
    total_insulation_cost = insulation_cost_per_thickness * area * insulation_thickness

    # Annualized insulation cost
    annual_insulation_cost = total_insulation_cost / analysis_period_years

    # Net annual savings
    net_annual_savings = annual_cost_savings - annual_insulation_cost

    # Simple payback period (years)
    if annual_cost_savings > 0:
        payback_period_years = total_insulation_cost / annual_cost_savings
    else:
        payback_period_years = float("inf")

    return {
        "heat_loss_reduction_percent": heat_loss_reduction_percent,
        "annual_energy_savings": annual_energy_savings,
        "annual_cost_savings": annual_cost_savings,
        "total_insulation_cost": total_insulation_cost,
        "annual_insulation_cost": annual_insulation_cost,
        "net_annual_savings": net_annual_savings,
        "payback_period_years": payback_period_years,
    }


def _optimize_economic_thickness(input_data: InsulationInput, _q_uninsulated: float) -> float:
    """Find optimal insulation thickness by minimizing total cost.

    Total cost = Capital cost (amortized) + Energy cost
    Minimize: C_total(t) = C_insulation(t) + C_energy(t)

    Parameters
    ----------
    input_data : InsulationInput
        Input data with economic parameters.
    _q_uninsulated : float
        Baseline heat loss without insulation (W).

    Returns
    -------
    float
        Optimal insulation thickness (m).
    """

    def total_annual_cost(thickness: float) -> float:
        """Objective function: total annualized cost."""
        # Calculate insulated heat loss
        q_ins = _calculate_heat_loss_insulated(
            input_data.pipe_diameter,
            input_data.pipe_length,
            input_data.T_surface_uninsulated,
            input_data.T_ambient,
            input_data.h_ambient,
            thickness,
            input_data.thermal_conductivity_insulation,
        )

        # Annual energy cost
        annual_energy_kwh = (q_ins * input_data.energy_annual_operating_hours) / 1e6  # W × h → MWh
        annual_energy_cost = annual_energy_kwh * input_data.energy_cost

        # Annualized insulation cost
        volume, mass = _calculate_material_quantities(
            input_data.pipe_diameter,
            input_data.pipe_length,
            thickness,
            input_data.density_insulation,
        )
        r2 = input_data.pipe_diameter / 2.0 + thickness
        area_outer = 2.0 * math.pi * r2 * input_data.pipe_length
        insulation_capital_cost = input_data.insulation_cost_per_thickness * area_outer * thickness
        annual_insulation_cost = insulation_capital_cost / input_data.analysis_period_years

        # Total annualized cost
        total_cost = annual_energy_cost + annual_insulation_cost

        return total_cost

    # Optimize thickness within bounds
    result = minimize_scalar(
        total_annual_cost,
        bounds=(input_data.insulation_thickness_min, input_data.insulation_thickness_max),
        method="bounded",
    )

    return cast(float, result.x)


def _optimize_temperature_constrained(input_data: InsulationInput) -> float:
    """Find minimum insulation thickness to meet surface temperature constraint.

    Solves for thickness such that T_surface ≤ T_limit.

    Parameters
    ----------
    input_data : InsulationInput
        Input data with temperature constraint.

    Returns
    -------
    float
        Minimum insulation thickness to meet constraint (m).
    """
    t_limit = input_data.surface_temp_limit

    def temperature_error(thickness: float) -> float:
        """Objective: minimize (T_surface - T_limit)²."""
        t_surf = _calculate_surface_temperature(
            input_data.pipe_diameter,
            input_data.T_surface_uninsulated,
            input_data.T_ambient,
            input_data.h_ambient,
            thickness,
            input_data.thermal_conductivity_insulation,
        )
        return (t_surf - t_limit) ** 2

    # Optimize thickness to meet temperature constraint
    result = minimize_scalar(
        temperature_error,
        bounds=(input_data.insulation_thickness_min, input_data.insulation_thickness_max),
        method="bounded",
    )

    return cast(float, result.x)
