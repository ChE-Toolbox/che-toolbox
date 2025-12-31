# Chemical Engineering Thermodynamic Toolbox

A production-grade thermodynamic calculation toolkit featuring multiple equations of state (Peng-Robinson, Van der Waals, Ideal Gas) and vapor-liquid equilibrium flash calculations for pure components and multi-component mixtures.

## Features

### Equations of State
- **Peng-Robinson EOS:** Industry-standard cubic EOS with high accuracy for real gases
- **Van der Waals EOS:** Classic cubic EOS demonstrating non-ideal behavior
- **Ideal Gas Law:** Reference baseline for comparing real gas deviations

### Calculations
- **Compressibility Factor (Z):** Calculate real gas behavior across all three EOS models
- **Fugacity Coefficients:** Determine chemical potential for phase equilibrium (Peng-Robinson)
- **Vapor Pressure:** Calculate saturation pressure across subcritical range (Peng-Robinson)
- **PT Flash:** Vapor-liquid equilibrium calculations for binary mixtures using Rachford-Rice algorithm
- **Cross-Model Comparison:** Compare Z-factors across Ideal Gas, Van der Waals, and Peng-Robinson

### Validation & Tools
- **NIST Validation:** Verified against NIST WebBook data for 5 reference compounds
- **CLI Tools:** Command-line interfaces for all EOS models and flash calculations
- **Python API:** Flexible library for integration into larger applications
- **Mixture Support:** Multi-component systems with van der Waals mixing rules

## Quick Start

### Installation

```bash
# Install in development mode
pip install -e .
```

### Python API

#### Peng-Robinson EOS
```python
from src.compounds.database import CompoundDatabase
from src.eos.peng_robinson import PengRobinsonEOS

db = CompoundDatabase()
methane = db.get("methane")
eos = PengRobinsonEOS()

z = eos.calculate_z_factor(300.0, 5000000.0, methane)
phi = eos.calculate_fugacity_coefficient(300.0, 5000000.0, methane)
state = eos.calculate_state(300.0, 5000000.0, methane)

print(f"Z = {state.z_factor:.4f}")
print(f"φ = {phi:.4f}")
print(f"Phase = {state.phase}")
```

#### Van der Waals EOS
```python
from src.compounds.database import CompoundDatabase
from src.eos import VanDerWaalsEOS

db = CompoundDatabase()
methane = db.get("methane")
vdw = VanDerWaalsEOS()

# Calculate molar volume and Z-factor
v_molar = vdw.calculate_volume(methane.tc, methane.pc, 300.0, 50e6)
z_factor = VanDerWaalsEOS.calculate_Z(50e6, 300.0, v_molar)

print(f"Molar Volume = {v_molar:.6e} m³/mol")
print(f"Z factor (VDW) = {z_factor:.4f}")
```

#### Ideal Gas Law
```python
from src.eos import IdealGasEOS

ideal = IdealGasEOS()

# Calculate volume and Z-factor (Z is always 1.0)
volume = ideal.calculate_volume(n=1.0, temperature=300.0, pressure=101325.0)
z_factor = IdealGasEOS.calculate_Z(101325.0, 300.0, volume)

print(f"Volume = {volume:.6e} m³")
print(f"Z factor (Ideal) = {z_factor}")  # Always 1.0
```

#### Cross-Model Comparison
```python
from src.compounds.database import CompoundDatabase
from src.eos import compare_compressibility_factors

db = CompoundDatabase()
methane = db.get("methane")

# Compare all three models at same conditions
results = compare_compressibility_factors(methane, temperature=300.0, pressure=50e6)

print(f"Ideal Gas Z:     {results['ideal_Z']:.6f}")
print(f"Van der Waals Z: {results['vdw_Z']:.6f}")
print(f"Peng-Robinson Z: {results['pr_Z']:.6f}")
```

