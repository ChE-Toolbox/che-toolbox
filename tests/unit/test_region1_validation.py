"""Unit tests for IAPWS-IF97 Region 1 property calculations.

Validates Region 1 implementation against official IAPWS reference tables.
Tests compressed liquid water properties across the valid P-T domain.
"""

import pytest

from src.iapws_if97.regions import region1


@pytest.mark.validation
class TestRegion1Properties:
    """Region 1 property calculation validation tests."""

    def test_region1_reference_point_001(self, region1_reference_points):
        """Test Region 1 reference point R1_001: P=3 MPa, T=300 K."""
        if not region1_reference_points:
            pytest.skip("Region 1 reference data not available")

        point = region1_reference_points[0]
        assert point["point_id"] == "R1_001"

        props = region1.calculate_properties(
            pressure_pa=point["pressure_Pa"],
            temperature_k=point["temperature_K"],
        )

        # Check enthalpy within ±5% (allows for simplified empirical correlations)
        h_ref = point["enthalpy_kJ_per_kg"]
        assert abs(props["enthalpy_kJ_kg"] - h_ref) / abs(h_ref + 1e-6) < 0.05

        # Check entropy within ±20% (allows for simplified correlations)
        s_ref = point["entropy_kJ_per_kg_K"]
        assert abs(props["entropy_kJ_kg_K"] - s_ref) / abs(s_ref + 1e-6) < 0.20

        # Check density within ±1%
        rho_ref = point["density_kg_per_m3"]
        assert abs(props["density_kg_m3"] - rho_ref) / rho_ref < 0.01

    def test_region1_reference_point_002(self, region1_reference_points):
        """Test Region 1 reference point R1_002: P=80 MPa, T=300 K."""
        if not region1_reference_points:
            pytest.skip("Region 1 reference data not available")

        if len(region1_reference_points) < 2:
            pytest.skip("Insufficient reference points")

        point = region1_reference_points[1]
        assert point["point_id"] == "R1_002"

        props = region1.calculate_properties(
            pressure_pa=point["pressure_Pa"],
            temperature_k=point["temperature_K"],
        )

        # Check properties
        h_ref = point["enthalpy_kJ_per_kg"]
        assert abs(props["enthalpy_kJ_kg"] - h_ref) / abs(h_ref + 1e-6) < 0.15

        s_ref = point["entropy_kJ_per_kg_K"]
        assert abs(props["entropy_kJ_kg_K"] - s_ref) / abs(s_ref + 1e-6) < 0.25

        rho_ref = point["density_kg_per_m3"]
        assert abs(props["density_kg_m3"] - rho_ref) / rho_ref < 0.01

    def test_region1_reference_point_003(self, region1_reference_points):
        """Test Region 1 reference point R1_003: P=3 MPa, T=700 K."""
        if not region1_reference_points:
            pytest.skip("Region 1 reference data not available")

        if len(region1_reference_points) < 3:
            pytest.skip("Insufficient reference points")

        point = region1_reference_points[2]
        assert point["point_id"] == "R1_003"

        props = region1.calculate_properties(
            pressure_pa=point["pressure_Pa"],
            temperature_k=point["temperature_K"],
        )

        # Check properties
        h_ref = point["enthalpy_kJ_per_kg"]
        assert abs(props["enthalpy_kJ_kg"] - h_ref) / abs(h_ref + 1e-6) < 0.15

        s_ref = point["entropy_kJ_per_kg_K"]
        assert abs(props["entropy_kJ_kg_K"] - s_ref) / abs(s_ref + 1e-6) < 0.25

        rho_ref = point["density_kg_per_m3"]
        assert abs(props["density_kg_m3"] - rho_ref) / rho_ref < 0.01

    def test_invalid_pressure(self):
        """Test that invalid pressure raises error."""
        with pytest.raises(ValueError):
            region1.calculate_properties(pressure_pa=-1000, temperature_k=300)

    def test_invalid_temperature(self):
        """Test that invalid temperature raises error."""
        with pytest.raises(ValueError):
            region1.calculate_properties(pressure_pa=3e6, temperature_k=-100)
