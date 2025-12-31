# CLI Reference: Core Fluid Calculations

## Overview

The Core Fluid Calculations CLI provides command-line access to all pipe flow, pump sizing, and valve sizing calculations.

## Installation

```bash
pip install -e .
```

## General Usage

```bash
fluids <module> <command> [options]
```

**Modules:**
- `pipe` - Pipe flow calculations
- `pump` - Pump sizing calculations
- `valve` - Valve sizing calculations

**Global Options:**
- `--output-format {json,text}` - Output format (default: text)
- `--verbosity {minimal,standard,detailed}` - Output detail level (default: standard)
- `--help` - Show help message

---

## Pipe Flow Commands

### Reynolds Number

Calculate Reynolds number for pipe flow.

```bash
fluids pipe reynolds \
  --density <value> \
  --velocity <value> \
  --diameter <value> \
  --viscosity <value> \
  [--unit-system {SI,US}] \
  [--output-format {json,text}] \
  [--verbosity {minimal,standard,detailed}]
```

**Required Arguments:**
- `--density` - Fluid density (kg/m³ for SI, lb/ft³ for US)
- `--velocity` - Flow velocity (m/s for SI, ft/s for US)
- `--diameter` - Pipe diameter (m for SI, ft for US)
- `--viscosity` - Dynamic viscosity (Pa·s for SI, lb/(ft·s) for US)

**Optional Arguments:**
- `--unit-system` - Unit system: SI or US (default: SI)
- `--output-format` - Output format: json or text (default: text)
- `--verbosity` - Output detail: minimal, standard, or detailed (default: standard)

**Example (SI units):**
```bash
fluids pipe reynolds \
  --density 1000.0 \
  --velocity 2.0 \
  --diameter 0.05 \
  --viscosity 0.001
```

**Output:**
```
Reynolds Number Calculation
============================
Reynolds Number: 100000.0
Flow Regime: turbulent

Formula: Re = ρVD/μ
  ρ (density) = 1000.0 kg/m³
  V (velocity) = 2.0 m/s
  D (diameter) = 0.05 m
  μ (viscosity) = 0.001 Pa·s

Flow regime classification:
  - Re < 2300: Laminar
  - 2300 ≤ Re ≤ 4000: Transitional
  - Re > 4000: Turbulent
```

**Example (JSON output):**
```bash
fluids pipe reynolds \
  --density 1000.0 \
  --velocity 2.0 \
  --diameter 0.05 \
  --viscosity 0.001 \
  --output-format json \
  --verbosity minimal
```

**Output:**
```json
{
  "value": 100000.0,
  "regime": "turbulent",
  "formula_used": "Re = ρVD/μ"
}
```

---

### Friction Factor

Calculate Darcy friction factor.

```bash
fluids pipe friction \
  --reynolds <value> \
  --roughness <value> \
  --diameter <value> \
  [--unit-system {SI,US}] \
  [--output-format {json,text}] \
  [--verbosity {minimal,standard,detailed}]
```

**Required Arguments:**
- `--reynolds` - Reynolds number (dimensionless)
- `--roughness` - Absolute pipe roughness (m for SI, ft for US)
- `--diameter` - Pipe diameter (m for SI, ft for US)

**Example:**
```bash
fluids pipe friction \
  --reynolds 100000.0 \
  --roughness 0.000045 \
  --diameter 0.05
```

**Output:**
```
Friction Factor Calculation
============================
Friction Factor: 0.0185
Method: colebrook

Flow Regime: Turbulent (Re > 4000)
Formula: Colebrook-White equation (implicit)
  1/√f = -2.0 log₁₀(ε/(3.7D) + 2.51/(Re√f))

Parameters:
  Re = 100000.0
  ε (roughness) = 0.000045 m
  D (diameter) = 0.05 m
  ε/D (relative roughness) = 0.0009
```

---

### Pressure Drop

Calculate pressure drop using Darcy-Weisbach equation.

```bash
fluids pipe pressure-drop \
  --friction-factor <value> \
  --length <value> \
  --diameter <value> \
  --velocity <value> \
  --density <value> \
  [--unit-system {SI,US}] \
  [--output-format {json,text}] \
  [--verbosity {minimal,standard,detailed}]
```

**Required Arguments:**
- `--friction-factor` - Darcy friction factor (dimensionless)
- `--length` - Pipe length (m for SI, ft for US)
- `--diameter` - Pipe diameter (m for SI, ft for US)
- `--velocity` - Flow velocity (m/s for SI, ft/s for US)
- `--density` - Fluid density (kg/m³ for SI, lb/ft³ for US)

