# Python Library API Contract

**Feature**: 002-heat-exchanger-calc
**Date**: 2025-12-30
**Type**: Function-based API (four calculation modules)

This document specifies the public Python API for the heat exchanger calculations library.

---

## Module: heat_calc.lmtd

### Function: calculate_lmtd

```python
def calculate_lmtd(input_data: LMTDInput) -> LMTDResult:
    """
    Calculate heat transfer rate and LMTD for heat exchangers.

    Supports counterflow, parallel flow, and crossflow configurations.
    Applies correction factors (F) for non-ideal geometries.

    Parameters
    ----------
    input_data : LMTDInput
        Input specification including:
        - hot_fluid: FluidState (T_inlet, T_outlet, mdot)
        - cold_fluid: FluidState (T_inlet, T_outlet, mdot)
        - exchanger: HeatExchangerConfiguration (type, area, F_correction)

    Returns
    -------
    LMTDResult
        Results including:
        - heat_transfer_rate: Quantity [W or kW]
        - LMTD_arithmetic: Quantity [K]
        - LMTD_effective: Quantity [K] (after correction)
        - configuration_used: str
        - energy_balance_error_percent: float
        - intermediate_values: dict (all intermediate calculations)
        - calculation_method: str (reference)
        - source_reference: str (literature source)

    Raises
    ------
    ValidationError
        If input violates constraints (e.g., T_inlet = T_outlet for either fluid).
    ValueError
        If numerical computation fails (e.g., negative LMTD).

    Examples
    --------
    >>> from heat_calc.models import LMTDInput, FluidState, HeatExchangerConfiguration
    >>> from heat_calc.lmtd import calculate_lmtd
    >>> from pint import Quantity
    >>>
    >>> hot = FluidState(
    ...     T_inlet=Quantity(100, "degC"),
    ...     T_outlet=Quantity(60, "degC"),
    ...     mdot=Quantity(10, "kg/s")
    ... )
    >>> cold = FluidState(
    ...     T_inlet=Quantity(20, "degC"),
    ...     T_outlet=Quantity(40, "degC"),
    ...     mdot=Quantity(12, "kg/s")
    ... )
    >>> exchanger = HeatExchangerConfiguration(
    ...     configuration="counterflow",
    ...     area=Quantity(50, "m**2")
    ... )
    >>> result = calculate_lmtd(LMTDInput(hot, cold, exchanger))
    >>> print(result.heat_transfer_rate)  # doctest: +SKIP
    400.0 kilowatt

    Notes
    -----
    - Requires inlet and outlet temperatures for BOTH fluids
    - Uses energy balance to validate results (< 1% error required)
    - LMTD calculation accounts for counterflow advantage vs parallel flow
    - Correction factor F must be in [0, 1]; typically from manufacturer charts
    """
```

---

## Module: heat_calc.ntu

### Function: calculate_ntu

```python
def calculate_ntu(input_data: NTUInput) -> NTUResult:
    """
    Calculate NTU (Number of Transfer Units) and heat exchanger effectiveness.

    Determines outlet temperatures given inlet conditions and UA product.
    Supports multiple heat exchanger configurations.

    Parameters
    ----------
    input_data : NTUInput
        Input specification including:
        - T_hot_inlet, T_cold_inlet: Quantity (inlet temperatures)
        - mdot_hot, mdot_cold: Quantity (mass flow rates)
        - cp_hot, cp_cold: Quantity (specific heat capacities)
        - UA: Quantity (overall heat transfer coefficient × area)
        - configuration: str (counterflow, parallel_flow, shell_and_tube_1_2, etc.)
        - T_hot_outlet or T_cold_outlet: Optional (if provided, calculate the other)

    Returns
    -------
    NTUResult
        Results including:
        - NTU: float (dimensionless)
        - effectiveness: float (0 ≤ ε ≤ 1)
        - heat_transfer_rate: Quantity [W or kW]
        - T_hot_outlet, T_cold_outlet: Quantity (calculated outlet temperatures)
        - C_hot, C_cold, C_min, C_max: Quantity (heat capacity rates)
        - C_ratio: float (C_min / C_max)
        - Q_max: Quantity (maximum possible heat transfer)
        - effectiveness_theoretical_max: float (limit as NTU → ∞)
        - energy_balance_error_percent: float

    Raises
    ------
    ValidationError
        If input violates constraints (e.g., both outlet temperatures provided).
    ValueError
        If NTU calculation fails.

    Examples
    --------
    >>> from heat_calc.models import NTUInput
    >>> from heat_calc.ntu import calculate_ntu
    >>> from pint import Quantity
    >>>
    >>> ntu_input = NTUInput(
    ...     T_hot_inlet=Quantity(100, "degC"),
    ...     T_cold_inlet=Quantity(20, "degC"),
    ...     mdot_hot=Quantity(10, "kg/s"),
    ...     mdot_cold=Quantity(12, "kg/s"),
    ...     cp_hot=Quantity(4000, "J/(kg*K)"),
    ...     cp_cold=Quantity(4000, "J/(kg*K)"),
    ...     UA=Quantity(20, "kW/K"),
    ...     configuration="counterflow"
    ... )
    >>> result = calculate_ntu(ntu_input)
    >>> print(f"Effectiveness: {result.effectiveness:.3f}")  # doctest: +SKIP
    Effectiveness: 0.745

    Notes
    -----
    - NTU and effectiveness are related by configuration-specific equations
    - Counterflow is most efficient (highest effectiveness for given NTU)
    - Effectiveness approaches 1.0 as NTU increases (diminishing returns)
    - Accepts one inlet and one outlet (calculates the missing outlet)
    """
```

