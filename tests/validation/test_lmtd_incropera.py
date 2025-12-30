"""Validation tests for LMTD calculations against reference data.

Compares LMTD calculation results against published examples from
Incropera et al. "Fundamentals of Heat and Mass Transfer" and NIST
reference data to ensure accuracy.

Reference: data/reference_test_cases.json
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from heat_calc.lmtd import calculate_lmtd
from heat_calc.models import (
    FluidState,
    HeatExchangerConfiguration,
    LMTDInput,
)


@pytest.fixture
def reference_data() -> Dict[str, Any]:
    """Load reference test cases from JSON file."""
    ref_file = Path(__file__).parent.parent.parent / "data" / "reference_test_cases.json"
    with open(ref_file, "r") as f:
        return json.load(f)


class TestLMTDIncoprora:
    """Test LMTD calculations against Incropera reference examples."""

    def test_incropera_counterflow_basic(self, reference_data: Dict[str, Any]) -> None:
        """Test LMTD_001: Incropera Example 10.1 - Counterflow."""
        case = reference_data["lmtd"][0]
        assert case["case_id"] == "LMTD_001"

        # Create input from reference case
        hot_in = FluidState(
            temperature=case["hot_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )
        hot_out = FluidState(
            temperature=case["hot_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )
        cold_in = FluidState(
            temperature=case["cold_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )
        cold_out = FluidState(
            temperature=case["cold_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )

        config = HeatExchangerConfiguration(
            configuration=case["configuration"],
            area=case["area_m2"],
            overall_heat_transfer_coefficient=case["heat_transfer_rate_w"] / (case["area_m2"] * case["expected_lmtd_k"])
        )

        input_data = LMTDInput(
            hot_fluid_inlet=hot_in,
            hot_fluid_outlet=hot_out,
            cold_fluid_inlet=cold_in,
            cold_fluid_outlet=cold_out,
            heat_exchanger=config
        )

        result = calculate_lmtd(input_data)

        # Check success
        assert result.success, f"Calculation failed: {result.error_message}"

        # Verify LMTD matches reference within tolerance
        tolerance = case["tolerance_percent"] / 100.0
        expected_lmtd = case["expected_lmtd_k"]
        relative_error = abs(result.lmtd_arithmetic - expected_lmtd) / expected_lmtd

        assert relative_error < tolerance, \
            f"LMTD error {relative_error*100:.2f}% exceeds {case['tolerance_percent']:.1f}% tolerance. " \
            f"Expected {expected_lmtd:.2f} K, got {result.lmtd_arithmetic:.2f} K"

    def test_incropera_parallel_flow(self, reference_data: Dict[str, Any]) -> None:
        """Test LMTD_002: Incropera Example 10.2 - Parallel flow."""
        case = reference_data["lmtd"][1]
        assert case["case_id"] == "LMTD_002"

        hot_in = FluidState(
            temperature=case["hot_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )
        hot_out = FluidState(
            temperature=case["hot_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )
        cold_in = FluidState(
            temperature=case["cold_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )
        cold_out = FluidState(
            temperature=case["cold_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )

        config = HeatExchangerConfiguration(
            configuration=case["configuration"],
            area=case["area_m2"],
            overall_heat_transfer_coefficient=case["heat_transfer_rate_w"] / (case["area_m2"] * case["expected_lmtd_k"])
        )

        input_data = LMTDInput(
            hot_fluid_inlet=hot_in,
            hot_fluid_outlet=hot_out,
            cold_fluid_inlet=cold_in,
            cold_fluid_outlet=cold_out,
            heat_exchanger=config
        )

        result = calculate_lmtd(input_data)

        assert result.success
        tolerance = case["tolerance_percent"] / 100.0
        expected_lmtd = case["expected_lmtd_k"]
        relative_error = abs(result.lmtd_arithmetic - expected_lmtd) / expected_lmtd

        assert relative_error < tolerance, \
            f"LMTD error {relative_error*100:.2f}% exceeds {case['tolerance_percent']:.1f}%"

    def test_incropera_crossflow_unmixed(self, reference_data: Dict[str, Any]) -> None:
        """Test LMTD_003: Incropera Example 10.3 - Crossflow unmixed."""
        case = reference_data["lmtd"][2]
        assert case["case_id"] == "LMTD_003"

        hot_in = FluidState(
            temperature=case["hot_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )
        hot_out = FluidState(
            temperature=case["hot_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )
        cold_in = FluidState(
            temperature=case["cold_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )
        cold_out = FluidState(
            temperature=case["cold_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4200.0
        )

        config = HeatExchangerConfiguration(
            configuration=case["configuration"],
            area=case["area_m2"],
            correction_factor=case.get("correction_factor_f", 0.90),
            overall_heat_transfer_coefficient=case["heat_transfer_rate_w"] / (case["area_m2"] * case["expected_lmtd_k"])
        )

        input_data = LMTDInput(
            hot_fluid_inlet=hot_in,
            hot_fluid_outlet=hot_out,
            cold_fluid_inlet=cold_in,
            cold_fluid_outlet=cold_out,
            heat_exchanger=config
        )

        result = calculate_lmtd(input_data)

        assert result.success
        tolerance = case["tolerance_percent"] / 100.0
        expected_lmtd = case["expected_lmtd_k"]
        relative_error = abs(result.lmtd_arithmetic - expected_lmtd) / expected_lmtd

        assert relative_error < tolerance

    def test_nist_reference_water_water(self, reference_data: Dict[str, Any]) -> None:
        """Test LMTD_004: NIST water-water counterflow case."""
        case = reference_data["lmtd"][3]
        assert case["case_id"] == "LMTD_004"

        hot_in = FluidState(
            temperature=case["hot_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4180.0
        )
        hot_out = FluidState(
            temperature=case["hot_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4180.0
        )
        cold_in = FluidState(
            temperature=case["cold_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4180.0
        )
        cold_out = FluidState(
            temperature=case["cold_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4180.0
        )

        config = HeatExchangerConfiguration(
            configuration=case["configuration"],
            area=case["area_m2"],
            overall_heat_transfer_coefficient=case["heat_transfer_rate_w"] / (case["area_m2"] * case["expected_lmtd_k"])
        )

        input_data = LMTDInput(
            hot_fluid_inlet=hot_in,
            hot_fluid_outlet=hot_out,
            cold_fluid_inlet=cold_in,
            cold_fluid_outlet=cold_out,
            heat_exchanger=config
        )

        result = calculate_lmtd(input_data)

        assert result.success
        tolerance = case["tolerance_percent"] / 100.0
        expected_lmtd = case["expected_lmtd_k"]
        relative_error = abs(result.lmtd_arithmetic - expected_lmtd) / expected_lmtd

        assert relative_error < tolerance

    def test_near_pinch_point(self, reference_data: Dict[str, Any]) -> None:
        """Test LMTD_005: Near-pinch-point case with low effectiveness."""
        case = reference_data["lmtd"][4]
        assert case["case_id"] == "LMTD_005"

        hot_in = FluidState(
            temperature=case["hot_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4180.0
        )
        hot_out = FluidState(
            temperature=case["hot_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4180.0
        )
        cold_in = FluidState(
            temperature=case["cold_inlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4180.0
        )
        cold_out = FluidState(
            temperature=case["cold_outlet_temp_k"],
            mass_flow_rate=1.0,
            specific_heat=4180.0
        )

        config = HeatExchangerConfiguration(
            configuration=case["configuration"],
            area=case["area_m2"],
            overall_heat_transfer_coefficient=case["heat_transfer_rate_w"] / (case["area_m2"] * case["expected_lmtd_k"])
        )

        input_data = LMTDInput(
            hot_fluid_inlet=hot_in,
            hot_fluid_outlet=hot_out,
            cold_fluid_inlet=cold_in,
            cold_fluid_outlet=cold_out,
            heat_exchanger=config
        )

        result = calculate_lmtd(input_data)

        assert result.success
        tolerance = case["tolerance_percent"] / 100.0
        expected_lmtd = case["expected_lmtd_k"]
        relative_error = abs(result.lmtd_arithmetic - expected_lmtd) / expected_lmtd

        assert relative_error < tolerance, \
            f"Near-pinch case: LMTD error {relative_error*100:.2f}% exceeds {case['tolerance_percent']:.1f}%"


class TestLMTDRobustness:
    """Test LMTD calculation robustness across multiple configurations."""

    def test_all_lmtd_reference_cases(self, reference_data: Dict[str, Any]) -> None:
        """Test all LMTD reference cases pass with required tolerance."""
        lmtd_cases = reference_data["lmtd"]
        passed = 0
        failed = 0

        for case in lmtd_cases:
            hot_in = FluidState(
                temperature=case["hot_inlet_temp_k"],
                mass_flow_rate=1.0,
                specific_heat=4180.0
            )
            hot_out = FluidState(
                temperature=case["hot_outlet_temp_k"],
                mass_flow_rate=1.0,
                specific_heat=4180.0
            )
            cold_in = FluidState(
                temperature=case["cold_inlet_temp_k"],
                mass_flow_rate=1.0,
                specific_heat=4180.0
            )
            cold_out = FluidState(
                temperature=case["cold_outlet_temp_k"],
                mass_flow_rate=1.0,
                specific_heat=4180.0
            )

            config = HeatExchangerConfiguration(
                configuration=case["configuration"],
                area=case["area_m2"],
                correction_factor=case.get("correction_factor_f"),
                overall_heat_transfer_coefficient=case["heat_transfer_rate_w"] / (case["area_m2"] * case["expected_lmtd_k"])
            )

            input_data = LMTDInput(
                hot_fluid_inlet=hot_in,
                hot_fluid_outlet=hot_out,
                cold_fluid_inlet=cold_in,
                cold_fluid_outlet=cold_out,
                heat_exchanger=config
            )

            result = calculate_lmtd(input_data)

            if result.success:
                tolerance = case["tolerance_percent"] / 100.0
                expected_lmtd = case["expected_lmtd_k"]
                relative_error = abs(result.lmtd_arithmetic - expected_lmtd) / expected_lmtd

                if relative_error < tolerance:
                    passed += 1
                else:
                    failed += 1
            else:
                failed += 1

        # Require 100% pass rate
        assert failed == 0, f"{failed} out of {len(lmtd_cases)} reference cases failed"
        assert passed == len(lmtd_cases), f"Only {passed} out of {len(lmtd_cases)} passed"
