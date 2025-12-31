# Contributing to IAPWS-IF97 Steam Properties Library

Thank you for interest in contributing! This guide outlines expectations for code quality, testing, and commit conventions.

---

## Development Setup

```bash
git clone https://github.com/chemeng-toolbox/iapws-if97.git
cd iapws-if97
pip install -e ".[dev]"
```

**Python**: 3.11+ required  
**Dependencies**: NumPy 1.24+, SciPy 1.10+, Pint 0.23+, Pydantic 2.x

---

## Code Style

### Type Hints (Required)

All functions must have complete type hints. Target: `mypy --strict` passes with zero errors.

```python
# ✓ Good
def h_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
    """Calculate enthalpy at (P, T)."""
    ...

# ✗ Bad (missing return type)
def h_pt(self, pressure: Quantity, temperature: Quantity):
    ...
```

### NumPy-Style Docstrings

All public classes and methods must have docstrings with Parameters, Returns, Raises sections.

```python
def h_pt(self, pressure: Quantity, temperature: Quantity) -> Quantity:
    """Calculate enthalpy at given pressure and temperature.

    Parameters
    ----------
    pressure : Quantity
        Input pressure (any Pint-compatible unit).
    temperature : Quantity
        Input temperature (any Pint-compatible unit).

    Returns
    -------
    Quantity
        Enthalpy in kJ/kg (SI units).

    Raises
    ------
    InputRangeError
        If pressure or temperature outside valid range.
    NumericalInstabilityError
        If Region 3 and too close to critical point.
    """
```

### Formatting

Use Ruff for formatting and linting:

```bash
# Format all source code
ruff format src/ tests/

# Lint check
ruff check src/ tests/ --fix
```

### Import Organization

Ruff handles import sorting. No manual rearrangement needed.

---

## Testing Requirements

### Test Coverage

Minimum **80% coverage** across `src/iapws_if97/`. Exceptions:
- CLI formatters (coverage not critical)
- Example/demo code
- Dead code paths (defended by mypy)

Run tests with coverage:

```bash
pytest --cov=src/iapws_if97 --cov-report=html
```

### Test Structure

- **Unit tests**: `tests/unit/` - Individual functions and region equations
- **Validation tests**: `tests/validation/` - Against IAPWS-IF97 reference tables
- **Integration tests**: `tests/integration/` - End-to-end workflows

### Writing Tests

```python
import pytest
from iapws_if97 import SteamTable, InputRangeError, ureg

class TestH_pt:
    def setup_method(self):
        """Create fresh SteamTable for each test."""
        self.steam = SteamTable()

    def test_region1_basic(self):
        """Test Region 1 property calculation."""
        h = self.steam.h_pt(10 * ureg.MPa, 500 * ureg.K)
        assert h.magnitude == pytest.approx(3373.7, rel=0.001)  # ±0.1%

    def test_input_validation_pressure_low(self):
        """Test InputRangeError for pressure below minimum."""
        with pytest.raises(InputRangeError) as exc_info:
            self.steam.h_pt(0.001 * ureg.Pa, 500 * ureg.K)
        assert "Pressure" in str(exc_info.value)

    def test_singularity_detection(self):
        """Test NumericalInstabilityError near critical point."""
        with pytest.raises(NumericalInstabilityError):
            self.steam.h_pt(22.1 * ureg.MPa, 374 * ureg.K)
```

### Test Markers

Use pytest markers for test categorization:

```python
@pytest.mark.unit
def test_polynomial_evaluation():
    ...

@pytest.mark.integration
def test_full_pt_workflow():
    ...

@pytest.mark.validation
def test_region1_reference_points():
    ...

@pytest.mark.slow
def test_saturation_convergence():
    ...
```

Run tests by marker:

```bash
pytest -m validation  # Only validation tests
pytest -m "not slow"  # Skip slow tests
```

---

## Commit Messages

Follow [conventional commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature (Region 3 equations, etc)
- **fix**: Bug fix
- **test**: Test additions or fixes
- **docs**: Documentation updates
- **refactor**: Code reorganization
- **perf**: Performance improvements
- **chore**: Dependency updates, config changes

### Examples

```bash
# Good feature commit
git commit -m "feat(region3): implement cubic equation solver with convergence safeguards

- Add Newton-Raphson iteration for density calculation
- Set convergence tolerance to 1e-3 Pa
- Test against 200 IAPWS reference points
- Fixes #42"

# Good fix commit
git commit -m "fix(saturation): correct Wagner-Pruss coefficient sign

- Coefficient n3 had inverted sign, causing 0.1% error
- Verified against official IAPWS document
- Update validation tests"

# Good test commit
git commit -m "test(region1): add edge case tests for critical region boundary"
```

---

## Pull Request Process

1. **Create branch** from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```

2. **Implement changes** with tests and documentation

3. **Verify quality**:
   ```bash
   ruff format src/ tests/
   ruff check src/ tests/
   mypy --strict src/
   pytest --cov=src/iapws_if97
   ```

4. **Write clear PR description**:
   - Summary of changes
   - Why this change is needed
   - Test results (coverage %)
   - Any breaking changes

5. **Address review feedback** (no force-push on shared branches)

6. **Merge only when approved** and all checks pass

---

## Areas for Contribution

### High Priority

- Quality-based property lookups (P-h, T-s) → v2.0
- Derivative calculations (cp, cv, speed of sound)
- Transport properties (viscosity, thermal conductivity)
- Web calculator component (static Next.js interface)

### Medium Priority

- Vectorized NumPy operations for bulk calculations
- Performance optimization (Numba JIT compilation)
- Caching framework and utilities
- Additional language bindings (C API)

### Documentation

- Region equation derivations
- Numerical method explanations
- Engineering workflow examples
- Troubleshooting guide

---

## Code Review Checklist

Reviewers verify:

- [ ] Type hints complete (`mypy --strict` passes)
- [ ] Docstrings present (Parameters, Returns, Raises)
- [ ] Tests added for new functionality (unit + integration)
- [ ] Coverage maintained/improved (>80% target)
- [ ] Accuracy requirements met (±0.03-0.2% per region)
- [ ] Exception handling appropriate
- [ ] No breaking changes to public API
- [ ] Commit messages follow conventions

---

## Questions & Discussion

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use Discussions tab for architecture decisions
- **Email**: Contact core team at [info@example.com]

---

## License

By contributing, you agree that your contributions are licensed under the same MIT license as the project.

---

Thank you for making IAPWS-IF97 better! 🎉
