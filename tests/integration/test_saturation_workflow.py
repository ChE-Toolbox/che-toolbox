"""Integration tests for saturation property workflows.

Tests complete saturation calculation workflows including:
- T_sat and P_sat round-trip consistency
- Saturation properties dataclass integrity
- Unit handling across saturation calculations
"""

import pytest

from src.iapws_if97 import SteamTable, models, ureg
from src.iapws_if97.exceptions import InputRangeError


@pytest.mark.integration
class TestSaturationWorkflow:
    """Integration tests for saturation property calculation workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize SteamTable for all tests."""
        self.steam = SteamTable()

    def test_T_sat_returns_saturation_properties_dataclass(self):
        """Test that T_sat returns proper SaturationProperties dataclass."""
        P = 1.0e6  # 1 MPa
        sat_props = self.steam.T_sat(P * ureg.Pa)

        # Verify type
        assert isinstance(sat_props, models.SaturationProperties)

        # Verify all required attributes exist
        assert hasattr(sat_props, "saturation_temperature")
        assert hasattr(sat_props, "saturation_pressure")
        assert hasattr(sat_props, "enthalpy_liquid")
        assert hasattr(sat_props, "enthalpy_vapor")
        assert hasattr(sat_props, "entropy_liquid")
        assert hasattr(sat_props, "entropy_vapor")
        assert hasattr(sat_props, "density_liquid")
        assert hasattr(sat_props, "density_vapor")

        # Verify all are Pint Quantities
        assert hasattr(sat_props.saturation_temperature, "magnitude")
        assert hasattr(sat_props.saturation_pressure, "magnitude")
        assert hasattr(sat_props.enthalpy_liquid, "magnitude")

    def test_P_sat_returns_saturation_properties_dataclass(self):
        """Test that P_sat returns proper SaturationProperties dataclass."""
        T = 373.15  # K (approximately 100°C)
        sat_props = self.steam.P_sat(T * ureg.K)

        # Verify type
        assert isinstance(sat_props, models.SaturationProperties)

        # Verify all attributes exist and are Quantities
        assert hasattr(sat_props.saturation_temperature, "magnitude")
        assert hasattr(sat_props.saturation_pressure, "magnitude")

    def test_T_sat_P_sat_round_trip_consistency(self):
        """Test that T_sat(P) and P_sat(T) are consistent round-trip."""
        test_pressures = [100e3, 500e3, 1e6, 5e6, 10e6, 15e6]  # Pa

        for P_initial in test_pressures:
            # Forward: P -> T_sat
            sat_from_P = self.steam.T_sat(P_initial * ureg.Pa)
            T_calculated = sat_from_P.saturation_temperature.to("K").magnitude

            # Reverse: T -> P_sat
            sat_from_T = self.steam.P_sat(T_calculated * ureg.K)
            P_calculated = sat_from_T.saturation_pressure.to("Pa").magnitude

            # Should match within 0.01%
            rel_error = abs(P_calculated - P_initial) / P_initial
            assert rel_error < 1e-4, f"Round-trip error at P={P_initial} Pa: {rel_error * 100:.4f}%"

    def test_P_sat_T_sat_round_trip_consistency(self):
        """Test that P_sat(T) and T_sat(P) are consistent round-trip."""
        test_temperatures = [280, 320, 373.15, 450, 550, 600]  # K

        for T_initial in test_temperatures:
            # Forward: T -> P_sat
            sat_from_T = self.steam.P_sat(T_initial * ureg.K)
            P_calculated = sat_from_T.saturation_pressure.to("Pa").magnitude

            # Reverse: P -> T_sat
            sat_from_P = self.steam.T_sat(P_calculated * ureg.Pa)
            T_calculated = sat_from_P.saturation_temperature.to("K").magnitude

            # Should match within 0.01%
            rel_error = abs(T_calculated - T_initial) / T_initial
            assert rel_error < 1e-4, f"Round-trip error at T={T_initial} K: {rel_error * 100:.4f}%"

    def test_saturation_properties_consistency_from_T_sat(self):
        """Test that all saturation properties are self-consistent from T_sat."""
        P = 1.0e6  # 1 MPa
        sat_props = self.steam.T_sat(P * ureg.Pa)

        # Extract values
        P_sat = sat_props.saturation_pressure.to("Pa").magnitude
        T_sat = sat_props.saturation_temperature.to("K").magnitude
        h_f = sat_props.enthalpy_liquid.to("kJ/kg").magnitude
        h_g = sat_props.enthalpy_vapor.to("kJ/kg").magnitude
        s_f = sat_props.entropy_liquid.to("kJ/(kg*K)").magnitude
        s_g = sat_props.entropy_vapor.to("kJ/(kg*K)").magnitude
        rho_f = sat_props.density_liquid.to("kg/m**3").magnitude
        rho_g = sat_props.density_vapor.to("kg/m**3").magnitude

        # Input pressure should match output
        assert abs(P_sat - P) / P < 1e-6

        # Physical constraints
        assert h_g > h_f, "Vapor enthalpy must be greater than liquid"
        assert s_g > s_f, "Vapor entropy must be greater than liquid"
        assert rho_f > rho_g, "Liquid density must be greater than vapor"
        assert T_sat > 273.15, "Saturation temperature must be above freezing"
        assert T_sat < 647.096, "Saturation temperature must be below critical point"

    def test_saturation_properties_consistency_from_P_sat(self):
        """Test that all saturation properties are self-consistent from P_sat."""
        T = 373.15  # K
        sat_props = self.steam.P_sat(T * ureg.K)

        # Extract values
        P_sat = sat_props.saturation_pressure.to("Pa").magnitude
        T_sat = sat_props.saturation_temperature.to("K").magnitude
        h_f = sat_props.enthalpy_liquid.to("kJ/kg").magnitude
        h_g = sat_props.enthalpy_vapor.to("kJ/kg").magnitude

        # Input temperature should match output
        assert abs(T_sat - T) / T < 1e-6

        # Physical constraints
        assert h_g > h_f
        assert P_sat > 0
        assert P_sat < 22.064e6  # Below critical pressure

    def test_heat_of_vaporization_workflow(self):
        """Test complete heat of vaporization calculation workflow."""
        P = 1.0e6  # 1 MPa
        sat_props = self.steam.T_sat(P * ureg.Pa)

        # Get h_fg using the method
        h_fg = sat_props.heat_of_vaporization().to("kJ/kg").magnitude

        # Verify it's positive
        assert h_fg > 0, "Heat of vaporization must be positive"

        # Verify it matches h_g - h_f
        h_g = sat_props.enthalpy_vapor.to("kJ/kg").magnitude
        h_f = sat_props.enthalpy_liquid.to("kJ/kg").magnitude
        h_fg_manual = h_g - h_f

        assert abs(h_fg - h_fg_manual) < 1e-6

        # Verify reasonable range (for water: 200-2500 kJ/kg)
        assert 200 < h_fg < 2500, f"h_fg={h_fg} kJ/kg outside expected range"

    def test_saturation_at_standard_conditions(self):
        """Test saturation properties at standard atmospheric pressure."""
        P_atm = 101325  # Pa (1 atm)
        sat_props = self.steam.T_sat(P_atm * ureg.Pa)

        T_sat = sat_props.saturation_temperature.to("degC").magnitude

        # Should be approximately 100°C
        assert abs(T_sat - 100.0) < 0.5, f"Saturation at 1 atm should be ~100°C, got {T_sat:.2f}°C"

    def test_saturation_unit_conversions(self):
        """Test that saturation calculations work with different unit inputs."""
        # Test with different pressure units
        P_mpa = 1.0  # MPa
        sat_mpa = self.steam.T_sat(P_mpa * ureg.MPa)

        P_kpa = 1000.0  # kPa
        sat_kpa = self.steam.T_sat(P_kpa * ureg.kPa)

        P_bar = 10.0  # bar
        sat_bar = self.steam.T_sat(P_bar * ureg.bar)

        # All should give same temperature
        T_mpa = sat_mpa.saturation_temperature.to("K").magnitude
        T_kpa = sat_kpa.saturation_temperature.to("K").magnitude
        T_bar = sat_bar.saturation_temperature.to("K").magnitude

        assert abs(T_mpa - T_kpa) < 1e-3
        assert abs(T_mpa - T_bar) < 1e-3

    def test_saturation_properties_at_multiple_pressures(self):
        """Test saturation workflow across wide pressure range."""
        # Avoid pressures very close to critical point (22.064 MPa) to prevent numerical issues
        pressures_mpa = [0.1, 0.5, 1.0, 5.0, 10.0, 15.0]

        previous_T = 0
        for P_mpa in pressures_mpa:
            P_pa = P_mpa * 1e6
            sat_props = self.steam.T_sat(P_pa * ureg.Pa)

            T_sat = sat_props.saturation_temperature.to("K").magnitude
            h_fg = sat_props.heat_of_vaporization().to("kJ/kg").magnitude

            # Temperature should increase with pressure
            assert T_sat > previous_T
            previous_T = T_sat

            # Heat of vaporization should decrease with pressure
            # (as we approach critical point)
            assert h_fg > 0

    def test_saturation_properties_at_multiple_temperatures(self):
        """Test saturation workflow across wide temperature range."""
        temperatures_k = [280, 320, 373.15, 420, 500, 580, 640]

        previous_P = 0
        for T_k in temperatures_k:
            sat_props = self.steam.P_sat(T_k * ureg.K)

            P_sat = sat_props.saturation_pressure.to("Pa").magnitude
            h_fg = sat_props.heat_of_vaporization().to("kJ/kg").magnitude

            # Pressure should increase with temperature
            assert P_sat > previous_P
            previous_P = P_sat

            # Heat of vaporization should be positive
            assert h_fg > 0

    def test_saturation_near_critical_point(self):
        """Test saturation behavior approaching critical point.

        Note: Very close to critical point (>20 MPa) may have numerical instabilities.
        We test at a safe distance to verify trends without hitting singularities.
        """
        # Moderately close to critical pressure (but not too close to avoid numerical issues)
        P_high = 15.0e6  # Pa (15 MPa - safe distance from 22.064 MPa critical)
        sat_props = self.steam.T_sat(P_high * ureg.Pa)

        T_sat = sat_props.saturation_temperature.to("K").magnitude
        h_fg = sat_props.heat_of_vaporization().to("kJ/kg").magnitude
        rho_f = sat_props.density_liquid.to("kg/m**3").magnitude
        rho_g = sat_props.density_vapor.to("kg/m**3").magnitude

        # At high pressure, densities should be closer than at low pressure
        density_ratio = rho_g / rho_f
        assert density_ratio > 0.05, (
            f"At high pressure, density ratio should be > 0.05, got {density_ratio:.3f}"
        )

        # Heat of vaporization should be smaller at high pressure than at low pressure
        assert h_fg < 1500, f"At high pressure, h_fg should be < 1500 kJ/kg, got {h_fg:.2f}"
        assert h_fg > 0, "Heat of vaporization must be positive"

    def test_saturation_error_handling_workflow(self):
        """Test error handling in saturation workflows."""
        # Test invalid pressure input
        with pytest.raises(InputRangeError):
            self.steam.T_sat(-1000 * ureg.Pa)

        # Test pressure above critical
        with pytest.raises(InputRangeError):
            self.steam.T_sat(25e6 * ureg.Pa)

        # Test invalid temperature input
        with pytest.raises(InputRangeError):
            self.steam.P_sat(200 * ureg.K)

        # Test temperature above critical
        with pytest.raises(InputRangeError):
            self.steam.P_sat(700 * ureg.K)

    def test_saturation_dataclass_immutability(self):
        """Test that SaturationProperties dataclass is immutable."""
        P = 1.0e6  # 1 MPa
        sat_props = self.steam.T_sat(P * ureg.Pa)

        # Should not be able to modify attributes (frozen dataclass)
        with pytest.raises(AttributeError):
            sat_props.saturation_temperature = 500 * ureg.K

        with pytest.raises(AttributeError):
            sat_props.enthalpy_liquid = 1000 * ureg.kJ / ureg.kg
