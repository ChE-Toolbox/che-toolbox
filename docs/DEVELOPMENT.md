# Development Guide

## Setup

### Prerequisites

- Python 3.11 or higher
- pip or pip3
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/anthropics/che-toolbox.git
cd che-toolbox/heat
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Development Workflow

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run specific test category:
```bash
pytest tests/unit/          # Unit tests
pytest tests/validation/    # Validation tests
```

Run with coverage:
```bash
pytest tests/ --cov=src/heat_calc --cov-report=html
```

### Type Checking

Run mypy with strict mode:
```bash
mypy src/heat_calc --strict
```

### Code Formatting

Format code:
```bash
black src/ tests/
isort src/ tests/
```

Check formatting:
```bash
black --check src/ tests/
isort --check src/ tests/
flake8 src/ tests/
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pre-commit install
```

Run hooks on all files:
```bash
pre-commit run --all-files
```

## Project Structure

```
heat/
├── src/heat_calc/           # Main library code
│   ├── models/              # Pydantic data models
│   ├── cli/                 # CLI interface
│   ├── utils/               # Utilities and constants
│   ├── lmtd.py              # LMTD calculations
│   ├── ntu.py               # NTU calculations
│   ├── convection.py        # Convection calculations
│   └── insulation.py        # Insulation calculations
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   └── validation/          # Validation tests
├── data/                    # Data files
│   └── reference_test_cases.json  # Validation reference data
├── docs/                    # Documentation
└── specs/                   # Feature specifications
```

## Adding New Features

1. **Write the specification**: Create a user story in `specs/002-heat-exchanger-calc/spec.md`

2. **Write tests first** (TDD):
   - Unit tests in `tests/unit/`
   - Validation tests in `tests/validation/`

3. **Implement the feature**:
   - Create Pydantic models in `src/heat_calc/models/`
   - Implement calculation logic
   - Add CLI command if needed

4. **Validate**:
   - All tests pass
   - Type checking passes (mypy --strict)
   - Code formatting passes
   - Documentation updated

## Code Style

- **Line Length**: 120 characters
- **Type Hints**: Required on all functions (100% coverage)
- **Docstrings**: NumPy format
- **Imports**: isort with black compatibility
- **Linting**: flake8 with custom config

### Example Function

```python
def calculate_something(input_data: InputModel) -> ResultModel:
    """Calculate something using the method.

    Parameters
    ----------
    input_data : InputModel
        Input specification with units validated by Pint.

    Returns
    -------
    ResultModel
        Results including primary value, intermediates, and metadata.

    Raises
    ------
    ValidationError
        If input violates constraints.
    ValueError
        If calculation fails.

    Examples
    --------
    >>> from heat_calc.models import InputModel
    >>> result = calculate_something(InputModel(...))
    >>> print(result.primary_value)
    """
    # Implementation
    pass
```

## Testing Strategy

### Unit Tests (80% of effort)
- Test individual functions in isolation
- Mock external dependencies
- Fast execution (<1s per test file)

### Validation Tests (15% of effort)
- Compare against literature examples
- Use realistic parameter ranges
- Document source (book, paper, standard)

### Integration Tests (5% of effort)
- Test complete workflows
- Verify unit conversions
- Test error handling across interfaces

## Validation Sources

All calculations are validated against:
- **Incropera**: "Fundamentals of Heat and Mass Transfer" (9th edition)
- **NIST**: NIST WebBook and reference databases
- **Perry's**: Chemical Engineers' Handbook
- **GPSA**: Gas Processors Suppliers Association Engineering Data Book

Document the validation source in test comments:
```python
def test_lmtd_counterflow_incropera():
    """Test LMTD counterflow against Incropera Example 10.1 (p. 452)."""
    # Test implementation
```

## Performance Guidelines

- All calculations must complete within 100ms
- Target: Most calculations complete in <10ms
- Profile with: `pytest tests/ --benchmark`

## Documentation

- Update README.md for user-facing changes
- Update docs/API.md with new functions
- Update specs/ for design decisions
- Add docstrings to all public functions

## Release Process

1. Update version in `src/heat_calc/__init__.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.0.0`
4. Push: `git push origin main --tags`

## Troubleshooting

### mypy errors with Pint

Add to mypy.ini:
```ini
[mypy-pint.*]
ignore_missing_imports = False
```

### SciPy import errors

Ensure scipy>=1.10.0 is installed:
```bash
pip install --upgrade scipy
```

### Test discovery issues

Ensure test files are named `test_*.py` and are in the `tests/` directory.

## Getting Help

- Check existing documentation in `specs/`
- Review test examples in `tests/`
- See quickstart guide in `specs/002-heat-exchanger-calc/quickstart.md`