**Example:**
```bash
fluids pipe pressure-drop \
  --friction-factor 0.0185 \
  --length 100.0 \
  --diameter 0.05 \
  --velocity 2.0 \
  --density 1000.0
```

**Output:**
```
Pressure Drop Calculation
==========================
Pressure Drop: 74000.0 Pa (0.74 bar)

Formula: ΔP = f × (L/D) × (ρV²/2)
  f = 0.0185
  L = 100.0 m
  D = 0.05 m
  ρ = 1000.0 kg/m³
  V = 2.0 m/s

Calculation:
  L/D = 2000.0
  ρV²/2 = 2000.0 Pa
  ΔP = 0.0185 × 2000.0 × 2000.0 = 74000.0 Pa
```

---

## Pump Sizing Commands

### Total Head

Calculate total pump head required.

```bash
fluids pump head \
  --static <value> \
  --dynamic <value> \
  --friction <value> \
  [--unit-system {SI,US}] \
  [--output-format {json,text}] \
  [--verbosity {minimal,standard,detailed}]
```

**Required Arguments:**
- `--static` - Static head (elevation difference) in m or ft
- `--dynamic` - Dynamic head (velocity head) in m or ft
- `--friction` - Friction losses in m or ft

**Example:**
```bash
fluids pump head \
  --static 10.0 \
  --dynamic 0.5 \
  --friction 5.0
```

**Output:**
```
Total Pump Head Calculation
============================
Total Head: 15.5 m

Components:
  Static head:    10.0 m
  Dynamic head:    0.5 m
  Friction losses: 5.0 m

Formula: H_total = H_static + H_dynamic + H_friction
```

---

### Pump Power

Calculate pump power requirement.

```bash
fluids pump power \
  --flow-rate <value> \
  --density <value> \
  --head <value> \
  --efficiency <value> \
  [--unit-system {SI,US}] \
  [--output-format {json,text}] \
  [--verbosity {minimal,standard,detailed}]
```

**Required Arguments:**
- `--flow-rate` - Volumetric flow rate (m³/s for SI, gpm for US)
- `--density` - Fluid density (kg/m³ for SI, lb/ft³ for US)
- `--head` - Total head (m for SI, ft for US)
- `--efficiency` - Pump efficiency (0-1, e.g., 0.75 for 75%)

**Example:**
```bash
fluids pump power \
  --flow-rate 0.01 \
  --density 1000.0 \
  --head 15.5 \
  --efficiency 0.75
```

**Output:**
```
Pump Power Calculation
======================
Power Required: 2034.0 W (2.034 kW)

Formula: P = Q × ρ × g × H / η
  Q (flow rate) = 0.01 m³/s
  ρ (density) = 1000.0 kg/m³
  g (gravity) = 9.81 m/s²
  H (head) = 15.5 m
  η (efficiency) = 0.75

Hydraulic power: 1525.5 W
Shaft power: 2034.0 W (accounting for 75% efficiency)
```

---

### NPSH Available

Calculate Net Positive Suction Head Available.

```bash
fluids pump npsh-available \
  --inlet-pressure <value> \
  --vapor-pressure <value> \
  --inlet-height <value> \
  --density <value> \
  [--unit-system {SI,US}] \
  [--output-format {json,text}] \
  [--verbosity {minimal,standard,detailed}]
```

**Required Arguments:**
- `--inlet-pressure` - Inlet pressure (Pa for SI, psi for US)
- `--vapor-pressure` - Fluid vapor pressure (Pa for SI, psi for US)
- `--inlet-height` - Inlet elevation (m for SI, ft for US)
- `--density` - Fluid density (kg/m³ for SI, lb/ft³ for US)

**Example:**
```bash
fluids pump npsh-available \
  --inlet-pressure 101325.0 \
  --vapor-pressure 2339.0 \
  --inlet-height 2.0 \
  --density 1000.0
```

**Output:**
```
NPSH Available Calculation
===========================
NPSH Available: 12.1 m

Formula: NPSH_a = (P_inlet - P_vapor)/(ρg) + H_inlet
  P_inlet = 101325.0 Pa
  P_vapor = 2339.0 Pa
  ρ = 1000.0 kg/m³
  g = 9.81 m/s²
  H_inlet = 2.0 m

Components:
  Pressure head: 10.1 m
  Static head: 2.0 m
```

---

### Cavitation Risk Assessment

Assess cavitation risk.