#### PT Flash Calculation
```python
import numpy as np
from src.compounds.database import CompoundDatabase
from src.eos import FlashPT

db = CompoundDatabase()
ethane = db.get("ethane")
propane = db.get("propane")

# Binary mixture: 60% ethane, 40% propane
flash = FlashPT()
result = flash.calculate(
    z=np.array([0.6, 0.4]),
    temperature=300.0,
    pressure=2e6,
    critical_temperatures=np.array([ethane.tc, propane.tc]),
    critical_pressures=np.array([ethane.pc, propane.pc]),
    acentric_factors=np.array([ethane.omega, propane.omega]),
)

print(f"Convergence: {result.convergence.value}")
print(f"Liquid Fraction: {result.L:.4f}")
print(f"Vapor Fraction: {result.V:.4f}")
print(f"Liquid Comp: {result.x}")
print(f"Vapor Comp: {result.y}")
```

### Command-Line Interface

#### Peng-Robinson EOS
```bash
# Calculate Z factor
pr-calc z-factor methane -T 300 -P 50

# Calculate fugacity
pr-calc fugacity ethane -T 350 -P 30

# Calculate vapor pressure
pr-calc vapor-pressure water -T 373.15

# Get complete state
pr-calc state methane -T 200 -P 50 -f json

# List available compounds
pr-calc list-compounds

# Run NIST validation
pr-calc validate methane
```

#### Van der Waals EOS
```bash
# Calculate molar volume
vdw-calc volume methane -T 300 -P 50

# Calculate Z-factor
vdw-calc z-factor ethane -T 350 -P 30

# Compare with other EOS models
vdw-calc compare methane -T 300 -P 50

# JSON output
vdw-calc volume propane -T 400 -P 15 -f json
```

#### Ideal Gas Law
```bash
# Calculate volume
ideal-calc volume -T 298.15 -P 1.01325

# Calculate Z-factor (always 1.0)
ideal-calc z-factor -T 300 -P 50

# Calculate state
ideal-calc state -T 300 -P 101.325 -n 2.0

# JSON output
ideal-calc volume -T 273.15 -P 1.01325 -f json
```

#### PT Flash Calculation
```bash
# Binary flash calculation
flash-calc calculate ethane propane -T 300 -P 20 --z1 0.6 --z2 0.4

# Flash with JSON output
flash-calc calculate methane propane -T 280 -P 30 --z1 0.55 --z2 0.45 -f json

# Validate flash calculations
flash-calc validate --test-case ethane-propane
flash-calc validate --test-case all
```

## Available Compounds

- Methane (CH₄)
- Ethane (C₂H₆)
- Propane (C₃H₈)
- n-Butane (C₄H₁₀)
- Water (H₂O)

## Documentation

- **[API Reference](docs/api_reference.md)** - Complete API documentation
- **[Theory](docs/theory.md)** - Mathematical foundations
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[CLI Interface](specs/001-peng-robinson/contracts/cli_interface.md)** - Command reference

## Accuracy

Validated against NIST WebBook:

| EOS Model | Property | Accuracy |
|-----------|----------|----------|
| Peng-Robinson | Z factor | ±5% |
| Peng-Robinson | Fugacity coefficient | ±10% |
| Peng-Robinson | Vapor pressure | ±5% |
| Van der Waals | Z factor | ±2% |
| PT Flash | Material balance | <1e-6 |
| PT Flash | Liquid/Vapor fractions | ±5% |

## Performance

- Z factor calculation: <1 ms
- Vapor pressure: <50 ms
- Full validation (250 points): ~100 ms per compound

## Testing

```bash
# Run all tests
pytest tests/

# Run specific category
pytest tests/unit/
pytest tests/integration/
pytest tests/validation/

# Coverage report
pytest --cov=src tests/
```

## Code Quality

```bash
# Lint
ruff check src/

# Type check
mypy --strict src/

# Format
ruff format src/
```

## License

MIT License - see LICENSE file

## Citation

```bibtex
@software{chemingtoolbox2025,
  title={Peng-Robinson EOS Thermodynamic Engine},
  author={ChE-Toolbox Contributors},
  year={2025},
  url={https://github.com/ChE-Toolbox/che-toolbox}
}
```

## Status

✅ Production-ready
✅ Validated against NIST
✅ Comprehensive test coverage (>80%)
✅ Full documentation

Last Updated: December 2025
