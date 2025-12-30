"""Integration tests for SteamTable P-T property lookup workflow.

Tests the complete flow from user API through region routing
to property calculation and unit handling.
"""

import pytest

from src.iapws_if97 import SteamTable, SteamProperties
from src.iapws_if97.exceptions import InputRangeError, InvalidStateError


@pytest.mark.integration
class TestSteamTablePTLookup:
    """Integration tests for pressure-temperature property lookups."""

    def test_steamtable_initialization(self, steam_table):
        """Test that SteamTable initializes successfully."""
        assert steam_table is not None
        assert hasattr(steam_table, "properties")
        assert hasattr(steam_table, "enthalpy_pt")
        assert hasattr(steam_table, "entropy_pt")
        assert hasattr(steam_table, "density_pt")
        assert hasattr(steam_table, "internal_energy_pt")

    def test_steamtable_region1_point(self, steam_table):
        """Test Region 1 lookup through SteamTable API."""
        # Region 1: Compressed liquid at P=3 MPa, T=300 K
        props = steam_table.properties(pressure_pa=3e6, temperature_k=300)

        assert isinstance(props, SteamProperties)
        assert props.pressure is not None
        assert props.temperature is not None
        assert props.enthalpy is not None
        assert props.entropy is not None
        assert props.density is not None
        assert props.internal_energy is not None

        # Check that values are reasonable
        assert props.enthalpy.magnitude > 0
        assert props.entropy.magnitude > 0
        assert props.density.magnitude > 0

    def test_steamtable_region2_point(self, steam_table):
        """Test Region 2 lookup through SteamTable API."""
        # Region 2: Superheated steam at P=35 kPa, T=700 K
        props = steam_table.properties(pressure_pa=35e3, temperature_k=700)

        assert isinstance(props, SteamProperties)
        assert props.pressure is not None
        assert props.temperature is not None
        assert props.enthalpy is not None

        # Steam should have lower density than liquid
        assert props.density.magnitude < 10  # kg/m³

    def test_steamtable_region3_point(self, steam_table):
        """Test Region 3 lookup through SteamTable API."""
        # Region 3: Supercritical at P=25 MPa, T=650 K
        props = steam_table.properties(pressure_pa=25e6, temperature_k=650)

        assert isinstance(props, SteamProperties)
        assert props.enthalpy is not None
        assert props.entropy is not None

    def test_steamtable_enthalpy_pt_method(self, steam_table):
        """Test enthalpy_pt convenience method."""
        h = steam_table.enthalpy_pt(pressure_pa=3e6, temperature_k=300)

        assert h is not None
        assert hasattr(h, "magnitude")
        assert h.magnitude > 0

    def test_steamtable_entropy_pt_method(self, steam_table):
        """Test entropy_pt convenience method."""
        s = steam_table.entropy_pt(pressure_pa=3e6, temperature_k=300)

        assert s is not None
        assert hasattr(s, "magnitude")
        assert s.magnitude > 0

    def test_steamtable_density_pt_method(self, steam_table):
        """Test density_pt convenience method."""
        rho = steam_table.density_pt(pressure_pa=3e6, temperature_k=300)

        assert rho is not None
        assert hasattr(rho, "magnitude")
        assert rho.magnitude > 0

    def test_steamtable_internal_energy_pt_method(self, steam_table):
        """Test internal_energy_pt convenience method."""
        u = steam_table.internal_energy_pt(pressure_pa=3e6, temperature_k=300)

        assert u is not None
        assert hasattr(u, "magnitude")
        assert u.magnitude > 0

    def test_steamtable_invalid_pressure_raises_error(self, steam_table):
        """Test that invalid pressure raises InputRangeError."""
        with pytest.raises(InputRangeError):
            steam_table.properties(pressure_pa=-1000, temperature_k=300)

    def test_steamtable_invalid_temperature_raises_error(self, steam_table):
        """Test that invalid temperature raises InputRangeError."""
        with pytest.raises(InputRangeError):
            steam_table.properties(pressure_pa=3e6, temperature_k=-100)

    def test_steamtable_saturation_point_raises_error(self, steam_table):
        """Test that saturation line conditions raise InvalidStateError."""
        # Note: This test may need adjustment based on saturation pressure estimation
        # Using approximate saturation conditions
        with pytest.raises(InvalidStateError):
            steam_table.properties(pressure_pa=100e3, temperature_k=372.756)

    def test_steamtable_multiple_regions(self, steam_table):
        """Test lookups across all three regions."""
        # Region 1 point
        r1_props = steam_table.properties(pressure_pa=50e6, temperature_k=350)
        assert r1_props.enthalpy is not None

        # Region 2 point
        r2_props = steam_table.properties(pressure_pa=0.1e6, temperature_k=500)
        assert r2_props.enthalpy is not None

        # Region 3 point
        r3_props = steam_table.properties(pressure_pa=50e6, temperature_k=700)
        assert r3_props.enthalpy is not None

        # Region 2 should have lower density than Region 1
        assert r2_props.density.magnitude < r1_props.density.magnitude
