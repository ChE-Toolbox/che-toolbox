"""Integration tests for cross-EOS model comparisons.

Tests the compare_compressibility_factors() utility function and
validates that all three EOS models (Ideal Gas, Van der Waals, Peng-Robinson)
produce consistent results across various conditions.
"""

import pytest
from src.eos import (
    compare_compressibility_factors,
    IdealGasEOS,
    VanDerWaalsEOS,
    PengRobinsonEOS,
)
from src.compounds.models import Compound


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def methane():
    """Methane compound with full critical properties."""
    return Compound(
        name="methane",
        formula="CH4",
        cas_number="74-82-8",
        molar_mass=0.016043,
        tc=190.564,  # K
        pc=4.5992e6,  # Pa
        omega=0.0115,
    )


@pytest.fixture
def ethane():
    """Ethane compound with full critical properties."""
    return Compound(
        name="ethane",
        formula="C2H6",
        cas_number="74-84-0",
        molar_mass=0.03007,
        tc=305.32,  # K
        pc=4.8722e6,  # Pa
        omega=0.0995,
    )


@pytest.fixture
def propane():
    """Propane compound with full critical properties."""
    return Compound(
        name="propane",
        formula="C3H8",
        cas_number="74-98-6",
        molar_mass=0.04410,
        tc=369.83,  # K
        pc=4.2512e6,  # Pa
        omega=0.1523,
    )


# ==============================================================================
# T059: Create tests/unit/test_integration.py with cross-EOS comparison fixtures
# ==============================================================================
class TestCrossEOSFixtures:
    """Test fixtures are properly configured for integration testing."""

    def test_methane_fixture(self, methane):
        """Verify methane fixture has all required properties."""
        assert methane.tc > 0
        assert methane.pc > 0
        assert methane.omega >= 0
        assert methane.name == "methane"

    def test_ethane_fixture(self, ethane):
        """Verify ethane fixture has all required properties."""
        assert ethane.tc > 0
        assert ethane.pc > 0
        assert ethane.omega >= 0
        assert ethane.name == "ethane"

    def test_propane_fixture(self, propane):
        """Verify propane fixture has all required properties."""
        assert propane.tc > 0
        assert propane.pc > 0
        assert propane.omega >= 0
        assert propane.name == "propane"


# ==============================================================================
# T060-T061: Test compare_compressibility_factors() function
# ==============================================================================
class TestCompareCompressibilityFactorsFunction:
    """Test the compare_compressibility_factors() utility function."""

    def test_function_exists(self):
        """Verify compare_compressibility_factors is importable."""
        from src.eos import compare_compressibility_factors
        assert callable(compare_compressibility_factors)

    def test_function_signature(self, methane):
        """Verify function accepts correct parameters."""
        result = compare_compressibility_factors(
            compound=methane,
            temperature=300.0,
            pressure=50e6,
        )
        assert isinstance(result, dict)

    def test_invalid_temperature(self, methane):
        """Test function raises on invalid temperature."""
        with pytest.raises(ValueError, match="Temperature must be positive"):
            compare_compressibility_factors(methane, temperature=0, pressure=1e6)

        with pytest.raises(ValueError, match="Temperature must be positive"):
            compare_compressibility_factors(methane, temperature=-100, pressure=1e6)

    def test_invalid_pressure(self, methane):
        """Test function raises on invalid pressure."""
        with pytest.raises(ValueError, match="Pressure must be positive"):
            compare_compressibility_factors(methane, temperature=300, pressure=0)

        with pytest.raises(ValueError, match="Pressure must be positive"):
            compare_compressibility_factors(methane, temperature=300, pressure=-1e6)

    def test_invalid_compound_missing_tc(self):
        """Test function raises when compound missing critical temperature."""
        bad_compound = Compound(
            name="bad",
            formula="XX",
            cas_number="000-00-0",
            molar_mass=0.01,
            tc=0,  # Invalid
            pc=4.5e6,
            omega=0.1,
        )
        with pytest.raises(ValueError, match="valid critical temperature"):
            compare_compressibility_factors(bad_compound, 300, 1e6)

    def test_invalid_compound_missing_pc(self):
        """Test function raises when compound missing critical pressure."""
        bad_compound = Compound(
            name="bad",
            formula="XX",
            cas_number="000-00-0",
            molar_mass=0.01,
            tc=300,
            pc=0,  # Invalid
            omega=0.1,
        )
        with pytest.raises(ValueError, match="valid critical pressure"):
            compare_compressibility_factors(bad_compound, 300, 1e6)


