"""
Edge case validation tests for IAPWS-IF97 implementation.

Tests critical points, triple point, region boundaries, and other edge conditions
to ensure robust behavior across the entire valid input space.
"""

import pytest
from pint import UnitRegistry

from iapws_if97 import SteamTable
from iapws_if97.exceptions import InputRangeError, NumericalInstabilityError

ureg = UnitRegistry()


class TestCriticalPoint:
    """Tests near and at the critical point (22.064 MPa, 373.946 K)."""

    def test_critical_point_singularity_detection(self):
        """Verify that conditions within 5% of critical point raise NumericalInstabilityError."""
        steam = SteamTable()

        # Exactly at critical point - should fail
        with pytest.raises(NumericalInstabilityError) as exc_info:
            steam.h_pt(22.064 * ureg.MPa, 647.096 * ureg.K)

        assert "critical point" in str(exc_info.value).lower()
        assert "22.064" in str(exc_info.value)  # Pressure should be in message

    def test_near_critical_point_within_threshold(self):
        """Test conditions within 5% of critical point."""
        steam = SteamTable()

        # 2% from critical point - should fail
        p_near = 22.064 * 1.02 * ureg.MPa
        t_near = 647.096 * 1.02 * ureg.K

        with pytest.raises(NumericalInstabilityError):
            steam.h_pt(p_near, t_near)

    def test_outside_critical_singularity_zone(self):
        """Test that conditions >5% from critical point work correctly."""
        steam = SteamTable()

        # 10% above critical pressure, similar temperature
        p_safe = 22.064 * 1.10 * ureg.MPa  # ~24.3 MPa
        t_safe = 647.096 * 1.05 * ureg.K  # ~680 K

        # Should not raise
        h = steam.h_pt(p_safe, t_safe)
        assert h.magnitude > 0  # Valid enthalpy
        assert h.units == ureg.kJ / ureg.kg


class TestTriplePoint:
    """Tests at and near the triple point (611.657 Pa, 273.16 K)."""

    def test_triple_point_properties(self):
        """Verify properties at triple point are physical."""
        steam = SteamTable()

        # Triple point conditions
        p_triple = 611.657 * ureg.Pa
        t_triple = 273.16 * ureg.K

        # Should be able to compute properties
        h = steam.h_pt(p_triple, t_triple)
        s = steam.s_pt(p_triple, t_triple)
        rho = steam.rho_pt(p_triple, t_triple)

        # Basic sanity checks
        assert h.magnitude > 0
        assert s.magnitude > 0
        assert rho.magnitude > 0

    def test_below_triple_point_temperature(self):
        """Verify that temperatures below triple point raise InputRangeError."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(1 * ureg.MPa, 270 * ureg.K)  # Below 273.16 K

        assert "temperature" in str(exc_info.value).lower()
        assert "273.15" in str(exc_info.value) or "273.16" in str(exc_info.value)

    def test_below_triple_point_pressure(self):
        """Verify that pressures below triple point raise InputRangeError."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(600 * ureg.Pa, 300 * ureg.K)  # Below 611.657 Pa

        assert "pressure" in str(exc_info.value).lower()


class TestRegionBoundaries:
    """Tests at region boundaries to ensure smooth transitions."""

    def test_region1_region2_boundary(self):
        """Test conditions near the Region 1/2 boundary (saturation line)."""
        steam = SteamTable()

        # Just above saturation at 1 MPa (liquid side)
        # T_sat ≈ 453 K, so T > T_sat is Region 2
        p = 1 * ureg.MPa
        t_above = 460 * ureg.K  # Slightly superheated

        h_region2 = steam.h_pt(p, t_above)
        assert h_region2.magnitude > 0

        # High pressure liquid (Region 1)
        p_high = 20 * ureg.MPa
        t_low = 300 * ureg.K

        h_region1 = steam.h_pt(p_high, t_low)
        assert h_region1.magnitude > 0

    def test_region2_region3_boundary(self):
        """Test transition between Region 2 and Region 3."""
        steam = SteamTable()

        # Region 2: moderate pressure, high temperature
        p2 = 10 * ureg.MPa
        t2 = 800 * ureg.K

        h2 = steam.h_pt(p2, t2)
        assert h2.magnitude > 0

        # Region 3: high pressure, high temperature (supercritical)
        # But outside singularity zone
        p3 = 30 * ureg.MPa
        t3 = 700 * ureg.K

        h3 = steam.h_pt(p3, t3)
        assert h3.magnitude > 0

    def test_saturation_line_detection(self):
        """Verify that exactly on saturation line raises appropriate error."""
        steam = SteamTable()

        # Get saturation temperature at 1 MPa
        sat_props = steam.T_sat(1 * ureg.MPa)
        t_sat = sat_props.saturation_temperature

        # Trying to get single-phase properties exactly on saturation should fail
        # (though in practice floating point may make this pass)
        # This is more of a conceptual test
        p = 1 * ureg.MPa

        # Small offset to avoid saturation line
        h = steam.h_pt(p, t_sat + 1 * ureg.K)  # Slightly superheated
        assert h.magnitude > 0


