"""Pytest configuration and fixtures for IAPWS-IF97 test suite.

Provides:
- IAPWS reference data fixtures
- Test data loaders
- Common test utilities
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import pytest


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

    def _load_tables(region: str) -> List[Dict[str, Any]]:
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
        except (json.JSONDecodeError, IOError) as e:
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


# Pytest configuration
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "validation: IAPWS validation tests")
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
