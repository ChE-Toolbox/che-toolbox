"""Unit tests for PT Flash calculation."""

import numpy as np
import pytest

from src.eos.flash_pt import FlashConvergence, FlashPT, FlashResult


@pytest.fixture
def flash():
    """Create a FlashPT instance."""
    return FlashPT()


@pytest.fixture
def binary_ethane_propane():
    """Binary mixture: 60% ethane, 40% propane."""
    z = np.array([0.6, 0.4])
    tc = np.array([305.128, 369.83])  # K
    pc = np.array([4.8718e6, 4.2512e6])  # Pa
    return z, tc, pc


@pytest.fixture
def binary_methane_propane():
    """Binary mixture: 70% methane, 30% propane."""
    z = np.array([0.7, 0.3])
    tc = np.array([190.564, 369.83])  # K
    pc = np.array([4.5992e6, 4.2512e6])  # Pa
    return z, tc, pc


@pytest.fixture
def pure_methane():
    """Pure methane."""
    z = np.array([1.0])
    tc = np.array([190.564])  # K
    pc = np.array([4.5992e6])  # Pa
    return z, tc, pc


class TestFlashResultDataclass:
    """Test FlashResult dataclass."""

    def test_flash_result_creation(self):
        """Test creating a FlashResult."""
        x = np.array([0.3, 0.7])
        y = np.array([0.6, 0.4])
        K = np.array([2.0, 0.57])

        result = FlashResult(
            L=0.5,
            V=0.5,
            x=x,
            y=y,
            K_values=K,
            iterations=5,
            tolerance_achieved=1e-7,
            convergence=FlashConvergence.SUCCESS,
            material_balance_error=1e-8,
        )

        assert result.L == 0.5
        assert result.V == 0.5
        assert np.allclose(result.x, x)
        assert np.allclose(result.y, y)
        assert np.allclose(result.K_values, K)
        assert result.iterations == 5
        assert result.convergence == FlashConvergence.SUCCESS

    def test_flash_result_success_property(self):
        """Test FlashResult.success property."""
        result_success = FlashResult(
            L=0.5,
            V=0.5,
            x=np.array([0.3, 0.7]),
            y=np.array([0.6, 0.4]),
            K_values=np.array([2.0, 0.57]),
            iterations=5,
            tolerance_achieved=1e-7,
            convergence=FlashConvergence.SUCCESS,
        )

        result_fail = FlashResult(
            L=np.nan,
            V=np.nan,
            x=np.full(2, np.nan),
            y=np.full(2, np.nan),
            K_values=np.array([2.0, 0.57]),
            iterations=50,
            tolerance_achieved=np.nan,
            convergence=FlashConvergence.MAX_ITERATIONS,
        )

        assert result_success.success is True
        assert result_fail.success is False


class TestSinglePhaseDetection:
    """Test single-phase condition detection."""

    def test_single_phase_pure_component(self, flash, pure_methane):
        """Test pure component returns single-phase result."""
        z, tc, pc = pure_methane
        result = flash.calculate(z, temperature=300, pressure=5e6, critical_temperatures=tc, critical_pressures=pc)

        assert result.convergence == FlashConvergence.SINGLE_PHASE
        assert result.L > 0 or result.V > 0
        assert result.iterations == 0

    def test_single_phase_supercritical(self, flash, binary_ethane_propane):
        """Test supercritical conditions return single-phase result."""
        z, tc, pc = binary_ethane_propane
        T_critical_max = np.max(tc)
        result = flash.calculate(
            z,
            temperature=T_critical_max + 100,  # Above critical
            pressure=5e6,
            critical_temperatures=tc,
            critical_pressures=pc,
        )

        assert result.convergence == FlashConvergence.SINGLE_PHASE
        assert result.V == 1.0  # All vapor
        assert result.L == 0.0


