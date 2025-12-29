# Contributing to ChemEng Toolbox

Thank you for your interest in contributing to ChemEng Toolbox! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- GitHub account

### Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/che-toolbox.git
cd che-toolbox

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install development dependencies
pip install -e "packages/core[dev]"

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests to verify setup
pytest packages/
```

## Constitution and Principles

All contributions must comply with the [ChemEng Toolbox Constitution](.specify/memory/constitution.md). Key principles:

### I. Library-First Architecture
- Every feature starts as a standalone library
- Self-contained, independently testable
- Clear purpose required

### II. Multi-Interface Design
- Expose functionality via Python API, CLI, and web interface
- Follow text I/O protocol for CLI tools

### III. Validation-First Development (NON-NEGOTIABLE)
- All calculations MUST be validated against authoritative sources
- Minimum 80% test coverage
- 100% type coverage (pyright --strict)
- Red-Green-Refactor workflow required

### IV. Public Domain Data Only
- Only use NIST, CoolProp, IAPWS-IF97, PubChem, or JANAF Tables
- NO proprietary databases (DIPPR, Aspen, etc.)
- Document all data sources

### V. Cost-Free Operation
- Must stay within free tier limits
- Zero monthly cost target

## Types of Contributions

### Good First Issues

Perfect for newcomers:
- Add chemical compound to database
- Fix typos in documentation
- Add examples to calculators
- Improve error messages

### Medium Complexity

Requires some domain knowledge:
- Implement new correlation
- Add validation tests
- Create web calculator UI
- Write tutorials

### Advanced

Requires deep expertise:
- New module implementation
- Performance optimization
- Complex algorithm implementation

## Contribution Workflow

### 1. Find or Create an Issue

- Check existing issues first
- For new features, create an issue for discussion
- Wait for maintainer approval before starting work

### 2. Create a Branch

```bash
# For features
git checkout -b feature/short-description

# For bug fixes
git checkout -b fix/issue-number-description

# For documentation
git checkout -b docs/description
```

### 3. Make Changes

Follow the coding standards:

```python
from typing import NamedTuple
from pydantic import BaseModel, Field


class EOSResult(NamedTuple):
    """Result from equation of state calculation.

    Attributes:
        Z: Compressibility factor (dimensionless)
        fugacity: Fugacity coefficient (dimensionless)
    """
    Z: float
    fugacity: float


class PengRobinson:
    """Peng-Robinson equation of state (1976).

    Reference:
        Peng, D.-Y., Robinson, D.B. (1976).
        Ind. Eng. Chem. Fundam. 15(1), 59-64.
        DOI: 10.1021/i160057a011
    """

    def __init__(self, compound: str) -> None:
        """Initialize Peng-Robinson EOS for a compound.

        Args:
            compound: Compound name or CAS number

        Raises:
            ValueError: If compound not found in database
        """
        pass
```

### 4. Write Tests

**Unit Tests** (required):
```python
import pytest
from chemeng.thermo import PengRobinson


def test_peng_robinson_initialization():
    """Test PR EOS initialization."""
    pr = PengRobinson("methane")
    assert pr.compound == "methane"


def test_invalid_compound():
    """Test error handling for invalid compound."""
    with pytest.raises(ValueError, match="Unknown compound"):
        PengRobinson("invalid-compound-xyz")
```

**Validation Tests** (required for calculations):
```python
@pytest.mark.parametrize("T,P,Z_expected,source", [
    (190.564, 4.5992e6, 0.286, "SVA Table B.1"),
    (200, 1e6, 0.968, "NIST WebBook"),
])
def test_compressibility_validation(T, P, Z_expected, source):
    """Validate against literature values."""
    pr = PengRobinson("methane")
    Z = pr.calculate(T=T, P=P).Z
    assert abs(Z - Z_expected) / Z_expected < 0.005, f"Source: {source}"
```

### 5. Add Documentation

- Docstrings for all public functions/classes (NumPy style)
- Type hints for all parameters and returns
- Examples in docstrings
- Update relevant markdown docs

### 6. Run Quality Checks

```bash
# Format code
ruff format .

