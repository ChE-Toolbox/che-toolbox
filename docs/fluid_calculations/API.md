# API Reference: Core Fluid Calculations

## Overview

The Core Fluid Calculations library provides engineering calculations for:
- **Pipe Flow Analysis**: Reynolds number, friction factor, pressure drop
- **Pump Sizing**: Head calculations, power requirements, NPSH analysis
- **Valve Sizing**: Cv calculations, flow rate prediction, valve selection

All calculations support SI and US customary units with automatic conversion.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from fluids.pipe import calculate_reynolds, calculate_friction_factor, calculate_pressure_drop
from fluids.pump import calculate_total_head, calculate_power_required, calculate_npsh_available
from fluids.valve import calculate_cv_required, calculate_flow_rate_through_valve

# Pipe flow calculations
reynolds_result = calculate_reynolds(
    density=1000.0,      # kg/m³
    velocity=2.0,        # m/s
    diameter=0.05,       # m
    viscosity=0.001,     # Pa·s
    unit_system="SI"
)
print(f"Reynolds number: {reynolds_result['value']:.0f} ({reynolds_result['regime']})")

# Pump sizing
head = calculate_total_head(
    static_head=10.0,    # m
    dynamic_head=0.5,    # m
    friction_losses=5.0  # m
)
print(f"Total head: {head['value']:.2f} {head['unit']}")

