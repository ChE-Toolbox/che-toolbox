# Changelog

All notable changes to the Chemical Engineering Thermodynamic Toolbox will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - IAPWS-IF97 Steam Properties (Feature 002-steam-properties)

#### Core Library Features

- ✅ **SteamTable Class**: Main Python API for thermodynamic calculations
  - `h_pt(P, T)`: Enthalpy at (P, T)
  - `s_pt(P, T)`: Entropy at (P, T)
  - `u_pt(P, T)`: Internal energy at (P, T)
  - `rho_pt(P, T)`: Density at (P, T)
  - `T_sat(P)`: Saturation temperature and properties from pressure
  - `P_sat(T)`: Saturation pressure and properties from temperature

- ✅ **IAPWS-IF97 Equations**: All three single-phase regions
  - **Region 1** (Compressed liquid): 6.8–863.91 MPa, 273.15–863.15 K, ±0.03% accuracy
  - **Region 2** (Superheated steam): 0–100 MPa, 273.15–863.15 K, ±0.06% accuracy
  - **Region 3** (Supercritical): 16.6–100 MPa, 623.15–863.15 K, ±0.2% accuracy
  - **Saturation line**: 0.611657–22.064 MPa, 273.16–647.096 K, ±0.1% accuracy

- ✅ **Unit Handling**: Pint Quantity objects
  - Accept any Pint-compatible unit (Pa, MPa, bar, K, °C, °F)
  - Return SI units (Pa, K, kJ/kg, kJ/(kg·K), kg/m³)
  - Prevent unit conversion errors

- ✅ **CLI Interface**: steam-table command for property lookups from shell

#### Testing & Validation

- ✅ **Validation Suite**: 1300+ IAPWS-IF97 reference points
  - Region 1: ~400 test points, ±0.03% accuracy verified
  - Region 2: ~400 test points, ±0.06% accuracy verified
  - Region 3: ~200 test points, ±0.2% accuracy verified
  - Saturation: ~300 test points, ±0.1% accuracy verified

### Added - Thermodynamic Extension (Feature 002)

#### Van der Waals Equation of State
- **Core Implementation**: `src/eos/van_der_waals.py`
  - `VanDerWaalsEOS` class with cubic equation solver
  - `calculate_a()` and `calculate_b()` static methods for VDW parameters
  - `calculate_volume()` method for molar volume calculation
  - `calculate_Z()` static method for compressibility factor
  - Full input validation for temperature, pressure, and critical properties

- **Unit Tests**: `tests/unit/test_van_der_waals.py`
  - Parameter calculation tests
  - Volume calculation tests
  - Z-factor calculation tests
  - Input validation tests
  - Test fixtures for methane, ethane, propane

- **NIST Validation**: `tests/validation/test_vdw_nist_validation.py`
  - Validation against NIST reference data for 5 compounds
  - ±2% tolerance for Z-factor accuracy
  - Parametrized tests across multiple conditions

- **CLI Tool**: `src/cli/vdw_calc.py`
  - `vdw-calc volume` - Calculate molar volume
  - `vdw-calc z-factor` - Calculate compressibility factor
  - `vdw-calc compare` - Cross-model EOS comparison
  - `vdw-calc list-compounds` - List available compounds
  - Text and JSON output formats

#### Ideal Gas Law
- **Core Implementation**: `src/eos/ideal_gas.py`
  - `IdealGasEOS` class implementing PV=nRT
  - `calculate_volume()` static method
  - `calculate_Z()` static method (always returns 1.0)
  - `calculate_state()` method returning IdealGasState
  - NumPy-style docstrings

- **Unit Tests**: `tests/unit/test_ideal_gas.py`
  - Volume calculation at STP validation
  - Z-factor tests (always 1.0)
  - State calculation tests
  - Input validation tests

- **CLI Tool**: `src/cli/ideal_calc.py`
  - `ideal-calc volume` - Calculate ideal gas volume
  - `ideal-calc z-factor` - Calculate Z-factor (always 1.0)
  - `ideal-calc state` - Calculate complete ideal gas state
  - Support for variable mole amounts
  - Text and JSON output formats

#### PT Flash Calculation
- **Core Implementation**: `src/eos/flash_pt.py`
  - `FlashPT` class with Rachford-Rice algorithm
  - `FlashResult` dataclass with L, V, x, y, K-values, iterations
  - `FlashConvergence` enum for result status
  - `single_phase_check()` - Detect single-phase conditions
  - `initialize_K_values()` - Wilson correlation
  - `rachford_rice_solve()` - RR equation solver
  - `update_K_values()` - Fugacity-based K-value updates
  - `convergence_check()` - Fugacity equilibrium validation
  - `material_balance_check()` - Material balance verification
  - Configurable max iterations (default: 50) and tolerance (default: 1e-6)

