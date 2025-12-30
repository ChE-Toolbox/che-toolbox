# data-setup Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-29

## Active Technologies
- Python 3.11+ + NumPy 1.24+ (polynomial roots), SciPy 1.10+ (Brent's method optimization), Pint 0.23+ (unit handling), Pydantic 2.x (data validation) (001-peng-robinson)
- JSON files for compound database (critical properties: Tc, Pc, acentric factor); NIST reference data for validation (001-peng-robinson)

- Python 3.11+ + CoolProp 7.x, Pint 0.23+, Pydantic 2.x, NumPy 1.24+ (001-data-foundations)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 001-peng-robinson: Added Python 3.11+ + NumPy 1.24+ (polynomial roots), SciPy 1.10+ (Brent's method optimization), Pint 0.23+ (unit handling), Pydantic 2.x (data validation)

- 001-data-foundations: Added Python 3.11+ + CoolProp 7.x, Pint 0.23+, Pydantic 2.x, NumPy 1.24+

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
