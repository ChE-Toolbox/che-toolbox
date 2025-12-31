# CLI Interface Contract

**Feature**: 001-peng-robinson
**Interface**: Command-Line Interface
**Date**: 2025-12-29

## Overview

This document defines the command-line interface for the Peng-Robinson EOS thermodynamic engine. The CLI follows UNIX text I/O conventions: arguments/stdin → stdout, errors → stderr, with support for both human-readable and JSON output formats.

---

## Command Structure

```bash
pr-calc <command> [options] [arguments]
```

### Global Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output-format` | `-f` | `{text,json}` | `text` | Output format (human-readable or JSON) |
| `--units-temp` | | `{K,degC,degF}` | `K` | Temperature unit for output |
| `--units-pressure` | | `{bar,Pa,kPa,MPa,psi,atm}` | `bar` | Pressure unit for output |
| `--verbose` | `-v` | flag | `False` | Enable verbose logging to stderr |
| `--version` | | flag | - | Show version and exit |
| `--help` | `-h` | flag | - | Show help message and exit |

---

## Commands

### 1. `z-factor` - Calculate Compressibility Factor

**Purpose**: Calculate Z factor for pure component or mixture

**Syntax**:
```bash
pr-calc z-factor <compound> --temperature <T> --pressure <P> [options]
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `compound` | str | Yes | Compound name (e.g., "methane") or path to mixture JSON |
| `--temperature`, `-T` | float | Yes | Temperature value |
| `--pressure`, `-P` | float | Yes | Pressure value |
| `--temp-unit` | str | No | Temperature unit (default: K) |
| `--pressure-unit` | str | No | Pressure unit (default: bar) |
| `--phase` | `{vapor,liquid,all}` | No | Phase to return (default: all) |

**Output** (text format):
```
Compound: methane
Temperature: 300.00 K
Pressure: 50.00 bar
Phase: supercritical
Z factor: 0.941
```

**Output** (JSON format):
```json
{
  "compound": "methane",
  "temperature": {"value": 300.0, "unit": "K"},
  "pressure": {"value": 50.0, "unit": "bar"},
  "phase": "supercritical",
  "z_factor": 0.941
}
```

**Examples**:
```bash
# Basic usage
pr-calc z-factor methane -T 300 -P 50

# With custom units
pr-calc z-factor water -T 100 --temp-unit degC -P 1 --pressure-unit atm

# JSON output
pr-calc z-factor methane -T 300 -P 50 --output-format json

# Two-phase region (returns both phases)
pr-calc z-factor methane -T 150 -P 10

# Specify phase
pr-calc z-factor methane -T 150 -P 10 --phase vapor
```

**Exit Codes**:
- `0`: Success
- `1`: Invalid arguments (negative T/P, unknown compound)
- `2`: Calculation failure (no positive roots)

---

### 2. `fugacity` - Calculate Fugacity Coefficient

**Purpose**: Calculate fugacity coefficient for pure component or mixture

**Syntax**:
```bash
pr-calc fugacity <compound> --temperature <T> --pressure <P> [options]
```

**Arguments**: Same as `z-factor` command

**Output** (text format):
```
Compound: methane
Temperature: 300.00 K
Pressure: 50.00 bar
Phase: supercritical
Fugacity coefficient: 0.892
Fugacity: 44.60 bar
```

**Output** (JSON format):
```json
{
  "compound": "methane",
  "temperature": {"value": 300.0, "unit": "K"},
  "pressure": {"value": 50.0, "unit": "bar"},
  "phase": "supercritical",
  "fugacity_coefficient": 0.892,
  "fugacity": {"value": 44.60, "unit": "bar"}
}
```

**Examples**:
```bash
pr-calc fugacity propane -T 350 -P 30
pr-calc fugacity water -T 400 -P 100 --output-format json
```

---

### 3. `vapor-pressure` - Calculate Vapor Pressure

**Purpose**: Calculate saturation pressure at given temperature

**Syntax**:
```bash
pr-calc vapor-pressure <compound> --temperature <T> [options]
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `compound` | str | Yes | Pure compound name |
| `--temperature`, `-T` | float | Yes | Temperature value |
| `--temp-unit` | str | No | Temperature unit (default: K) |

**Output** (text format):
```
Compound: water
Temperature: 373.15 K (100.00 °C)
Critical temperature: 647.10 K
Vapor pressure: 1.0133 bar (14.696 psi)
```