# ==============================================================================
# T062: Test cross-model comparison returns dict with all three Z-factors
# ==============================================================================
class TestCrossModelComparisonOutput:
    """Test that cross-model comparison returns complete results."""

    def test_returns_dict_with_three_z_factors(self, methane):
        """Verify function returns dict with ideal_Z, vdw_Z, pr_Z."""
        result = compare_compressibility_factors(methane, 300, 50e6)

        assert isinstance(result, dict)
        assert 'ideal_Z' in result
        assert 'vdw_Z' in result
        assert 'pr_Z' in result
        assert len(result) == 3

    def test_all_z_factors_are_floats(self, ethane):
        """Verify all Z-factors are numeric."""
        result = compare_compressibility_factors(ethane, 350, 20e6)

        assert isinstance(result['ideal_Z'], float)
        assert isinstance(result['vdw_Z'], float)
        assert isinstance(result['pr_Z'], float)

    def test_all_z_factors_positive(self, propane):
        """Verify all Z-factors are positive."""
        result = compare_compressibility_factors(propane, 400, 15e6)

        assert result['ideal_Z'] > 0
        assert result['vdw_Z'] > 0
        assert result['pr_Z'] > 0

    def test_all_z_factors_in_physical_range(self, methane):
        """Verify all Z-factors in typical range [0.1, 1.5]."""
        result = compare_compressibility_factors(methane, 300, 30e6)

        assert 0.1 <= result['ideal_Z'] <= 1.5
        assert 0.1 <= result['vdw_Z'] <= 1.5
        assert 0.1 <= result['pr_Z'] <= 1.5

    def test_ideal_z_always_unity(self, methane):
        """Verify ideal_Z is always exactly 1.0."""
        # Test at various conditions
        conditions = [
            (300, 1e6),
            (300, 50e6),
            (500, 1e5),
            (200, 10e6),
        ]

        for T, P in conditions:
            result = compare_compressibility_factors(methane, T, P)
            assert result['ideal_Z'] == 1.0, \
                f"Ideal Z should be 1.0 at T={T}, P={P}"


# ==============================================================================
# T063: Test Z-factor ordering (Z_ideal ≥ Z_vdw, Z_pr for realistic conditions)
# ==============================================================================
class TestZFactorOrdering:
    """Test Z-factor ordering relationships across models."""

    def test_z_ideal_equals_unity(self, methane):
        """Test that ideal gas Z is always 1.0 (baseline)."""
        result = compare_compressibility_factors(methane, 300, 50e6)
        assert result['ideal_Z'] == 1.0

    def test_z_nonideal_less_than_ideal_at_moderate_pressure(self, methane):
        """At moderate pressure, non-ideal Z < ideal Z due to attractive forces."""
        T = 300  # K
        P = 30e6  # 30 MPa (moderate to high pressure)

        result = compare_compressibility_factors(methane, T, P)

        # At moderate pressure, attractive forces dominate → Z < 1.0
        assert result['vdw_Z'] <= result['ideal_Z'], \
            "VDW Z should be ≤ ideal Z at moderate pressure"
        assert result['pr_Z'] <= result['ideal_Z'], \
            "PR Z should be ≤ ideal Z at moderate pressure"

    def test_z_ordering_ethane_high_pressure(self, ethane):
        """Test Z-factor ordering for ethane at high pressure."""
        T = 350  # K
        P = 20e6  # 20 MPa

        result = compare_compressibility_factors(ethane, T, P)

        # Expected: Z_ideal = 1.0 ≥ Z_pr ≈ Z_vdw (both < 1.0)
        assert result['ideal_Z'] == 1.0
        assert result['vdw_Z'] < 1.0, "VDW should show non-ideal behavior"
        assert result['pr_Z'] < 1.0, "PR should show non-ideal behavior"
        assert result['ideal_Z'] >= result['vdw_Z']
        assert result['ideal_Z'] >= result['pr_Z']

    def test_z_ordering_propane_moderate_pressure(self, propane):
        """Test Z-factor ordering for propane at moderate conditions."""
        T = 400  # K
        P = 15e6  # 15 MPa

        result = compare_compressibility_factors(propane, T, P)

        # All models should give positive Z-factors
        assert result['ideal_Z'] == 1.0
        assert result['vdw_Z'] > 0
        assert result['pr_Z'] > 0

        # Non-ideal models should show Z < 1 at these conditions
        assert result['vdw_Z'] <= result['ideal_Z']
        assert result['pr_Z'] <= result['ideal_Z']

    def test_all_models_converge_at_low_pressure(self, methane):
        """At low pressure, all models converge to ideal gas behavior."""
        T = 300  # K
        P = 1e5  # 0.1 MPa (atmospheric pressure, very low)

        result = compare_compressibility_factors(methane, T, P)

        # At low pressure, Z → 1.0 for all models
        assert result['ideal_Z'] == 1.0
        assert abs(result['vdw_Z'] - 1.0) < 0.05, \
            "VDW should approach ideal at low pressure"
        assert abs(result['pr_Z'] - 1.0) < 0.05, \
            "PR should approach ideal at low pressure"

    def test_pr_more_accurate_than_vdw(self, ethane):
        """PR typically more accurate than VDW (accounts for acentric factor).

        This is a qualitative test - PR should generally give results
        closer to experimental data, but we can't test absolute accuracy
        without NIST reference values.
        """
        T = 350  # K
        P = 20e6  # 20 MPa

        result = compare_compressibility_factors(ethane, T, P)

        # Both should be non-ideal
        assert result['vdw_Z'] < 1.0
        assert result['pr_Z'] < 1.0

        # Both should be in reasonable range
        assert 0.5 <= result['vdw_Z'] <= 1.0
        assert 0.5 <= result['pr_Z'] <= 1.0