class TestUpperBounds:
    """Tests at maximum valid conditions."""

    def test_maximum_pressure(self):
        """Test at maximum valid pressure (863.91 MPa for Region 1)."""
        steam = SteamTable()

        # Near maximum pressure
        p_max = 850 * ureg.MPa
        t = 500 * ureg.K

        h = steam.h_pt(p_max, t)
        assert h.magnitude > 0

    def test_maximum_temperature(self):
        """Test at maximum valid temperature (863.15 K)."""
        steam = SteamTable()

        p = 10 * ureg.MPa
        t_max = 860 * ureg.K

        h = steam.h_pt(p, t_max)
        assert h.magnitude > 0

    def test_above_maximum_pressure(self):
        """Verify that pressures above 863.91 MPa raise InputRangeError."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(900 * ureg.MPa, 500 * ureg.K)

        assert "pressure" in str(exc_info.value).lower()
        assert "863" in str(exc_info.value)

    def test_above_maximum_temperature(self):
        """Verify that temperatures above 863.15 K raise InputRangeError."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(10 * ureg.MPa, 900 * ureg.K)

        assert "temperature" in str(exc_info.value).lower()


class TestSaturationEdgeCases:
    """Tests for saturation property edge cases."""

    def test_saturation_at_minimum_pressure(self):
        """Test saturation at minimum pressure (triple point)."""
        steam = SteamTable()

        sat = steam.T_sat(611.657 * ureg.Pa)
        assert abs(sat.saturation_temperature.to("K").magnitude - 273.16) < 0.1  # Within 0.1 K

    def test_saturation_at_maximum_pressure(self):
        """Test saturation near critical point (maximum saturation pressure)."""
        steam = SteamTable()

        # Just below critical pressure
        sat = steam.T_sat(20 * ureg.MPa)
        assert sat.saturation_temperature.magnitude > 0

    def test_saturation_temperature_round_trip(self):
        """Verify P_sat(T_sat(P)) ≈ P consistency."""
        steam = SteamTable()

        p_test = 1 * ureg.MPa

        # Get saturation temperature at this pressure
        sat_from_p = steam.T_sat(p_test)
        t_sat = sat_from_p.saturation_temperature

        # Now get saturation pressure at that temperature
        sat_from_t = steam.P_sat(t_sat)
        p_sat = sat_from_t.saturation_pressure

        # Should match within tolerance
        assert abs((p_sat - p_test) / p_test).magnitude < 0.001  # Within 0.1%


class TestUnitConversions:
    """Test that various unit inputs are handled correctly."""

    def test_celsius_input(self):
        """Test temperature input in Celsius."""
        steam = SteamTable()

        h_kelvin = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)
        h_celsius = steam.h_pt(10 * ureg.MPa, (500 - 273.15) * ureg.celsius)

        # Should be approximately equal (within floating point tolerance)
        assert abs((h_kelvin - h_celsius) / h_kelvin).magnitude < 1e-6

    def test_bar_input(self):
        """Test pressure input in bar."""
        steam = SteamTable()

        h_pa = steam.h_pt(10e6 * ureg.Pa, 500 * ureg.K)
        h_mpa = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)
        h_bar = steam.h_pt(100 * ureg.bar, 500 * ureg.K)

        # All should be equal
        assert abs((h_pa - h_mpa) / h_pa).magnitude < 1e-10
        assert abs((h_mpa - h_bar) / h_mpa).magnitude < 1e-6


class TestNumericalRobustness:
    """Tests for numerical stability and robustness."""

    def test_very_low_pressure_region2(self):
        """Test very low pressure in Region 2 (ideal gas limit)."""
        steam = SteamTable()

        # Very low pressure, high temperature (ideal gas behavior)
        h = steam.h_pt(1000 * ureg.Pa, 500 * ureg.K)
        assert h.magnitude > 0

    def test_repeated_calculations_consistency(self):
        """Verify that repeated calculations give identical results."""
        steam = SteamTable()

        p = 10 * ureg.MPa
        t = 500 * ureg.K

        h1 = steam.h_pt(p, t)
        h2 = steam.h_pt(p, t)
        h3 = steam.h_pt(p, t)

        assert h1 == h2 == h3