**Output** (JSON format):
```json
{
  "compound": "water",
  "temperature": {"value": 373.15, "unit": "K"},
  "critical_temperature": {"value": 647.10, "unit": "K"},
  "vapor_pressure": {"value": 1.0133, "unit": "bar"},
  "convergence": {
    "converged": true,
    "iterations": 8,
    "residual": 1.2e-8
  }
}
```

**Examples**:
```bash
# Basic usage
pr-calc vapor-pressure water -T 373.15

# Custom units
pr-calc vapor-pressure water -T 100 --temp-unit degC --units-pressure psi

# JSON output
pr-calc vapor-pressure methane -T 150 --output-format json
```

**Exit Codes**:
- `0`: Success
- `1`: Temperature ≥ Tc (supercritical)
- `3`: Convergence warning (returns best estimate with warning to stderr)

---

### 4. `state` - Calculate Complete State

**Purpose**: Calculate all properties (Z, fugacity, vapor pressure if applicable)

**Syntax**:
```bash
pr-calc state <compound> --temperature <T> --pressure <P> [options]
```

**Arguments**: Same as `z-factor` command

**Output** (text format):
```
Compound: methane
Temperature: 300.00 K
Pressure: 50.00 bar
Reduced T: 1.574
Reduced P: 1.087
Phase: supercritical

Properties:
  Z factor: 0.941
  Fugacity coefficient: 0.892
  Fugacity: 44.60 bar
```

**Output** (JSON format):
```json
{
  "compound": "methane",
  "temperature": {"value": 300.0, "unit": "K"},
  "pressure": {"value": 50.0, "unit": "bar"},
  "reduced_temperature": 1.574,
  "reduced_pressure": 1.087,
  "phase": "supercritical",
  "z_factor_vapor": 0.941,
  "fugacity_coef_vapor": 0.892,
  "fugacity_vapor": {"value": 44.60, "unit": "bar"}
}
```

**Examples**:
```bash
pr-calc state methane -T 200 -P 50
pr-calc state water -T 500 -P 100 --output-format json
```

---

### 5. `mixture` - Calculate Mixture Properties

**Purpose**: Calculate properties for multi-component mixture

**Syntax**:
```bash
pr-calc mixture <mixture_file> --temperature <T> --pressure <P> [options]
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `mixture_file` | path | Yes | Path to JSON file defining mixture |
| `--temperature`, `-T` | float | Yes | Temperature value |
| `--pressure`, `-P` | float | Yes | Pressure value |
| `--temp-unit` | str | No | Temperature unit (default: K) |
| `--pressure-unit` | str | No | Pressure unit (default: bar) |

**Mixture File Format** (JSON):
```json
{
  "name": "natural_gas",
  "components": [
    {"name": "methane", "mole_fraction": 0.85},
    {"name": "ethane", "mole_fraction": 0.10},
    {"name": "propane", "mole_fraction": 0.05}
  ],
  "binary_interaction_params": {
    "methane-ethane": 0.003,
    "methane-propane": 0.012,
    "ethane-propane": 0.006
  }
}
```

**Output** (text format):
```
Mixture: natural_gas
Components:
  methane    (85.0%)
  ethane     (10.0%)
  propane    (5.0%)

Temperature: 250.00 K
Pressure: 40.00 bar
Phase: vapor

Mixture Properties:
  Z factor: 0.873
  Fugacity coefficient: 0.824
```

**Output** (JSON format):
```json
{
  "mixture": "natural_gas",
  "components": [
    {"name": "methane", "mole_fraction": 0.85},
    {"name": "ethane", "mole_fraction": 0.10},
    {"name": "propane", "mole_fraction": 0.05}
  ],
  "temperature": {"value": 250.0, "unit": "K"},
  "pressure": {"value": 40.0, "unit": "bar"},
  "phase": "vapor",
  "z_factor": 0.873,
  "fugacity_coefficient": 0.824,
  "component_fugacities": [
    {"component": "methane", "fugacity_coef": 0.831, "fugacity": {"value": 28.25, "unit": "bar"}},
    {"component": "ethane", "fugacity_coef": 0.795, "fugacity": {"value": 3.18, "unit": "bar"}},
    {"component": "propane", "fugacity_coef": 0.742, "fugacity": {"value": 1.48, "unit": "bar"}}
  ]
}
```

**Examples**:
```bash
pr-calc mixture natural_gas.json -T 250 -P 40
pr-calc mixture my_mixture.json -T 300 -P 50 --output-format json
```

---

### 6. `validate` - Run NIST Validation Tests

**Purpose**: Validate implementation against NIST reference data

**Syntax**:
```bash
pr-calc validate [compound] [options]
```

**Arguments**:

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `compound` | str | No | Specific compound to validate (default: all) |
| `--property` | `{z-factor,fugacity,vapor-pressure,all}` | No | Property to validate (default: all) |
| `--report` | path | No | Path to save detailed validation report |

**Output** (text format):
```
NIST Validation Results
========================

