# CLI Interface Contract

**Feature**: 002-heat-exchanger-calc
**Date**: 2025-12-30
**Type**: Command-Line Interface specification

This document specifies the CLI commands, arguments, input/output formats, and error handling for the heat exchanger calculations library.

---

## CLI Commands Overview

Four main commands, one per calculation module:

```bash
calculate-lmtd [OPTIONS] [INPUT_FILE]
calculate-ntu [OPTIONS] [INPUT_FILE]
calculate-convection [OPTIONS] [INPUT_FILE]
calculate-insulation [OPTIONS] [INPUT_FILE]
```

All commands accept input from:
- File: `calculate-lmtd input.json`
- stdin: `cat input.json | calculate-lmtd -` or `calculate-lmtd --stdin`
- Interactive: `calculate-lmtd --interactive`

---

## Command 1: calculate-lmtd

### Signature

```bash
calculate-lmtd [OPTIONS] [INPUT_FILE]

Options:
  -f, --format {json,yaml,table}   Output format (default: json)
  -o, --output FILE                Write to file instead of stdout
  --verbose / --quiet              Include/suppress extra info
  -h, --help                       Show help and exit
```

### Input Format

**JSON**:
```json
{
  "hot_fluid": {
    "T_inlet": "100 degC",
    "T_outlet": "60 degC",
    "mdot": "10 kg/s"
  },
  "cold_fluid": {
    "T_inlet": "20 degC",
    "T_outlet": "40 degC",
    "mdot": "12 kg/s"
  },
  "exchanger": {
    "configuration": "counterflow",
    "area": "50 m**2",
    "F_correction": 1.0
  }
}
```

**YAML**:
```yaml
hot_fluid:
  T_inlet: 100 degC
  T_outlet: 60 degC
  mdot: 10 kg/s
cold_fluid:
  T_inlet: 20 degC
  T_outlet: 40 degC
  mdot: 12 kg/s
exchanger:
  configuration: counterflow
  area: 50 m**2
  F_correction: 1.0
```

### Output Format (Default: JSON)

```json
{
  "calculation_method": "LMTD_Counterflow_v1",
  "source_reference": "Incropera_9e_p452",
  "confidence_tolerance": 1.0,
  "heat_transfer_rate": "400.0 kilowatt",
  "LMTD_arithmetic": "40.3 kelvin",
  "LMTD_effective": "40.3 kelvin",
  "T_difference_hot": "40.0 kelvin",
  "T_difference_cold": "20.0 kelvin",
  "configuration_used": "counterflow",
  "energy_balance_hot": "400.0 kilowatt",
  "energy_balance_cold": "400.0 kilowatt",
  "energy_balance_error_percent": 0.25,
  "intermediate_values": {
    "ln_ratio": 1.3863,
    "ln_ratio_check": 1.3863
  }
}
```

### Output Format (--format table)

```
LMTD Heat Exchanger Calculation
═══════════════════════════════════════════════
Configuration:           counterflow
Area:                    50.0 m²
Hot inlet:               100.0 °C
Hot outlet:              60.0 °C
Cold inlet:              20.0 °C
Cold outlet:             40.0 °C
───────────────────────────────────────────────
Heat transfer rate:      400.0 kW
LMTD (arithmetic):       40.3 K
LMTD (effective):        40.3 K
F-correction factor:     1.0
Energy balance error:    0.25%
───────────────────────────────────────────────
Source: Incropera 9th edition, Page 452
Confidence tolerance:    1.0%
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Input validation error |
| 2 | Calculation error |
| 3 | File I/O error |
| 4 | Unknown error |

### Examples

```bash
# From file
calculate-lmtd input.json

# From file, save to output
calculate-lmtd input.json -o results.json

# From stdin
cat input.json | calculate-lmtd -

# Interactive entry
calculate-lmtd --interactive

# Verbose output (includes all intermediate values)
calculate-lmtd input.json --verbose

# Tabular output for human reading
calculate-lmtd input.json --format table