---

## Module: heat_calc.convection

### Function: calculate_convection

```python
def calculate_convection(input_data: ConvectionGeometry) -> ConvectionResult:
    """
    Calculate convection heat transfer coefficient using published correlations.

    Supports multiple geometries: flat plates, pipes, cylinders, natural convection.
    Automatically selects appropriate correlation based on geometry type and flow regime.

    Parameters
    ----------
    input_data : ConvectionGeometry
        Polymorphic input (one of):
        - FlatPlateConvection: Laminar or turbulent over flat surface
        - CylinderCrossflowConvection: Cylinder in cross-flow (perpendicular approach)
        - PipeFlowConvection: Internal pipe flow (laminar, turbulent)
        - VerticalPlateNaturalConvection: Free convection from vertical surface

        Each includes:
        - geometry_type: Literal (discriminator)
        - fluid_properties: FluidProperties (ρ, μ, cp, k)
        - characteristic dimensions (length, diameter, etc.)
        - temperature conditions (surface, bulk, ambient)

    Returns
    -------
    ConvectionResult
        Results including:
        - h: Quantity [W/(m**2*K)] (convection coefficient)
        - Reynolds: float (Re = ρVL/μ for forced convection)
        - Prandtl: float (Pr = cp*μ/k)
        - Nusselt: float (Nu = h*L/k)
        - Grashof, Rayleigh: float or None (for natural convection)
        - flow_regime: str (laminar, turbulent, transitional)
        - correlation_equation: str (e.g., "Dittus-Boelert")
        - correlation_coefficients: dict (correlation parameters)
        - is_within_correlation_range: bool (parameter validity check)
        - applicable_range: dict (validity bounds for each parameter)

    Raises
    ------
    ValidationError
        If input violates constraints (e.g., negative velocity).
    ValueError
        If correlation calculation fails or parameters out of range (warns but continues).

    Examples
    --------
    >>> from heat_calc.models import PipeFlowConvection, FluidProperties
    >>> from heat_calc.convection import calculate_convection
    >>> from pint import Quantity
    >>>
    >>> fluid = FluidProperties(
    ...     density=Quantity(983, "kg/m**3"),
    ...     dynamic_viscosity=Quantity(0.000467, "Pa*s"),
    ...     specific_heat=Quantity(4190, "J/(kg*K)"),
    ...     thermal_conductivity=Quantity(0.65, "W/(m*K)")
    ... )
    >>> pipe_input = PipeFlowConvection(
    ...     diameter=Quantity(0.05, "m"),
    ...     length=Quantity(10, "m"),
    ...     flow_velocity=Quantity(2.0, "m/s"),
    ...     fluid_properties=fluid,
    ...     surface_temperature=Quantity(80, "degC"),
    ...     bulk_fluid_temperature=Quantity(60, "degC")
    ... )
    >>> result = calculate_convection(pipe_input)
    >>> print(f"h = {result.h}")  # doctest: +SKIP
    h = 11230.0 W/(m**2*K)

    Notes
    -----
    - Correlations are standardized from Incropera or Perry's Chemical Engineer's Handbook
    - Reynolds/Prandtl/Nusselt numbers are dimensionless (pure numbers)
    - Grashof number only applies to natural convection
    - Warnings issued if parameters outside correlation's published validity range
    - Laminar-turbulent transition occurs at Re ≈ 5×10^5 for flat plate
    """
```