Compound: methane
  Z factor:         245 / 250 tests passed (98.0%)
  Fugacity:         228 / 250 tests passed (91.2%)
  Vapor pressure:   19 / 20 tests passed (95.0%)

Overall: 492 / 520 tests passed (94.6%)
```

**Output** (JSON format):
```json
{
  "validation_results": {
    "methane": {
      "z_factor": {"passed": 245, "total": 250, "pass_rate": 0.980},
      "fugacity": {"passed": 228, "total": 250, "pass_rate": 0.912},
      "vapor_pressure": {"passed": 19, "total": 20, "pass_rate": 0.950}
    },
    "overall": {"passed": 492, "total": 520, "pass_rate": 0.946}
  }
}
```

**Examples**:
```bash
# Validate all compounds
pr-calc validate

# Validate specific compound
pr-calc validate methane

# Validate specific property
pr-calc validate --property z-factor

# Generate detailed report
pr-calc validate --report validation_report.json
```

**Exit Codes**:
- `0`: All tests passed
- `4`: Some tests failed (non-zero exit for CI/CD)

---

### 7. `list-compounds` - List Available Compounds

**Purpose**: Show all compounds in database

**Syntax**:
```bash
pr-calc list-compounds [options]
```

**Output** (text format):
```
Available Compounds
===================

ethane        (C2H6)   Tc=305.32 K   Pc=48.72 bar   ω=0.099
methane       (CH4)    Tc=190.56 K   Pc=45.99 bar   ω=0.011
n-butane      (C4H10)  Tc=425.12 K   Pc=37.96 bar   ω=0.200
propane       (C3H8)   Tc=369.83 K   Pc=42.48 bar   ω=0.152
water         (H2O)    Tc=647.10 K   Pc=220.64 bar  ω=0.345
```

**Output** (JSON format):
```json
{
  "compounds": [
    {
      "name": "ethane",
      "formula": "C2H6",
      "critical_temperature": {"value": 305.32, "unit": "K"},
      "critical_pressure": {"value": 48.72, "unit": "bar"},
      "acentric_factor": 0.099
    }
  ]
}
```

**Examples**:
```bash
pr-calc list-compounds
pr-calc list-compounds --output-format json
```

---

## Standard Input/Output

### Batch Processing via stdin

Commands can read input from stdin for batch processing:

```bash
# Input file: batch_calculations.txt
methane 300 50
ethane 350 30
propane 400 20

