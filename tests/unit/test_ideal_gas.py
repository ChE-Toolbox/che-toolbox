"""Unit tests for Ideal Gas Law implementation."""

import pytest

from src.compounds.models import Compound
from src.eos.ideal_gas import IdealGasEOS
from src.eos.models import PhaseType


@pytest.fixture
def ideal_gas():
    """Create an Ideal Gas EOS instance."""
    return IdealGasEOS()


@pytest.fixture
def methane():
    """Methane compound (unused for ideal gas but useful for consistency)."""
    return Compound(
        name="Methane",
        formula="CH4",
        tc=190.564,
        pc=4.5992e6,
        acentric_factor=0.011,
    )


@pytest.fixture
def water():
    """Water compound."""
    return Compound(
        name="Water",
        formula="H2O",
        tc=647.096,
        pc=22.064e6,
        acentric_factor=0.344,
    )


class TestIdealGasVolumeCalculation:
    """Test volume calculations for ideal gas."""

    def test_calculate_volume_positive_output(self, ideal_gas):
        """Test calculate_volume returns positive volume."""
        V = ideal_gas.calculate_volume(n=1.0, temperature=298.15, pressure=101325)
        assert V > 0
        assert isinstance(V, float)

    def test_calculate_volume_stp_condition(self, ideal_gas):
        """Test volume at STP (Standard Temperature and Pressure).

        At STP: T=273.15K, P=101325 Pa
        For 1 mole: V = nRT/P = 1*8.314462618*273.15/101325 ≈ 0.022414 m³
        """
        V = ideal_gas.calculate_volume(n=1.0, temperature=273.15, pressure=101325)
        # Should be approximately 0.022414 m^3/mol at STP
        assert pytest.approx(0.022414, rel=1e-3) == V

    def test_calculate_volume_room_conditions(self, ideal_gas):
        """Test volume at room conditions (25°C, 1 atm).

        T=298.15K, P=101325 Pa
        V = 1*8.314462618*298.15/101325 ≈ 0.024465 m³
        """
        V = ideal_gas.calculate_volume(n=1.0, temperature=298.15, pressure=101325)
        assert pytest.approx(0.024465, rel=1e-3) == V

    def test_calculate_volume_scales_with_moles(self, ideal_gas):
        """Test volume scales linearly with number of moles."""
        V1 = ideal_gas.calculate_volume(n=1.0, temperature=300, pressure=1e5)
        V2 = ideal_gas.calculate_volume(n=2.0, temperature=300, pressure=1e5)
        assert pytest.approx(2 * V1, rel=1e-10) == V2

    def test_calculate_volume_scales_with_temperature(self, ideal_gas):
        """Test volume scales linearly with temperature (V ∝ T at constant P)."""
        V1 = ideal_gas.calculate_volume(n=1.0, temperature=300, pressure=1e5)
        V2 = ideal_gas.calculate_volume(n=1.0, temperature=600, pressure=1e5)
        assert pytest.approx(2 * V1, rel=1e-10) == V2

    def test_calculate_volume_inverse_with_pressure(self, ideal_gas):
        """Test volume is inversely proportional to pressure (V ∝ 1/P at constant T)."""
        V1 = ideal_gas.calculate_volume(n=1.0, temperature=300, pressure=1e5)
        V2 = ideal_gas.calculate_volume(n=1.0, temperature=300, pressure=2e5)
        assert pytest.approx(V1 / 2, rel=1e-10) == V2

    def test_calculate_volume_invalid_temperature(self, ideal_gas):
        """Test calculate_volume raises on non-positive temperature."""
        with pytest.raises(ValueError, match="Temperature must be positive"):
            ideal_gas.calculate_volume(n=1.0, temperature=0, pressure=1e5)
        with pytest.raises(ValueError, match="Temperature must be positive"):
            ideal_gas.calculate_volume(n=1.0, temperature=-100, pressure=1e5)

    def test_calculate_volume_invalid_pressure(self, ideal_gas):
        """Test calculate_volume raises on non-positive pressure."""
        with pytest.raises(ValueError, match="Pressure must be positive"):
            ideal_gas.calculate_volume(n=1.0, temperature=300, pressure=0)
        with pytest.raises(ValueError, match="Pressure must be positive"):
            ideal_gas.calculate_volume(n=1.0, temperature=300, pressure=-1e5)

    def test_calculate_volume_invalid_moles(self, ideal_gas):
        """Test calculate_volume raises on non-positive moles."""
        with pytest.raises(ValueError, match="Number of moles must be positive"):
            ideal_gas.calculate_volume(n=0, temperature=300, pressure=1e5)
        with pytest.raises(ValueError, match="Number of moles must be positive"):
            ideal_gas.calculate_volume(n=-1, temperature=300, pressure=1e5)


class TestIdealGasMolarVolumeCalculation:
    """Test molar volume calculations."""

    def test_calculate_volume_molar_positive_output(self, ideal_gas):
        """Test calculate_volume_molar returns positive molar volume."""
        v_m = ideal_gas.calculate_volume_molar(temperature=300, pressure=1e5)
        assert v_m > 0
        assert isinstance(v_m, float)

    def test_calculate_volume_molar_at_stp(self, ideal_gas):
        """Test molar volume at STP."""
        v_m = ideal_gas.calculate_volume_molar(temperature=273.15, pressure=101325)
        assert v_m == pytest.approx(0.022414, rel=1e-3)

    def test_calculate_volume_molar_consistency(self, ideal_gas):
        """Test molar volume is consistent with total volume."""
        n = 2.5
        T = 350
        P = 2e5
        V_total = ideal_gas.calculate_volume(n=n, temperature=T, pressure=P)
        v_molar = ideal_gas.calculate_volume_molar(temperature=T, pressure=P)
        assert V_total == pytest.approx(n * v_molar, rel=1e-10)

    def test_calculate_volume_molar_invalid_temperature(self, ideal_gas):
        """Test raises on non-positive temperature."""
        with pytest.raises(ValueError, match="Temperature must be positive"):
            ideal_gas.calculate_volume_molar(temperature=0, pressure=1e5)

    def test_calculate_volume_molar_invalid_pressure(self, ideal_gas):
        """Test raises on non-positive pressure."""
        with pytest.raises(ValueError, match="Pressure must be positive"):
            ideal_gas.calculate_volume_molar(temperature=300, pressure=0)


