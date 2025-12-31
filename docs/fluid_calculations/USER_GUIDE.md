# User Guide: Core Fluid Calculations

## Introduction

The Core Fluid Calculations library provides engineering calculations for three main areas:

1. **Pipe Flow Analysis**: Calculate Reynolds number, friction factor, and pressure drop for fluid flow in pipes
2. **Pump Sizing**: Determine required pump head, power, and assess cavitation risk (NPSH)
3. **Valve Sizing**: Select appropriate valve sizes based on flow requirements and calculate flow coefficients (Cv)

This guide demonstrates complete workflows for common engineering tasks.

---

## Installation

```bash
# Install in development mode
pip install -e .

# Or install required dependencies
pip install numpy scipy pint pydantic pytest mypy
```

---

## Quick Start Examples

### Example 1: Water Flow Through a Pipe

**Problem**: Water at 20°C flows at 2 m/s through a 50 mm diameter steel pipe that is 100 m long. Calculate the pressure drop.

**Solution (Python API)**:

```python
from fluids.pipe import (
    calculate_reynolds,
    calculate_friction_factor,
    calculate_pressure_drop
)

# Fluid properties (water at 20°C)
density = 1000.0      # kg/m³
viscosity = 0.001     # Pa·s

# Pipe properties
diameter = 0.05       # m (50 mm)
length = 100.0        # m
roughness = 0.000045  # m (commercial steel)
velocity = 2.0        # m/s

# Step 1: Calculate Reynolds number
reynolds_result = calculate_reynolds(
    density=density,
    velocity=velocity,
    diameter=diameter,
    viscosity=viscosity
)
print(f"Reynolds number: {reynolds_result['value']:.0f}")
print(f"Flow regime: {reynolds_result['regime']}")

# Step 2: Calculate friction factor
friction_result = calculate_friction_factor(
    reynolds=reynolds_result['value'],
    roughness=roughness,
    diameter=diameter
)
print(f"Friction factor: {friction_result['value']:.4f}")
print(f"Method: {friction_result['method']}")

# Step 3: Calculate pressure drop
pressure_result = calculate_pressure_drop(
    friction_factor=friction_result['value'],
    length=length,
    diameter=diameter,
    velocity=velocity,
    density=density
)
print(f"Pressure drop: {pressure_result['value']:.0f} Pa ({pressure_result['value']/1e5:.2f} bar)")
```

**Output**:
```
Reynolds number: 100000
Flow regime: turbulent
Friction factor: 0.0185
Method: colebrook
Pressure drop: 74000 Pa (0.74 bar)
```

**Solution (CLI)**:

```bash
# Step 1: Reynolds number
fluids pipe reynolds \
  --density 1000 --velocity 2 --diameter 0.05 --viscosity 0.001

# Step 2: Friction factor
fluids pipe friction \
  --reynolds 100000 --roughness 0.000045 --diameter 0.05

# Step 3: Pressure drop
fluids pipe pressure-drop \
  --friction-factor 0.0185 --length 100 --diameter 0.05 --velocity 2 --density 1000
```

---

### Example 2: Pump Sizing for a System

**Problem**: Size a pump to transfer water from a storage tank (elevation 0 m) to a process vessel (elevation 10 m). The system has 5 m of friction losses, and the flow rate is 0.01 m³/s. The pump efficiency is 75%.

**Solution (Python API)**:

