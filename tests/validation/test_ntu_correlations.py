"""Validation tests for NTU-effectiveness correlations.

Tests NTU calculations against published correlations and reference data from:
- Incropera & DeWitt: "Fundamentals of Heat and Mass Transfer"
- Perry's Chemical Engineers' Handbook
- ESCOA NTU effectiveness charts
"""

import json
import math
from pathlib import Path

import pytest

from heat_calc.models.ntu_input import NTUInput
from heat_calc.ntu import calculate_ntu


class TestNTUCorrelationValidation:
    """Validate NTU correlations against published references."""

    def test_counterflow_incropera_example_11_3(self):
        """Validate against Incropera Example 11.3.

        Source: Incropera & DeWitt, 9th ed., Page 684
        Configuration: Counterflow heat exchanger
        Hot water: m_h = 2 kg/s, T_h,in = 90°C, cp = 4180 J/(kg·K)
        Cold water: m_c = 1 kg/s, T_c,in = 30°C, cp = 4180 J/(kg·K)
        UA = 10,000 W/K
        """
        input_data = NTUInput(
            T_hot_inlet=363.15,  # 90°C
            T_cold_inlet=303.15,  # 30°C
            mdot_hot=2.0,
            mdot_cold=1.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=10000.0,
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        # Expected values from Incropera
        # C_min = 1 × 4180 = 4180 W/K
        # C_ratio = 4180 / 8360 = 0.5
        # NTU = 10000 / 4180 ≈ 2.39
        # Expected ε ≈ 0.826
        # Q ≈ 0.826 × 4180 × 60 ≈ 207 kW

        assert result.success
        assert abs(result.C_ratio - 0.5) < 0.01
        assert abs(result.NTU - 2.39) < 0.05
        assert abs(result.effectiveness - 0.826) < 0.02  # 2% tolerance
        assert abs(result.heat_transfer_rate - 207000) < 5000  # 5 kW tolerance

    def test_parallel_flow_effectiveness_limit(self):
        """Validate parallel flow effectiveness approaches theoretical maximum.

        Source: Incropera & DeWitt, Figure 11.14
        For C_r = 0.5, NTU → ∞, ε_max = 1/(1+C_r) = 0.667
        """
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=2.0,
            mdot_cold=1.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=500000.0,  # Very large UA for high NTU
            configuration="parallel_flow",
        )

        result = calculate_ntu(input_data)

        # Theoretical max for C_r=0.5: ε_max = 1/1.5 ≈ 0.667
        assert result.success
        assert abs(result.effectiveness_theoretical_max - 0.667) < 0.01
        assert abs(result.effectiveness - 0.667) < 0.02

    def test_crossflow_unmixed_perrys_correlation(self):
        """Validate crossflow unmixed/unmixed against Perry's Handbook.

        Source: Perry's Chemical Engineers' Handbook, 8th ed., Section 11
        Configuration: Crossflow, both fluids unmixed
        For NTU = 1.0, C_r = 0.75, ε ≈ 0.47
        """
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=2.0,
            mdot_cold=1.5,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=6270.0,  # NTU = 1.0
            configuration="crossflow_unmixed_both",
        )

        result = calculate_ntu(input_data)

        # Expected: NTU ≈ 1.0, C_r ≈ 0.75, ε ≈ 0.47
        # Note: Different references use slightly different crossflow correlations
        assert result.success
        assert abs(result.NTU - 1.0) < 0.05
        assert abs(result.C_ratio - 0.75) < 0.01
        assert abs(result.effectiveness - 0.47) < 0.05  # 5% tolerance for correlation differences

    def test_counterflow_c_ratio_zero_limit(self):
        """Validate C_ratio = 0 limit case.

        Source: Incropera & DeWitt, Equation 11.30
        For C_r = 0, ε = 1 - exp(-NTU)
        With NTU = 2, ε = 1 - exp(-2) ≈ 0.865
        """
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=1.0,
            mdot_cold=100.0,  # Very large cold side → C_r ≈ 0
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=8360.0,  # NTU = 2.0
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        # Expected: C_r ≈ 0, NTU ≈ 2, ε ≈ 0.865
        expected_eff = 1.0 - math.exp(-2.0)
        assert result.success
        assert result.C_ratio < 0.02
        assert abs(result.NTU - 2.0) < 0.05
        assert abs(result.effectiveness - expected_eff) < 0.02

    def test_counterflow_c_ratio_one_limit(self):
        """Validate C_ratio = 1 limit case.

        Source: Incropera & DeWitt, Equation 11.33
        For C_r = 1, ε = NTU / (1 + NTU)
        With NTU = 2, ε = 2/3 ≈ 0.667
        """
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=2.0,
            mdot_cold=2.0,  # Equal mass flows → C_r = 1
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=16720.0,  # NTU = 2.0
            configuration="counterflow",
        )

        result = calculate_ntu(input_data)

        # Expected: C_r = 1, NTU = 2, ε = 2/3 ≈ 0.667
        expected_eff = 2.0 / (1.0 + 2.0)
        assert result.success
        assert abs(result.C_ratio - 1.0) < 0.01
        assert abs(result.NTU - 2.0) < 0.05
        assert abs(result.effectiveness - expected_eff) < 0.01