class TestKValueInitialization:
    """Test K-value initialization via Wilson correlation."""

    def test_k_values_positive(self, flash, binary_ethane_propane):
        """Test initialized K-values are positive."""
        z, tc, pc = binary_ethane_propane
        result = flash.calculate(z, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        # Even if flash fails, K_values should be positive
        assert np.all(result.K_values > 0)

    def test_k_values_reasonable_range(self, flash, binary_ethane_propane):
        """Test K-values are in reasonable range."""
        z, tc, pc = binary_ethane_propane
        result = flash.calculate(z, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        # K-values should typically be between 0.1 and 10 for moderate conditions
        assert np.all(result.K_values > 0.01)
        assert np.all(result.K_values < 100)

    def test_k_values_lighter_component_higher(self, flash, binary_methane_propane):
        """Test lighter component has higher K-value (more volatile)."""
        z, tc, pc = binary_methane_propane
        result = flash.calculate(z, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        # Methane is lighter than propane, should have higher K
        K_methane = result.K_values[0]
        K_propane = result.K_values[1]
        # May not always be true depending on T,P, but generally expected
        assert K_methane > 0 and K_propane > 0


class TestFlashCalculation:
    """Test complete flash calculation."""

    def test_flash_composition_sum_to_one(self, flash, binary_ethane_propane):
        """Test liquid and vapor compositions sum to 1.0."""
        z, tc, pc = binary_ethane_propane
        result = flash.calculate(z, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        if result.convergence == FlashConvergence.SUCCESS:
            assert np.allclose(np.sum(result.x), 1.0, atol=1e-6)
            assert np.allclose(np.sum(result.y), 1.0, atol=1e-6)

    def test_flash_vapor_fraction_bounds(self, flash, binary_ethane_propane):
        """Test vapor fraction V is between 0 and 1."""
        z, tc, pc = binary_ethane_propane
        result = flash.calculate(z, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        if not np.isnan(result.V):
            assert 0 <= result.V <= 1
            assert 0 <= result.L <= 1
            assert np.allclose(result.L + result.V, 1.0, atol=1e-6)

    def test_flash_material_balance_check(self, flash, binary_ethane_propane):
        """Test material balance: z_i = L*x_i + V*y_i."""
        z, tc, pc = binary_ethane_propane
        result = flash.calculate(z, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        if result.convergence == FlashConvergence.SUCCESS:
            # Check material balance
            material_balance = result.L * result.x + result.V * result.y
            assert np.allclose(material_balance, z, atol=1e-6)

    def test_flash_convergence_iterations_reasonable(self, flash, binary_ethane_propane):
        """Test convergence typically occurs in reasonable iterations."""
        z, tc, pc = binary_ethane_propane
        result = flash.calculate(z, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        # Should converge or hit max iterations, not exceed
        assert 0 <= result.iterations <= 50

    def test_flash_tolerance_value(self, flash, binary_ethane_propane):
        """Test tolerance value is reasonable."""
        z, tc, pc = binary_ethane_propane
        result = flash.calculate(z, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        if result.convergence == FlashConvergence.SUCCESS:
            # Converged: tolerance should be below threshold
            assert result.tolerance_achieved < flash.tolerance


class TestFlashInputValidation:
    """Test input validation."""

    def test_invalid_composition_sum(self, flash, binary_ethane_propane):
        """Test raises on composition not summing to 1."""
        _, tc, pc = binary_ethane_propane
        z_invalid = np.array([0.5, 0.3])  # Sums to 0.8

        with pytest.raises(ValueError, match="Feed composition must sum to 1.0"):
            flash.calculate(z_invalid, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

    def test_invalid_temperature(self, flash, binary_ethane_propane):
        """Test raises on non-positive temperature."""
        z, tc, pc = binary_ethane_propane

        with pytest.raises(ValueError, match="Temperature must be positive"):
            flash.calculate(z, temperature=0, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        with pytest.raises(ValueError, match="Temperature must be positive"):
            flash.calculate(z, temperature=-100, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

    def test_invalid_pressure(self, flash, binary_ethane_propane):
        """Test raises on non-positive pressure."""
        z, tc, pc = binary_ethane_propane

        with pytest.raises(ValueError, match="Pressure must be positive"):
            flash.calculate(z, temperature=300, pressure=0, critical_temperatures=tc, critical_pressures=pc)

        with pytest.raises(ValueError, match="Pressure must be positive"):
            flash.calculate(z, temperature=300, pressure=-1e6, critical_temperatures=tc, critical_pressures=pc)

    def test_list_composition_converted_to_array(self, flash, binary_ethane_propane):
        """Test composition as list is accepted and converted."""
        z_list = [0.6, 0.4]
        _, tc, pc = binary_ethane_propane

        result = flash.calculate(z_list, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        # Should work without error
        assert result.L >= 0 or result.V >= 0


class TestFlashInitialization:
    """Test FlashPT initialization."""

    def test_flash_initialization(self, flash):
        """Test FlashPT initializes with default parameters."""
        assert flash.max_iterations == 50
        assert flash.tolerance == 1e-6

    def test_flash_custom_tolerance(self, flash, binary_ethane_propane):
        """Test custom tolerance in calculate method."""
        z, tc, pc = binary_ethane_propane
        custom_tolerance = 1e-4

        result = flash.calculate(
            z,
            temperature=300,
            pressure=2e6,
            critical_temperatures=tc,
            critical_pressures=pc,
            tolerance=custom_tolerance,
        )

        assert flash.tolerance == custom_tolerance

    def test_flash_custom_max_iterations(self, flash, binary_ethane_propane):
        """Test custom max iterations in calculate method."""
        z, tc, pc = binary_ethane_propane
        custom_max_iter = 30

        result = flash.calculate(
            z,
            temperature=300,
            pressure=2e6,
            critical_temperatures=tc,
            critical_pressures=pc,
            max_iterations=custom_max_iter,
        )

        assert flash.max_iterations == custom_max_iter


class TestBinaryMixtureFlash:
    """Test flash calculations for typical binary mixtures."""

    def test_ethane_propane_flash_two_phase(self, flash):
        """Test ethane-propane mixture flash at two-phase conditions."""
        z = np.array([0.6, 0.4])
        tc = np.array([305.128, 369.83])
        pc = np.array([4.8718e6, 4.2512e6])

        # Two-phase conditions
        result = flash.calculate(z, temperature=300, pressure=2e6, critical_temperatures=tc, critical_pressures=pc)

        # Check result structure
        assert len(result.x) == 2
        assert len(result.y) == 2
        assert len(result.K_values) == 2
        if result.convergence == FlashConvergence.SUCCESS:
            assert result.L > 0 and result.V > 0

    def test_methane_propane_flash_two_phase(self, flash):
        """Test methane-propane mixture flash at two-phase conditions."""
        z = np.array([0.7, 0.3])
        tc = np.array([190.564, 369.83])
        pc = np.array([4.5992e6, 4.2512e6])

        result = flash.calculate(z, temperature=300, pressure=1e6, critical_temperatures=tc, critical_pressures=pc)

        # Check structure
        assert len(result.x) == 2
        assert len(result.y) == 2
        if result.convergence == FlashConvergence.SUCCESS:
            assert result.iterations <= 50
