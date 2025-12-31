"""Integration tests for pure component workflow."""

import pytest

from src.compounds.database import CompoundDatabase
from src.eos.models import PhaseType
from src.eos.peng_robinson import PengRobinsonEOS


class TestPureComponentWorkflow:
    """Test complete pure component workflow."""

    @pytest.fixture
    def eos(self) -> PengRobinsonEOS:
        """Create EOS solver."""
        return PengRobinsonEOS()

    @pytest.fixture
    def db(self) -> CompoundDatabase:
        """Create compound database."""
        return CompoundDatabase("data/compounds.json")

    def test_methane_calculation_at_moderate_conditions(
        self, eos: PengRobinsonEOS, db: CompoundDatabase
    ) -> None:
        """Test methane calculation at moderate T and P."""
        methane = db.get("methane")
        assert methane is not None

        # 150 K (below Tc=190.564K), 1 bar (100 kPa)
        state = eos.calculate_state(150.0, 1e5, methane)

        assert state.temperature == 150.0
        assert state.pressure == 1e5
        assert state.composition == "methane"
        assert state.z_factor is not None
        assert state.fugacity_coefficient is not None
        assert state.fugacity is not None
        # At low T and P, should be vapor or two-phase
        assert state.phase in (PhaseType.VAPOR, PhaseType.TWO_PHASE)

    def test_methane_liquid_region(self, eos: PengRobinsonEOS, db: CompoundDatabase) -> None:
        """Test methane in liquid region."""
        methane = db.get("methane")
        assert methane is not None

        # 150 K, 50 bar (high pressure for liquid)
        state = eos.calculate_state(150.0, 5e6, methane)

        assert state.temperature == 150.0
        assert state.pressure == 5e6
        assert 0.1 < state.z_factor < 0.6  # Liquid-like Z factor

    def test_water_supercritical(self, eos: PengRobinsonEOS, db: CompoundDatabase) -> None:
        """Test water in supercritical region."""
        water = db.get("water")
        assert water is not None

        # Above critical point
        state = eos.calculate_state(700.0, 3e7, water)

        assert state.phase == PhaseType.SUPERCRITICAL

    def test_propane_phase_identification(
        self, eos: PengRobinsonEOS, db: CompoundDatabase
    ) -> None:
        """Test phase identification for propane."""
        propane = db.get("propane")
        assert propane is not None

        # Below critical point
        state = eos.calculate_state(300.0, 1e6, propane)
        assert state.phase in (
            PhaseType.VAPOR,
            PhaseType.LIQUID,
            PhaseType.TWO_PHASE,
        )

    def test_multcompound_retrieval(self, db: CompoundDatabase) -> None:
        """Test retrieving multiple compounds."""
        compounds_needed = ["methane", "ethane", "propane", "n-butane", "water"]
        for name in compounds_needed:
            compound = db.get(name)
            assert compound is not None
            assert compound.name == name
