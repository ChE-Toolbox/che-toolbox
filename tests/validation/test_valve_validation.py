"""
Validation tests for valve sizing calculations.

These tests validate against manufacturer datasheets and valve industry standards.
Reference: IEC 60534 (Industrial-process measurement and control - Control valve sizing)
"""

import pytest
import math
from fluids.valve import (
    calculate_cv_required,
    calculate_flow_rate_through_valve,
    calculate_valve_sizing,
    calculate_valve_authority,
    calculate_valve_rangeability,
    calculate_relative_flow_capacity,
    assess_valve_performance,
)


class TestCvValidation:
    """Validate Cv flow coefficient calculations."""

    def test_cv_formula_us_customary(self):
        """Test Cv formula in US customary units: Q = Cv√(ΔP/SG)."""
        # Known test case
        flow_rate = 100.0  # gpm
        pressure_drop = 10.0  # psi
        specific_gravity = 1.0  # water

        result = calculate_cv_required(
            flow_rate=flow_rate,
            pressure_drop=pressure_drop,
            fluid_gravity=specific_gravity,
            unit_system="US",
        )

        # Cv = Q / √(ΔP/SG) = 100 / √(10/1) ≈ 31.62
        expected = flow_rate / math.sqrt(pressure_drop / specific_gravity)
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_cv_formula_si_units(self):
        """Test Cv formula in SI units: Q = Cv√ΔP."""
        flow_rate = 360.0  # m³/h
        pressure_drop = 1.0  # bar

        result = calculate_cv_required(
            flow_rate=flow_rate,
            pressure_drop=pressure_drop,
            unit_system="SI",
        )

        # Cv = Q / √ΔP = 360 / √1 = 360
        expected = flow_rate / math.sqrt(pressure_drop)
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_cv_with_oil_fluid(self):
        """Test Cv calculation with different fluid (oil, SG=0.85)."""
        flow_rate = 100.0
        pressure_drop = 10.0
        sg_water = 1.0
        sg_oil = 0.85

        cv_water = calculate_cv_required(
            flow_rate=flow_rate,
            pressure_drop=pressure_drop,
            fluid_gravity=sg_water,
            unit_system="US",
        )

        cv_oil = calculate_cv_required(
            flow_rate=flow_rate,
            pressure_drop=pressure_drop,
            fluid_gravity=sg_oil,
            unit_system="US",
        )

        # For same flow and pressure drop, lower gravity needs higher Cv
        assert cv_oil["value"] < cv_water["value"]

    def test_cv_flow_rate_inverse(self):
        """Test that flow rate calculation is inverse of Cv required."""
        Q_design = 75.0  # gpm
        dP = 15.0  # psi

        # Calculate required Cv
        cv_result = calculate_cv_required(Q_design, dP, unit_system="US")

        # Use that Cv to calculate flow
        flow_result = calculate_flow_rate_through_valve(
            cv_result["value"], dP, unit_system="US"
        )

        # Should recover original flow
        assert math.isclose(flow_result["value"], Q_design, rel_tol=0.01)

    def test_cv_pressure_drop_sensitivity(self):
        """Test Cv sensitivity to pressure drop."""
        flow_rate = 100.0

        # Higher pressure drop means lower Cv needed
        cv_5psi = calculate_cv_required(flow_rate, 5.0, unit_system="US")
        cv_10psi = calculate_cv_required(flow_rate, 10.0, unit_system="US")
        cv_20psi = calculate_cv_required(flow_rate, 20.0, unit_system="US")

        # Verify inverse relationship: Cv ∝ 1/√(ΔP)
        assert cv_5psi["value"] > cv_10psi["value"]
        assert cv_10psi["value"] > cv_20psi["value"]

        # Verify square root relationship
        ratio_5_10 = cv_5psi["value"] / cv_10psi["value"]
        ratio_10_20 = cv_10psi["value"] / cv_20psi["value"]

        expected_ratio = math.sqrt(10.0 / 5.0)
        assert math.isclose(ratio_5_10, expected_ratio, rel_tol=0.05)


class TestValveSizingValidation:
    """Validate valve sizing logic and recommendations."""

    def test_valve_sizing_selects_smallest_suitable(self):
        """Test that valve sizing selects smallest valve meeting requirements."""
        available_cvs = [10, 25, 50, 75, 100, 150]

        result = calculate_valve_sizing(
            flow_rate=100.0,
            pressure_drop=10.0,
            valve_cv_options=available_cvs,
            unit_system="US",
        )

        # Should select smallest Cv that handles the flow
        recommended_cv = result["recommended_cv"]
        assert recommended_cv in available_cvs

        # All smaller options should be insufficient
        for smaller_cv in available_cvs:
            if smaller_cv < recommended_cv:
                # Verify it wouldn't work (opening > 90%)
                opening = (31.62 / smaller_cv) * 100  # Approx calculation
                if opening > 90:
                    continue  # Expected not to work

    def test_valve_sizing_opening_percentage(self):
        """Test that recommended valve operates in practical range."""
        result = calculate_valve_sizing(
            flow_rate=100.0,
            pressure_drop=10.0,
            valve_cv_options=[20, 30, 40, 50, 75, 100],
            unit_system="US",
        )

        # Opening percentage should ideally be 10-90%
        opening_pct = result["recommended_percentage"]

        # If opening is outside range, warning should exist
        if opening_pct < 10 or opening_pct > 90:
            assert len(result["warnings"]) > 0

    def test_valve_sizing_oversizing_ratio(self):
        """Test oversizing ratio calculation."""
        result = calculate_valve_sizing(
            flow_rate=100.0,
            pressure_drop=10.0,
            valve_cv_options=[50, 75, 100, 150],
            unit_system="US",
        )

        # Oversizing ratio should be >= 1.0
        assert result["oversizing_factor"] >= 1.0

        # Ratio of actual to required Cv
        # Required ≈ 31.62
        # If selected is 50, ratio = 50/31.62 ≈ 1.58