```bash
fluids pump cavitation-risk \
  --npsh-available <value> \
  --npsh-required <value> \
  [--safety-margin <value>] \
  [--output-format {json,text}]
```

**Required Arguments:**
- `--npsh-available` - NPSH available (m or ft)
- `--npsh-required` - NPSH required by pump (m or ft)

**Optional Arguments:**
- `--safety-margin` - Minimum safety margin (default: 0.5 m or 1.64 ft)

**Example:**
```bash
fluids pump cavitation-risk \
  --npsh-available 12.1 \
  --npsh-required 3.0
```

**Output:**
```
Cavitation Risk Assessment
===========================
Risk Level: SAFE

NPSH Margin: 9.1 m
  NPSH Available: 12.1 m
  NPSH Required: 3.0 m
  Safety Margin: 0.5 m

Assessment: Adequate NPSH margin. No cavitation risk.
```

---

## Valve Sizing Commands

### Cv Required

Calculate required valve Cv.

```bash
fluids valve cv \
  --flow-rate <value> \
  --pressure-drop <value> \
  [--specific-gravity <value>] \
  [--unit-system {SI,US}] \
  [--output-format {json,text}] \
  [--verbosity {minimal,standard,detailed}]
```

**Required Arguments:**
- `--flow-rate` - Volumetric flow rate (m³/h for SI, gpm for US)
- `--pressure-drop` - Pressure drop across valve (bar for SI, psi for US)

**Optional Arguments:**
- `--specific-gravity` - Fluid specific gravity (default: 1.0 for water)
- `--unit-system` - Unit system: SI or US (default: SI)

**Example:**
```bash
fluids valve cv \
  --flow-rate 100.0 \
  --pressure-drop 2.0 \
  --specific-gravity 1.0
```

**Output:**
```
Valve Cv Calculation
====================
Required Cv: 70.7 (m³/h)/√bar

Formula: Cv = Q / √(ΔP)
  Q (flow rate) = 100.0 m³/h
  ΔP (pressure drop) = 2.0 bar
  sg (specific gravity) = 1.0

Calculation:
  Cv = 100.0 / √2.0 = 70.7
```

---

### Flow Rate Through Valve

Calculate flow rate through valve.

```bash
fluids valve flow-rate \
  --cv <value> \
  --pressure-drop <value> \
  [--specific-gravity <value>] \
  [--unit-system {SI,US}] \
  [--output-format {json,text}]
```

**Required Arguments:**
- `--cv` - Valve flow coefficient
- `--pressure-drop` - Pressure drop (bar for SI, psi for US)

**Example:**
```bash
fluids valve flow-rate \
  --cv 70.7 \
  --pressure-drop 2.0
```

**Output:**
```
Valve Flow Rate Calculation
============================
Flow Rate: 100.0 m³/h

Formula: Q = Cv × √(ΔP)
  Cv = 70.7
  ΔP = 2.0 bar
```

---

### Valve Sizing

Select appropriate valve size from available options.

```bash
fluids valve sizing \
  --flow-rate <value> \
  --pressure-drop <value> \
  --cv-options <cv1> <cv2> <cv3> ... \
  [--specific-gravity <value>] \
  [--unit-system {SI,US}] \
  [--output-format {json,text}]
```

**Required Arguments:**
- `--flow-rate` - Required flow rate (m³/h for SI, gpm for US)
- `--pressure-drop` - Pressure drop (bar for SI, psi for US)
- `--cv-options` - List of available valve Cv values

**Example:**
```bash
fluids valve sizing \
  --flow-rate 100.0 \
  --pressure-drop 2.0 \
  --cv-options 50 75 100 150 200
```

**Output:**
```
Valve Sizing Recommendation
============================
Recommended Valve: Cv = 75

Required Cv: 70.7
Recommended Cv: 75
Opening at Design Flow: 94.3%
Oversizing Factor: 1.06x

Alternative Options:
  - Cv 100: Opening 70.7%, Oversizing 1.41x
  - Cv 150: Opening 47.1%, Oversizing 2.12x

Recommendation: Cv 75 provides best match with minimal oversizing
and operates in acceptable control range (10-90% opening).
```

---

### Valve Authority

Calculate valve authority.

```bash
fluids valve authority \
  --valve-drop <value> \
  --system-drop <value> \
  [--output-format {json,text}]
```

**Required Arguments:**
- `--valve-drop` - Pressure drop across valve
- `--system-drop` - System pressure drop (excluding valve)

**Example:**
```bash
fluids valve authority \
  --valve-drop 2.0 \
  --system-drop 3.0
```

