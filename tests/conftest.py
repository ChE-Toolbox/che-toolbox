"""Pytest configuration and fixtures for Chemical Engineering Thermodynamic Toolbox.

Provides:
- IAPWS-IF97 steam properties test fixtures and reference data
- Fluid calculations test fixtures (pipe flow, pump sizing, valve sizing)
- Common test utilities and reference data loaders
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest


# ============================================================================
# IAPWS-IF97 Steam Properties Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def reference_data_dir() -> Path:
    """Get path to IAPWS reference data directory.

    Returns:
        Path to validation/iapws_tables.json directory
    """
    return Path(__file__).parent.parent / "src" / "iapws_if97" / "validation"


@pytest.fixture(scope="session")
def load_reference_tables() -> callable:
    """Fixture providing function to load IAPWS reference tables.

    Returns:
        Function to load JSON reference data by region
    """

    def _load_tables(region: str) -> list[dict[str, Any]]:
        """Load reference test points for given region.

        Args:
            region: Region name ('region1', 'region2', 'region3', 'saturation')

        Returns:
            List of reference test point dictionaries
        """
        ref_file = (
            Path(__file__).parent.parent / "src" / "iapws_if97" / "validation" / "iapws_tables.json"
        )

        if not ref_file.exists():
            pytest.skip(f"IAPWS reference tables not found at {ref_file}")

        try:
            with open(ref_file) as f:
                data = json.load(f)
            return data.get("regions", {}).get(region, [])
        except (OSError, json.JSONDecodeError) as e:
            pytest.skip(f"Could not load reference tables: {e}")

    return _load_tables


@pytest.fixture(scope="session")
def region1_reference_points(load_reference_tables):
    """IAPWS-IF97 Region 1 reference test points (400+ points).

    Yields:
        List of Region 1 test points with expected values
    """
    return load_reference_tables("region1")


@pytest.fixture(scope="session")
def region2_reference_points(load_reference_tables):
    """IAPWS-IF97 Region 2 reference test points (400+ points).

    Yields:
        List of Region 2 test points with expected values
    """
    return load_reference_tables("region2")


@pytest.fixture(scope="session")
def region3_reference_points(load_reference_tables):
    """IAPWS-IF97 Region 3 reference test points (200+ points).

    Yields:
        List of Region 3 test points with expected values
    """
    return load_reference_tables("region3")


@pytest.fixture(scope="session")
def saturation_reference_points(load_reference_tables):
    """IAPWS-IF97 Saturation line reference test points (300+ points).

    Yields:
        List of saturation test points with expected values
    """
    return load_reference_tables("saturation")


@pytest.fixture
def steam_table():
    """SteamTable instance for testing.

    Yields:
        Initialized SteamTable object
    """
    try:
        from src.iapws_if97 import SteamTable

        return SteamTable()
    except ImportError:
        pytest.skip("SteamTable not yet implemented")


@pytest.fixture
def ureg():
    """Pint UnitRegistry for testing.

    Yields:
        UnitRegistry instance with SI units
    """
    from src.iapws_if97.units import ureg

    return ureg


# ============================================================================
# Fluid Calculations Fixtures
# ============================================================================


@pytest.fixture
def standard_water() -> Dict[str, float]:
    """
    Standard water properties at 20°C and 1 atm.

    Returns:
        Dictionary with water properties (density, viscosity, etc.)
    """
    return {
        "density": 998.0,  # kg/m³ at 20°C
        "dynamic_viscosity": 0.001002,  # Pa·s at 20°C
        "kinematic_viscosity": 1.004e-6,  # m²/s at 20°C
        "specific_gravity": 0.998,
        "temperature": 293.15,  # 20°C in Kelvin
        "pressure": 101325,  # 1 atm in Pa
        "vapor_pressure": 2337,  # Pa at 20°C
    }


@pytest.fixture
def standard_pipe() -> Dict[str, float]:
    """
    Standard steel pipe dimensions for testing.

    Returns:
        Dictionary with pipe geometry (diameter, length, roughness)
    """
    return {
        "diameter": 0.05,  # 50 mm in meters
        "length": 100.0,  # 100 meters
        "absolute_roughness": 0.000045,  # 0.045 mm for commercial steel in meters
        "material": "steel",
    }


@pytest.fixture
def standard_pump() -> Dict[str, Any]:
    """
    Standard centrifugal pump specifications.

    Returns:
        Dictionary with pump parameters
    """
    return {
        "name": "Standard Centrifugal Pump",
        "type": "centrifugal",
        "design_point": {
            "flow_rate": 0.05,  # m³/s
            "head": 50.0,  # m
            "power": 25000,  # W
        },
        "efficiency": 0.75,  # 75%
        "npsh_required": 0.5,  # m
        "efficiency_curve": {
            0.02: 0.65,
            0.05: 0.75,
            0.08: 0.73,
        },
    }


@pytest.fixture
def standard_valve() -> Dict[str, Any]:
    """
    Standard ball valve specifications.

    Returns:
        Dictionary with valve parameters
    """
    return {
        "name": "Standard Ball Valve",
        "type": "ball",
        "nominal_size": "2 inch",
        "cv_rating": {
            "fully_open": 4.4,
            "75_percent": 3.3,
            "50_percent": 2.2,
            "25_percent": 1.1,
        },
        "rangeability": 4.0,  # Max flow / min flow
    }


@pytest.fixture
def crane_tp410_reference_data() -> Dict[str, Dict[str, float]]:
    """
    Reference data from Crane TP-410 for validation.

    Returns:
        Dictionary with validation reference values
    """
    return {
        "reynolds_laminar": {
            "re_value": 1000,
            "friction_factor": 0.064,  # 64/Re = 64/1000
        },
        "reynolds_turbulent": {
            "re_value": 10000,
            "friction_factor": 0.032,  # Approximate from Churchill equation
        },
        "pressure_drop": {
            "diameter": 0.05,  # m
            "length": 100.0,  # m
            "velocity": 2.0,  # m/s
            "friction_factor": 0.03,
            "density": 1000,  # kg/m³
            "expected_pressure_drop": 6000,  # Pa (approximate)
        },
    }


@pytest.fixture
def turbulent_flow_cases() -> list[Dict[str, float]]:
    """
    Test cases for turbulent flow regimes.

    Returns:
        List of test cases with flow parameters
    """
    return [
        {
            "velocity": 0.5,
            "diameter": 0.05,
            "density": 998,
            "viscosity": 0.001,
            "expected_re": 24900,
            "regime": "turbulent",
        },
        {
            "velocity": 2.0,
            "diameter": 0.05,
            "density": 998,
            "viscosity": 0.001,
            "expected_re": 99600,
            "regime": "turbulent",
        },
        {
            "velocity": 5.0,
            "diameter": 0.1,
            "density": 998,
            "viscosity": 0.001,
            "expected_re": 499000,
            "regime": "turbulent",
        },
    ]


@pytest.fixture
def laminar_flow_cases() -> list[Dict[str, float]]:
    """
    Test cases for laminar flow regimes.

    Returns:
        List of test cases with flow parameters
    """
    return [
        {
            "velocity": 0.001,
            "diameter": 0.05,
            "density": 998,
            "viscosity": 0.001,
            "expected_re": 49.9,
            "regime": "laminar",
        },
        {
            "velocity": 0.05,
            "diameter": 0.02,
            "density": 998,
            "viscosity": 0.005,
            "expected_re": 199.2,
            "regime": "laminar",
        },
    ]


@pytest.fixture
def transitional_flow_cases() -> list[Dict[str, float]]:
    """
    Test cases for transitional flow regimes (Re 2300-4000).

    Returns:
        List of test cases with flow parameters
    """
    return [
        {
            "velocity": 0.23,
            "diameter": 0.05,
            "density": 998,
            "viscosity": 0.001,
            "expected_re": 11487,
            "regime": "transitional",
            "expected_warning": "Reynolds in transitional zone",
        },
        {
            "velocity": 0.4,
            "diameter": 0.05,
            "density": 998,
            "viscosity": 0.001,
            "expected_re": 19920,
            "regime": "transitional",
            "expected_warning": "Reynolds in transitional zone",
        },
    ]


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "validation: validation tests against standards")
    config.addinivalue_line("markers", "slow: slow running tests")


def pytest_collection_modifyitems(config, items):
    """Add markers based on test module location."""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "validation" in str(item.fspath):
            item.add_marker(pytest.mark.validation)
