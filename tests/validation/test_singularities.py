"""
Singularity validation tests for IAPWS-IF97 implementation.

Ensures that numerical instabilities near the critical point are properly detected
and that RuntimeError is raised with appropriate diagnostic messages.
"""

import pytest
from pint import UnitRegistry

from iapws_if97 import SteamTable
from iapws_if97.exceptions import NumericalInstabilityError

ureg = UnitRegistry()

# Critical point constants
CRITICAL_PRESSURE_MPA = 22.064
CRITICAL_TEMPERATURE_K = 647.096
SINGULARITY_THRESHOLD = 0.05  # 5% from critical point


class TestCriticalPointSingularity:
    """Tests for singularity detection near the critical point."""

    def test_exactly_at_critical_point(self):
        """Test that exactly at critical point raises NumericalInstabilityError."""
        steam = SteamTable()

        with pytest.raises(NumericalInstabilityError) as exc_info:
            steam.h_pt(CRITICAL_PRESSURE_MPA * ureg.MPa, CRITICAL_TEMPERATURE_K * ureg.K)

        error_msg = str(exc_info.value).lower()
        assert "critical point" in error_msg
        assert "singularity" in error_msg or "instability" in error_msg

    def test_1_percent_from_critical_point(self):
        """Test 1% distance from critical point (well within 5% threshold)."""
        steam = SteamTable()

        # 1% higher in both dimensions
        p = CRITICAL_PRESSURE_MPA * 1.01 * ureg.MPa
        t = CRITICAL_TEMPERATURE_K * 1.01 * ureg.K

        with pytest.raises(NumericalInstabilityError):
            steam.h_pt(p, t)

    def test_2_percent_from_critical_point(self):
        """Test 2% distance from critical point (within 5% threshold)."""
        steam = SteamTable()

        p = CRITICAL_PRESSURE_MPA * 1.02 * ureg.MPa
        t = CRITICAL_TEMPERATURE_K * 1.02 * ureg.K

        with pytest.raises(NumericalInstabilityError):
            steam.h_pt(p, t)

    def test_4_percent_from_critical_point(self):
        """Test 4% distance from critical point (within 5% threshold)."""
        steam = SteamTable()

        p = CRITICAL_PRESSURE_MPA * 1.04 * ureg.MPa
        t = CRITICAL_TEMPERATURE_K * 1.04 * ureg.K

        with pytest.raises(NumericalInstabilityError):
            steam.h_pt(p, t)

    def test_6_percent_from_critical_point_should_pass(self):
        """Test 6% distance from critical point (outside 5% threshold, should work)."""
        steam = SteamTable()

        p = CRITICAL_PRESSURE_MPA * 1.06 * ureg.MPa
        t = CRITICAL_TEMPERATURE_K * 1.06 * ureg.K

        # Should not raise (outside singularity zone)
        h = steam.h_pt(p, t)
        assert h.magnitude > 0

    def test_10_percent_from_critical_point_should_pass(self):
        """Test 10% distance from critical point (well outside threshold)."""
        steam = SteamTable()

        p = CRITICAL_PRESSURE_MPA * 1.10 * ureg.MPa
        t = CRITICAL_TEMPERATURE_K * 1.10 * ureg.K

        # Should work fine
        h = steam.h_pt(p, t)
        s = steam.s_pt(p, t)
        rho = steam.rho_pt(p, t)

        assert h.magnitude > 0
        assert s.magnitude > 0
        assert rho.magnitude > 0


class TestSingularityInDifferentDirections:
    """Test singularity detection in various directions from critical point."""

    def test_above_critical_pressure_at_critical_temperature(self):
        """Test slightly above critical pressure, at critical temperature."""
        steam = SteamTable()

        # 3% above critical pressure, exactly at critical temperature
        p = CRITICAL_PRESSURE_MPA * 1.03 * ureg.MPa
        t = CRITICAL_TEMPERATURE_K * ureg.K

        with pytest.raises(NumericalInstabilityError):
            steam.h_pt(p, t)

    def test_at_critical_pressure_above_critical_temperature(self):
        """Test at critical pressure, slightly above critical temperature."""
        steam = SteamTable()

        p = CRITICAL_PRESSURE_MPA * ureg.MPa
        t = CRITICAL_TEMPERATURE_K * 1.03 * ureg.K

        with pytest.raises(NumericalInstabilityError):
            steam.h_pt(p, t)

    def test_below_critical_pressure_near_critical_temperature(self):
        """Test below critical pressure, near critical temperature."""
        steam = SteamTable()

        # 2% below critical point
        p = CRITICAL_PRESSURE_MPA * 0.98 * ureg.MPa
        t = CRITICAL_TEMPERATURE_K * 0.98 * ureg.K

        with pytest.raises(NumericalInstabilityError):
            steam.h_pt(p, t)