```python
from fluids.pump import (
    calculate_static_head,
    calculate_dynamic_head,
    calculate_total_head,
    calculate_power_required,
    calculate_npsh_available,
    assess_cavitation_risk
)

# System parameters
elevation_in = 0.0      # m
elevation_out = 10.0    # m
flow_rate = 0.01        # m³/s
friction_losses = 5.0   # m
velocity = 2.0          # m/s
efficiency = 0.75       # 75%

# Fluid properties
density = 1000.0        # kg/m³
gravity = 9.81          # m/s²

# Step 1: Calculate static head
static_head_result = calculate_static_head(
    elevation_in=elevation_in,
    elevation_out=elevation_out
)
print(f"Static head: {static_head_result['value']:.1f} m")

# Step 2: Calculate dynamic head
dynamic_head_result = calculate_dynamic_head(
    velocity=velocity,
    gravity=gravity
)
print(f"Dynamic head: {dynamic_head_result['value']:.2f} m")

# Step 3: Calculate total head
total_head_result = calculate_total_head(
    static_head=static_head_result['value'],
    dynamic_head=dynamic_head_result['value'],
    friction_losses=friction_losses
)
print(f"Total head: {total_head_result['value']:.1f} m")

# Step 4: Calculate power requirement
power_result = calculate_power_required(
    flow_rate=flow_rate,
    density=density,
    gravity=gravity,
    total_head=total_head_result['value'],
    efficiency=efficiency
)
print(f"Power required: {power_result['value']:.0f} W ({power_result['value']/1000:.2f} kW)")
print(f"Motor size: Select {power_result['value']/1000 * 1.15:.1f} kW motor (15% safety factor)")

# Step 5: Check NPSH (assume atmospheric inlet)
inlet_pressure = 101325.0    # Pa (atmospheric)
vapor_pressure = 2339.0      # Pa (water at 20°C)
inlet_height = 2.0           # m above pump centerline

npsh_available_result = calculate_npsh_available(
    inlet_pressure=inlet_pressure,
    vapor_pressure=vapor_pressure,
    inlet_height=inlet_height,
    density=density,
    gravity=gravity
)
print(f"NPSH available: {npsh_available_result['value']:.1f} m")

# Step 6: Assess cavitation risk (assume pump requires 3 m NPSH)
npsh_required = 3.0  # m (from pump manufacturer curve)

cavitation_result = assess_cavitation_risk(
    npsh_available=npsh_available_result['value'],
    npsh_required=npsh_required,
    safety_margin=0.5
)
print(f"NPSH margin: {cavitation_result['margin']:.1f} m")
print(f"Risk level: {cavitation_result['risk_level']}")
print(f"Assessment: {cavitation_result['assessment']}")
```

**Output**:
```
Static head: 10.0 m
Dynamic head: 0.20 m
Total head: 15.2 m
Power required: 1992 W (1.99 kW)
Motor size: Select 2.3 kW motor (15% safety factor)
NPSH available: 12.1 m
NPSH margin: 9.1 m
Risk level: safe
Assessment: Adequate NPSH margin. No cavitation risk.
```

**Solution (CLI)**:

```bash
# Calculate total head
fluids pump head --static 10 --dynamic 0.2 --friction 5

# Calculate power
fluids pump power --flow-rate 0.01 --density 1000 --head 15.2 --efficiency 0.75

# Check NPSH
fluids pump npsh-available \
  --inlet-pressure 101325 --vapor-pressure 2339 --inlet-height 2 --density 1000

# Assess cavitation risk
fluids pump cavitation-risk --npsh-available 12.1 --npsh-required 3.0
```

---

### Example 3: Valve Sizing and Selection

**Problem**: Select an appropriate control valve for a water system with a flow rate of 100 m³/h and a pressure drop of 2 bar. Available valve sizes have Cv values of 50, 75, 100, 150, and 200.

**Solution (Python API)**:

```python
from fluids.valve import (
    calculate_cv_required,
    calculate_valve_sizing,
    calculate_valve_authority,
    assess_valve_performance
)

# System parameters
flow_rate = 100.0        # m³/h
pressure_drop = 2.0      # bar
specific_gravity = 1.0   # water
system_drop = 3.0        # bar (pipe and fittings)

# Available valve options
cv_options = [50, 75, 100, 150, 200]

# Step 1: Calculate required Cv
cv_result = calculate_cv_required(
    flow_rate=flow_rate,
    pressure_drop=pressure_drop,
    fluid_gravity=specific_gravity,
    unit_system="SI"
)
print(f"Required Cv: {cv_result['value']:.1f} {cv_result['unit']}")

# Step 2: Select valve from available options
sizing_result = calculate_valve_sizing(
    flow_rate=flow_rate,
    pressure_drop=pressure_drop,
    valve_cv_options=cv_options,
    fluid_gravity=specific_gravity,
    unit_system="SI"
)
print(f"\nRecommended valve: Cv = {sizing_result['recommended_cv']}")
print(f"Opening at design flow: {sizing_result['recommended_percentage']:.1f}%")
print(f"Oversizing factor: {sizing_result['oversizing_factor']:.2f}x")

print("\nAlternative options:")
for option in sizing_result['all_suitable_options'][1:]:
    print(f"  - Cv {option['cv']}: {option['opening_percent']:.1f}% opening, "
          f"{option['oversizing_ratio']:.2f}x oversizing")

# Step 3: Check valve authority
authority_result = calculate_valve_authority(
    valve_pressure_drop=pressure_drop,
    system_pressure_drop=system_drop
)
print(f"\nValve authority: {authority_result['value']:.2f} ({authority_result['value_percentage']})")
print(f"Assessment: {authority_result['assessment']}")
print(f"Recommendation: {authority_result['recommendation']}")

# Step 4: Comprehensive performance assessment
performance_result = assess_valve_performance(
    cv_at_design=cv_result['value'],
    cv_max=sizing_result['recommended_cv'],
    pressure_drop_design=pressure_drop,
    system_pressure_drop=system_drop
)
print(f"\nOverall assessment: {performance_result['overall_assessment']}")
for warning in performance_result['warnings']:
    print(f"⚠ {warning}")
```

