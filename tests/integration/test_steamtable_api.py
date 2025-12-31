"""
Integration tests for SteamTable Python API.

Tests the public API with examples from quickstart.md to ensure usability
and correct Pint unit handling.
"""

import pytest
from pint import UnitRegistry

from iapws_if97 import SteamTable
from iapws_if97.exceptions import InputRangeError

ureg = UnitRegistry()


class TestBasicPTLookups:
    """Test basic pressure-temperature property lookups."""

    def test_enthalpy_lookup_region1(self):
        """Test enthalpy calculation in Region 1 (compressed liquid)."""
        steam = SteamTable()

        # Region 1: high pressure liquid
        h = steam.h_pt(10 * ureg.MPa, 300 * ureg.K)

        assert h.units == ureg.kJ / ureg.kg
        assert h.magnitude > 0
        assert h.magnitude < 500  # Liquid enthalpy should be relatively low

    def test_enthalpy_lookup_region2(self):
        """Test enthalpy calculation in Region 2 (superheated steam)."""
        steam = SteamTable()

        # Region 2: low pressure, moderate temperature
        h = steam.h_pt(0.1 * ureg.MPa, 400 * ureg.K)

        assert h.units == ureg.kJ / ureg.kg
        assert h.magnitude > 2000  # Steam enthalpy should be higher

    def test_entropy_lookup(self):
        """Test entropy calculation."""
        steam = SteamTable()

        s = steam.s_pt(1 * ureg.MPa, 500 * ureg.K)

        assert s.units == ureg.kJ / (ureg.kg * ureg.K)
        assert s.magnitude > 0

    def test_internal_energy_lookup(self):
        """Test internal energy calculation."""
        steam = SteamTable()

        u = steam.u_pt(5 * ureg.MPa, 600 * ureg.K)

        assert u.units == ureg.kJ / ureg.kg
        assert u.magnitude > 0

    def test_density_lookup(self):
        """Test density calculation."""
        steam = SteamTable()

        rho = steam.rho_pt(10 * ureg.MPa, 300 * ureg.K)

        assert rho.units == ureg.kg / (ureg.m**3)
        assert rho.magnitude > 0
        assert rho.magnitude > 900  # Liquid water density should be high


class TestUnitHandling:
    """Test Pint unit handling and conversions."""

    def test_pressure_in_bar(self):
        """Test that pressure in bar is handled correctly."""
        steam = SteamTable()

        h_mpa = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)
        h_bar = steam.h_pt(100 * ureg.bar, 500 * ureg.K)

        # Should be approximately equal (within floating point tolerance)
        assert abs((h_mpa - h_bar) / h_mpa).magnitude < 1e-6

    def test_temperature_in_kelvin(self):
        """Test temperature input in Kelvin."""
        steam = SteamTable()

        h = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)

        assert h.magnitude > 0

    def test_output_unit_extraction(self):
        """Test extracting magnitude and units from output."""
        steam = SteamTable()

        h = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)

        # Extract magnitude
        h_value = h.magnitude
        assert isinstance(h_value, float)

        # Convert units
        h_in_j_per_kg = h.to("J/kg")
        assert h_in_j_per_kg.magnitude == h_value * 1000  # kJ to J


class TestSaturationAPI:
    """Test saturation property API."""

    def test_t_sat_basic(self):
        """Test T_sat returns saturation properties."""
        steam = SteamTable()

        sat = steam.T_sat(1 * ureg.MPa)

        # Check that all required fields are present
        assert hasattr(sat, "saturation_temperature")
        assert hasattr(sat, "saturation_pressure")
        assert hasattr(sat, "enthalpy_liquid")
        assert hasattr(sat, "enthalpy_vapor")
        assert hasattr(sat, "entropy_liquid")
        assert hasattr(sat, "entropy_vapor")
        assert hasattr(sat, "density_liquid")
        assert hasattr(sat, "density_vapor")

    def test_t_sat_temperature_range(self):
        """Test T_sat returns reasonable saturation temperature."""
        steam = SteamTable()

        sat = steam.T_sat(1 * ureg.MPa)

        # At 1 MPa, T_sat should be around 453 K (180°C)
        t_sat_k = sat.saturation_temperature.to("K").magnitude
        assert 450 < t_sat_k < 460

    def test_p_sat_basic(self):
        """Test P_sat returns saturation properties."""
        steam = SteamTable()

        sat = steam.P_sat(373.15 * ureg.K)  # 100°C

        # Check structure
        assert hasattr(sat, "saturation_pressure")
        assert hasattr(sat, "saturation_temperature")

    def test_p_sat_pressure_range(self):
        """Test P_sat returns reasonable saturation pressure."""
        steam = SteamTable()

        sat = steam.P_sat(373.15 * ureg.K)  # 100°C

        # At 100°C, P_sat should be around 0.101325 MPa (1 atm)
        p_sat_mpa = sat.saturation_pressure.to("MPa").magnitude
        assert 0.09 < p_sat_mpa < 0.11

    def test_saturation_liquid_vapor_properties(self):
        """Test that liquid and vapor properties are correctly ordered."""
        steam = SteamTable()

        sat = steam.T_sat(1 * ureg.MPa)

        # Vapor enthalpy should be greater than liquid enthalpy
        assert sat.enthalpy_vapor.magnitude > sat.enthalpy_liquid.magnitude

        # Liquid density should be greater than vapor density
        assert sat.density_liquid.magnitude > sat.density_vapor.magnitude