class TestDiagnosticMessages:
    """Verify that singularity error messages provide helpful diagnostics."""

    def test_error_message_contains_distance(self):
        """Verify error message includes distance metric."""
        steam = SteamTable()

        with pytest.raises(NumericalInstabilityError) as exc_info:
            steam.h_pt(CRITICAL_PRESSURE_MPA * ureg.MPa, CRITICAL_TEMPERATURE_K * ureg.K)

        error_msg = str(exc_info.value)

        # Should mention distance or threshold
        assert (
            "distance" in error_msg.lower() or "threshold" in error_msg.lower() or "%" in error_msg
        )

    def test_error_message_contains_critical_point_values(self):
        """Verify error message includes critical point coordinates."""
        steam = SteamTable()

        with pytest.raises(NumericalInstabilityError) as exc_info:
            steam.h_pt(CRITICAL_PRESSURE_MPA * ureg.MPa, CRITICAL_TEMPERATURE_K * ureg.K)

        error_msg = str(exc_info.value)

        # Should mention critical point pressure and/or temperature
        assert (
            "22.064" in error_msg
            or "22.06" in error_msg
            or "647" in error_msg
            or "374" in error_msg
        )

    def test_error_message_contains_suggestion(self):
        """Verify error message provides actionable suggestion."""
        steam = SteamTable()

        with pytest.raises(NumericalInstabilityError) as exc_info:
            steam.h_pt(CRITICAL_PRESSURE_MPA * ureg.MPa, CRITICAL_TEMPERATURE_K * ureg.K)

        error_msg = str(exc_info.value).lower()

        # Should provide guidance
        assert (
            "suggestion" in error_msg
            or "move" in error_msg
            or "away" in error_msg
            or "increase" in error_msg
            or "decrease" in error_msg
        )


class TestAllPropertiesRaiseSingularityError:
    """Verify all property methods detect singularities."""

    def test_enthalpy_singularity(self):
        """Test that h_pt raises singularity error."""
        steam = SteamTable()

        with pytest.raises(NumericalInstabilityError):
            steam.h_pt(CRITICAL_PRESSURE_MPA * ureg.MPa, CRITICAL_TEMPERATURE_K * ureg.K)

    def test_entropy_singularity(self):
        """Test that s_pt raises singularity error."""
        steam = SteamTable()

        with pytest.raises(NumericalInstabilityError):
            steam.s_pt(CRITICAL_PRESSURE_MPA * ureg.MPa, CRITICAL_TEMPERATURE_K * ureg.K)

    def test_internal_energy_singularity(self):
        """Test that u_pt raises singularity error."""
        steam = SteamTable()

        with pytest.raises(NumericalInstabilityError):
            steam.u_pt(CRITICAL_PRESSURE_MPA * ureg.MPa, CRITICAL_TEMPERATURE_K * ureg.K)

    def test_density_singularity(self):
        """Test that rho_pt raises singularity error."""
        steam = SteamTable()

        with pytest.raises(NumericalInstabilityError):
            steam.rho_pt(CRITICAL_PRESSURE_MPA * ureg.MPa, CRITICAL_TEMPERATURE_K * ureg.K)


class TestConvergenceFailureDocumentation:
    """Tests to document known convergence failure scenarios."""

    def test_document_critical_region_behavior(self):
        """Document that critical region is explicitly excluded."""
        steam = SteamTable()

        # This test documents the expected behavior: explicit fail near critical point
        # rather than attempting to compute unreliable values

        # Within singularity zone: should fail
        try:
            steam.h_pt(CRITICAL_PRESSURE_MPA * ureg.MPa, CRITICAL_TEMPERATURE_K * ureg.K)
            pytest.fail("Expected NumericalInstabilityError for critical point conditions")
        except NumericalInstabilityError as e:
            # Expected - document that this is intentional
            assert "critical point" in str(e).lower()

        # Outside singularity zone: should work
        h = steam.h_pt(
            CRITICAL_PRESSURE_MPA * 1.10 * ureg.MPa, CRITICAL_TEMPERATURE_K * 1.10 * ureg.K
        )
        assert h.magnitude > 0

    def test_boundary_of_singularity_zone(self):
        """Test behavior exactly at the boundary of the singularity zone."""
        steam = SteamTable()

        # At approximately 5% distance (boundary case)
        # This might be implementation-dependent
        p_boundary = CRITICAL_PRESSURE_MPA * 1.05 * ureg.MPa
        t_boundary = CRITICAL_TEMPERATURE_K * 1.05 * ureg.K

        # Behavior at boundary may vary slightly depending on implementation
        # Document what actually happens
        try:
            h = steam.h_pt(p_boundary, t_boundary)
            # If it works, it should return valid value
            assert h.magnitude > 0
        except NumericalInstabilityError:
            # If it fails, that's also acceptable at the boundary
            pass