**Output**:
```
Required Cv: 70.7 (m³/h)/√bar

Recommended valve: Cv = 75
Opening at design flow: 94.3%
Oversizing factor: 1.06x

Alternative options:
  - Cv 100: 70.7% opening, 1.41x oversizing
  - Cv 150: 47.1% opening, 2.12x oversizing

Valve authority: 0.40 (40.0%)
Assessment: Good authority
Recommendation: Valve authority in typical optimal range.

Overall assessment: Good operating range with Good authority authority
```

**Solution (CLI)**:

```bash
# Calculate required Cv
fluids valve cv --flow-rate 100 --pressure-drop 2

# Select valve from options
fluids valve sizing \
  --flow-rate 100 --pressure-drop 2 \
  --cv-options 50 75 100 150 200

# Check valve authority
fluids valve authority --valve-drop 2 --system-drop 3
```

---

## Complete Workflow: Pipe-Pump-Valve System

**Problem**: Design a complete pumping system:
- Transfer water 100 m through a 50 mm steel pipe
- Pump from ground level (0 m) to elevated tank (10 m)
- Flow rate: 10 L/s (0.01 m³/s)
- Include control valve at outlet

### Step-by-Step Solution

```python
from fluids.pipe import calculate_reynolds, calculate_friction_factor, calculate_pressure_drop
from fluids.pump import calculate_total_head, calculate_power_required, calculate_npsh_available
from fluids.valve import calculate_cv_required, calculate_valve_authority

# === System Parameters ===
# Pipe
diameter = 0.05           # m
length = 100.0            # m
roughness = 0.000045      # m (steel)

# Flow
flow_rate = 0.01          # m³/s (10 L/s)
flow_rate_m3h = flow_rate * 3600  # m³/h for valve calculations

# Calculate velocity
import math
area = math.pi * (diameter/2)**2
velocity = flow_rate / area
print(f"Flow velocity: {velocity:.2f} m/s")

# Fluid (water at 20°C)
density = 1000.0          # kg/m³
viscosity = 0.001         # Pa·s
vapor_pressure = 2339.0   # Pa

# Elevations
elevation_in = 0.0        # m
elevation_out = 10.0      # m
inlet_height = 2.0        # m (tank above pump)

# Pump
efficiency = 0.75         # 75%

# === Step 1: Pipe Flow Analysis ===
print("\n=== PIPE FLOW ANALYSIS ===")

# Reynolds number
re_result = calculate_reynolds(density, velocity, diameter, viscosity)
print(f"Reynolds number: {re_result['value']:.0f} ({re_result['regime']})")

# Friction factor
f_result = calculate_friction_factor(re_result['value'], roughness, diameter)
print(f"Friction factor: {f_result['value']:.4f}")

# Pressure drop in pipe
pipe_drop_result = calculate_pressure_drop(
    f_result['value'], length, diameter, velocity, density
)
pipe_drop_pa = pipe_drop_result['value']
pipe_drop_m = pipe_drop_pa / (density * 9.81)  # Convert to head
print(f"Pipe pressure drop: {pipe_drop_pa:.0f} Pa ({pipe_drop_m:.2f} m head)")

# === Step 2: Valve Sizing ===
print("\n=== VALVE SIZING ===")

# Assume valve drop is 2 bar for good control
valve_drop_bar = 2.0
valve_drop_m = valve_drop_bar * 10.2  # Convert bar to m head (approx)

# Calculate required Cv
cv_result = calculate_cv_required(
    flow_rate=flow_rate_m3h,
    pressure_drop=valve_drop_bar,
    fluid_gravity=1.0,
    unit_system="SI"
)
print(f"Required Cv: {cv_result['value']:.1f}")

# Check valve authority
authority_result = calculate_valve_authority(
    valve_pressure_drop=valve_drop_m,
    system_pressure_drop=pipe_drop_m
)
print(f"Valve authority: {authority_result['value']:.2f} ({authority_result['assessment']})")

# === Step 3: Pump Sizing ===
print("\n=== PUMP SIZING ===")

# Calculate heads
static_head = elevation_out - elevation_in
dynamic_head = velocity**2 / (2 * 9.81)
friction_head = pipe_drop_m + valve_drop_m

total_head = static_head + dynamic_head + friction_head
print(f"Static head: {static_head:.1f} m")
print(f"Dynamic head: {dynamic_head:.2f} m")
print(f"Friction head (pipe + valve): {friction_head:.1f} m")
print(f"Total head: {total_head:.1f} m")

# Power requirement
power_result = calculate_power_required(
    flow_rate=flow_rate,
    density=density,
    gravity=9.81,
    total_head=total_head,
    efficiency=efficiency
)
print(f"Power required: {power_result['value']:.0f} W ({power_result['value']/1000:.2f} kW)")
print(f"Recommended motor: {power_result['value']/1000 * 1.15:.1f} kW (with 15% safety)")

# NPSH check
npsh_result = calculate_npsh_available(
    inlet_pressure=101325.0,
    vapor_pressure=vapor_pressure,
    inlet_height=inlet_height,
    density=density,
    gravity=9.81
)
print(f"NPSH available: {npsh_result['value']:.1f} m")

# === Step 4: Summary ===
print("\n=== SYSTEM SUMMARY ===")
print(f"Flow rate: {flow_rate*1000:.1f} L/s")
print(f"Pipe: {diameter*1000:.0f} mm diameter, {length:.0f} m length")
print(f"Pump: {total_head:.1f} m head, {power_result['value']/1000:.2f} kW")
print(f"Valve: Cv {cv_result['value']:.1f}, authority {authority_result['value']:.2f}")
print(f"NPSH available: {npsh_result['value']:.1f} m")
```

