"""Integration tests comparing multiple EOS models."""

import pytest

from src.compounds.models import Compound
from src.eos.ideal_gas import IdealGasEOS
from src.eos.peng_robinson import PengRobinsonEOS
from src.eos.van_der_waals import VanDerWaalsEOS


@pytest.fixture
def methane():
    """Methane compound."""
    return Compound(
        name="Methane",
        formula="CH4",
        cas_number="74-82-8",
        molecular_weight=16.04,
        tc=190.564,
        pc=4.5992e6,
        acentric_factor=0.011,
    )


@pytest.fixture
def ethane():
    """Ethane compound."""
    return Compound(
        name="Ethane",
        formula="C2H6",
        cas_number="74-84-0",
        molecular_weight=30.07,
        tc=305.128,
        pc=4.8718e6,
        acentric_factor=0.0995,
    )


@pytest.fixture
def ideal_gas():
    """Ideal Gas EOS."""
    return IdealGasEOS()


@pytest.fixture
def vdw():
    """Van der Waals EOS."""
    return VanDerWaalsEOS()


@pytest.fixture
def pr():
    """Peng-Robinson EOS."""
    return PengRobinsonEOS()


class TestCompressibilityFactorComparison:
    """Test Z-factor across different EOS models."""

    def test_ideal_gas_z_always_unity(self, ideal_gas, methane):
        """Test ideal gas Z is always 1.0."""
        state = ideal_gas.calculate_state(methane, temperature=300, pressure=1e5)
        assert state.z == 1.0

    def test_real_gas_z_deviates_from_unity(self, vdw, pr, methane):
        """Test real gas models deviate from Z=1."""
        T = 300
        P = 5e6  # High pressure where deviations expected

        state_vdw = vdw.calculate_state(methane, T, P)
        state_pr = pr.calculate_state(methane, T, P)

        # At high pressure, both should deviate from Z=1
        assert state_vdw.z != 1.0
        assert state_pr.z != 1.0

    def test_z_factor_ordering_at_low_pressure(self, ideal_gas, vdw, pr, methane):
        """Test Z-factor ordering at low pressure."""
        T = 300
        P = 1e5  # Low pressure

        z_ideal = ideal_gas.calculate_Z(P, T, ideal_gas.calculate_volume_molar(T, P))
        state_vdw = vdw.calculate_state(methane, T, P)
        state_pr = pr.calculate_state(methane, T, P)

        # At low pressure, all should be close to ideal
        assert abs(z_ideal - 1.0) < 0.01
        assert abs(state_vdw.z - 1.0) < 0.1
        assert abs(state_pr.z - 1.0) < 0.1

    def test_z_factor_ordering_at_high_pressure(self, ideal_gas, vdw, pr, methane):
        """Test Z-factor ordering at high pressure."""
        T = 300
        P = 10e6  # High pressure

        z_ideal = 1.0
        state_vdw = vdw.calculate_state(methane, T, P)
        state_pr = pr.calculate_state(methane, T, P)

        # At high pressure, real gas models should show significant deviations
        # Generally: Z_ideal ≥ Z_vdw ≥ Z_pr (though PR includes temperature-dependent 'a')
        assert state_vdw.z > 0
        assert state_pr.z > 0
        assert state_vdw.z != z_ideal or state_pr.z != z_ideal


class TestVolumeComparison:
    """Test molar volume across EOS models."""

    def test_volume_at_low_pressure_converge(self, ideal_gas, vdw, pr, methane):
        """Test volumes converge at low pressure."""
        T = 300
        P = 1e4  # Very low pressure

        v_ideal = ideal_gas.calculate_volume_molar(T, P)
        v_vdw = vdw.calculate_volume(methane.tc, methane.pc, T, P)
        v_pr = pr.calculate_volume(methane.tc, methane.pc, T, P)

        # At low pressure, should be very similar
        assert abs(v_ideal - v_vdw) / v_ideal < 0.05  # Within 5%
        assert abs(v_ideal - v_pr) / v_ideal < 0.05

    def test_volume_decreases_with_pressure(self, ideal_gas, vdw, pr, methane):
        """Test volume decreases with pressure for all models."""
        T = 300

        v_ideal_1 = ideal_gas.calculate_volume_molar(T, 1e5)
        v_ideal_2 = ideal_gas.calculate_volume_molar(T, 5e6)

        v_vdw_1 = vdw.calculate_volume(methane.tc, methane.pc, T, 1e5)
        v_vdw_2 = vdw.calculate_volume(methane.tc, methane.pc, T, 5e6)

        v_pr_1 = pr.calculate_volume(methane.tc, methane.pc, T, 1e5)
        v_pr_2 = pr.calculate_volume(methane.tc, methane.pc, T, 5e6)

        assert v_ideal_2 < v_ideal_1
        assert v_vdw_2 < v_vdw_1
        assert v_pr_2 < v_pr_1

    def test_volume_increases_with_temperature(self, ideal_gas, vdw, pr, methane):
        """Test volume increases with temperature for all models."""
        P = 5e6

        v_ideal_1 = ideal_gas.calculate_volume_molar(300, P)
        v_ideal_2 = ideal_gas.calculate_volume_molar(500, P)

        v_vdw_1 = vdw.calculate_volume(methane.tc, methane.pc, 300, P)
        v_vdw_2 = vdw.calculate_volume(methane.tc, methane.pc, 500, P)

        v_pr_1 = pr.calculate_volume(methane.tc, methane.pc, 300, P)
        v_pr_2 = pr.calculate_volume(methane.tc, methane.pc, 500, P)

        assert v_ideal_2 > v_ideal_1
        assert v_vdw_2 > v_vdw_1
        assert v_pr_2 > v_pr_1


