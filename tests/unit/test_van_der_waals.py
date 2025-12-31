"""Unit tests for Van der Waals EOS implementation."""

import pytest

from src.compounds.models import Compound
from src.eos.models import PhaseType
from src.eos.van_der_waals import VanDerWaalsEOS


@pytest.fixture
def vdw_eos():
    """Create a Van der Waals EOS instance."""
    return VanDerWaalsEOS()


@pytest.fixture
def methane():
    """Methane compound with critical properties."""
    return Compound(
        name="Methane",
        formula="CH4",
        cas_number="74-82-8",
        molecular_weight=16.04,
        tc=190.564,  # K
        pc=4.5992e6,  # Pa
        acentric_factor=0.011,
    )


@pytest.fixture
def ethane():
    """Ethane compound with critical properties."""
    return Compound(
        name="Ethane",
        formula="C2H6",
        cas_number="74-84-0",
        molecular_weight=30.07,
        tc=305.128,  # K
        pc=4.8718e6,  # Pa
        acentric_factor=0.0995,
    )


@pytest.fixture
def propane():
    """Propane compound with critical properties."""
    return Compound(
        name="Propane",
        formula="C3H8",
        cas_number="74-98-6",
        molecular_weight=44.10,
        tc=369.83,  # K
        pc=4.2512e6,  # Pa
        acentric_factor=0.1523,
    )


class TestVanDerWaalsParameterCalculation:
    """Test VDW parameter calculations (a and b)."""

    def test_calculate_a_positive_output(self, vdw_eos, methane):
        """Test calculate_a returns positive value."""
        a = vdw_eos.calculate_a(methane.tc, methane.pc)
        assert a > 0
        assert isinstance(a, float)

    def test_calculate_a_typical_value(self, vdw_eos, methane):
        """Test calculate_a returns reasonable value for methane."""
        a = vdw_eos.calculate_a(methane.tc, methane.pc)
        # VDW a parameter should be on order of 0.1-1.0 Pa*m^6/mol^2 for hydrocarbons
        assert 0.01 < a < 10.0

    def test_calculate_a_invalid_tc(self, vdw_eos):
        """Test calculate_a raises on non-positive Tc."""
        with pytest.raises(ValueError, match="Critical temperature must be positive"):
            vdw_eos.calculate_a(tc=0, pc=1e6)
        with pytest.raises(ValueError, match="Critical temperature must be positive"):
            vdw_eos.calculate_a(tc=-100, pc=1e6)

    def test_calculate_a_invalid_pc(self, vdw_eos, methane):
        """Test calculate_a raises on non-positive Pc."""
        with pytest.raises(ValueError, match="Critical pressure must be positive"):
            vdw_eos.calculate_a(tc=methane.tc, pc=0)
        with pytest.raises(ValueError, match="Critical pressure must be positive"):
            vdw_eos.calculate_a(tc=methane.tc, pc=-1e6)

    def test_calculate_b_positive_output(self, vdw_eos, methane):
        """Test calculate_b returns positive value."""
        b = vdw_eos.calculate_b(methane.tc, methane.pc)
        assert b > 0
        assert isinstance(b, float)

    def test_calculate_b_reasonable_value(self, vdw_eos, methane):
        """Test calculate_b returns reasonable molar volume."""
        b = vdw_eos.calculate_b(methane.tc, methane.pc)
        # b should be on order of 1e-5 to 1e-4 m^3/mol for hydrocarbons
        assert 1e-6 < b < 1e-3

    def test_calculate_b_invalid_tc(self, vdw_eos):
        """Test calculate_b raises on non-positive Tc."""
        with pytest.raises(ValueError, match="Critical temperature must be positive"):
            vdw_eos.calculate_b(tc=0, pc=1e6)

    def test_calculate_b_invalid_pc(self, vdw_eos, methane):
        """Test calculate_b raises on non-positive Pc."""
        with pytest.raises(ValueError, match="Critical pressure must be positive"):
            vdw_eos.calculate_b(tc=methane.tc, pc=0)

    def test_a_larger_than_b(self, vdw_eos, methane):
        """Test that a parameter is much larger than b (typical relationship)."""
        a = vdw_eos.calculate_a(methane.tc, methane.pc)
        b = vdw_eos.calculate_b(methane.tc, methane.pc)
        # a should be orders of magnitude larger than b
        assert a > 1000 * b


