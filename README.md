# Peng-Robinson EOS Thermodynamic Engine

A production-grade implementation of the Peng-Robinson equation of state for calculating thermodynamic properties of pure components and multi-component mixtures.

## Features

- **Compressibility Factor (Z):** Calculate real gas behavior with high accuracy
- **Fugacity Coefficients:** Determine chemical potential for phase equilibrium calculations
- **Vapor Pressure:** Calculate saturation pressure across the entire subcritical range
- **Mixture Support:** Handle multi-component systems with van der Waals mixing rules
- **NIST Validation:** Verified against NIST WebBook data for 5 reference compounds
- **CLI Tool:** Command-line interface for quick calculations
- **Python API:** Flexible library for integration into larger applications

## Quick Start

### Installation

```bash
# Install in development mode
pip install -e .
```

### Python API

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

### Command-Line Interface

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

| Property | Accuracy |
|----------|----------|
| Z factor | ±5% |
| Fugacity coefficient | ±10% |
| Vapor pressure | ±5% |

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