# Batch processing
for f in cases/*.json; do
  calculate-lmtd "$f" --format json -o "results/$(basename $f)"
done
```

---

## Command 2: calculate-ntu

### Signature

```bash
calculate-ntu [OPTIONS] [INPUT_FILE]

Options:
  -f, --format {json,yaml,table}   Output format (default: json)
  -o, --output FILE                Write to file instead of stdout
  --verbose / --quiet              Include/suppress intermediate values
  -h, --help                       Show help and exit
```

### Input Format

**JSON**:
```json
{
  "T_hot_inlet": "100 degC",
  "T_cold_inlet": "20 degC",
  "mdot_hot": "10 kg/s",
  "mdot_cold": "12 kg/s",
  "cp_hot": "4000 J/(kg*K)",
  "cp_cold": "4000 J/(kg*K)",
  "UA": "20 kW/K",
  "configuration": "counterflow"
}
```

### Output Format (Default: JSON)

```json
{
  "calculation_method": "NTU_Counterflow_v1",
  "source_reference": "NIST_NTU_Tables",
  "confidence_tolerance": 2.0,
  "NTU": 0.833,
  "effectiveness": 0.745,
  "heat_transfer_rate": "596.0 kilowatt",
  "T_hot_outlet": "73.3 degC",
  "T_cold_outlet": "39.6 degC",
  "C_hot": "40.0 kilowatt / kelvin",
  "C_cold": "48.0 kilowatt / kelvin",
  "C_min": "40.0 kilowatt / kelvin",
  "C_max": "48.0 kilowatt / kelvin",
  "C_ratio": 0.833,
  "Q_max": "800.0 kilowatt",
  "effectiveness_theoretical_max": 0.909,
  "energy_balance_error_percent": 0.1,
  "intermediate_values": {...}
}
```

### Examples

```bash
# From file
calculate-ntu ntu_input.yaml

# Find outlet temperature given UA
calculate-ntu input.json --format table

# Verify with verbose intermediate values
calculate-ntu input.json --verbose
```

---

## Command 3: calculate-convection

### Signature

```bash
calculate-convection [OPTIONS] [INPUT_FILE]

Options:
  -t, --type {flat_plate,pipe,cylinder,natural_convection}
                                   Geometry type (if not in input)
  -f, --format {json,yaml,table}   Output format (default: json)
  -o, --output FILE                Write to file instead of stdout
  --verbose / --quiet              Include/suppress dimensionless numbers
  -h, --help                       Show help and exit
```

### Input Format (Pipe Example)

**JSON**:
```json
{
  "geometry_type": "pipe_flow",
  "diameter": "0.05 m",
  "length": "10 m",
  "flow_velocity": "2.0 m/s",
  "fluid_properties": {
    "density": "983 kg/m**3",
    "dynamic_viscosity": "0.000467 Pa*s",
    "specific_heat": "4190 J/(kg*K)",
    "thermal_conductivity": "0.65 W/(m*K)"
  },
  "surface_temperature": "80 degC",
  "bulk_fluid_temperature": "60 degC"
}
```

### Output Format (Default: JSON)

```json
{
  "calculation_method": "Gnielinski_Turbulent_Pipe_v1",
  "source_reference": "Incropera_9e_p470",
  "confidence_tolerance": 5.0,
  "h": "11230.0 W/(m**2*K)",
  "Reynolds": 10950.0,
  "Prandtl": 7.20,
  "Nusselt": 85.4,
  "Grashof": null,
  "Rayleigh": null,
  "flow_regime": "turbulent",
  "correlation_equation": "Gnielinski (turbulent pipe)",
  "correlation_coefficients": {
    "f": 0.0289,
    "a": 0.0289,
    "b": 1.0,
    "c": 0.667
  },
  "is_within_correlation_range": true,
  "applicable_range": {
    "Reynolds": [4000, 1000000],
    "Prandtl": [0.5, 2000],
    "length_diameter_ratio": [10, 400]
  }
}
```

### Output Format (--format table)

```
Convection Heat Transfer Coefficient
═════════════════════════════════════════════════
Geometry:                pipe_flow (D=50 mm, L=10 m)
Fluid velocity:          2.0 m/s
Surface temperature:     80.0 °C
Bulk temperature:        60.0 °C
───────────────────────────────────────────────
Reynolds number (Re):    10950
Prandtl number (Pr):     7.20
Nusselt number (Nu):     85.4
───────────────────────────────────────────────
Convection coefficient h: 11230.0 W/(m²·K)
Flow regime:             turbulent
Correlation:             Gnielinski (turbulent pipe)
───────────────────────────────────────────────
✓ Parameters within correlation range
Confidence tolerance:    5.0%
Source: Incropera 9th edition, Page 470
```

### Examples

```bash
# From file with geometry type in JSON
calculate-convection pipe_input.json

# Alternative: specify geometry type via flag
calculate-convection -t pipe_flow --format table < stdin

# Verbose output (show dimensionless numbers)
calculate-convection cylinder.json --verbose

# Save results
calculate-convection flat_plate.yaml -o results.json
```

---

## Command 4: calculate-insulation

### Signature

```bash
calculate-insulation [OPTIONS] [INPUT_FILE]

Options:
  -f, --format {json,yaml,table}   Output format (default: json)
  -o, --output FILE                Write to file instead of stdout
  --sensitivity                    Include sensitivity analysis (±20% energy cost)
  --verbose / --quiet              Include/suppress optimization details
  -h, --help                       Show help and exit
```

### Input Format

**JSON**:
```json
{
  "pipe_diameter": "0.1 m",
  "pipe_length": "100 m",
  "T_surface_uninsulated": "150 degC",
  "T_ambient": "25 degC",
  "h_ambient": "25 W/(m**2*K)",
  "insulation_material": "mineral_wool",
  "thermal_conductivity_insulation": "0.04 W/(m*K)",
  "density_insulation": "100 kg/m**3",
  "energy_cost": "12 USD/GJ",
  "energy_annual_operating_hours": 8760,
  "insulation_cost_per_thickness": "50 USD/(m**2*m)",
  "analysis_period_years": 10,
  "insulation_thickness_min": "0.02 m",
  "insulation_thickness_max": "0.15 m"
}
```

### Output Format (Default: JSON)

```json
{
  "calculation_method": "Economic_Optimization_v1",
  "source_reference": "Engineering_Economics_Standard",
  "confidence_tolerance": 10.0,
  "optimal_insulation_thickness": "0.075 m",
  "optimization_mode": "economic_payback",
  "Q_uninsulated": "13500.0 W",
  "Q_insulated": "1200.0 W",
  "heat_loss_reduction_percent": 91.1,
  "annual_energy_savings": "105.2 MWh",
  "annual_cost_savings": 1262.40,
  "annual_insulation_cost": 237.50,
  "net_annual_savings": 1024.90,
  "payback_period_years": 2.9,
  "intermediate_values": {
    "insulation_area": 33.3,
    "insulation_capital_cost": 6973.5,
    "total_cost_function": [...],
    "optimization_method": "minimize(total_cost)"
  }
}
```

### Output Format (--format table)

```
Insulation Sizing & Economic Analysis
═════════════════════════════════════════════════════════════
Pipe Geometry:
  Diameter:              100.0 mm (OD, uninsulated)
  Length:                100.0 m
  Surface temperature:   150.0 °C (uninsulated)
  Ambient temperature:   25.0 °C
───────────────────────────────────────────────────────────────
Insulation Material:     mineral_wool
  Thermal conductivity:  0.04 W/(m·K)
  Density:               100 kg/m³
───────────────────────────────────────────────────────────────
OPTIMAL THICKNESS:       75 mm (0.075 m)

Heat Loss Reduction:
  Without insulation:    13500.0 W
  With insulation:       1200.0 W
  Reduction:             91.1%
───────────────────────────────────────────────────────────────
Economic Analysis (10-year period @ $12/GJ):
  Annual energy saved:   105.2 MWh
  Annual savings:        $1,262.40
  Annual insulation:     $237.50 (amortized)
  Net annual savings:    $1,024.90

  Payback period:        2.9 years
  Total savings (10yr):  $10,249 ✓
───────────────────────────────────────────────────────────────
Optimization mode:       economic_payback (cost minimization)
Confidence tolerance:    10.0%
```

### Examples

```bash
# From file
calculate-insulation insulation.json

# Table output for decision makers
calculate-insulation insulation.json --format table

# With sensitivity analysis (show ±20% variations)
calculate-insulation insulation.json --sensitivity --format table

# Batch for multiple pipe diameters
for dia in 50 100 150; do
  sed "s/DIAMETER/$dia/" template.json | calculate-insulation - -o "results_${dia}mm.json"
done
```

---

## Common Options & Behaviors

### Input File Handling

```bash
# From file (JSON or YAML auto-detected)
calculate-lmtd input.json        # JSON
calculate-lmtd input.yaml        # YAML

# From stdin
cat input.json | calculate-lmtd -

# Interactive (prompts for input)
calculate-lmtd --interactive

# If no file specified, defaults to stdin
calculate-lmtd < input.json
```

### Output Options

```bash
# To stdout (default)
calculate-lmtd input.json

# To file
calculate-lmtd input.json --output results.json

# Create parent directories if needed
calculate-lmtd input.json -o results/2025-12/case1.json

# Append to file (if --append flag supported)
calculate-lmtd input.json >> results.json
```

### Format Selection

```bash
# JSON (default, parseable by machines)
calculate-lmtd input.json --format json

# YAML (human-readable, also parseable)
calculate-lmtd input.json --format yaml

# Table (human-readable, NOT parseable, for reports/display)
calculate-lmtd input.json --format table
```

### Verbosity

```bash
# Default: show main results
calculate-lmtd input.json

# Verbose: include all intermediate calculations
calculate-lmtd input.json --verbose

# Quiet: show only status (exit code indicates success/failure)
calculate-lmtd input.json --quiet
```

---

## Error Handling

### Validation Errors (exit code 1)

```bash
$ calculate-lmtd bad_input.json
Error: Invalid input
  Field: hot_fluid.T_inlet
  Message: ensure this value is greater than 0
  Suggestion: Check that T_inlet is a valid temperature >= 0 K
```

### Calculation Errors (exit code 2)

```bash
$ calculate-lmtd problematic.json
Error: Calculation failed
  Message: LMTD approaches zero; temperatures too close
  Suggestion: Check that inlet/outlet temperatures have meaningful differences
```

### File I/O Errors (exit code 3)

```bash
$ calculate-lmtd nonexistent.json
Error: Cannot read file
  File: nonexistent.json
  Reason: No such file or directory
```

### Help & Version

```bash
$ calculate-lmtd --help
Usage: calculate-lmtd [OPTIONS] [INPUT_FILE]

Calculate LMTD heat transfer...
Options:
  -f, --format {json,yaml,table}
  -o, --output FILE
  -v, --verbose
  -h, --help

$ calculate-lmtd --version
heat-calc 1.0.0
```

---

## Streaming & Pipelines

All commands support Unix piping:

```bash
# Pipeline: LMTD → NTU verification
calculate-lmtd input.json | jq '.heat_transfer_rate' | ...

# Batch processing with jq
jq -r '.[] | @json' cases.jsonl | while read case; do
  echo "$case" | calculate-lmtd - --format json
done >> results.jsonl

# Extract specific fields
calculate-lmtd input.json --format json | jq '.heat_transfer_rate, .LMTD_effective'

# Validate all cases
for case in cases/*.json; do
  if ! calculate-lmtd "$case" --quiet > /dev/null; then
    echo "FAILED: $case"
  fi
done
```

---

## Environment Variables (Optional)

```bash
# Set default output format
export HEAT_CALC_FORMAT=table

# Suppress colors in output
export HEAT_CALC_NO_COLOR=1

# Verbose by default
export HEAT_CALC_VERBOSE=1
```

---

## Exit Codes Summary

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | Calculation completed; results valid |
| 1 | Input error | Validation failed on input data |
| 2 | Calculation error | Numerical method diverged |
| 3 | File I/O error | Cannot read/write file |
| 4 | Unknown error | Unexpected exception |

---

## Performance

CLI overhead is minimal; all timing is calculation time:

```bash
# Typical execution
$ time calculate-lmtd input.json > /dev/null
real    0m0.015s
user    0m0.008s
sys     0m0.004s

# Batch: 100 cases
$ time for i in {1..100}; do calculate-lmtd input.json > /dev/null; done
real    0m1.500s
user    0m0.800s
sys     0m0.400s
# Average: 15 ms per call ✓ (within SC-007 constraint)
```