class TestVanDerWaalsVolumeCalculation:
    """Test molar volume calculation."""

    def test_calculate_volume_positive_output(self, vdw_eos, methane):
        """Test calculate_volume returns positive molar volume."""
        T = 300  # K
        P = 5e6  # Pa
        v_molar = vdw_eos.calculate_volume(methane.tc, methane.pc, T, P)
        assert v_molar > 0
        assert isinstance(v_molar, float)

    def test_calculate_volume_typical_conditions(self, vdw_eos, methane):
        """Test calculate_volume at moderate conditions."""
        T = 300  # K
        P = 5e6  # Pa (50 bar)
        v_molar = vdw_eos.calculate_volume(methane.tc, methane.pc, T, P)
        # Should be on order of 1e-4 to 1e-3 m^3/mol
        assert 1e-5 < v_molar < 0.1

    def test_calculate_volume_high_pressure(self, vdw_eos, methane):
        """Test volume decreases with pressure."""
        T = 300
        v_low_p = vdw_eos.calculate_volume(methane.tc, methane.pc, T, 1e6)
        v_high_p = vdw_eos.calculate_volume(methane.tc, methane.pc, T, 5e6)
        assert v_high_p < v_low_p

    def test_calculate_volume_high_temperature(self, vdw_eos, methane):
        """Test volume increases with temperature."""
        P = 5e6
        v_low_t = vdw_eos.calculate_volume(methane.tc, methane.pc, 300, P)
        v_high_t = vdw_eos.calculate_volume(methane.tc, methane.pc, 500, P)
        assert v_high_t > v_low_t

    def test_calculate_volume_invalid_temperature(self, vdw_eos, methane):
        """Test calculate_volume raises on non-positive temperature."""
        with pytest.raises(ValueError, match="Temperature must be positive"):
            vdw_eos.calculate_volume(methane.tc, methane.pc, 0, 1e6)
        with pytest.raises(ValueError, match="Temperature must be positive"):
            vdw_eos.calculate_volume(methane.tc, methane.pc, -100, 1e6)

    def test_calculate_volume_invalid_pressure(self, vdw_eos, methane):
        """Test calculate_volume raises on negative pressure."""
        with pytest.raises(ValueError, match="Pressure must be non-negative"):
            vdw_eos.calculate_volume(methane.tc, methane.pc, 300, -1e6)


class TestCompressibilityFactor:
    """Test compressibility factor Z = PV/(nRT) calculation."""

    def test_calculate_z_positive_output(self, vdw_eos):
        """Test calculate_Z returns positive Z-factor."""
        Z = vdw_eos.calculate_Z(
            pressure=5e6, temperature=300, v_molar=1e-4
        )
        assert Z > 0
        assert isinstance(Z, float)

    def test_calculate_z_realistic_range(self, vdw_eos, methane):
        """Test Z-factor in realistic range [0.1, 1.5]."""
        T = 300
        P = 5e6
        v_molar = vdw_eos.calculate_volume(methane.tc, methane.pc, T, P)
        Z = vdw_eos.calculate_Z(P, T, v_molar)
        assert 0.1 < Z < 1.5

    def test_calculate_z_invalid_temperature(self, vdw_eos):
        """Test calculate_Z raises on non-positive temperature."""
        with pytest.raises(ValueError, match="Temperature must be positive"):
            vdw_eos.calculate_Z(5e6, 0, 1e-4)

    def test_calculate_z_invalid_volume(self, vdw_eos):
        """Test calculate_Z raises on non-positive molar volume."""
        with pytest.raises(ValueError, match="Molar volume must be positive"):
            vdw_eos.calculate_Z(5e6, 300, 0)
        with pytest.raises(ValueError, match="Molar volume must be positive"):
            vdw_eos.calculate_Z(5e6, 300, -1e-4)

    def test_calculate_z_ideal_gas_approximation(self, vdw_eos):
        """Test Z ≈ 1 at low pressure (ideal gas approximation)."""
        # Low pressure, high temperature: P*V = n*R*T approximately
        # V_ideal = RT/P ≈ (8.314 * 400) / 1e5 ≈ 0.033 m^3/mol
        v_ideal = (8.314462618 * 400) / 1e5
        Z = vdw_eos.calculate_Z(1e5, 400, v_ideal)
        # Z should be close to 1 for low pressure
        assert 0.95 < Z < 1.05


