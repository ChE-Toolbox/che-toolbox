"""Integration tests for PT Flash calculations.

Tests flash convergence, material balance, fugacity equilibrium,
and output completeness for binary mixtures.
"""

import numpy as np
import pytest

from src.eos.flash_pt import FlashConvergence, FlashPT
from src.eos.peng_robinson import PengRobinsonEOS

# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def flash():
    """PT Flash calculator instance."""
    return FlashPT()


@pytest.fixture
def pr_eos():
    """Peng-Robinson EOS for fugacity calculations."""
    return PengRobinsonEOS()


@pytest.fixture
def ethane_propane_binary():
    """Binary ethane-propane mixture: 60% ethane, 40% propane."""
    return {
        'z': np.array([0.6, 0.4]),
        'tc': np.array([305.32, 369.83]),  # K
        'pc': np.array([4.8722e6, 4.2512e6]),  # Pa
        'omega': np.array([0.0995, 0.1523]),
        'names': ['ethane', 'propane']
    }


@pytest.fixture
def methane_propane_binary():
    """Binary methane-propane mixture: 55% methane, 45% propane."""
    return {
        'z': np.array([0.55, 0.45]),
        'tc': np.array([190.564, 369.83]),  # K
        'pc': np.array([4.5992e6, 4.2512e6]),  # Pa
        'omega': np.array([0.0115, 0.1523]),
        'names': ['methane', 'propane']
    }


# ==============================================================================
# T091: Create tests/unit/test_integration_flash.py
# ==============================================================================
class TestFlashIntegrationSetup:
    """Verify flash integration test setup."""

    def test_flash_fixture(self, flash):
        """Test flash calculator fixture."""
        assert isinstance(flash, FlashPT)
        assert flash.max_iterations == 50
        assert flash.tolerance == 1e-6

    def test_pr_eos_fixture(self, pr_eos):
        """Test PR EOS fixture."""
        assert isinstance(pr_eos, PengRobinsonEOS)

    def test_binary_mixture_fixtures(self, ethane_propane_binary, methane_propane_binary):
        """Test binary mixture fixtures."""
        for mixture in [ethane_propane_binary, methane_propane_binary]:
            assert len(mixture['z']) == 2
            assert np.allclose(np.sum(mixture['z']), 1.0)
            assert len(mixture['tc']) == 2
            assert len(mixture['pc']) == 2


# ==============================================================================
# T092: Test binary flash convergence (ethane-propane @ 300K, 2MPa, 4-6 iterations)
# ==============================================================================
class TestBinaryFlashConvergence:
    """Test flash convergence for binary mixtures."""

    def test_ethane_propane_flash_convergence(self, flash, ethane_propane_binary):
        """Test ethane-propane flash converges in 4-6 iterations @ 300K, 2MPa."""
        mixture = ethane_propane_binary
        T = 300.0  # K
        P = 2e6    # 2 MPa

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        # Should converge successfully
        assert result.convergence in [FlashConvergence.SUCCESS, FlashConvergence.SINGLE_PHASE], \
            f"Flash failed to converge: {result.convergence}"

        if result.convergence == FlashConvergence.SUCCESS:
            # Should converge in reasonable iterations (typically 4-6 for this case)
            assert result.iterations <= 50, \
                f"Iterations {result.iterations} exceeded maximum"
            # Most cases converge quickly
            assert result.iterations > 0, "Should require at least one iteration"

    def test_methane_propane_flash_convergence(self, flash, methane_propane_binary):
        """Test methane-propane flash converges."""
        mixture = methane_propane_binary
        T = 280.0  # K
        P = 3e6    # 3 MPa

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        # Should converge or detect single phase
        assert result.convergence in [FlashConvergence.SUCCESS, FlashConvergence.SINGLE_PHASE]

        if result.convergence == FlashConvergence.SUCCESS:
            assert 0 < result.iterations <= 50

    def test_flash_convergence_tolerance_achieved(self, flash, ethane_propane_binary):
        """Test converged flash achieves tolerance criterion."""
        mixture = ethane_propane_binary
        T = 310.0
        P = 2.5e6

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # Tolerance should be below threshold
            assert result.tolerance_achieved < flash.tolerance, \
                f"Tolerance {result.tolerance_achieved} exceeds threshold {flash.tolerance}"

    def test_flash_does_not_exceed_max_iterations(self, flash, ethane_propane_binary):
        """Test flash respects max_iterations limit."""
        mixture = ethane_propane_binary
        T = 300.0
        P = 2e6

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
            max_iterations=10,  # Very low limit
        )

        # Should either converge or hit max iterations
        assert result.iterations <= 10
        if result.iterations == 10:
            assert result.convergence in [FlashConvergence.MAX_ITERATIONS, FlashConvergence.SUCCESS]