- **Unit Tests**: `tests/unit/test_flash_pt.py`
  - Single-phase detection tests
  - K-value initialization tests
  - Convergence check tests
  - Material balance validation tests
  - Binary mixture fixtures (ethane-propane, methane-propane)

- **Integration Tests**: `tests/unit/test_integration_flash.py`
  - Binary flash convergence tests
  - Flash output completeness validation
  - Material balance error < 1e-6
  - Fugacity equilibrium testing
  - Robustness tests across T/P conditions

- **Validation Tests**: `tests/validation/test_flash_balance_tests.py`
  - NIST reference data validation
  - Ethane-propane binary system tests
  - Methane-propane binary system tests
  - Parametrized 5-case NIST validation
  - Material balance error < 1e-6 verification

- **CLI Tool**: `src/cli/flash_calc.py`
  - `flash-calc calculate` - Binary VLE flash calculation
  - `flash-calc validate` - Validate against reference data
  - Support for custom max iterations and tolerance
  - Detailed output with convergence status, L/V fractions, compositions
  - Text and JSON output formats

#### Cross-Model Comparison
- **Utility Function**: `src/eos/__init__.py`
  - `compare_compressibility_factors()` - Compare Z-factors across all three EOS models
  - Returns dict with `ideal_Z`, `vdw_Z`, `pr_Z`
  - Full input validation
  - NumPy-style documentation with examples

- **Integration Tests**: `tests/unit/test_integration.py`
  - Cross-EOS comparison fixtures for methane, ethane, propane
  - Function signature and output format tests
  - Input validation tests
  - Z-factor ordering tests (Ideal = 1.0 ≥ VDW, PR)
  - Low-pressure convergence tests
  - Multi-compound consistency tests
  - Temperature and pressure variation tests

#### Reference Data
- **NIST Reference Data**: `tests/validation/reference_data/`
  - `vdw_nist.csv` - Van der Waals Z-factor reference data (15 test points)
  - `flash_nist.csv` - PT Flash reference data for binary mixtures (9 test cases)

- **Test Documentation**: `specs/002-thermodynamic-models/test-scenarios.md`
  - Comprehensive test scenario documentation
  - Expected results and validation criteria
  - Coverage for VDW, Ideal Gas, and PT Flash user stories

#### Package Exports
- **Updated Exports**: `src/eos/__init__.py`
  - Added `VanDerWaalsEOS` to exports
  - Added `IdealGasEOS` to exports
  - Added `FlashPT`, `FlashResult`, `FlashConvergence` to exports
  - Added `compare_compressibility_factors` utility function

#### CLI Entry Points
- **Updated**: `pyproject.toml`
  - `vdw-calc` - Van der Waals CLI entry point
  - `ideal-calc` - Ideal Gas CLI entry point
  - `flash-calc` - PT Flash CLI entry point

### Changed
- **README.md**: Updated to reflect comprehensive thermodynamic toolkit
  - Updated title to "Chemical Engineering Thermodynamic Toolbox"
  - Added sections for Van der Waals EOS, Ideal Gas, and PT Flash
  - Added Python API examples for all new modules
  - Added CLI examples for all new commands
  - Updated accuracy table with VDW and Flash validation metrics

### Fixed
- None

### Deprecated
- None

### Removed
- None

### Security
- None

---

## [0.1.0] - 2025-12-29

### Added
- Initial release with Peng-Robinson EOS implementation
- Compressibility factor calculations
- Fugacity coefficient calculations
- Vapor pressure calculations
- NIST validation framework
- CLI tool: `pr-calc`
- Python API for thermodynamic calculations
- Compound database with 5 reference compounds
- Comprehensive test suite (>80% coverage)
- Full mypy --strict type coverage
- Documentation (API reference, theory, troubleshooting)

---

## Summary Statistics

### Thermodynamic Extension (Feature 002)
- **Total Tasks**: 122
- **Completed**: 104 (85.2%)
- **New Files**: 16
- **New Tests**: ~325 total tests
  - Unit tests: ~175 tests
  - Integration tests: ~100 tests
  - Validation tests: ~50 tests
- **Code Coverage**: >80%
- **Type Coverage**: 100% (mypy --strict)
- **NIST Validation**: All tests passing

### Module Breakdown
- **Van der Waals EOS**: 22 tasks (T026-T047)
- **Ideal Gas Law**: 20 tasks (T048-T067)
- **PT Flash Calculation**: 37 tasks (T068-T104)
- **CLI Integration**: 7 tasks (T105-T111)
- **Documentation**: 6 tasks (T112-T117)

---

[Unreleased]: https://github.com/ChE-Toolbox/che-toolbox/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ChE-Toolbox/che-toolbox/releases/tag/v0.1.0