# Process batch
cat batch_calculations.txt | pr-calc z-factor --batch --output-format json
```

**Batch Output** (JSON):
```json
[
  {"compound": "methane", "temperature": 300, "pressure": 50, "z_factor": 0.941},
  {"compound": "ethane", "temperature": 350, "pressure": 30, "z_factor": 0.887},
  {"compound": "propane", "temperature": 400, "pressure": 20, "z_factor": 0.913}
]
```

---

## Error Handling

### Error Messages (stderr)

All errors written to stderr with descriptive messages:

```bash
$ pr-calc z-factor methane -T -10 -P 50
Error: Temperature must be positive, got T=-10.0 K
```

```bash
$ pr-calc vapor-pressure water -T 700
Error: Temperature 700.0 K exceeds critical temperature 647.1 K
```

```bash
$ pr-calc z-factor benzene -T 300 -P 50
Error: Compound 'benzene' not found in database
Available compounds: ethane, methane, n-butane, propane, water
```

### Warnings (stderr)

Non-fatal warnings written to stderr:

```bash
$ pr-calc vapor-pressure water -T 646
Warning: Temperature 646.0 K is very close to critical temperature 647.1 K
Warning: Vapor pressure iteration did not converge after 100 iterations
Best estimate: P = 219.5 bar (residual = 2.3e-4)
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PR_CALC_DATA_PATH` | `./data` | Path to compound database directory |
| `PR_CALC_SOLVER` | `hybrid` | Default solver method (numpy/analytical/hybrid) |
| `PR_CALC_MAX_ITER` | `100` | Default max iterations for vapor pressure |
| `PR_CALC_TOLERANCE` | `1e-6` | Default convergence tolerance |

**Example**:
```bash
export PR_CALC_DATA_PATH=/opt/chemeng/data
export PR_CALC_SOLVER=numpy
pr-calc z-factor methane -T 300 -P 50
```

---

## Exit Codes Summary

| Code | Meaning | Example |
|------|---------|---------|
| `0` | Success | Calculation completed successfully |
| `1` | Invalid input | Negative T/P, unknown compound, invalid composition |
| `2` | Calculation failure | No positive roots, numerical instability |
| `3` | Convergence warning | Vapor pressure did not converge (returns best estimate) |
| `4` | Validation failure | NIST validation tests failed |
| `5` | File not found | Mixture file or data file missing |

---

## Examples: Common Workflows

### 1. Quick Property Lookup

```bash
# What's the Z factor for methane at reservoir conditions?
pr-calc z-factor methane -T 350 -P 200

# Convert output units
pr-calc z-factor methane -T 177 --temp-unit degF -P 2900 --pressure-unit psi
```

### 2. Vapor Pressure Table Generation

```bash
# Generate vapor pressure table for water
for T in 300 320 340 360 380; do
  pr-calc vapor-pressure water -T $T --output-format json
done | jq -s '.'
```

### 3. Mixture Composition Sweep

```bash
# Create mixture file programmatically
cat > mixture.json <<EOF
{
  "components": [
    {"name": "methane", "mole_fraction": 0.7},
    {"name": "ethane", "mole_fraction": 0.3}
  ]
}
EOF

# Calculate properties
pr-calc mixture mixture.json -T 250 -P 40
```

### 4. Validation for CI/CD

```bash
# Run validation in CI pipeline
pr-calc validate --output-format json > validation_results.json

# Check exit code
if [ $? -eq 0 ]; then
  echo "Validation passed"
else
  echo "Validation failed"
  exit 1
fi
```

---

## Shell Completion

Install shell completion for bash/zsh:

```bash
# Bash
pr-calc --install-completion bash
source ~/.bashrc

# Zsh
pr-calc --install-completion zsh
source ~/.zshrc

# Enable tab completion
pr-calc z-factor <TAB>  # Shows: methane, ethane, propane, n-butane, water
```

---

## Performance

Typical execution times on modern hardware:

| Command | Typical Time | Notes |
|---------|--------------|-------|
| `z-factor` | <10 ms | Single calculation |
| `fugacity` | <15 ms | Includes Z factor + integration |
| `vapor-pressure` | <100 ms | Iterative, temperature-dependent |
| `state` | <20 ms | Excludes vapor pressure |
| `validate` (all) | <30 s | ~740 test cases across 5 compounds |

---

## Version Information

Display version and build information:

```bash
$ pr-calc --version
pr-calc 0.1.0
Python: 3.11.5
NumPy: 1.24.3
SciPy: 1.10.1
Pint: 0.23
Pydantic: 2.5.0
```

---

## Integration with Other Tools

### Use with jq (JSON processing)

```bash
# Extract specific field
pr-calc z-factor methane -T 300 -P 50 -f json | jq '.z_factor'

# Process batch results
cat batch.txt | pr-calc z-factor --batch -f json | jq 'map(.z_factor) | add / length'
```

### Use with gnuplot (plotting)

```bash
# Generate data for plotting
for P in 10 20 30 40 50; do
  Z=$(pr-calc z-factor methane -T 300 -P $P -f json | jq '.z_factor')
  echo "$P $Z"
done | gnuplot -p -e 'plot "-" using 1:2 with lines'
```

### Use in shell scripts

```bash
#!/bin/bash
# Calculate deviation from ideal gas

T=300
P=50
compound="methane"

Z=$(pr-calc z-factor $compound -T $T -P $P -f json | jq '.z_factor')
deviation=$(echo "scale=3; ($Z - 1.0) * 100" | bc)

echo "Deviation from ideal gas: ${deviation}%"
```
