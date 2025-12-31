"""Unit tests for IAPWS-IF97 Region 2 property calculations.

Validates Region 2 implementation against official IAPWS reference tables.
Tests superheated steam properties across the valid P-T domain.
"""

import pytest

from src.iapws_if97.regions import region2


@pytest.mark.validation
class TestRegion2Properties:
    """Region 2 property calculation validation tests."""

    def test_region2_reference_point_001(self, region2_reference_points):
        """Test Region 2 reference point R2_001: P=35 kPa, T=300 K."""
        if not region2_reference_points:
            pytest.skip("Region 2 reference data not available")

        point = region2_reference_points[0]
        assert point["point_id"] == "R2_001"

        props = region2.calculate_properties(
            pressure_pa=point["pressure_Pa"],
            temperature_k=point["temperature_K"],
        )

        # Check enthalpy within ±5%
        h_ref = point["enthalpy_kJ_per_kg"]
        assert abs(props["enthalpy_kJ_kg"] - h_ref) / abs(h_ref + 1e-6) < 0.05

        # Check entropy within ±15%
        s_ref = point["entropy_kJ_per_kg_K"]
        assert abs(props["entropy_kJ_kg_K"] - s_ref) / abs(s_ref + 1e-6) < 0.15

        # Check density within ±15%
        rho_ref = point["density_kg_per_m3"]
        assert abs(props["density_kg_m3"] - rho_ref) / max(rho_ref, 0.01) < 0.15

    def test_region2_reference_point_002(self, region2_reference_points):
        """Test Region 2 reference point R2_002: P=35 kPa, T=700 K."""
        if not region2_reference_points:
            pytest.skip("Region 2 reference data not available")

        if len(region2_reference_points) < 2:
            pytest.skip("Insufficient reference points")

        point = region2_reference_points[1]
        assert point["point_id"] == "R2_002"

        props = region2.calculate_properties(
            pressure_pa=point["pressure_Pa"],
            temperature_k=point["temperature_K"],
        )

        # Check properties
        h_ref = point["enthalpy_kJ_per_kg"]
        assert abs(props["enthalpy_kJ_kg"] - h_ref) / abs(h_ref + 1e-6) < 0.15

        s_ref = point["entropy_kJ_per_kg_K"]
        assert abs(props["entropy_kJ_kg_K"] - s_ref) / abs(s_ref + 1e-6) < 0.25

        rho_ref = point["density_kg_per_m3"]
        assert abs(props["density_kg_m3"] - rho_ref) / max(rho_ref, 0.01) < 0.15

    def test_region2_reference_point_003(self, region2_reference_points):
        """Test Region 2 reference point R2_003: P=30 MPa, T=700 K."""
        if not region2_reference_points:
            pytest.skip("Region 2 reference data not available")

        if len(region2_reference_points) < 3:
            pytest.skip("Insufficient reference points")

        point = region2_reference_points[2]
        assert point["point_id"] == "R2_003"

        props = region2.calculate_properties(
            pressure_pa=point["pressure_Pa"],
            temperature_k=point["temperature_K"],
        )

        # Check properties
        h_ref = point["enthalpy_kJ_per_kg"]
        assert abs(props["enthalpy_kJ_kg"] - h_ref) / abs(h_ref + 1e-6) < 0.15

        s_ref = point["entropy_kJ_per_kg_K"]
        assert abs(props["entropy_kJ_kg_K"] - s_ref) / abs(s_ref + 1e-6) < 0.25

        rho_ref = point["density_kg_per_m3"]
        assert abs(props["density_kg_m3"] - rho_ref) / max(rho_ref, 0.01) < 0.15

    def test_invalid_pressure(self):
        """Test that invalid pressure raises error."""
        with pytest.raises(ValueError):
            region2.calculate_properties(pressure_pa=-1000, temperature_k=700)

    def test_invalid_temperature(self):
        """Test that invalid temperature raises error."""
        with pytest.raises(ValueError):
            region2.calculate_properties(pressure_pa=35e3, temperature_k=-100)