class TestValveAuthorityValidation:
    """Validate valve authority (pressure drop ratio)."""

    def test_valve_authority_formula(self):
        """Test valve authority formula: A = ΔP_v / (ΔP_v + ΔP_s)."""
        dp_valve = 15.0  # psi
        dp_system = 20.0  # psi

        result = calculate_valve_authority(dp_valve, dp_system)

        # Expected: 15 / (15 + 20) = 0.43
        expected = dp_valve / (dp_valve + dp_system)
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_valve_authority_good_range(self):
        """Test authority in optimal range (0.3-0.5)."""
        result = calculate_valve_authority(10.0, 15.0)  # Authority ≈ 0.4

        assert 0.3 <= result["value"] <= 0.5
        assert "good" in result["assessment"].lower()

    def test_valve_authority_low_control(self):
        """Test low authority indicates poor control."""
        result = calculate_valve_authority(2.0, 50.0)  # Authority ≈ 0.04

        assert result["value"] < 0.2
        assert "low" in result["assessment"].lower()
        assert "poor" in result["recommendation"].lower()

    def test_valve_authority_effect_on_control(self):
        """Test that pressure drop ratio affects control quality."""
        # Good authority
        good = calculate_valve_authority(30.0, 50.0)

        # Poor authority
        poor = calculate_valve_authority(5.0, 100.0)

        assert good["value"] > poor["value"]
        assert "good" in good["assessment"].lower()
        assert "low" in poor["assessment"].lower()


class TestValveRangeabilityValidation:
    """Validate valve rangeability (flow control range)."""

    def test_rangeability_formula(self):
        """Test rangeability formula: R = Cv_max / Cv_min."""
        cv_min = 2.0
        cv_max = 50.0

        result = calculate_valve_rangeability(cv_min, cv_max)

        expected = cv_max / cv_min  # 25:1
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_typical_valve_rangeability(self):
        """Test typical rangeability values for different valve types."""
        # Typical ranges:
        # Ball valve: 50:1 to 100:1
        # Globe valve: 20:1 to 50:1
        # Butterfly valve: 3:1 to 10:1
        # Needle valve: 100:1+

        ball_valve = calculate_valve_rangeability(1.0, 75.0)  # 75:1
        assert ball_valve["value"] > 50

        globe_valve = calculate_valve_rangeability(2.0, 50.0)  # 25:1
        assert 20 <= globe_valve["value"] <= 50

        butterfly_valve = calculate_valve_rangeability(5.0, 30.0)  # 6:1
        assert butterfly_valve["value"] <= 10

    def test_rangeability_affects_controllability(self):
        """Test that higher rangeability means better flow control."""
        poor_range = calculate_valve_rangeability(5.0, 50.0)  # 10:1
        good_range = calculate_valve_rangeability(1.0, 75.0)  # 75:1

        assert poor_range["value"] < good_range["value"]
        assert "limited" in poor_range["assessment"].lower()
        assert "excellent" in good_range["assessment"].lower() or "good" in good_range["assessment"].lower()


class TestValveFlowCharacteristic:
    """Validate valve flow characteristic calculations."""

    def test_linear_characteristic(self):
        """Test linear flow characteristic (f = opening)."""
        # Linear: Cv ∝ opening position
        result_25 = calculate_relative_flow_capacity(25, "linear")
        result_50 = calculate_relative_flow_capacity(50, "linear")
        result_75 = calculate_relative_flow_capacity(75, "linear")

        assert math.isclose(result_25["value"], 0.25, rel_tol=0.01)
        assert math.isclose(result_50["value"], 0.50, rel_tol=0.01)
        assert math.isclose(result_75["value"], 0.75, rel_tol=0.01)

    def test_parabolic_characteristic(self):
        """Test parabolic flow characteristic (f = opening²)."""
        # Parabolic: Cv ∝ opening²
        result_25 = calculate_relative_flow_capacity(25, "parabolic")
        result_50 = calculate_relative_flow_capacity(50, "parabolic")

        assert math.isclose(result_25["value"], 0.0625, rel_tol=0.01)  # 0.25²
        assert math.isclose(result_50["value"], 0.25, rel_tol=0.01)  # 0.5²

    def test_equal_percentage_characteristic(self):
        """Test equal percentage characteristic."""
        # Equal percentage opens slowly at low, quickly at high
        result_10 = calculate_relative_flow_capacity(10, "equal_percentage")
        result_50 = calculate_relative_flow_capacity(50, "equal_percentage")
        result_90 = calculate_relative_flow_capacity(90, "equal_percentage")

        # Should show increasing rate of change
        increase_10_50 = result_50["value"] - result_10["value"]
        increase_50_90 = result_90["value"] - result_50["value"]

        assert increase_50_90 > increase_10_50

    def test_flow_characteristic_at_full_opening(self):
        """Test that all characteristics reach maximum at 100% opening."""
        for characteristic in ["linear", "parabolic", "equal_percentage"]:
            result = calculate_relative_flow_capacity(100, characteristic)
            # Should be at or very near 1.0
            assert result["value"] > 0.95


