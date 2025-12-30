"""Unit tests for Pydantic data models."""

import pytest

from src.compounds.models import Compound
from src.eos.models import BinaryInteractionParameter, Mixture, PhaseType, ThermodynamicState
from src.validation.models import ValidationResult, ValidationTestCase


class TestPhaseType:
    """Test PhaseType enum."""

    def test_phase_type_values(self) -> None:
        """Test that all phase types are defined."""
        assert PhaseType.VAPOR.value == "vapor"
        assert PhaseType.LIQUID.value == "liquid"
        assert PhaseType.SUPERCRITICAL.value == "supercritical"
        assert PhaseType.TWO_PHASE.value == "two_phase"
        assert PhaseType.UNKNOWN.value == "unknown"


class TestCompound:
    """Test Compound model."""

    def test_valid_compound(self) -> None:
        """Test creating a valid compound."""
        c = Compound(
            name="methane",
            cas_number="74-82-8",
            molecular_weight=16.043,
            tc=190.564,
            pc=4599200.0,
            acentric_factor=0.011,
        )
        assert c.name == "methane"
        assert c.tc == 190.564

    def test_invalid_critical_temperature(self) -> None:
        """Test that Tc must be positive."""
        with pytest.raises(ValueError):
            Compound(
                name="methane",
                cas_number="74-82-8",
                molecular_weight=16.043,
                tc=-190.564,
                pc=4599200.0,
                acentric_factor=0.011,
            )

    def test_invalid_acentric_factor(self) -> None:
        """Test that acentric factor must be in range."""
        with pytest.raises(ValueError):
            Compound(
                name="methane",
                cas_number="74-82-8",
                molecular_weight=16.043,
                tc=190.564,
                pc=4599200.0,
                acentric_factor=2.5,
            )


class TestMixture:
    """Test Mixture model."""

    def test_valid_mixture(self) -> None:
        """Test creating a valid mixture."""
        m = Mixture(
            compound_names=["methane", "ethane"],
            mole_fractions=[0.8, 0.2],
        )
        assert len(m.compound_names) == 2
        assert sum(m.mole_fractions) == pytest.approx(1.0)

    def test_invalid_mole_fraction_sum(self) -> None:
        """Test that mole fractions must sum to 1.0."""
        with pytest.raises(ValueError, match="sum to"):
            Mixture(
                compound_names=["methane", "ethane"],
                mole_fractions=[0.8, 0.3],
            )

    def test_invalid_negative_mole_fraction(self) -> None:
        """Test that mole fractions must be non-negative."""
        with pytest.raises(ValueError, match="between 0 and 1"):
            Mixture(
                compound_names=["methane", "ethane"],
                mole_fractions=[-0.1, 1.1],
            )

    def test_invalid_length_mismatch(self) -> None:
        """Test that compound_names and mole_fractions must have same length."""
        with pytest.raises(ValueError, match="length"):
            Mixture(
                compound_names=["methane", "ethane", "propane"],
                mole_fractions=[0.8, 0.2],
            )


class TestBinaryInteractionParameter:
    """Test BinaryInteractionParameter model."""

    def test_valid_kij(self) -> None:
        """Test creating valid binary interaction parameter."""
        kij = BinaryInteractionParameter(
            compound_i="methane",
            compound_j="ethane",
            kij=-0.001,
        )
        assert kij.compound_i == "methane"
        assert kij.kij == -0.001

    def test_invalid_kij_bounds(self) -> None:
        """Test that kij must be within bounds."""
        with pytest.raises(ValueError):
            BinaryInteractionParameter(
                compound_i="methane",
                compound_j="ethane",
                kij=0.6,
            )


class TestThermodynamicState:
    """Test ThermodynamicState model."""

    def test_valid_state(self) -> None:
        """Test creating a valid thermodynamic state."""
        state = ThermodynamicState(
            temperature=300.0,
            pressure=1e5,
            composition="methane",
            phase=PhaseType.VAPOR,
            z_factor=0.95,
            fugacity_coefficient=0.98,
            fugacity=9.8e4,
        )
        assert state.temperature == 300.0
        assert state.phase == PhaseType.VAPOR

    def test_invalid_temperature(self) -> None:
        """Test that temperature must be positive."""
        with pytest.raises(ValueError):
            ThermodynamicState(
                temperature=-300.0,
                pressure=1e5,
                composition="methane",
            )


class TestValidationTestCase:
    """Test ValidationTestCase model."""

    def test_valid_test_case(self) -> None:
        """Test creating a valid validation test case."""
        tc = ValidationTestCase(
            compound_name="methane",
            temperature=300.0,
            pressure=1e5,
            expected_z_factor=0.95,
            expected_fugacity=9.5e4,
        )
        assert tc.compound_name == "methane"
        assert tc.tolerance_z == 0.05  # default 5%


class TestValidationResult:
    """Test ValidationResult model."""

    def test_valid_result(self) -> None:
        """Test creating a valid validation result."""
        tc = ValidationTestCase(
            compound_name="methane",
            temperature=300.0,
            pressure=1e5,
            expected_z_factor=0.95,
        )
        result = ValidationResult(
            test_case=tc,
            calculated_z_factor=0.94,
            z_factor_passed=True,
            z_factor_deviation=0.0105,
        )
        assert result.z_factor_passed is True