class TestErrorHandling:
    """Test exception handling and error messages."""

    def test_input_range_error_low_pressure(self):
        """Test InputRangeError for pressure below valid range."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(100 * ureg.Pa, 500 * ureg.K)  # Well below triple point

        error_msg = str(exc_info.value).lower()
        assert "pressure" in error_msg

    def test_input_range_error_high_temperature(self):
        """Test InputRangeError for temperature above valid range."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(10 * ureg.MPa, 1000 * ureg.K)  # Above max temperature

        error_msg = str(exc_info.value).lower()
        assert "temperature" in error_msg

    def test_error_message_contains_parameter_name(self):
        """Test that error messages include parameter names."""
        steam = SteamTable()

        with pytest.raises(InputRangeError) as exc_info:
            steam.h_pt(10 * ureg.MPa, 1000 * ureg.K)

        error_msg = str(exc_info.value)
        # Should mention either Temperature or the value
        assert "temperature" in error_msg.lower() or "1000" in error_msg or "863" in error_msg


class TestConsistencyAndPhysics:
    """Test thermodynamic consistency and physical reasonableness."""

    def test_properties_positive(self):
        """Test that all properties are positive."""
        steam = SteamTable()

        p = 10 * ureg.MPa
        t = 500 * ureg.K

        h = steam.h_pt(p, t)
        s = steam.s_pt(p, t)
        u = steam.u_pt(p, t)
        rho = steam.rho_pt(p, t)

        assert h.magnitude > 0
        assert s.magnitude > 0
        assert u.magnitude > 0
        assert rho.magnitude > 0

    def test_enthalpy_increases_with_temperature(self):
        """Test that enthalpy increases with temperature at constant pressure."""
        steam = SteamTable()

        p = 10 * ureg.MPa

        h1 = steam.h_pt(p, 300 * ureg.K)
        h2 = steam.h_pt(p, 400 * ureg.K)
        h3 = steam.h_pt(p, 500 * ureg.K)

        assert h2.magnitude > h1.magnitude
        assert h3.magnitude > h2.magnitude

    def test_density_decreases_with_temperature_gas(self):
        """Test that density decreases with temperature for gas phase."""
        steam = SteamTable()

        # Region 2 (gas)
        p = 0.1 * ureg.MPa

        rho1 = steam.rho_pt(p, 400 * ureg.K)
        rho2 = steam.rho_pt(p, 500 * ureg.K)

        # For ideal gas, density decreases with temperature at constant pressure
        assert rho2.magnitude < rho1.magnitude


class TestQuickstartExamples:
    """Test examples from quickstart.md to ensure they work."""

    def test_quickstart_example_1(self):
        """Test first example from quickstart: 10 MPa, 500K."""
        steam = SteamTable()

        h = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)

        # Should return a valid Pint Quantity
        assert h.units == ureg.kJ / ureg.kg
        assert h.magnitude > 0

    def test_quickstart_example_2(self):
        """Test second example from quickstart: 0.1 MPa, 200°C (converted to K)."""
        steam = SteamTable()

        # Convert Celsius to Kelvin: 200°C = 473.15 K
        s = steam.s_pt(0.1 * ureg.MPa, 473.15 * ureg.K)

        # Should return valid entropy
        assert s.units == ureg.kJ / (ureg.kg * ureg.K)
        assert s.magnitude > 0

    def test_quickstart_saturation_example(self):
        """Test saturation example from quickstart: T_sat at 1 MPa."""
        steam = SteamTable()

        sat = steam.T_sat(1 * ureg.MPa)

        # Check that saturation temperature is reasonable
        assert sat.saturation_temperature.magnitude > 400  # Should be > 400 K
        assert sat.saturation_temperature.magnitude < 500  # Should be < 500 K

        # Check that liquid/vapor properties exist
        assert sat.enthalpy_liquid.magnitude > 0
        assert sat.enthalpy_vapor.magnitude > sat.enthalpy_liquid.magnitude


class TestAPIUsability:
    """Test API usability and design."""

    def test_steamtable_instantiation(self):
        """Test that SteamTable can be instantiated without arguments."""
        steam = SteamTable()
        assert steam is not None

    def test_method_signatures(self):
        """Test that all public methods have expected signatures."""
        steam = SteamTable()

        # Check that methods exist
        assert hasattr(steam, "h_pt")
        assert hasattr(steam, "s_pt")
        assert hasattr(steam, "u_pt")
        assert hasattr(steam, "rho_pt")
        assert hasattr(steam, "T_sat")
        assert hasattr(steam, "P_sat")

        # Check that methods are callable
        assert callable(steam.h_pt)
        assert callable(steam.s_pt)
        assert callable(steam.u_pt)
        assert callable(steam.rho_pt)
        assert callable(steam.T_sat)
        assert callable(steam.P_sat)