**Output:**
```
Valve Authority Calculation
============================
Valve Authority: 0.40 (40.0%)

Formula: Authority = ΔP_valve / (ΔP_valve + ΔP_system)
  ΔP_valve = 2.0
  ΔP_system = 3.0
  ΔP_total = 5.0

Assessment: Good authority
Ideal Range: 0.3 - 0.5 (30-50%)

Recommendation: Valve authority in typical optimal range.
```

---

## Output Formats

### Text Format (default)

Human-readable format with headers, formulas, and explanations.

```bash
fluids pipe reynolds --density 1000 --velocity 2 --diameter 0.05 --viscosity 0.001
```

### JSON Format

Machine-readable JSON for programmatic use.

```bash
fluids pipe reynolds \
  --density 1000 --velocity 2 --diameter 0.05 --viscosity 0.001 \
  --output-format json
```

Output:
```json
{
  "value": 100000.0,
  "regime": "turbulent",
  "formula_used": "Re = ρVD/μ",
  "warnings": [],
  "intermediate_values": {
    "density": 1000.0,
    "velocity": 2.0,
    "diameter": 0.05,
    "viscosity": 0.001
  },
  "source": "Reynolds number calculation"
}
```

---

## Verbosity Levels

### Minimal

Only essential results.

```bash
--verbosity minimal
```

Example output:
```
Reynolds Number: 100000.0 (turbulent)
```

### Standard (default)

Results with formulas and key parameters.

```bash
--verbosity standard
```

Example output:
```
Reynolds Number: 100000.0
Flow Regime: turbulent
Formula: Re = ρVD/μ
```

### Detailed

Complete calculation tree with all intermediate values, formulas, and references.

```bash
--verbosity detailed
```

Example output includes:
- All intermediate calculations
- Complete formula derivations
- Alternative methods considered
- Validation data sources
- Warnings and recommendations

---

## Error Handling

The CLI provides clear error messages for invalid inputs:

```bash
fluids pipe reynolds --density -1000 --velocity 2 --diameter 0.05 --viscosity 0.001
```

Output:
```
Error: Density must be positive
```

Common errors:
- **Negative values**: "Value must be positive"
- **Zero values**: "Value cannot be zero"
- **Out of range**: "Value out of acceptable range"
- **Missing arguments**: "Missing required argument: --density"
- **Invalid unit system**: "Unit system must be 'SI' or 'US'"

---

## Examples and Workflows

### Complete Pipe Flow Analysis

```bash
# Step 1: Calculate Reynolds number
fluids pipe reynolds --density 1000 --velocity 2 --diameter 0.05 --viscosity 0.001

# Step 2: Calculate friction factor
fluids pipe friction --reynolds 100000 --roughness 0.000045 --diameter 0.05

# Step 3: Calculate pressure drop
fluids pipe pressure-drop --friction-factor 0.0185 --length 100 --diameter 0.05 --velocity 2 --density 1000
```

### Complete Pump Sizing

```bash
# Calculate total head
fluids pump head --static 10 --dynamic 0.5 --friction 5

# Calculate power requirement
fluids pump power --flow-rate 0.01 --density 1000 --head 15.5 --efficiency 0.75

# Check NPSH
fluids pump npsh-available --inlet-pressure 101325 --vapor-pressure 2339 --inlet-height 2 --density 1000

# Assess cavitation risk
fluids pump cavitation-risk --npsh-available 12.1 --npsh-required 3.0
```

### Valve Selection

```bash
# Calculate required Cv
fluids valve cv --flow-rate 100 --pressure-drop 2

# Select from available valves
fluids valve sizing --flow-rate 100 --pressure-drop 2 --cv-options 50 75 100 150

# Check valve authority
fluids valve authority --valve-drop 2 --system-drop 3
```

---

## Tips and Best Practices

1. **Use JSON format for scripting**: Easier to parse programmatically
2. **Start with standard verbosity**: Provides good balance of detail
3. **Check warnings**: Important for identifying potential issues
4. **Validate units**: Double-check input units match the selected unit system
5. **Save outputs**: Redirect to file for documentation: `fluids pipe reynolds ... > results.txt`
6. **Chain calculations**: Use shell scripting to automate multi-step workflows

---

## Getting Help

```bash
# General help
fluids --help

# Module-specific help
fluids pipe --help
fluids pump --help
fluids valve --help

# Command-specific help
fluids pipe reynolds --help
fluids pump power --help
fluids valve cv --help
```