# Lint
ruff check .

# Type check
pyright packages/core/

# Run tests
pytest packages/ -v

# Check coverage
pytest packages/ --cov=packages --cov-report=term-missing
```

### 7. Commit Changes

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <description>

git commit -m "feat(thermo): add SRK equation of state"
git commit -m "fix(fluids): correct Reynolds number calculation"
git commit -m "docs: update installation guide"
git commit -m "test: add validation for methanol properties"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance tasks

### 8. Push and Create Pull Request

```bash
git push origin your-branch-name
gh pr create --fill
```

## Pull Request Guidelines

### PR Checklist

- [ ] Code follows constitution principles
- [ ] All tests pass (`pytest packages/ -v`)
- [ ] Type checking passes (`pyright packages/core/`)
- [ ] Linting passes (`ruff check .`)
- [ ] Code coverage >80% for new code
- [ ] Validation tests included (for calculations)
- [ ] Documentation updated
- [ ] Commit messages follow conventional format
- [ ] PR description explains changes clearly

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Constitution Compliance
- [ ] I. Library-First: Code is in standalone library
- [ ] II. Multi-Interface: Exposed via Python API (+ CLI/web if applicable)
- [ ] III. Validation-First: Validated against literature (source cited)
- [ ] IV. Public Domain Data: All data is openly licensed
- [ ] V. Cost-Free: No paid services introduced
- [ ] VII. Simplicity: No over-engineering, YAGNI applied

## Testing
- Unit tests: Yes/No
- Validation tests: Yes/No (with source citation)
- Coverage: X%

## References
- Literature source 1
- Literature source 2
```

## Adding Chemical Compounds

### Data Requirements

1. **Source**: Must be public domain (NIST, CoolProp, IAPWS, PubChem)
2. **Properties**: Minimum required:
   - CAS number
   - Molecular weight
   - Critical temperature
   - Critical pressure
   - Acentric factor
3. **Validation**: Include test comparing to source data

### Example Contribution

```json
{
  "cas": "67-64-1",
  "name": "Acetone",
  "formula": "C3H6O",
  "molecular_weight": 58.080,
  "critical_temperature": 508.1,
  "critical_pressure": 4.70e6,
  "acentric_factor": 0.309,
  "source": "NIST WebBook",
  "source_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C67641",
  "contributor": "github.com/username",
  "date_added": "2025-12-29"
}
```

## Adding Calculations/Correlations

### Requirements

1. **Literature Reference**: Published paper, textbook, or standard
2. **Validation Data**: Example values from literature
3. **Documentation**: Clear docstrings with assumptions and limitations
4. **Tests**: Both unit tests and validation tests

### Example

```python
def darcy_friction_factor(Re: float, roughness: float, diameter: float) -> float:
    """Calculate Darcy friction factor using Colebrook equation.

    Valid for turbulent flow (Re > 4000) in circular pipes.

    Args:
        Re: Reynolds number (dimensionless), must be > 4000
        roughness: Absolute pipe roughness (m)
        diameter: Pipe diameter (m)

    Returns:
        Darcy friction factor (dimensionless)

    Raises:
        ValueError: If Re <= 4000 or inputs are negative

    References:
        Colebrook, C.F. (1939). J. Inst. Civil Engineers, 11(4), 133-156.

    Examples:
        >>> f = darcy_friction_factor(Re=1e5, roughness=0.000045, diameter=0.1)
        >>> print(f"{f:.5f}")
        0.01809
    """
    # Implementation here
```

## Review Process

1. Maintainer reviews PR (best-effort basis)
2. Automated checks must pass (tests, type check, lint)
3. If changes requested, update PR
4. Once approved, maintainer merges

**Response Time**: Best effort (this is a personal project)

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/ChE-Toolbox/che-toolbox/discussions)
- **Bugs**: Open an [Issue](https://github.com/ChE-Toolbox/che-toolbox/issues)
- **Documentation**: Check [docs/](./docs/)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes
- Special mentions for significant contributions

Thank you for contributing to ChemEng Toolbox!