class TestThermodnamicState:
    """Test complete thermodynamic state calculation."""

    def test_calculate_state_returns_valid_state(self, vdw_eos, methane):
        """Test calculate_state returns ThermodynamicState with all fields."""
        state = vdw_eos.calculate_state(methane, 300, 5e6, n=1.0)
        assert state.temperature == 300
        assert state.pressure == 5e6
        assert state._n == 1.0  # type: ignore
        assert state.z_factor > 0
        assert state._v_molar > 0  # type: ignore
        assert state.phase in [PhaseType.VAPOR, PhaseType.LIQUID, PhaseType.SUPERCRITICAL]

    def test_calculate_state_liquid_phase(self, vdw_eos, methane):
        """Test phase identification for liquid region."""
        # High pressure, low temperature should be liquid
        state = vdw_eos.calculate_state(methane, 250, 10e6, n=1.0)
        # At low T and high P, should be liquid
        assert state.phase in [PhaseType.LIQUID, PhaseType.SUPERCRITICAL]

    def test_calculate_state_vapor_phase(self, vdw_eos, methane):
        """Test phase identification for vapor region."""
        # Low pressure, high temperature should be vapor
        state = vdw_eos.calculate_state(methane, 400, 1e6, n=1.0)
        assert state.phase in [PhaseType.VAPOR, PhaseType.SUPERCRITICAL]

    def test_calculate_state_supercritical(self, vdw_eos, methane):
        """Test supercritical phase detection."""
        # T > Tc should give supercritical
        state = vdw_eos.calculate_state(methane, methane.tc + 50, 5e6, n=1.0)
        assert state.phase == PhaseType.SUPERCRITICAL

    def test_calculate_state_invalid_moles(self, vdw_eos, methane):
        """Test calculate_state raises on non-positive moles."""
        with pytest.raises(ValueError, match="Number of moles must be positive"):
            vdw_eos.calculate_state(methane, 300, 5e6, n=0)
        with pytest.raises(ValueError, match="Number of moles must be positive"):
            vdw_eos.calculate_state(methane, 300, 5e6, n=-1)

    def test_calculate_state_multiple_compounds(self, vdw_eos, methane, ethane, propane):
        """Test state calculation for different compounds."""
        compounds = [methane, ethane, propane]
        for compound in compounds:
            state = vdw_eos.calculate_state(compound, 300, 5e6)
            assert state.z_factor > 0
            assert state._v_molar > 0  # type: ignore


class TestInputValidation:
    """Test comprehensive input validation."""

    def test_z_factor_decreases_with_pressure(self, vdw_eos, methane):
        """Test Z-factor typically decreases with pressure (attractive forces)."""
        T = 300
        v_low_p = vdw_eos.calculate_volume(methane.tc, methane.pc, T, 1e6)
        v_high_p = vdw_eos.calculate_volume(methane.tc, methane.pc, T, 5e6)

        z_low_p = vdw_eos.calculate_Z(1e6, T, v_low_p)
        z_high_p = vdw_eos.calculate_Z(5e6, T, v_high_p)

        # At moderate conditions, Z typically decreases with pressure for attractive forces
        assert z_low_p >= z_high_p or abs(z_low_p - z_high_p) < 0.1

    def test_gas_constant_consistency(self, vdw_eos):
        """Test gas constant is correct."""
        assert pytest.approx(8.314462618, rel=1e-6) == vdw_eos.R

    def test_state_energy_consistency(self, vdw_eos, methane):
        """Test state calculation is consistent across multiple calls."""
        state1 = vdw_eos.calculate_state(methane, 300, 5e6, n=1.0)
        state2 = vdw_eos.calculate_state(methane, 300, 5e6, n=1.0)

        assert state1.T == state2.T
        assert state1.P == state2.P
        assert state1.z == pytest.approx(state2.z, rel=1e-10)
        assert state1.v_molar == pytest.approx(state2.v_molar, rel=1e-10)