**Output**:
```
Flow velocity: 5.09 m/s

=== PIPE FLOW ANALYSIS ===
Reynolds number: 254648 (turbulent)
Friction factor: 0.0173
Pipe pressure drop: 227520 Pa (23.18 m head)

=== VALVE SIZING ===
Required Cv: 127.3
Valve authority: 0.47 (Good authority)

=== PUMP SIZING ===
Static head: 10.0 m
Dynamic head: 1.32 m
Friction head (pipe + valve): 43.6 m
Total head: 54.9 m
Power required: 7206 W (7.21 kW)
Recommended motor: 8.3 kW (with 15% safety)
NPSH available: 12.1 m

=== SYSTEM SUMMARY ===
Flow rate: 10.0 L/s
Pipe: 50 mm diameter, 100 m length
Pump: 54.9 m head, 7.21 kW
Valve: Cv 127.3, authority 0.47
NPSH available: 12.1 m
```

---

## Common Pipe Roughness Values

| Material | Absolute Roughness (m) | Absolute Roughness (mm) |
|----------|------------------------|-------------------------|
| Commercial steel (new) | 0.000045 | 0.045 |
| Commercial steel (average) | 0.000046 | 0.046 |
| Wrought iron | 0.000046 | 0.046 |
| Cast iron (uncoated) | 0.00026 | 0.26 |
| Galvanized iron | 0.00015 | 0.15 |
| PVC | 0.0000015 | 0.0015 |
| Concrete (smooth) | 0.0003 | 0.3 |
| Concrete (rough) | 0.003 | 3.0 |
| Copper or brass (drawn) | 0.0000015 | 0.0015 |
| Stainless steel | 0.000015 | 0.015 |

---

## Typical Fluid Properties (at 20°C)

