"""Unit conversion test suite for SC-004 success criterion.

This module tests at least 12 common unit conversion pairs to verify
mathematical correctness and dimensional consistency.

Success Criterion SC-004: Unit conversions work for 12+ common pairs
(K/C/F, Pa/bar/psi, kg/m³/lb/ft³, J/cal, etc.)
"""

import pytest

from chemeng_core.units import DimensionalityError, create_unit_handler


class TestUnitConversions:
    """Test suite for common engineering unit conversions."""

    @pytest.fixture
    def handler(self):
        """Create a unit handler instance for tests."""
        return create_unit_handler()

    # Temperature conversions (3 pairs)
    def test_kelvin_to_celsius(self, handler):
        """Test K to °C conversion."""
        result = handler.convert(373.15, "kelvin", "degC")
        assert abs(result - 100.0) < 0.01

    def test_celsius_to_fahrenheit(self, handler):
        """Test °C to °F conversion."""
        result = handler.convert(100, "degC", "degF")
        assert abs(result - 212.0) < 0.01

    def test_fahrenheit_to_kelvin(self, handler):
        """Test °F to K conversion."""
        result = handler.convert(32, "degF", "kelvin")
        assert abs(result - 273.15) < 0.01

    # Pressure conversions (4 pairs)
    def test_pascal_to_bar(self, handler):
        """Test Pa to bar conversion."""
        result = handler.convert(101325, "pascal", "bar")
        assert abs(result - 1.01325) < 0.0001

    def test_bar_to_psi(self, handler):
        """Test bar to psi conversion."""
        result = handler.convert(1, "bar", "psi")
        assert abs(result - 14.5038) < 0.001

    def test_psi_to_pascal(self, handler):
        """Test psi to Pa conversion."""
        result = handler.convert(14.6959, "psi", "pascal")
        assert abs(result - 101325) < 1.0

    def test_pascal_to_atm(self, handler):
        """Test Pa to atm conversion."""
        result = handler.convert(101325, "pascal", "atm")
        assert abs(result - 1.0) < 0.0001

    # Density conversions (2 pairs)
    def test_kg_m3_to_lb_ft3(self, handler):
        """Test kg/m³ to lb/ft³ conversion."""
        result = handler.convert(1000, "kg/m**3", "lb/ft**3")
        assert abs(result - 62.428) < 0.01

    def test_g_cm3_to_kg_m3(self, handler):
        """Test g/cm³ to kg/m³ conversion."""
        result = handler.convert(1, "g/cm**3", "kg/m**3")
        assert abs(result - 1000) < 0.01

    # Energy conversions (3 pairs)
    def test_joule_to_calorie(self, handler):
        """Test J to cal conversion."""
        result = handler.convert(4.184, "joule", "calorie")
        assert abs(result - 1.0) < 0.001

    def test_kj_to_btu(self, handler):
        """Test kJ to BTU conversion."""
        result = handler.convert(1.055, "kilojoule", "BTU")
        assert abs(result - 1.0) < 0.01

    def test_kj_mol_to_j_mol(self, handler):
        """Test kJ/mol to J/mol conversion."""
        result = handler.convert(1, "kJ/mol", "J/mol")
        assert abs(result - 1000) < 0.01

    # Total: 12 unit pairs tested

    def test_incompatible_units_raise_error(self, handler):
        """Test that converting incompatible units raises DimensionalityError."""
        with pytest.raises(DimensionalityError):
            handler.convert(100, "kelvin", "pascal")

    def test_is_compatible_temperature_pressure(self, handler):
        """Test dimensional compatibility checking."""
        assert handler.is_compatible("kelvin", "degC")
        assert handler.is_compatible("pascal", "bar")
        assert not handler.is_compatible("kelvin", "pascal")
        assert not handler.is_compatible("kg/m**3", "kelvin")


class TestQuantityConversions:
    """Test QuantityDTO conversion functionality."""

    @pytest.fixture
    def handler(self):
        """Create a unit handler instance."""
        return create_unit_handler()

    def test_convert_quantity_temperature(self, handler):
        """Test QuantityDTO conversion for temperature."""
        from chemeng_core.compounds.models import QuantityDTO

        t_kelvin = QuantityDTO(magnitude=373.15, unit="kelvin")
        t_celsius = handler.convert_quantity(t_kelvin, "degC")

        assert abs(t_celsius.magnitude - 100.0) < 0.01
        assert t_celsius.unit == "degC"

    def test_convert_quantity_pressure(self, handler):
        """Test QuantityDTO conversion for pressure."""
        from chemeng_core.compounds.models import QuantityDTO

        p_pa = QuantityDTO(magnitude=101325, unit="pascal")
        p_bar = handler.convert_quantity(p_pa, "bar")

        assert abs(p_bar.magnitude - 1.01325) < 0.0001
        assert p_bar.unit == "bar"

    def test_convert_quantity_immutable(self, handler):
        """Test that QuantityDTO conversions return new instances."""
        from chemeng_core.compounds.models import QuantityDTO

        original = QuantityDTO(magnitude=100, unit="degC")
        converted = handler.convert_quantity(original, "kelvin")

        # Original unchanged
        assert original.magnitude == 100
        assert original.unit == "degC"

        # New instance created
        assert converted.magnitude != original.magnitude
        assert converted.unit != original.unit