---

## Module: heat_calc.insulation

### Function: calculate_insulation

```python
def calculate_insulation(input_data: InsulationInput) -> InsulationResult:
    """
    Calculate optimal insulation thickness for cylindrical pipes.

    Performs economic optimization (payback analysis) or satisfies temperature constraint.
    Returns optimal thickness, annual savings, and payback period.

    Parameters
    ----------
    input_data : InsulationInput
        Input specification including:
        - pipe_diameter, pipe_length: Quantity (uninsulated pipe dimensions)
        - T_surface_uninsulated: Quantity (surface temp without insulation)
        - T_ambient: Quantity (ambient/surrounding temperature)
        - h_ambient: Quantity (natural/forced convection to ambient)
        - insulation_material: str (name, e.g., 'fiberglass', 'mineral_wool')
        - thermal_conductivity_insulation: Quantity (k_ins)
        - energy_cost: Quantity [$/MWh or $/GJ] (energy price)
        - energy_annual_operating_hours: int (hours/year pipe is hot)
        - insulation_cost_per_thickness: Quantity [$/m²/m] (installed cost/thickness)
        - analysis_period_years: int (amortization period)
        - Optional constraints:
          - surface_temp_limit: Quantity (max surface temp for safety)
          - insulation_thickness_min, _max: Quantity (bounds on solution)

    Returns
    -------
    InsulationResult
        Results including:
        - optimal_insulation_thickness: Quantity [m]
        - optimization_mode: Literal["economic_payback", "temperature_constraint"]
        - Q_uninsulated, Q_insulated: Quantity [W] (heat loss comparison)
        - heat_loss_reduction_percent: float (%)

        If optimization_mode == "economic_payback":
        - annual_energy_savings: Quantity [MWh or GJ]
        - annual_cost_savings: float [$]
        - annual_insulation_cost: float [$]  (amortized)
        - net_annual_savings: float [$]
        - payback_period_years: float

        If optimization_mode == "temperature_constraint":
        - T_surface_insulated: Quantity (resulting surface temp)
        - T_surface_required: Quantity (constraint applied)

        Optional sensitivity analysis (if requested):
        - sensitivity: dict (results under +/- 20% variations in energy cost)

    Raises
    ------
    ValidationError
        If input violates constraints.
    ValueError
        If optimization fails (e.g., no feasible solution within thickness bounds).

    Examples
    --------
    >>> from heat_calc.models import InsulationInput
    >>> from heat_calc.insulation import calculate_insulation
    >>> from pint import Quantity
    >>>
    >>> insulation_input = InsulationInput(
    ...     pipe_diameter=Quantity(0.1, "m"),
    ...     pipe_length=Quantity(100, "m"),
    ...     T_surface_uninsulated=Quantity(150, "degC"),
    ...     T_ambient=Quantity(25, "degC"),
    ...     h_ambient=Quantity(25, "W/(m**2*K)"),
    ...     insulation_material="mineral_wool",
    ...     thermal_conductivity_insulation=Quantity(0.04, "W/(m*K)"),
    ...     energy_cost=Quantity(12, "USD/GJ"),
    ...     analysis_period_years=10
    ... )
    >>> result = calculate_insulation(insulation_input)
    >>> print(f"Payback: {result.payback_period_years:.1f} years")  # doctest: +SKIP
    Payback: 2.9 years

    Notes
    -----
    - Economic optimization minimizes (insulation_cost + energy_loss_cost)
    - Payback period is when cumulative savings = insulation investment
    - Temperature constraint mode sets thickness to achieve surface_temp_limit
    - Heat loss follows cylindrical shell conduction (radial): Q = 2πkL(T_in - T_out) / ln(r_o/r_i)
    - Annual savings = Energy_saved [MWh/yr] × Energy_Cost [$/MWh]
    - Assumes constant energy price over analysis period (conservative)
    """
```

