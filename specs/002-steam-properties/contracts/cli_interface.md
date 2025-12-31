# CLI Interface Contract: IAPWS-IF97 Steam Properties

**Feature**: 002-steam-properties | **Date**: 2025-12-30 | **Version**: 1.0.0

Command-line interface specification for steam property calculations.

---

## Installation

```bash
pip install iapws-if97[cli]
```

Makes `steam-table` command available in PATH.

---

## Command Structure

```
steam-table [global-options] <subcommand> [subcommand-options]
```

### Global Options

- `--help`: Show help and exit
- `--version`: Show version and exit
- `--json`: Output in JSON format (default: human-readable)
- `--verbose`: Include additional diagnostic information

---

## Subcommands

### 1. Property Lookup (P-T Input)

#### Synopsis

```
steam-table property --pressure <value> --temperature <value> [--unit-p UNIT] [--unit-t UNIT] [--property PROP]
```

#### Arguments

- `--pressure`, `-p` (required): Pressure value (number)
- `--temperature`, `-t` (required): Temperature value (number)
- `--unit-p`: Pressure unit [Pa | MPa | bar | atm | psi] (default: Pa)
- `--unit-t`: Temperature unit [K | C | F] (default: K)
- `--property`: Property to retrieve [h | s | u | rho | all] (default: all)

#### Examples

```bash
# Enthalpy in Region 1
steam-table property --pressure 10 --unit-p MPa --temperature 500 --unit-t C --property h
# Output: Enthalpy: 3373.7 kJ/kg

# All properties in JSON
steam-table property --json --pressure 10 --unit-p MPa --temperature 500 --unit-t C
# Output:
# {
#   "input": {
#     "pressure_Pa": 10000000,
#     "temperature_K": 773.15
#   },
#   "properties": {
#     "enthalpy_kJ_per_kg": 3373.7,
#     "entropy_kJ_per_kg_K": 6.5807,
#     "density_kg_per_m3": 55.783,
#     "internal_energy_kJ_per_kg": 3106.5
#   },
#   "region": "REGION1",
#   "accuracy_percent": 0.03
# }

# Multiple units
steam-table property --pressure 0.1 --unit-p MPa --temperature 200 --unit-t C
```

#### Output (Human-Readable)

```
Pressure: 10.000 MPa (100.00 bar, 1450.4 psi)
Temperature: 500.000°C (773.15 K, 932.00°F)
Region: REGION1

Enthalpy: 3373.7 kJ/kg
Entropy: 6.5807 kJ/(kg·K)
Density: 55.783 kg/m³
Internal Energy: 3106.5 kJ/kg

Accuracy: ±0.03% (per IAPWS-IF97 Region 1 standard)
```

#### Error Handling

```bash
# Out of range
$ steam-table property --pressure 0.001 --unit-p MPa --temperature 500 --unit-t C
Error: Pressure out of range. Valid: 0.611657 Pa ≤ P ≤ 863.91 MPa. Got: 1000 Pa
Exit code: 1

# Near critical point
$ steam-table property --pressure 22.1 --unit-p MPa --temperature 374 --unit-t K
Error: Region 3 singularity near critical point (22.064 MPa, 373.946 K). Distance: 0.3%. Suggestion: P ≥ 22.6 MPa or T ≥ 382 K
Exit code: 2

# On saturation line (wrong API)
$ steam-table property --pressure 1 --unit-p MPa --temperature 453 --unit-t K
Error: Pressure 1 MPa, Temperature 453 K: On saturation line. Use 'steam-table saturation' instead.
Exit code: 3
```

---

### 2. Saturation Properties

#### Synopsis - Saturation at Pressure

```
steam-table saturation --pressure <value> [--unit-p UNIT]
```

#### Arguments

- `--pressure`, `-p` (required): Saturation pressure
- `--unit-p`: Pressure unit [Pa | MPa | bar | atm | psi] (default: Pa)

#### Example

```bash
steam-table saturation --pressure 1 --unit-p MPa
# Output:
# Saturation Pressure: 1.000 MPa (10.00 bar)
# Saturation Temperature: 453.04 K (179.89°C, 355.81°F)
#
# Saturated Liquid (subscript 'f'):
#   Enthalpy: 417.36 kJ/kg
#   Entropy: 1.3026 kJ/(kg·K)
#   Density: 887.2 kg/m³
#
# Saturated Vapor (subscript 'g'):
#   Enthalpy: 2675.5 kJ/kg
#   Entropy: 7.1270 kJ/(kg·K)
#   Density: 5.15 kg/m³
#
# Latent Heat (h_fg): 2258.1 kJ/kg
# Accuracy: ±0.1% (per IAPWS-IF97 saturation standard)
```

#### Synopsis - Saturation at Temperature

```
steam-table saturation --temperature <value> [--unit-t UNIT]
```

#### Arguments

- `--temperature`, `-t` (required): Saturation temperature
- `--unit-t`: Temperature unit [K | C | F] (default: K)

#### Example

```bash
steam-table saturation --temperature 100 --unit-t C
# Output: (same as above, but input is temperature instead)
```

#### JSON Output

```bash
steam-table --json saturation --pressure 1 --unit-p MPa
# Output:
# {
#   "input": {
#     "saturation_pressure_Pa": 1000000
#   },
#   "saturation": {
#     "temperature_K": 453.04,
#     "pressure_Pa": 1000000
#   },
#   "liquid": {
#     "enthalpy_kJ_per_kg": 417.36,
#     "entropy_kJ_per_kg_K": 1.3026,
#     "density_kg_per_m3": 887.2
#   },
#   "vapor": {
#     "enthalpy_kJ_per_kg": 2675.5,
#     "entropy_kJ_per_kg_K": 7.1270,
#     "density_kg_per_m3": 5.15
#   },
#   "latent_heat_kJ_per_kg": 2258.1,
#   "accuracy_percent": 0.1
# }
```