class TestCompressibilityFactor:
    """Test compressibility factor for ideal gas."""

    def test_calculate_z_always_unity(self, ideal_gas):
        """Test Z-factor is always exactly 1.0 for ideal gas."""
        Z1 = ideal_gas.calculate_Z(pressure=1e5, temperature=300, v_molar=1e-4)
        Z2 = ideal_gas.calculate_Z(pressure=5e6, temperature=500, v_molar=1e-5)
        Z3 = ideal_gas.calculate_Z(pressure=1e3, temperature=100, v_molar=1e-2)

        assert Z1 == 1.0
        assert Z2 == 1.0
        assert Z3 == 1.0

    def test_calculate_z_exact_value(self, ideal_gas):
        """Test Z is exactly 1.0 (not approximate)."""
        Z = ideal_gas.calculate_Z(pressure=2.5e5, temperature=375, v_molar=1.234e-4)
        assert Z == 1.0 or Z == 1.0  # Exact equality
        assert isinstance(Z, float)


class TestThermodnamicState:
    """Test complete thermodynamic state calculation."""

    def test_calculate_state_returns_valid_state(self, ideal_gas, methane):
        """Test calculate_state returns valid ThermodynamicState."""
        state = ideal_gas.calculate_state(
            compound=methane, temperature=300, pressure=1e5, n=1.0
        )
        assert state.T == 300
        assert state.P == 1e5
        assert state.n == 1.0
        assert state.z == 1.0
        assert state.v_molar > 0
        assert state.phase == PhaseType.VAPOR

    def test_calculate_state_default_conditions(self, ideal_gas):
        """Test calculate_state with default conditions."""
        state = ideal_gas.calculate_state()
        assert state.T == 298.15
        assert state.P == 101325
        assert state.n == 1.0
        assert state.z == 1.0
        assert state.phase == PhaseType.VAPOR

    def test_calculate_state_always_vapor_phase(self, ideal_gas):
        """Test ideal gas is always vapor phase."""
        state1 = ideal_gas.calculate_state(temperature=100, pressure=1e6)
        state2 = ideal_gas.calculate_state(temperature=1000, pressure=1e3)
        assert state1.phase == PhaseType.VAPOR
        assert state2.phase == PhaseType.VAPOR

    def test_calculate_state_without_compound(self, ideal_gas):
        """Test calculate_state works without compound (compound is unused)."""
        state = ideal_gas.calculate_state(
            compound=None, temperature=350, pressure=2e5, n=1.5
        )
        assert state.T == 350
        assert state.P == 2e5
        assert state.n == 1.5
        assert state.z == 1.0

    def test_calculate_state_invalid_temperature(self, ideal_gas, methane):
        """Test calculate_state raises on non-positive temperature."""
        with pytest.raises(ValueError, match="Temperature must be positive"):
            ideal_gas.calculate_state(compound=methane, temperature=0, pressure=1e5)

    def test_calculate_state_invalid_pressure(self, ideal_gas, methane):
        """Test calculate_state raises on non-positive pressure."""
        with pytest.raises(ValueError, match="Pressure must be positive"):
            ideal_gas.calculate_state(compound=methane, temperature=300, pressure=0)

    def test_calculate_state_invalid_moles(self, ideal_gas, methane):
        """Test calculate_state raises on non-positive moles."""
        with pytest.raises(ValueError, match="Number of moles must be positive"):
            ideal_gas.calculate_state(compound=methane, temperature=300, pressure=1e5, n=0)


class TestGasConstant:
    """Test gas constant value."""

    def test_gas_constant_value(self, ideal_gas):
        """Test gas constant R is correct."""
        assert pytest.approx(8.314462618, rel=1e-10) == ideal_gas.R

    def test_gas_constant_type(self, ideal_gas):
        """Test gas constant is a float."""
        assert isinstance(ideal_gas.R, float)


class TestIdealGasComparisonWithReality:
    """Test where ideal gas deviates from real behavior."""

    def test_molar_volume_comparison(self, ideal_gas):
        """Test molar volumes are predictable with ideal gas law.

        For verification, can be compared with real gas models later.
        """
        conditions = [
            (300, 1e5),  # Low pressure
            (300, 1e6),  # Moderate pressure
            (300, 1e7),  # High pressure
            (500, 1e5),  # High temperature
        ]

        for T, P in conditions:
            v_m = ideal_gas.calculate_volume_molar(T, P)
            # V = RT/P
            expected = (8.314462618 * T) / P
            assert v_m == pytest.approx(expected, rel=1e-10)

    def test_state_consistency_across_calls(self, ideal_gas):
        """Test repeated calculations give identical results."""
        state1 = ideal_gas.calculate_state(temperature=350, pressure=1.5e5, n=2.0)
        state2 = ideal_gas.calculate_state(temperature=350, pressure=1.5e5, n=2.0)

        assert state1.z == state2.z == 1.0
        assert state1.v_molar == state2.v_molar
        assert state1.phase == state2.phase