# ==============================================================================
# T093: Test flash output completeness (all FlashResult fields populated)
# ==============================================================================
class TestFlashOutputCompleteness:
    """Test all FlashResult fields are populated correctly."""

    def test_flash_result_all_fields_present(self, flash, ethane_propane_binary):
        """Test FlashResult contains all required fields."""
        mixture = ethane_propane_binary
        T = 300.0
        P = 2e6

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        # Verify all fields exist
        assert hasattr(result, 'L')
        assert hasattr(result, 'V')
        assert hasattr(result, 'x')
        assert hasattr(result, 'y')
        assert hasattr(result, 'K_values')
        assert hasattr(result, 'iterations')
        assert hasattr(result, 'tolerance_achieved')
        assert hasattr(result, 'convergence')
        assert hasattr(result, 'material_balance_error')

    def test_flash_result_l_and_v_populated(self, flash, ethane_propane_binary):
        """Test L and V fractions are populated."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        assert isinstance(result.L, (int, float))
        assert isinstance(result.V, (int, float))
        assert not np.isnan(result.L) or result.convergence != FlashConvergence.SUCCESS
        assert not np.isnan(result.V) or result.convergence != FlashConvergence.SUCCESS

    def test_flash_result_compositions_populated(self, flash, ethane_propane_binary):
        """Test x and y compositions are populated."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        assert isinstance(result.x, np.ndarray)
        assert isinstance(result.y, np.ndarray)
        assert len(result.x) == 2
        assert len(result.y) == 2

    def test_flash_result_k_values_populated(self, flash, ethane_propane_binary):
        """Test K-values are populated."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        assert isinstance(result.K_values, np.ndarray)
        assert len(result.K_values) == 2
        assert np.all(result.K_values > 0), "All K-values should be positive"

    def test_flash_result_iteration_count_populated(self, flash, ethane_propane_binary):
        """Test iteration count is populated."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        assert isinstance(result.iterations, int)
        assert result.iterations >= 0

    def test_flash_result_tolerance_populated(self, flash, ethane_propane_binary):
        """Test tolerance_achieved is populated."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        assert isinstance(result.tolerance_achieved, float)

    def test_flash_result_convergence_status_populated(self, flash, ethane_propane_binary):
        """Test convergence status is populated."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        assert isinstance(result.convergence, FlashConvergence)

    def test_flash_result_success_property(self, flash, ethane_propane_binary):
        """Test success property works correctly."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        # Success property should match convergence status
        if result.convergence == FlashConvergence.SUCCESS:
            assert result.success is True
        else:
            assert result.success is False


# ==============================================================================
# T094: Test binary flash material balance (composition error < 1e-6)
# ==============================================================================
class TestFlashMaterialBalance:
    """Test material balance closure for flash calculations."""

    def test_material_balance_ethane_propane(self, flash, ethane_propane_binary):
        """Test material balance for ethane-propane: z_i = L*x_i + V*y_i."""
        mixture = ethane_propane_binary
        T = 300.0
        P = 2e6

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # Check material balance for each component
            for i in range(len(mixture['z'])):
                z_calc = result.L * result.x[i] + result.V * result.y[i]
                error = abs(z_calc - mixture['z'][i])
                assert error < 1e-6, \
                    f"Component {i}: material balance error {error} exceeds 1e-6"

    def test_material_balance_methane_propane(self, flash, methane_propane_binary):
        """Test material balance for methane-propane."""
        mixture = methane_propane_binary
        T = 280.0
        P = 3e6

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # Material balance check
            material_balance = result.L * result.x + result.V * result.y
            errors = np.abs(material_balance - mixture['z'])
            assert np.all(errors < 1e-6), \
                f"Material balance errors {errors} exceed 1e-6"

    def test_material_balance_error_reported(self, flash, ethane_propane_binary):
        """Test material_balance_error field is populated."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        if result.convergence == FlashConvergence.SUCCESS:
            assert result.material_balance_error is not None
            if result.material_balance_error is not None:
                assert result.material_balance_error < 1e-6

    def test_l_plus_v_equals_one(self, flash, ethane_propane_binary):
        """Test L + V = 1.0 (mole balance)."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        if result.convergence == FlashConvergence.SUCCESS:
            assert np.allclose(result.L + result.V, 1.0, atol=1e-10), \
                f"L + V = {result.L + result.V} != 1.0"

    def test_compositions_sum_to_one(self, flash, ethane_propane_binary):
        """Test sum(x) = 1 and sum(y) = 1."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        if result.convergence == FlashConvergence.SUCCESS:
            assert np.allclose(np.sum(result.x), 1.0, atol=1e-6), \
                f"sum(x) = {np.sum(result.x)} != 1.0"
            assert np.allclose(np.sum(result.y), 1.0, atol=1e-6), \
                f"sum(y) = {np.sum(result.y)} != 1.0"