# Valve sizing
cv_result = calculate_cv_required(
    flow_rate=100.0,           # m³/h
    pressure_drop=2.0,         # bar
    fluid_gravity=1.0,         # dimensionless
    unit_system="SI"
)
print(f"Required Cv: {cv_result['value']:.2f} {cv_result['unit']}")
```

---

## Module: `fluids.pipe`

Pipe flow analysis calculations.

### `calculate_reynolds(density, velocity, diameter, viscosity, unit_system='SI')`

Calculate Reynolds number for pipe flow.

**Parameters:**
- `density` (float): Fluid density in kg/m³ (SI) or lb/ft³ (US)
- `velocity` (float): Flow velocity in m/s (SI) or ft/s (US)
- `diameter` (float): Pipe diameter in m (SI) or ft (US)
- `viscosity` (float): Dynamic viscosity in Pa·s (SI) or lb/(ft·s) (US)
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: Reynolds number (dimensionless)
- `'regime'`: Flow regime ('laminar', 'transitional', or 'turbulent')
- `'formula_used'`: Calculation formula
- `'warnings'`: List of warnings if any
- `'source'`: Reference information

**Raises:**
- `ValueError`: If any input is invalid (negative/zero values)

**Example:**
```python
result = calculate_reynolds(
    density=1000.0,
    velocity=2.0,
    diameter=0.05,
    viscosity=0.001
)
# Returns: {'value': 100000.0, 'regime': 'turbulent', ...}
```

---

### `calculate_friction_factor(reynolds, roughness, diameter, unit_system='SI')`

Calculate Darcy friction factor for pipe flow.

Uses:
- **Laminar** (Re < 2300): f = 64/Re
- **Transitional** (2300 ≤ Re ≤ 4000): Uses laminar formula + warning
- **Turbulent** (Re > 4000): Colebrook-White equation (implicit, solved iteratively)

**Parameters:**
- `reynolds` (float): Reynolds number (dimensionless)
- `roughness` (float): Absolute pipe roughness in m (SI) or ft (US)
- `diameter` (float): Pipe diameter in m (SI) or ft (US)
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: Friction factor (dimensionless)
- `'method'`: Calculation method used ('laminar_64/Re', 'colebrook', etc.)
- `'formula_used'`: Equation description
- `'warnings'`: List of warnings (e.g., transitional zone)
- `'intermediate_values'`: Dict of intermediate calculations
- `'source'`: Reference (Crane TP-410, Colebrook-White)

**Raises:**
- `ValueError`: If reynolds ≤ 0 or roughness/diameter negative

**Example:**
```python
result = calculate_friction_factor(
    reynolds=100000.0,
    roughness=0.000045,  # Steel pipe
    diameter=0.05
)
# Returns: {'value': 0.0185, 'method': 'colebrook', ...}
```

---

### `calculate_pressure_drop(friction_factor, length, diameter, velocity, density, unit_system='SI')`

Calculate pressure drop using Darcy-Weisbach equation.

Formula: ΔP = f × (L/D) × (ρV²/2)

**Parameters:**
- `friction_factor` (float): Darcy friction factor (dimensionless)
- `length` (float): Pipe length in m (SI) or ft (US)
- `diameter` (float): Pipe diameter in m (SI) or ft (US)
- `velocity` (float): Flow velocity in m/s (SI) or ft/s (US)
- `density` (float): Fluid density in kg/m³ (SI) or lb/ft³ (US)
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: Pressure drop in Pa (SI) or psi (US)
- `'unit'`: Pressure unit
- `'formula_used'`: Darcy-Weisbach formula
- `'intermediate_values'`: Components of calculation
- `'warnings'`: List of warnings if any
- `'source'`: Reference information

**Example:**
```python
result = calculate_pressure_drop(
    friction_factor=0.0185,
    length=100.0,
    diameter=0.05,
    velocity=2.0,
    density=1000.0
)
# Returns: {'value': 74000.0, 'unit': 'Pa', ...}
```

---

## Module: `fluids.pump`

Pump sizing and NPSH calculations.

### `calculate_static_head(elevation_in, elevation_out, unit_system='SI')`

Calculate static head (elevation difference).

**Parameters:**
- `elevation_in` (float): Inlet elevation in m (SI) or ft (US)
- `elevation_out` (float): Outlet elevation in m (SI) or ft (US)
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: Static head in m (SI) or ft (US)
- `'unit'`: Head unit
- `'elevation_change'`: Difference in elevation
- `'formula_used'`: Calculation description

**Example:**
```python
result = calculate_static_head(elevation_in=0.0, elevation_out=10.0)
# Returns: {'value': 10.0, 'unit': 'm', ...}
```

---

### `calculate_dynamic_head(velocity, gravity=9.81, unit_system='SI')`

Calculate dynamic head (velocity head).

Formula: h_dynamic = v²/(2g)

**Parameters:**
- `velocity` (float): Flow velocity in m/s (SI) or ft/s (US)
- `gravity` (float, optional): Gravitational acceleration, default 9.81 m/s² (SI) or 32.174 ft/s² (US)
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: Dynamic head in m (SI) or ft (US)
- `'unit'`: Head unit
- `'velocity'`: Input velocity
- `'formula_used'`: Formula description

---

### `calculate_total_head(static_head, dynamic_head, friction_losses, unit_system='SI')`

Calculate total pump head required.

Formula: H_total = H_static + H_dynamic + H_friction

**Parameters:**
- `static_head` (float): Static head in m (SI) or ft (US)
- `dynamic_head` (float): Dynamic head in m (SI) or ft (US)
- `friction_losses` (float): Friction losses in m (SI) or ft (US)
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: Total head in m (SI) or ft (US)
- `'unit'`: Head unit
- `'components'`: Dict of individual head components
- `'formula_used'`: Calculation formula

**Example:**
```python
result = calculate_total_head(
    static_head=10.0,
    dynamic_head=0.5,
    friction_losses=5.0
)
# Returns: {'value': 15.5, 'unit': 'm', ...}
```

---

### `calculate_power_required(flow_rate, density, gravity, total_head, efficiency, unit_system='SI')`

Calculate pump power requirement.

Formula: P = Q × ρ × g × H / η

**Parameters:**
- `flow_rate` (float): Volumetric flow rate in m³/s (SI) or gpm (US)
- `density` (float): Fluid density in kg/m³ (SI) or lb/ft³ (US)
- `gravity` (float): Gravitational acceleration in m/s² (SI) or ft/s² (US)
- `total_head` (float): Total head in m (SI) or ft (US)
- `efficiency` (float): Pump efficiency (0-1, e.g., 0.75 for 75%)
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: Power in W (SI) or hp (US)
- `'unit'`: Power unit
- `'hydraulic_power'`: Power before efficiency loss
- `'efficiency'`: Input efficiency
- `'formula_used'`: Calculation formula
- `'warnings'`: Warnings if efficiency is unusual

**Raises:**
- `ValueError`: If efficiency ≤ 0 or > 1

**Example:**
```python
result = calculate_power_required(
    flow_rate=0.01,      # m³/s
    density=1000.0,      # kg/m³
    gravity=9.81,        # m/s²
    total_head=15.5,     # m
    efficiency=0.75      # 75%
)
# Returns: {'value': 2034.0, 'unit': 'W', ...}
```

---

### `calculate_npsh_available(inlet_pressure, vapor_pressure, inlet_height, density, gravity=9.81, unit_system='SI')`

Calculate Net Positive Suction Head Available.

Formula: NPSH_a = (P_inlet - P_vapor)/(ρg) + H_inlet

**Parameters:**
- `inlet_pressure` (float): Inlet pressure in Pa (SI) or psi (US)
- `vapor_pressure` (float): Fluid vapor pressure in Pa (SI) or psi (US)
- `inlet_height` (float): Inlet elevation in m (SI) or ft (US)
- `density` (float): Fluid density in kg/m³ (SI) or lb/ft³ (US)
- `gravity` (float, optional): Gravitational acceleration, default 9.81 m/s²
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: NPSH available in m (SI) or ft (US)
- `'unit'`: Head unit
- `'pressure_head'`: Contribution from pressure difference
- `'static_head'`: Contribution from elevation
- `'formula_used'`: Calculation formula
- `'warnings'`: Warnings if NPSH is very low

**Example:**
```python
result = calculate_npsh_available(
    inlet_pressure=101325.0,  # Atmospheric pressure
    vapor_pressure=2339.0,    # Water vapor pressure at 20°C
    inlet_height=2.0,         # m
    density=1000.0            # kg/m³
)
# Returns: {'value': 12.1, 'unit': 'm', ...}
```

---

### `assess_cavitation_risk(npsh_available, npsh_required, safety_margin=0.5)`

Assess cavitation risk by comparing available and required NPSH.

**Parameters:**
- `npsh_available` (float): NPSH available in m (SI) or ft (US)
- `npsh_required` (float): NPSH required by pump in m (SI) or ft (US)
- `safety_margin` (float, optional): Minimum safety margin in m (SI) or ft (US), default 0.5

**Returns:** dict with keys:
- `'margin'`: NPSH_available - NPSH_required
- `'margin_unit'`: Unit of margin
- `'risk_level'`: 'safe', 'marginal', or 'high_risk'
- `'assessment'`: Textual assessment
- `'recommendations'`: List of corrective actions if needed
- `'warnings'`: Warnings if cavitation risk detected

**Example:**
```python
result = assess_cavitation_risk(
    npsh_available=12.1,
    npsh_required=3.0,
    safety_margin=0.5
)
# Returns: {'margin': 9.1, 'risk_level': 'safe', ...}
```

---

## Module: `fluids.valve`

Valve sizing and flow coefficient calculations.

### `calculate_cv_required(flow_rate, pressure_drop, fluid_gravity=1.0, unit_system='SI')`

Calculate required valve Cv for given flow and pressure drop.

**Formulas:**
- **SI**: Cv = Q / √(ΔP) where Q in m³/h, ΔP in bar
- **US**: Cv = Q / √(ΔP/sg) where Q in gpm, ΔP in psi, sg is specific gravity

**Parameters:**
- `flow_rate` (float): Volumetric flow rate in m³/h (SI) or gpm (US)
- `pressure_drop` (float): Pressure drop across valve in bar (SI) or psi (US)
- `fluid_gravity` (float, optional): Specific gravity (water=1.0), default 1.0
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: Required Cv coefficient
- `'unit'`: Cv unit
- `'flow_rate'`: Input flow rate
- `'pressure_drop'`: Input pressure drop
- `'specific_gravity'`: Fluid specific gravity
- `'formula_used'`: Calculation formula
- `'warnings'`: Warnings for very small/large Cv
- `'source'`: Reference (IEC 60534)

**Example:**
```python
result = calculate_cv_required(
    flow_rate=100.0,      # m³/h
    pressure_drop=2.0,    # bar
    fluid_gravity=1.0
)
# Returns: {'value': 70.7, 'unit': '(m³/h)/√bar', ...}
```

---

### `calculate_flow_rate_through_valve(cv, pressure_drop, fluid_gravity=1.0, unit_system='SI')`

Calculate flow rate through valve given Cv and pressure drop.

**Formulas:**
- **SI**: Q = Cv × √(ΔP)
- **US**: Q = Cv × √(ΔP/sg)

**Parameters:**
- `cv` (float): Valve flow coefficient
- `pressure_drop` (float): Pressure drop in bar (SI) or psi (US)
- `fluid_gravity` (float, optional): Specific gravity, default 1.0
- `unit_system` (str, optional): 'SI' or 'US', default 'SI'

**Returns:** dict with keys:
- `'value'`: Flow rate in m³/h (SI) or gpm (US)
- `'unit'`: Flow rate unit
- `'cv'`: Input Cv
- `'pressure_drop'`: Input pressure drop
- `'formula_used'`: Calculation formula
- `'warnings'`: Warnings for unusual flow rates

**Example:**
```python
result = calculate_flow_rate_through_valve(
    cv=70.7,
    pressure_drop=2.0,
    fluid_gravity=1.0
)
# Returns: {'value': 100.0, 'unit': 'm³/h', ...}
```

---

### `calculate_valve_authority(valve_pressure_drop, system_pressure_drop)`

Calculate valve authority (ratio of valve drop to total system drop).

Formula: Authority = ΔP_valve / (ΔP_valve + ΔP_system)

Typical ideal range: 0.3 - 0.5 (30-50%)

**Parameters:**
- `valve_pressure_drop` (float): Pressure drop across valve
- `system_pressure_drop` (float): System pressure drop (excluding valve)

**Returns:** dict with keys:
- `'value'`: Valve authority (0-1)
- `'value_percentage'`: Authority as percentage
- `'assessment'`: Qualitative assessment
- `'recommendation'`: Sizing advice
- `'ideal_range'`: Recommended authority range
- `'warnings'`: Warnings for poor authority

**Example:**
```python
result = calculate_valve_authority(
    valve_pressure_drop=2.0,
    system_pressure_drop=3.0
)
# Returns: {'value': 0.4, 'assessment': 'Good authority', ...}
```

---

### `calculate_valve_rangeability(cv_min, cv_max, min_controllable_opening_percent=5.0)`

Calculate valve rangeability (control range).

Rangeability = Cv_max / Cv_min

Typical values: 20:1 to 100:1 depending on valve type

**Parameters:**
- `cv_min` (float): Cv at minimum controllable opening
- `cv_max` (float): Cv at maximum opening
- `min_controllable_opening_percent` (float, optional): Minimum opening %, default 5.0

**Returns:** dict with keys:
- `'value'`: Rangeability ratio
- `'value_ratio'`: Formatted ratio (e.g., "50:1")
- `'assessment'`: Qualitative assessment
- `'recommendation'`: Application suitability
- `'typical_valve_types'`: Rangeability by valve type
- `'warnings'`: Warnings for poor rangeability

**Example:**
```python
result = calculate_valve_rangeability(cv_min=1.0, cv_max=50.0)
# Returns: {'value': 50.0, 'value_ratio': '50.0:1', 'assessment': 'Good rangeability', ...}
```

---

## Error Handling

All functions raise `ValueError` for invalid inputs:

```python
try:
    result = calculate_reynolds(
        density=-1000.0,  # Invalid: negative
        velocity=2.0,
        diameter=0.05,
        viscosity=0.001
    )
except ValueError as e:
    print(f"Error: {e}")
    # Output: "Error: Density must be positive"
```

## Unit Systems

All calculation functions accept `unit_system` parameter:
- `'SI'`: Metric units (meters, kilograms, Pascals, etc.)
- `'US'`: US customary units (feet, pounds, psi, etc.)

```python
# SI units
result_si = calculate_reynolds(1000.0, 2.0, 0.05, 0.001, unit_system='SI')

# US customary units
result_us = calculate_reynolds(62.4, 6.56, 0.164, 0.000672, unit_system='US')
```

## References

- **Crane TP-410**: Flow of Fluids Through Valves, Fittings, and Pipe
- **Darcy-Weisbach Equation**: Pressure drop in pipe flow
- **Colebrook-White Equation**: Friction factor for turbulent flow
- **IEC 60534**: Industrial-process control valves
- **Pump Hydraulics**: Standard engineering practices for pump sizing
- **NPSH Calculations**: Hydraulic Institute standards