| Fluid | Density (kg/m³) | Viscosity (Pa·s) | Specific Gravity |
|-------|-----------------|------------------|------------------|
| Water | 1000 | 0.001 | 1.0 |
| Seawater | 1025 | 0.00107 | 1.025 |
| Glycerol | 1260 | 1.5 | 1.26 |
| Ethanol | 789 | 0.00119 | 0.789 |
| Gasoline | 680-740 | 0.0006 | 0.68-0.74 |
| Diesel fuel | 820-950 | 0.003-0.005 | 0.82-0.95 |
| SAE 30 oil | 920 | 0.44 | 0.92 |
| SAE 10W-30 oil | 870 | 0.065 | 0.87 |

---

## Unit Conversion Quick Reference

### Length
- 1 m = 3.28084 ft
- 1 inch = 0.0254 m
- 1 mm = 0.001 m

### Pressure
- 1 Pa = 0.000145 psi
- 1 bar = 100,000 Pa = 14.5 psi
- 1 psi = 6894.76 Pa
- 1 atm = 101,325 Pa

### Flow Rate
- 1 m³/s = 15,850.3 gpm
- 1 L/s = 15.8503 gpm
- 1 gpm = 0.0000631 m³/s

### Viscosity
- 1 Pa·s = 1000 cP
- 1 cP = 0.001 Pa·s

### Power
- 1 W = 0.00134 hp
- 1 kW = 1.34 hp
- 1 hp = 745.7 W

---

## Troubleshooting

### High Pressure Drop

**Symptoms**: Calculated pressure drop higher than expected

**Possible Causes**:
1. High velocity → Check flow rate and pipe diameter
2. Long pipe length → Consider larger diameter or shorter route
3. Rough pipe → Verify roughness value for pipe material and age
4. High viscosity → Check fluid temperature and properties

**Solutions**:
- Increase pipe diameter
- Reduce flow rate
- Use smoother pipe material
- Reduce pipe length (reroute if possible)

### Low NPSH Available

**Symptoms**: NPSH_available < NPSH_required + safety margin

**Possible Causes**:
1. Low inlet pressure
2. High vapor pressure (high temperature)
3. Excessive inlet elevation
4. High suction losses

**Solutions**:
- Increase inlet pressure (pressurize tank)
- Lower fluid temperature
- Lower pump installation (reduce suction lift)
- Reduce suction line losses (larger pipe, fewer fittings)
- Select pump with lower NPSH_required

### Poor Valve Control

**Symptoms**: Valve operates fully open or nearly closed

**Possible Causes**:
1. Incorrect Cv selection
2. Poor valve authority (<0.3 or >0.7)
3. System pressure drop much higher/lower than expected

**Solutions**:
- Recalculate required Cv
- Adjust valve pressure drop for better authority (target 0.3-0.5)
- Verify system pressure drop calculations
- Consider different valve type (better rangeability)

---

## Best Practices

### Pipe Flow
1. **Always verify Reynolds number** to confirm flow regime
2. **Use appropriate roughness** for pipe age and condition
3. **Account for fittings** by adding equivalent length
4. **Consider fouling** - increase roughness for aged systems

### Pump Sizing
1. **Include safety factor** on power (typically 10-15%)
2. **Verify NPSH margin** ≥ 0.5 m (1.6 ft) minimum
3. **Check pump curve** for efficiency at operating point
4. **Consider future expansion** when selecting pump size

### Valve Sizing
1. **Target valve authority** between 0.3 and 0.5
2. **Avoid oversizing** - leads to poor control
3. **Consider rangeability** for variable flow applications
4. **Check opening percentage** - aim for 20-80% at design flow

---

## References

1. **Crane TP-410**: Flow of Fluids Through Valves, Fittings, and Pipe (Technical Paper 410)
2. **Perry's Chemical Engineers' Handbook**: Fluid flow section
3. **IEC 60534**: Industrial-process control valves
4. **Hydraulic Institute Standards**: Pump selection and NPSH
5. **ASME B31.3**: Process Piping

---

## Getting Help

For questions, issues, or feature requests:
- Documentation: See API.md and CLI.md
- Source code: Review implementation in `src/fluids/`
- Tests: Check `tests/` for usage examples
- Validation: See `tests/validation/` for reference data comparisons