---

### 3. Batch Processing

#### Synopsis

```
steam-table batch --input <file> --output <file> [--format json|csv] [--property PROP]
```

#### Arguments

- `--input`, `-i`: Input file (CSV or JSON with P-T columns)
- `--output`, `-o`: Output file (writes results)
- `--format`: Input/output format [csv | json] (default: csv)
- `--property`: Properties to calculate [h | s | u | rho | all] (default: all)
- `--units`: Specify units for input [pressure_unit,temperature_unit] (default: Pa,K)

#### Input CSV Format

```csv
pressure_MPa,temperature_C,description
10,500,Boiler outlet
0.05,200,Turbine exit
0.01,,Condenser
```

#### Output CSV Format

```csv
pressure_MPa,temperature_C,description,enthalpy_kJ_per_kg,entropy_kJ_per_kg_K,density_kg_per_m3,region,error
10,500,Boiler outlet,3373.7,6.5807,55.783,REGION1,
0.05,200,Turbine exit,2870.5,7.5064,0.0339,REGION2,
0.01,,Condenser,2583.6,8.6379,0.0056,REGION2,
```

#### Example

```bash
# Process multiple conditions
steam-table batch --input conditions.csv --output results.csv --property all --units MPa,C
# Creates results.csv with properties for each condition

# JSON batch
steam-table --json batch --input conditions.json --output results.json
```

---

### 4. Information & Validation

#### List Valid Ranges

```bash
steam-table info ranges
# Output:
# IAPWS-IF97 Valid Ranges
#
# Global:
#   Pressure: 0.611657 Pa to 863.91 MPa
#   Temperature: 273.15 K to 863.15 K
#
# Region 1 (Compressed Liquid):
#   Pressure: 6.8 MPa to 863.91 MPa
#   Temperature: 273.15 K to 863.15 K
#   Accuracy: ±0.03%
#
# Region 2 (Superheated Steam):
#   Pressure: 0 to 100 MPa
#   Temperature: 273.15 K to 863.15 K
#   Accuracy: ±0.06%
#
# Region 3 (Supercritical):
#   Pressure: 16.6 MPa to 100 MPa
#   Temperature: 623.15 K to 863.15 K
#   Accuracy: ±0.2%
#   Warning: Singularity within 5% of critical point (22.064 MPa, 373.946 K)
#
# Saturation Line:
#   Pressure: 0.611657 Pa to 22.064 MPa
#   Temperature: 273.16 K to 647.096 K
#   Accuracy: ±0.1%
```

#### Critical Point Information

```bash
steam-table info critical-point
# Output:
# Critical Point (IAPWS-IF97):
#   Pressure: 22.064 MPa
#   Temperature: 373.946 K (100.801°C)
#   Density: 322 kg/m³
#   Note: Equations are singular at this point. Avoid calculations within 5% of CP.
```

#### Version & Status

```bash
steam-table info version
# Output: iapws-if97 1.0.0 (IAPWS-IF97 Standard Compliance)

steam-table info status
# Output:
# Library: IAPWS-IF97 Steam Properties
# Version: 1.0.0
# Standard: IAPWS-IF97 Release on the Functional Specifications of 1997
# Validation: 1300+ reference points from official IAPWS tables
# Test Coverage: 85% (pytest)
```

---

## Exit Codes

- `0`: Success
- `1`: Input validation error (InputRangeError)
- `2`: Numerical instability error (NumericalInstabilityError)
- `3`: Invalid state error (InvalidStateError)
- `4`: File not found or I/O error
- `5`: Invalid arguments or usage error
- `255`: Unexpected internal error

---

## Environment Variables

- `STEAM_TABLE_UNITS`: Default units for input [Pa|MPa|bar], [K|C|F] (format: "Pa,K")
- `STEAM_TABLE_FORMAT`: Default output format [human|json]
- `STEAM_TABLE_PRECISION`: Output decimal places for floats (default: 4)

#### Example

```bash
export STEAM_TABLE_UNITS="MPa,C"
export STEAM_TABLE_FORMAT="json"
steam-table property --pressure 10 --temperature 500
# Uses MPa and °C by default; outputs JSON
```

---

## Piping & Scripting

### Reading from stdin (when input not specified)

```bash
echo "10 500" | steam-table property --stdin --unit-p MPa --unit-t C
# Reads pressure and temperature from stdin (space-separated)
```

### Scripting Examples

```bash
# Loop through multiple conditions
for p in 1 5 10 20; do
  steam-table --json property --pressure $p --unit-p MPa --temperature 500 --unit-t C
done | jq '.properties.enthalpy_kJ_per_kg'

# Process file line by line
cat conditions.txt | while read p t; do
  steam-table property --pressure $p --temperature $t --unit-p MPa --unit-t C
done > results.txt
```

---

## Configuration Files

Optional `~/.steamrc` or `/etc/steam-table/config.ini`:

```ini
[units]
pressure = MPa
temperature = C

[output]
format = json
precision = 6

[performance]
# Cache size for repeated queries (optional, future feature)
cache_size = 1000
```

---

## Help System

```bash
steam-table --help
steam-table property --help
steam-table saturation --help
steam-table batch --help
steam-table info --help
```

---

## Backward Compatibility

**CLI Version**: 1.0.0

Core commands (property, saturation, info) are stable. New subcommands may be added in future versions without breaking existing scripts.

**Breaking changes** to existing command syntax will include a deprecation period.