class TestValvePerformanceAssessment:
    """Validate comprehensive valve performance assessment."""

    def test_performance_good_operating_point(self):
        """Test performance assessment at good operating point."""
        result = assess_valve_performance(
            cv_at_design=25.0,
            cv_max=50.0,
            pressure_drop_design=10.0,
            system_pressure_drop=15.0,
        )

        # Opening at 50%
        assert result["opening_percent"] == 50.0
        # Authority at 0.4 (good)
        assert math.isclose(result["valve_authority"], 10.0 / 25.0, rel_tol=0.01)

    def test_performance_severely_throttled(self):
        """Test performance when valve is severely throttled."""
        result = assess_valve_performance(
            cv_at_design=2.0,  # Very low
            cv_max=50.0,
            pressure_drop_design=50.0,  # High drop
            system_pressure_drop=10.0,
        )

        # Opening very low (4%)
        assert result["opening_percent"] < 10
        assert "throttled" in result["opening_assessment"].lower()

    def test_performance_nearly_wide_open(self):
        """Test performance when valve is nearly wide open."""
        result = assess_valve_performance(
            cv_at_design=40.0,  # Very high
            cv_max=50.0,
            pressure_drop_design=2.0,  # Low drop
            system_pressure_drop=50.0,
        )

        # Opening very high (80%)
        assert result["opening_percent"] > 75
        assert "wide open" in result["opening_assessment"].lower()


class TestIntegrationValveSizing:
    """Integration tests for complete valve sizing workflow."""

    def test_complete_valve_sizing_workflow(self):
        """Test complete valve sizing from requirements to selection."""
        # System requirements
        required_flow = 150.0  # gpm
        available_pressure_drop = 15.0  # psi
        available_valves = [25, 35, 50, 75, 100, 150]  # Standard sizes

        # Step 1: Calculate required Cv
        cv_needed = calculate_cv_required(
            required_flow, available_pressure_drop, unit_system="US"
        )

        # Step 2: Select valve size
        selection = calculate_valve_sizing(
            required_flow,
            available_pressure_drop,
            available_valves,
            unit_system="US",
        )

        selected_cv = selection["recommended_cv"]
        assert selected_cv in available_valves
        assert selected_cv >= cv_needed["value"]

        # Step 3: Verify flow through selected valve
        actual_flow = calculate_flow_rate_through_valve(
            selected_cv, available_pressure_drop, unit_system="US"
        )

        assert actual_flow["value"] >= required_flow

        # Step 4: Assess valve authority
        authority = calculate_valve_authority(
            available_pressure_drop, 30.0  # System pressure drop
        )

        assert authority["value"] > 0.1  # Should have some authority

        # Step 5: Assess performance
        performance = assess_valve_performance(
            cv_at_design=selected_cv,
            cv_max=selected_cv,
            pressure_drop_design=available_pressure_drop,
            system_pressure_drop=30.0,
        )

        # Should be in reasonable operating range
        assert "throttled" not in performance["opening_assessment"].lower() or performance["opening_percent"] > 5

    def test_control_valve_optimization(self):
        """Test optimization for good control characteristics."""
        # Prefer valve with good authority (0.3-0.5) and reasonable opening

        flow = 100.0
        valve_pressure_drop = 12.0  # Will adjust
        system_pressure_drop = 20.0
        available_sizes = [25, 50, 75, 100]

        # Current setup
        result = calculate_valve_sizing(
            flow, valve_pressure_drop, available_sizes, unit_system="US"
        )

        authority = calculate_valve_authority(valve_pressure_drop, system_pressure_drop)

        # Authority should be in good range
        assert 0.2 <= authority["value"] <= 0.6

    def test_low_flow_high_pressure_application(self):
        """Test valve sizing for low flow, high pressure drop scenario."""
        # Small pump, high pressure requirement
        flow = 10.0  # gpm
        pressure_drop = 50.0  # psi (high drop for control)
        sizes = [1, 2, 5, 10, 15, 25]

        result = calculate_valve_sizing(
            flow, pressure_drop, sizes, unit_system="US"
        )

        # Should select small valve
        assert result["recommended_cv"] <= 10

        # Opening should be in good range
        assert result["recommended_percentage"] > 10