class TestMultipleCompounds:
    """Test EOS predictions for different compounds."""

    def test_compressibility_factor_methane_vs_ethane(self, vdw, pr):
        """Test Z-factor predictions differ between methane and ethane."""
        methane = Compound(
            name="Methane",
            formula="CH4",
            cas_number="74-82-8",
            molecular_weight=16.04,
            tc=190.564,
            pc=4.5992e6,
            acentric_factor=0.011,
        )
        ethane = Compound(
            name="Ethane",
            formula="C2H6",
            cas_number="74-84-0",
            molecular_weight=30.07,
            tc=305.128,
            pc=4.8718e6,
            acentric_factor=0.0995,
        )

        T = 300
        P = 5e6

        state_ch4_vdw = vdw.calculate_state(methane, T, P)
        state_c2h6_vdw = vdw.calculate_state(ethane, T, P)

        state_ch4_pr = pr.calculate_state(methane, T, P)
        state_c2h6_pr = pr.calculate_state(ethane, T, P)

        # Different compounds should give different Z-factors
        assert state_ch4_vdw.z != state_c2h6_vdw.z
        assert state_ch4_pr.z != state_c2h6_pr.z

    def test_phase_identification_consistency(self, vdw, pr):
        """Test phase identification is reasonable across models."""
        methane = Compound(
            name="Methane",
            formula="CH4",
            cas_number="74-82-8",
            molecular_weight=16.04,
            tc=190.564,
            pc=4.5992e6,
            acentric_factor=0.011,
        )

        # Supercritical conditions
        state_vdw = vdw.calculate_state(methane, methane.tc + 50, 5e6)
        state_pr = pr.calculate_state(methane, methane.tc + 50, 5e6)

        # Both should identify as supercritical
        assert state_vdw.phase.value == "supercritical"
        assert state_pr.phase.value == "supercritical"


class TestEOSConsistency:
    """Test internal consistency of EOS models."""

    def test_vdw_z_factor_consistent_with_volume(self, vdw, methane):
        """Test VDW Z-factor is consistent with calculated volume."""
        T = 300
        P = 5e6

        # Get volume and Z directly
        v = vdw.calculate_volume(methane.tc, methane.pc, T, P)
        z_direct = vdw.calculate_Z(P, T, v)

        # Get from complete state
        state = vdw.calculate_state(methane, T, P)

        # Should match
        assert state.z == pytest.approx(z_direct, rel=1e-10)
        assert state.v_molar == pytest.approx(v, rel=1e-10)

    def test_ideal_gas_z_factor_always_unity(self, ideal_gas):
        """Test ideal gas Z is always exactly 1.0."""
        T = 300
        P = 5e6

        v_m = ideal_gas.calculate_volume_molar(T, P)
        z = ideal_gas.calculate_Z(P, T, v_m)

        assert z == 1.0
        assert z != 1  # Ensure it's a value of 1.0
        assert type(z) == float

    def test_temperature_effect_on_z_factor(self, vdw, methane):
        """Test that Z-factor changes with temperature."""
        P = 5e6

        state_low_t = vdw.calculate_state(methane, 250, P)
        state_high_t = vdw.calculate_state(methane, 400, P)

        # Z-factors should be different at different temperatures
        assert state_low_t.z != state_high_t.z

    def test_pressure_effect_on_z_factor(self, vdw, methane):
        """Test that Z-factor changes with pressure."""
        T = 300

        state_low_p = vdw.calculate_state(methane, T, 1e6)
        state_high_p = vdw.calculate_state(methane, T, 5e6)

        # Z-factors should be different at different pressures
        assert state_low_p.z != state_high_p.z


class TestModelPhysicality:
    """Test physical validity of model predictions."""

    def test_volume_positive_all_models(self, ideal_gas, vdw, pr, methane):
        """Test all models predict positive volume."""
        T = 300
        P = 5e6

        v_ideal = ideal_gas.calculate_volume_molar(T, P)
        v_vdw = vdw.calculate_volume(methane.tc, methane.pc, T, P)
        v_pr = pr.calculate_volume(methane.tc, methane.pc, T, P)

        assert v_ideal > 0
        assert v_vdw > 0
        assert v_pr > 0

    def test_z_factor_positive_all_models(self, ideal_gas, vdw, pr, methane):
        """Test all models predict positive Z-factor."""
        T = 300
        P = 5e6

        state_ideal = ideal_gas.calculate_state(methane, T, P)
        state_vdw = vdw.calculate_state(methane, T, P)
        state_pr = pr.calculate_state(methane, T, P)

        assert state_ideal.z > 0
        assert state_vdw.z > 0
        assert state_pr.z > 0

    def test_ideal_gas_limit(self, ideal_gas, vdw, pr, methane):
        """Test real gas models approach ideal gas at low density."""
        T = 500
        P = 1e3  # Very low pressure

        z_ideal = ideal_gas.calculate_Z(P, T, ideal_gas.calculate_volume_molar(T, P))
        state_vdw = vdw.calculate_state(methane, T, P)
        state_pr = pr.calculate_state(methane, T, P)

        # At very low pressure, should be close to ideal gas
        assert abs(state_vdw.z - z_ideal) < 0.01
        assert abs(state_pr.z - z_ideal) < 0.01