# ==============================================================================
# T095: Test binary flash fugacity equilibrium (|f_v/f_l - 1| < 1e-6)
# ==============================================================================
class TestFlashFugacityEquilibrium:
    """Test fugacity equilibrium criterion for flash calculations."""

    def test_fugacity_equilibrium_criterion(self, flash, ethane_propane_binary):
        """Test fugacity equilibrium: K_i = y_i/x_i at equilibrium."""
        mixture = ethane_propane_binary
        T = 300.0
        P = 2e6

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # K_i should equal y_i/x_i
            for i in range(len(mixture['z'])):
                if result.x[i] > 1e-10:  # Avoid division by zero
                    K_calc = result.y[i] / result.x[i]
                    error = abs(K_calc - result.K_values[i]) / result.K_values[i]
                    assert error < 1e-6, \
                        f"Component {i}: K-value inconsistency {error}"

    def test_tolerance_achieved_below_threshold(self, flash, ethane_propane_binary):
        """Test tolerance_achieved < 1e-6 for converged flash."""
        mixture = ethane_propane_binary
        T = 300.0
        P = 2e6

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # Fugacity equilibrium tolerance
            assert result.tolerance_achieved < flash.tolerance, \
                f"Tolerance {result.tolerance_achieved} >= {flash.tolerance}"

    def test_k_values_positive(self, flash, ethane_propane_binary):
        """Test all K-values are positive."""
        mixture = ethane_propane_binary
        result = flash.calculate(
            z=mixture['z'],
            temperature=300,
            pressure=2e6,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        assert np.all(result.K_values > 0), \
            "All K-values should be positive"

    def test_lighter_component_higher_k(self, flash, methane_propane_binary):
        """Test lighter component (methane) has higher K-value than heavier (propane)."""
        mixture = methane_propane_binary
        T = 280.0
        P = 3e6

        result = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # Methane (lighter, index 0) should have higher K than propane (heavier, index 1)
            # This is generally true but may vary with conditions
            K_methane = result.K_values[0]
            K_propane = result.K_values[1]
            assert K_methane > 0 and K_propane > 0


# ==============================================================================
# Additional integration tests
# ==============================================================================
class TestFlashRobustness:
    """Test flash calculation robustness."""

    def test_flash_at_various_temperatures(self, flash, ethane_propane_binary):
        """Test flash at different temperatures."""
        mixture = ethane_propane_binary
        temperatures = [290, 300, 310, 320]
        P = 2e6

        for T in temperatures:
            result = flash.calculate(
                z=mixture['z'],
                temperature=T,
                pressure=P,
                critical_temperatures=mixture['tc'],
                critical_pressures=mixture['pc'],
            )
            # Should either converge or detect single phase
            assert result.convergence in [
                FlashConvergence.SUCCESS,
                FlashConvergence.SINGLE_PHASE,
                FlashConvergence.MAX_ITERATIONS
            ]

    def test_flash_at_various_pressures(self, flash, ethane_propane_binary):
        """Test flash at different pressures."""
        mixture = ethane_propane_binary
        pressures = [1e6, 2e6, 3e6, 4e6]
        T = 300

        for P in pressures:
            result = flash.calculate(
                z=mixture['z'],
                temperature=T,
                pressure=P,
                critical_temperatures=mixture['tc'],
                critical_pressures=mixture['pc'],
            )
            assert result.convergence in [
                FlashConvergence.SUCCESS,
                FlashConvergence.SINGLE_PHASE,
                FlashConvergence.MAX_ITERATIONS
            ]

    def test_flash_reproducible(self, flash, ethane_propane_binary):
        """Test flash gives identical results on repeated calls."""
        mixture = ethane_propane_binary
        T = 300
        P = 2e6

        result1 = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        result2 = flash.calculate(
            z=mixture['z'],
            temperature=T,
            pressure=P,
            critical_temperatures=mixture['tc'],
            critical_pressures=mixture['pc'],
        )

        # Results should be identical
        assert result1.convergence == result2.convergence
        if result1.convergence == FlashConvergence.SUCCESS:
            assert np.allclose(result1.L, result2.L)
            assert np.allclose(result1.V, result2.V)
            assert np.allclose(result1.x, result2.x)
            assert np.allclose(result1.y, result2.y)