# ==============================================================================
# Additional integration tests
# ==============================================================================
class TestCrossModelConsistency:
    """Test consistency across EOS models."""

    def test_multiple_compounds_all_return_valid_results(self, methane, ethane, propane):
        """Test all compounds produce valid cross-model results."""
        compounds = [methane, ethane, propane]
        T = 350
        P = 20e6

        for compound in compounds:
            result = compare_compressibility_factors(compound, T, P)

            assert 'ideal_Z' in result
            assert 'vdw_Z' in result
            assert 'pr_Z' in result
            assert result['ideal_Z'] == 1.0
            assert 0.1 <= result['vdw_Z'] <= 1.5
            assert 0.1 <= result['pr_Z'] <= 1.5

    def test_temperature_variation_consistent(self, methane):
        """Test cross-model comparison at various temperatures."""
        temperatures = [200, 300, 400, 500]
        P = 10e6

        for T in temperatures:
            result = compare_compressibility_factors(methane, T, P)

            # All should return valid Z-factors
            assert result['ideal_Z'] == 1.0
            assert result['vdw_Z'] > 0
            assert result['pr_Z'] > 0

    def test_pressure_variation_consistent(self, ethane):
        """Test cross-model comparison at various pressures."""
        pressures = [1e6, 5e6, 10e6, 20e6, 50e6]
        T = 350

        for P in pressures:
            result = compare_compressibility_factors(ethane, T, P)

            # All should return valid Z-factors
            assert result['ideal_Z'] == 1.0
            assert result['vdw_Z'] > 0
            assert result['pr_Z'] > 0

    def test_z_decreases_with_pressure(self, methane):
        """Test that non-ideal Z-factors decrease with pressure."""
        T = 300
        P_low = 5e6
        P_high = 50e6

        result_low = compare_compressibility_factors(methane, T, P_low)
        result_high = compare_compressibility_factors(methane, T, P_high)

        # Ideal gas unchanged
        assert result_low['ideal_Z'] == result_high['ideal_Z'] == 1.0

        # Non-ideal models: Z should decrease with pressure (attractive forces)
        # Allow small tolerance for numerical variations
        assert result_high['vdw_Z'] <= result_low['vdw_Z'] + 0.01
        assert result_high['pr_Z'] <= result_low['pr_Z'] + 0.01

    def test_comparison_reproducible(self, propane):
        """Test that multiple calls give identical results."""
        T = 400
        P = 15e6

        result1 = compare_compressibility_factors(propane, T, P)
        result2 = compare_compressibility_factors(propane, T, P)

        assert result1['ideal_Z'] == result2['ideal_Z']
        assert result1['vdw_Z'] == result2['vdw_Z']
        assert result1['pr_Z'] == result2['pr_Z']


class TestAllEOSModelsRunnable:
    """Test all three EOS models can run independently on same conditions."""

    def test_all_eos_models_calculate_volume(self, ethane):
        """Verify all three models can calculate volume without error."""
        T = 350
        P = 20e6

        # Ideal Gas
        ideal_eos = IdealGasEOS()
        v_ideal = ideal_eos.calculate_volume(n=1.0, temperature=T, pressure=P)
        assert v_ideal > 0

        # Van der Waals
        vdw_eos = VanDerWaalsEOS()
        v_vdw = vdw_eos.calculate_volume(ethane.tc, ethane.pc, T, P)
        assert v_vdw > 0

        # Peng-Robinson
        pr_eos = PengRobinsonEOS()
        v_pr = pr_eos.calculate_volume(ethane.tc, ethane.pc, T, P, ethane.omega)
        assert v_pr > 0

    def test_all_eos_models_calculate_z(self, methane):
        """Verify all three models can calculate Z-factor."""
        T = 300
        P = 30e6

        # Get volumes first
        ideal_eos = IdealGasEOS()
        vdw_eos = VanDerWaalsEOS()
        pr_eos = PengRobinsonEOS()

        v_ideal = ideal_eos.calculate_volume(1.0, T, P)
        v_vdw = vdw_eos.calculate_volume(methane.tc, methane.pc, T, P)
        v_pr = pr_eos.calculate_volume(methane.tc, methane.pc, T, P, methane.omega)

        # Calculate Z-factors
        Z_ideal = IdealGasEOS.calculate_Z(P, T, v_ideal)
        Z_vdw = VanDerWaalsEOS.calculate_Z(P, T, v_vdw)
        Z_pr = PengRobinsonEOS.calculate_Z(P, T, v_pr)

        # All should be positive
        assert Z_ideal > 0
        assert Z_vdw > 0
        assert Z_pr > 0

        # Ideal should be 1.0
        assert Z_ideal == 1.0

    def test_all_eos_models_no_exceptions_raised(self, propane):
        """Verify no exceptions raised during normal operation."""
        T = 400
        P = 15e6

        # Should not raise any exceptions
        try:
            result = compare_compressibility_factors(propane, T, P)
            assert result is not None
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")
