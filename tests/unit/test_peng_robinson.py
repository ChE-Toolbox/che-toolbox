"""Unit tests for Peng-Robinson EOS implementation."""

import pytest

from src.compounds.models import Compound
from src.eos.models import PhaseType
from src.eos.peng_robinson import PengRobinsonEOS


class TestPengRobinsonEOS:
    """Test PengRobinsonEOS class."""

    @pytest.fixture
    def methane(self) -> Compound:
        """Create methane compound."""
        return Compound(
            name="methane",
            cas_number="74-82-8",
            molecular_weight=16.043,
            tc=190.564,
            pc=4599200.0,
            acentric_factor=0.011,
        )

    @pytest.fixture
    def eos(self) -> PengRobinsonEOS:
        """Create EOS solver."""
        return PengRobinsonEOS()

    def test_calculate_a(self, eos: PengRobinsonEOS, methane: Compound) -> None:
        """Test 'a' parameter calculation."""
        a = eos.calculate_a(methane.tc, methane.pc, methane.acentric_factor, 300.0)
        assert a > 0
        assert isinstance(a, float)

    def test_calculate_b(self, eos: PengRobinsonEOS, methane: Compound) -> None:
        """Test 'b' parameter calculation."""
        b = eos.calculate_b(methane.tc, methane.pc)
        assert b > 0
        assert isinstance(b, float)

    def test_calculate_z_factor(self, eos: PengRobinsonEOS, methane: Compound) -> None:
        """Test Z factor calculation."""
        z_factors = eos.calculate_z_factor(300.0, 1e5, methane)
        assert len(z_factors) >= 1
        assert all(z > 0 for z in z_factors)
        assert z_factors == tuple(sorted(z_factors))

    def test_calculate_z_factor_invalid_temperature(
        self, eos: PengRobinsonEOS, methane: Compound
    ) -> None:
        """Test that invalid temperature raises error."""
        with pytest.raises(ValueError, match="Temperature"):
            eos.calculate_z_factor(-300.0, 1e5, methane)

    def test_calculate_z_factor_invalid_pressure(
        self, eos: PengRobinsonEOS, methane: Compound
    ) -> None:
        """Test that invalid pressure raises error."""
        with pytest.raises(ValueError, match="Pressure"):
            eos.calculate_z_factor(300.0, -1e5, methane)

    def test_calculate_fugacity_coefficient(self, eos: PengRobinsonEOS, methane: Compound) -> None:
        """Test fugacity coefficient calculation."""
        phi = eos.calculate_fugacity_coefficient(300.0, 1e5, methane)
        assert 0 < phi < 2  # Fugacity coefficient should be reasonable
        assert isinstance(phi, float)

    def test_fugacity_coefficient_vapor_phase(
        self, eos: PengRobinsonEOS, methane: Compound
    ) -> None:
        """Test fugacity coefficient for vapor phase."""
        phi_vapor = eos.calculate_fugacity_coefficient(300.0, 1e5, methane, phase=PhaseType.VAPOR)
        assert phi_vapor > 0

    def test_fugacity_coefficient_liquid_phase(
        self, eos: PengRobinsonEOS, methane: Compound
    ) -> None:
        """Test fugacity coefficient for liquid phase."""
        phi_liquid = eos.calculate_fugacity_coefficient(300.0, 1e5, methane, phase=PhaseType.LIQUID)
        assert phi_liquid > 0

    def test_identify_phase_supercritical(self, eos: PengRobinsonEOS, methane: Compound) -> None:
        """Test phase identification for supercritical conditions."""
        # Above critical temperature and pressure
        phase = eos.identify_phase(300.0, 1e7, methane)
        assert phase == PhaseType.SUPERCRITICAL

    def test_identify_phase(self, eos: PengRobinsonEOS, methane: Compound) -> None:
        """Test phase identification."""
        phase = eos.identify_phase(300.0, 1e5, methane)
        assert phase in (
            PhaseType.VAPOR,
            PhaseType.LIQUID,
            PhaseType.TWO_PHASE,
            PhaseType.SUPERCRITICAL,
        )

    def test_calculate_state(self, eos: PengRobinsonEOS, methane: Compound) -> None:
        """Test complete state calculation."""
        state = eos.calculate_state(300.0, 1e5, methane)
        assert state.temperature == 300.0
        assert state.pressure == 1e5
        assert state.composition == "methane"
        assert state.z_factor is not None
        assert state.z_factor > 0
        assert state.fugacity_coefficient is not None
        assert state.fugacity is not None
        assert state.phase is not None

    def test_calculate_a_invalid_temperature(self, eos: PengRobinsonEOS, methane: Compound) -> None:
        """Test that invalid temperature raises error."""
        with pytest.raises(ValueError, match="Temperature"):
            eos.calculate_a(methane.tc, methane.pc, methane.acentric_factor, -300.0)

    def test_calculate_b_invalid_critical_temp(self, eos: PengRobinsonEOS) -> None:
        """Test that invalid critical temperature raises error."""
        with pytest.raises(ValueError, match="Critical temperature"):
            eos.calculate_b(-190.564, 4599200.0)

    def test_calculate_vapor_pressure(self, eos: PengRobinsonEOS, methane: Compound) -> None:
        """Test vapor pressure calculation."""
        # Calculate at 200 K (well below critical temp 190.564 K... wait that's wrong)
        # Use 150 K which is below critical
        psat = eos.calculate_vapor_pressure(150.0, methane)
        assert psat > 0
        assert psat < methane.pc

    def test_calculate_vapor_pressure_supercritical(
        self, eos: PengRobinsonEOS, methane: Compound
    ) -> None:
        """Test that supercritical temperature raises error."""
        with pytest.raises(ValueError, match="critical"):
            eos.calculate_vapor_pressure(methane.tc + 10, methane)

    def test_calculate_vapor_pressure_at_critical_temp(
        self, eos: PengRobinsonEOS, methane: Compound
    ) -> None:
        """Test that at critical temperature raises error."""
        with pytest.raises(ValueError, match="critical"):
            eos.calculate_vapor_pressure(methane.tc, methane)