class TestNTUEnergyBalanceValidation:
    """Validate energy balance for all configurations."""

    @pytest.mark.parametrize(
        "configuration",
        [
            "counterflow",
            "parallel_flow",
            "shell_and_tube_1_2",
            "crossflow_unmixed_both",
            "crossflow_mixed_one",
        ],
    )
    def test_energy_balance_all_configurations(self, configuration):
        """Validate energy balance for all supported configurations."""
        input_data = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=2.0,
            mdot_cold=1.5,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=10000.0,
            configuration=configuration,
        )

        result = calculate_ntu(input_data)

        # Energy balance: Q_hot should equal Q_cold within 2%
        assert result.success
        assert result.energy_balance_error_percent < 2.0

        # Verify Q matches expected from outlet temperatures
        Q_hot = input_data.mdot_hot * input_data.cp_hot * (
            input_data.T_hot_inlet - result.T_hot_outlet
        )
        Q_cold = input_data.mdot_cold * input_data.cp_cold * (
            result.T_cold_outlet - input_data.T_cold_inlet
        )

        assert abs(Q_hot - result.heat_transfer_rate) < 100  # Within 100 W
        assert abs(Q_cold - result.heat_transfer_rate) < 100


class TestNTUThermodynamicLimits:
    """Validate thermodynamic constraints."""

    def test_effectiveness_increases_with_ntu(self):
        """Validate that effectiveness increases monotonically with NTU."""
        ua_values = [1000, 5000, 10000, 20000, 50000]
        previous_eff = 0.0

        for ua in ua_values:
            input_data = NTUInput(
                T_hot_inlet=373.15,
                T_cold_inlet=293.15,
                mdot_hot=2.0,
                mdot_cold=1.5,
                cp_hot=4180.0,
                cp_cold=4180.0,
                UA=float(ua),
                configuration="counterflow",
            )

            result = calculate_ntu(input_data)

            assert result.success
            assert result.effectiveness > previous_eff
            previous_eff = result.effectiveness

    def test_q_never_exceeds_q_max(self):
        """Validate Q ≤ Q_max for all cases."""
        # Test with various NTU and C_ratio combinations
        test_cases = [
            (1000, 1.0, 1.0),  # Low NTU
            (50000, 2.0, 1.5),  # High NTU
            (10000, 1.0, 100.0),  # C_r ≈ 0
            (10000, 2.0, 2.0),  # C_r = 1
        ]

        for ua, mdot_hot, mdot_cold in test_cases:
            input_data = NTUInput(
                T_hot_inlet=373.15,
                T_cold_inlet=293.15,
                mdot_hot=mdot_hot,
                mdot_cold=mdot_cold,
                cp_hot=4180.0,
                cp_cold=4180.0,
                UA=float(ua),
                configuration="counterflow",
            )

            result = calculate_ntu(input_data)

            assert result.success
            assert result.heat_transfer_rate <= result.Q_max * 1.01  # 1% tolerance


class TestNTUConfigurationComparison:
    """Compare effectiveness across different configurations."""

    def test_counterflow_most_effective(self):
        """Validate counterflow is most effective for same NTU and C_r."""
        base_input = {
            "T_hot_inlet": 373.15,
            "T_cold_inlet": 293.15,
            "mdot_hot": 2.0,
            "mdot_cold": 1.5,
            "cp_hot": 4180.0,
            "cp_cold": 4180.0,
            "UA": 10000.0,
        }

        counterflow = calculate_ntu(
            NTUInput(**base_input, configuration="counterflow")
        )
        parallel = calculate_ntu(
            NTUInput(**base_input, configuration="parallel_flow")
        )

        assert counterflow.success and parallel.success
        # Counterflow should have higher effectiveness than parallel
        assert counterflow.effectiveness > parallel.effectiveness

    def test_parallel_flow_lowest_effectiveness(self):
        """Validate parallel flow has lowest effectiveness limit."""
        input_data_parallel = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=2.0,
            mdot_cold=1.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=500000.0,  # Very high NTU
            configuration="parallel_flow",
        )

        input_data_counterflow = NTUInput(
            T_hot_inlet=373.15,
            T_cold_inlet=293.15,
            mdot_hot=2.0,
            mdot_cold=1.0,
            cp_hot=4180.0,
            cp_cold=4180.0,
            UA=500000.0,
            configuration="counterflow",
        )

        parallel = calculate_ntu(input_data_parallel)
        counterflow = calculate_ntu(input_data_counterflow)

        # At high NTU, counterflow approaches 1.0, parallel approaches < 1.0
        assert parallel.effectiveness_theoretical_max < 1.0
        assert counterflow.effectiveness_theoretical_max == 1.0
        assert parallel.effectiveness < counterflow.effectiveness