---

## Common Input/Output Models

### Input Model: FluidState (Shared across LMTD, NTU)

```python
class FluidState(BaseModel):
    """Single fluid stream properties."""

    T_inlet: Quantity
        Inlet temperature (must be in temperature units: K, °C, °F, etc.)

    T_outlet: Quantity
        Outlet temperature

    mdot: Quantity
        Mass flow rate (must be in mass/time units: kg/s, lb/s, etc.)

    Constraints:
    - T_inlet ≠ T_outlet (no zero temperature difference)
    - mdot > 0 (flow must be positive)
    - All temperatures >= 0 K (no unphysical values)
```

### Output Model: BaseCalculationResult (Shared across all modules)

```python
class BaseCalculationResult(BaseModel):
    """Base for all results; inherited by specific calculation results."""

    calculation_method: str
        Method/version used (e.g., "LMTD_Counterflow_v1", "Dittus-Boelert_v1")

    source_reference: str
        Literature source (e.g., "Incropera_9e_p452", "NIST_WebBook")

    confidence_tolerance: float
        Expected accuracy as percentage (e.g., 1.0 means ±1%)

    intermediate_values: dict[str, float]
        All intermediate calculations (enabled for inspection, debugging, validation)

    Constraints:
    - confidence_tolerance in [0.1, 10.0] (realistic bounds)
    - intermediate_values includes at least primary calculation steps
```

---

## Error Handling Contract

### ValidationError (Pydantic)

Raised when input violates model constraints:

```python
try:
    bad_input = LMTDInput(...)
except ValidationError as e:
    for error in e.errors():
        print(f"Field: {error['loc']}, Message: {error['msg']}")
        # Output: Field: ('hot_fluid', 'T_inlet'), Message: 'ensure this value is greater than 0'
```

### ValueError

Raised when calculation fails (e.g., non-convergence in NTU solving):

```python
try:
    result = calculate_ntu(input_data)
except ValueError as e:
    print(f"Calculation failed: {e}")
    # Output: Calculation failed: NTU iteration did not converge after 100 iterations
```

---

## Module Exports

Each module exports functions and types:

```python
# src/heat_calc/__init__.py
from heat_calc.lmtd import calculate_lmtd
from heat_calc.ntu import calculate_ntu
from heat_calc.convection import calculate_convection
from heat_calc.insulation import calculate_insulation
from heat_calc.models import (
    LMTDInput, LMTDResult,
    NTUInput, NTUResult,
    ConvectionGeometry, ConvectionResult,
    InsulationInput, InsulationResult,
    # ... other supporting types
)

__all__ = [
    "calculate_lmtd",
    "calculate_ntu",
    "calculate_convection",
    "calculate_insulation",
    "LMTDInput", "LMTDResult",
    "NTUInput", "NTUResult",
    "ConvectionGeometry", "ConvectionResult",
    "InsulationInput", "InsulationResult",
]
```

---

## Type Hints & IDE Support

All functions include full type annotations (mypy --strict compliant):

```python
from typing import Union, Literal
from pint import Quantity
from heat_calc.models import LMTDInput, LMTDResult

def calculate_lmtd(input_data: LMTDInput) -> LMTDResult:
    ...
```

IDEs (VS Code, PyCharm, etc.) provide:
- Autocomplete for function names and parameters
- Parameter type hints during development
- Return type information
- Jump-to-definition for model classes

---

## Performance Contract

All calculations execute within performance bounds:

| Function | Typical Runtime | Worst Case | Constraint |
|----------|-----------------|------------|-----------|
| calculate_lmtd | 1-2 ms | 5 ms | < 10 ms |
| calculate_ntu | 5-10 ms | 20 ms | < 50 ms |
| calculate_convection | 1-3 ms | 10 ms | < 20 ms |
| calculate_insulation | 10-20 ms | 100 ms | < 100 ms |
| **Total** | **~20-35 ms** | **~135 ms** | **< 100 ms (SC-007)** |

---

## Compatibility

- **Python Version**: 3.11+ (f-strings, type hints, match statements)
- **Dependency Versions**: Pinned in `pyproject.toml`; minimum versions specified in docstrings
- **Backwards Compatibility**: Version 1.0.0; breaking changes trigger major version bump

