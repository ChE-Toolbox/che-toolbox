# CLI Examples: IAPWS-IF97 Steam Properties

**Command**: `steam-table`
**Version**: 1.0.0
**Date**: 2025-12-30

---

## Table of Contents
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Property Lookups](#property-lookups)
- [Saturation Properties](#saturation-properties)
- [Output Formats](#output-formats)
- [Batch Processing](#batch-processing)
- [Scripting Workflows](#scripting-workflows)
- [Error Handling](#error-handling)

---

## Installation

```bash
# Install from source
pip install -e .

# Or from PyPI (when published)
pip install iapws-if97
```

After installation, the `steam-table` command will be available in your PATH.

---

## Basic Usage

### Help and Version

```bash
# Show help
steam-table --help

# Show version
steam-table --version
```

### Quick Property Lookup

```bash
# Calculate enthalpy at 10 MPa, 500°C
steam-table property --pressure "10 MPa" --temperature "500 C" --property h

# Output:
# Enthalpy: 3373.7 kJ/kg
```

---

## Property Lookups

### Single Property

Calculate one property at specified P-T conditions:

```bash
# Enthalpy
steam-table property --pressure "10 MPa" --temperature "500 K" --property h

# Entropy
steam-table property --pressure "1 MPa" --temperature "400 K" --property s

# Internal energy
steam-table property --pressure "5 MPa" --temperature "600 K" --property u

# Density
steam-table property --pressure "10 MPa" --temperature "300 K" --property rho
```

### All Properties

Calculate all available properties:

```bash
steam-table property --pressure "10 MPa" --temperature "500 K" --property all

# Output:
# Pressure: 10.000 MPa
# Temperature: 500.000 K
# Enthalpy: 3373.7 kJ/kg
# Entropy: 6.5807 kJ/(kg·K)
# Internal energy: 3106.5 kJ/kg
# Density: 55.783 kg/m³
```

### Unit Flexibility

The CLI accepts various pressure and temperature units:

```bash
# Pressure: Pa, kPa, MPa, bar, atm, psi
steam-table property --pressure "100 bar" --temperature "500 K" --property h
steam-table property --pressure "1000 kPa" --temperature "500 K" --property h
steam-table property --pressure "145 psi" --temperature "500 K" --property h

# Temperature: K, C (Celsius), F (Fahrenheit)
steam-table property --pressure "10 MPa" --temperature "227 C" --property h
steam-table property --pressure "10 MPa" --temperature "500 K" --property h
```

---

## Saturation Properties

### Saturation Temperature at Given Pressure

```bash
steam-table saturation --pressure "1 MPa"

# Output:
# Saturation Properties at P = 1.000 MPa
# Temperature: 453.04 K (179.89°C)
# Enthalpy (liquid): 417.36 kJ/kg
# Enthalpy (vapor): 2675.5 kJ/kg
# Entropy (liquid): 1.3026 kJ/(kg·K)
# Entropy (vapor): 7.1270 kJ/(kg·K)
# Density (liquid): 887.2 kg/m³
# Density (vapor): 5.15 kg/m³
# Heat of vaporization: 2258.1 kJ/kg
```

### Saturation Pressure at Given Temperature

```bash
steam-table saturation --temperature "100 C"

# Output:
# Saturation Properties at T = 373.15 K (100.00°C)
# Pressure: 0.1013 MPa (1.013 bar)
# Enthalpy (liquid): 419.04 kJ/kg
# Enthalpy (vapor): 2676.0 kJ/kg
# ...
```

---

## Output Formats

### JSON Output

For scripting and automation:

```bash
steam-table property --pressure "10 MPa" --temperature "500 K" --property h --json

# Output:
# {
#   "pressure_Pa": 10000000.0,
#   "temperature_K": 500.0,
#   "enthalpy_kJ_per_kg": 3373.7
# }
```

### JSON for All Properties

```bash
steam-table property --pressure "10 MPa" --temperature "500 K" --property all --json

# Output:
# {
#   "pressure_Pa": 10000000.0,
#   "temperature_K": 500.0,
#   "enthalpy_kJ_per_kg": 3373.7,
#   "entropy_kJ_per_kg_K": 6.5807,
#   "internal_energy_kJ_per_kg": 3106.5,
#   "density_kg_per_m3": 55.783
# }
```

### JSON for Saturation

```bash
steam-table saturation --pressure "1 MPa" --json

# Output:
# {
#   "saturation_pressure_Pa": 1000000.0,
#   "saturation_temperature_K": 453.04,
#   "enthalpy_liquid_kJ_per_kg": 417.36,
#   "enthalpy_vapor_kJ_per_kg": 2675.5,
#   "entropy_liquid_kJ_per_kg_K": 1.3026,
#   "entropy_vapor_kJ_per_kg_K": 7.1270,
#   "density_liquid_kg_per_m3": 887.2,
#   "density_vapor_kg_per_m3": 5.15,
#   "heat_of_vaporization_kJ_per_kg": 2258.1
# }
```

---

## Batch Processing

### Process Multiple Conditions

Create input file with multiple P-T conditions:

**conditions.txt**:
```
10 MPa, 500 K
1 MPa, 400 K
0.1 MPa, 373 K
```

Process all conditions:

```bash
# Using batch subcommand
steam-table batch --input conditions.txt --output results.jsonl --property all

# Or process line by line
while IFS=',' read -r pressure temperature; do
  steam-table property --pressure "$pressure" --temperature "$temperature" --property all --json
done < conditions.txt > results.jsonl
```

### Example Batch Script

**batch_calculate.sh**:
```bash
#!/bin/bash

# Calculate enthalpy for multiple conditions
PRESSURES=("1 MPa" "5 MPa" "10 MPa")
TEMPERATURES=("300 K" "400 K" "500 K")

for P in "${PRESSURES[@]}"; do
  for T in "${TEMPERATURES[@]}"; do
    echo "Calculating: P=$P, T=$T"
    steam-table property --pressure "$P" --temperature "$T" --property h --json
  done
done
```

---

## Scripting Workflows

### Extract Specific Values with jq

```bash
# Get just the enthalpy value
steam-table property --pressure "10 MPa" --temperature "500 K" --property h --json | jq '.enthalpy_kJ_per_kg'

# Output: 3373.7
```

### Process Multiple Points and Plot

**generate_h_vs_t.sh**:
```bash
#!/bin/bash

# Generate enthalpy vs temperature data at constant pressure
P="10 MPa"

echo "Temperature_K,Enthalpy_kJ_kg" > data.csv

for T in $(seq 300 50 800); do
  H=$(steam-table property --pressure "$P" --temperature "${T} K" --property h --json | jq '.enthalpy_kJ_per_kg')
  echo "${T},${H}" >> data.csv
done

echo "Data saved to data.csv"
```

### Saturation Curve Generation

**saturation_curve.sh**:
```bash
#!/bin/bash

# Generate saturation curve data
echo "Pressure_MPa,T_sat_K,h_f_kJ_kg,h_g_kJ_kg" > saturation.csv

for P_MPa in $(seq 0.1 0.5 20); do
  DATA=$(steam-table saturation --pressure "${P_MPa} MPa" --json)
  T_sat=$(echo $DATA | jq '.saturation_temperature_K')
  h_f=$(echo $DATA | jq '.enthalpy_liquid_kJ_per_kg')
  h_g=$(echo $DATA | jq '.enthalpy_vapor_kJ_per_kg')

  echo "${P_MPa},${T_sat},${h_f},${h_g}" >> saturation.csv
done

echo "Saturation curve data saved"
```

---

## Error Handling

### Out of Range Errors

```bash
steam-table property --pressure "1000 MPa" --temperature "500 K" --property h

# Output (stderr):
# Error: Pressure 1.000000e+09 Pa outside valid range. Valid: 6.116570e+02–8.639100e+08 Pa
# Exit code: 1
```

### Invalid State Errors

```bash
# Attempting single-phase calculation on saturation line
steam-table property --pressure "1 MPa" --temperature "453 K" --property h

# Output (stderr):
# Error: Conditions on saturation line (two-phase region). Use 'steam-table saturation' for saturation properties.
# Exit code: 2
```

### Numerical Instability Errors

```bash
# Too close to critical point
steam-table property --pressure "22 MPa" --temperature "647 K" --property h

# Output (stderr):
# Error: Conditions too close to critical point for reliable computation. Distance: 1.2%. Suggestion: Move at least 5% away.
# Exit code: 3
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Input validation error (out of range) |
| 2 | Invalid state error (saturation line, two-phase) |
| 3 | Numerical instability error (convergence failure, singularity) |
| 4 | General error (unexpected exception) |

---

## Advanced Examples

### Thermodynamic Cycle Analysis

Calculate properties for a simple Rankine cycle:

**rankine_cycle.sh**:
```bash
#!/bin/bash

echo "=== Rankine Cycle Analysis ==="

# State 1: Boiler exit (high pressure, high temperature)
echo -e "\nState 1: Boiler Exit"
steam-table property --pressure "10 MPa" --temperature "500 C" --property all

# State 2: Turbine exit (low pressure, expanded)
echo -e "\nState 2: Turbine Exit"
steam-table property --pressure "0.01 MPa" --temperature "320 K" --property all

# State 3: Condenser (saturation at low pressure)
echo -e "\nState 3: Condenser (Saturation)"
steam-table saturation --pressure "0.01 MPa"

# State 4: Pump exit (high pressure, compressed liquid)
echo -e "\nState 4: Pump Exit"
steam-table property --pressure "10 MPa" --temperature "320 K" --property all
```

### Property Comparison

Compare properties at different regions:

**compare_regions.sh**:
```bash
#!/bin/bash

echo "Enthalpy comparison at same temperature (500 K):"

echo -n "Region 1 (high P): "
steam-table property --pressure "20 MPa" --temperature "500 K" --property h

echo -n "Region 2 (low P): "
steam-table property --pressure "0.1 MPa" --temperature "500 K" --property h

echo -n "Region 3 (supercritical): "
steam-table property --pressure "30 MPa" --temperature "700 K" --property h
```

---

## Tips and Best Practices

1. **Use JSON for scripting**: `--json` flag produces machine-readable output
2. **Quote units**: Always quote pressure/temperature strings with units
3. **Check exit codes**: Use `$?` in bash to detect errors
4. **Pipe to jq**: Extract specific values from JSON output
5. **Batch processing**: Use loops or batch subcommand for multiple calculations
6. **Error handling**: Wrap CLI calls in try-catch or check exit codes

---

## Troubleshooting

**Q: Command not found: steam-table**
A: Ensure installation completed successfully and the package is installed in your active Python environment.

**Q: Units not recognized**
A: Use standard abbreviations: `MPa`, `kPa`, `Pa`, `bar`, `atm` for pressure; `K`, `C`, `F` for temperature.

**Q: Slow performance**
A: First calculation may be slower due to imports. Subsequent calls are fast. For many calculations, use Python API instead.

**Q: JSON output formatting**
A: Pipe through `jq` for pretty-printing: `steam-table ... --json | jq`

---

## See Also

- [Python API Documentation](api_reference.md)
- [Validation Results](validation_results.md)
- [Quickstart Guide](../specs/002-steam-properties/quickstart.md)

---

## References

- IAPWS-IF97 Standard: http://www.iapws.org/
- CLI Implementation: `src/iapws_if97_cli/cli.py`
- Example Scripts: `examples/` directory

