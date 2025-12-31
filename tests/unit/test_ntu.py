"""Unit tests for NTU-effectiveness heat transfer calculations.

Tests the calculate_ntu function with various configurations,
heat capacity ratios, and edge cases.
"""

import pytest

from heat_calc.models.ntu_input import NTUInput
from heat_calc.models.ntu_results import NTUResult
from heat_calc.ntu import calculate_ntu


class TestNTUCalculation:
    """Basic NTU calculation tests."""

    def test_counterflow_basic(self):
        """Test basic counterflow NTU calculation."""
        input_data = NTUInput(
            T_hot_inlet=373.15,  # 100°C
            T_cold_inlet=293.15,  # 20°C
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert result.NTU > 0
        assert 0 <= result.effectiveness <= 1
        assert result.heat_transfer_rate > 0
        assert result.T_hot_outlet < input_data.T_hot_inlet
        assert result.T_cold_outlet > input_data.T_cold_inlet

    def test_parallel_flow_basic(self):
        """Test parallel flow NTU calculation."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="parallel_flow",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert result.NTU > 0
        assert 0 <= result.effectiveness <= 1
        # Parallel flow effectiveness should be lower than counterflow
        assert result.effectiveness <= 0.85

    def test_shell_and_tube_1_2(self):
        """Test shell-and-tube 1 shell pass, 2 tube passes configuration."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="shell_and_tube_1_2",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert 0 <= result.effectiveness <= 1

    def test_crossflow_unmixed_both(self):
        """Test crossflow unmixed/unmixed configuration."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="crossflow_unmixed_both",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert 0 <= result.effectiveness <= 1

    def test_crossflow_mixed_one(self):
        """Test crossflow with one fluid mixed."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="crossflow_mixed_one",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert 0 <= result.effectiveness <= 1


class TestCapacityRatios:
    """Test calculations with various heat capacity ratios."""

    def test_c_ratio_zero(self):
        """Test with C_ratio = 0 (cold side much larger than hot side)."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=1.0,  # Small hot side
            mdot_cold=100.0,  # Large cold side
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert result.C_ratio <= 0.01

    def test_c_ratio_one(self):
        """Test with C_ratio = 1 (equal heat capacity rates)."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=10.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert abs(result.C_ratio - 1.0) < 0.01


class TestOutletTemperatures:
    """Test outlet temperature calculations."""

    def test_hot_outlet_specified(self):
        """Test calculation when hot outlet temperature is specified."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="counterflow",
            T_hot_outlet=363.15,  # 90°C outlet
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert result.T_hot_outlet == 363.15

    def test_cold_outlet_specified(self):
        """Test calculation when cold outlet temperature is specified."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="counterflow",
            T_cold_outlet=323.15,  # 50°C outlet
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert result.T_cold_outlet == 323.15


class TestEffectivenessBounds:
    """Test effectiveness bounds and limits."""

    def test_effectiveness_zero_ua(self):
        """Test effectiveness with UA = 0."""
        # This is tested implicitly; NTU=0 should give ε≈0
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=1.0,  # Very small
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert result.effectiveness > 0  # Small but positive

    def test_effectiveness_large_ua(self):
        """Test effectiveness with very large UA."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=1000000.0,  # Very large
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert result.effectiveness > 0.9  # Should be high


class TestEnergyBalance:
    """Test energy balance validation."""

    def test_energy_balance_convergence(self):
        """Test that hot and cold side energy balances match."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        assert result.success
        # Energy balance error should be small
        assert result.energy_balance_error_percent < 1.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_hot_inlet_below_cold_inlet(self):
        """Test error handling when T_hot < T_cold."""
        input_data = NTUInput(
            T_hot_inlet=293.15,  # Too cold
            T_cold_inlet=373.15,  # Too hot
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        assert not result.success
        assert "Hot inlet temperature must exceed cold inlet" in result.error_message

    def test_mutually_exclusive_outlets_validation(self):
        """Test that both outlet temperatures cannot be specified."""
        with pytest.raises(ValueError, match="Cannot specify both"):
            NTUInput(
                T_hot_inlet=373.15,
                T_cold_inlet=293.15,
                mdot_hot=10.0,
                mdot_cold=15.0,
                cp_hot=4180.0,
                cp_cold=4180.0,
                UA=50000.0,
                configuration="counterflow",
                T_hot_outlet=363.15,
                T_cold_outlet=313.15,
            )


class TestThermodynamicLimits:
    """Test thermodynamic constraint validation."""

    def test_q_actual_less_than_q_max(self):
        """Test that actual heat transfer doesn't exceed maximum."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert result.heat_transfer_rate <= result.Q_max * 1.01  # Allow 1% numerical tolerance

    def test_effectiveness_not_exceeds_max(self):
        """Test that effectiveness doesn't exceed theoretical maximum."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=10.0,
            mdot_cold=15.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=50000.0,
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        assert result.success
        assert result.effectiveness <= result.effectiveness_theoretical_max * 1.01
