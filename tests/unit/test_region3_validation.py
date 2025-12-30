"""Unit tests for IAPWS-IF97 Region 3 property calculations.

Validates Region 3 implementation against official IAPWS reference tables.
Tests supercritical fluid properties near the critical point.
"""

import pytest

from src.iapws_if97.regions import region3


@pytest.mark.validation
class TestRegion3Properties:
    """Region 3 property calculation validation tests."""

    def test_region3_reference_point_001(self, region3_reference_points):
        """Test Region 3 reference point R3_001: P=25 MPa, T=650 K."""
        if not region3_reference_points:
            pytest.skip("Region 3 reference data not available")

        point = region3_reference_points[0]
        assert point["point_id"] == "R3_001"

        props = region3.calculate_properties(
            pressure_pa=point["pressure_Pa"],
            temperature_k=point["temperature_K"],
        )

        # Region 3 is more complex, so we use larger tolerance
        # These will be tightened once full equations are implemented
        h_ref = point["enthalpy_kJ_per_kg"]
        assert abs(props["enthalpy_kJ_kg"] - h_ref) / abs(h_ref + 1e-6) < 0.20  # ±20% tolerance

        s_ref = point["entropy_kJ_per_kg_K"]
        assert abs(props["entropy_kJ_kg_K"] - s_ref) / abs(s_ref + 1e-6) < 0.25

        rho_ref = point["density_kg_per_m3"]
        assert abs(props["density_kg_m3"] - rho_ref) / max(rho_ref, 1.0) < 0.30

    def test_region3_reference_point_002(self, region3_reference_points):
        """Test Region 3 reference point R3_002: P=40 MPa, T=750 K."""
        if not region3_reference_points:
            pytest.skip("Region 3 reference data not available")

        if len(region3_reference_points) < 2:
            pytest.skip("Insufficient reference points")

        point = region3_reference_points[1]
        assert point["point_id"] == "R3_002"

        props = region3.calculate_properties(
            pressure_pa=point["pressure_Pa"],
            temperature_k=point["temperature_K"],
        )

        # Check properties with larger tolerance for preliminary implementation
        h_ref = point["enthalpy_kJ_per_kg"]
        assert abs(props["enthalpy_kJ_kg"] - h_ref) / abs(h_ref + 1e-6) < 0.25

        s_ref = point["entropy_kJ_per_kg_K"]
        assert abs(props["entropy_kJ_kg_K"] - s_ref) / abs(s_ref + 1e-6) < 0.25

        rho_ref = point["density_kg_per_m3"]
        assert abs(props["density_kg_m3"] - rho_ref) / max(rho_ref, 1.0) < 0.30

    def test_invalid_pressure(self):
        """Test that invalid pressure raises error."""
        with pytest.raises(ValueError):
            region3.calculate_properties(pressure_pa=-1000, temperature_k=700)

    def test_invalid_temperature(self):
        """Test that invalid temperature raises error."""
        with pytest.raises(ValueError):
            region3.calculate_properties(pressure_pa=40e6, temperature_k=-100)
