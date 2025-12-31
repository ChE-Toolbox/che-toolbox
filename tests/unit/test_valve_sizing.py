"""
Unit tests for valve sizing calculations.

Tests valve Cv, flow rate, and performance calculations.
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


class TestCvCalculations:
    """Test Cv (flow coefficient) calculations."""

    def test_cv_required_basic(self):
        """Test basic Cv requirement calculation."""
        result = calculate_cv_required(
            flow_rate=100.0,  # gpm
            pressure_drop=10.0,  # psi
            unit_system="US",
        )

        assert result["unit"] == "gpm/√psi/sg"
        assert result["value"] > 0
        # Cv = Q / sqrt(ΔP / sg) = 100 / sqrt(10 / 1) ≈ 31.62
        expected = 100.0 / math.sqrt(10.0 / 1.0)
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_cv_required_si_units(self):
        """Test Cv calculation in SI units."""
        result = calculate_cv_required(
            flow_rate=360.0,  # m³/h
            pressure_drop=1.0,  # bar
            unit_system="SI",
        )

        assert result["unit"] == "(m³/h)/√bar"
        assert result["value"] > 0
        # Cv = Q / sqrt(ΔP) = 360 / sqrt(1) = 360
        expected = 360.0 / math.sqrt(1.0)
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_cv_required_with_fluid_gravity(self):
        """Test Cv with different fluid specific gravity."""
        result_water = calculate_cv_required(
            flow_rate=100.0,
            pressure_drop=10.0,
            fluid_gravity=1.0,
            unit_system="US",
        )

        result_oil = calculate_cv_required(
            flow_rate=100.0,
            pressure_drop=10.0,
            fluid_gravity=0.8,  # Oil
            unit_system="US",
        )

        # Higher gravity means lower Cv needed for same flow
        assert result_oil["value"] < result_water["value"]

    def test_cv_required_very_small_warning(self):
        """Test warning for very small Cv values."""
        result = calculate_cv_required(
            flow_rate=0.01,  # Very small flow
            pressure_drop=100.0,  # High pressure drop
            unit_system="US",
        )

        assert len(result["warnings"]) > 0
        assert "small" in result["warnings"][0].lower()

    def test_cv_required_very_large_warning(self):
        """Test warning for very large Cv values."""
        result = calculate_cv_required(
            flow_rate=50000.0,  # Very large flow
            pressure_drop=0.1,  # Low pressure drop
            unit_system="US",
        )

        assert len(result["warnings"]) > 0
        assert "large" in result["warnings"][0].lower()

    def test_cv_required_invalid_pressure_drop(self):
        """Test validation of pressure drop."""
        with pytest.raises(ValueError):
            calculate_cv_required(
                flow_rate=100.0,
                pressure_drop=0.0,
                unit_system="US",
            )


class TestFlowRateCalculations:
    """Test flow rate through valve calculations."""

    def test_flow_rate_basic(self):
        """Test basic flow rate calculation."""
        cv = 50.0
        pressure_drop = 10.0

        result = calculate_flow_rate_through_valve(
            cv=cv,
            pressure_drop=pressure_drop,
            unit_system="US",
        )

        assert result["unit"] == "gpm"
        # Q = Cv * sqrt(ΔP / sg) = 50 * sqrt(10 / 1) ≈ 158.11
        expected = cv * math.sqrt(pressure_drop / 1.0)
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_flow_rate_si_units(self):
        """Test flow rate in SI units."""
        cv = 360.0
        pressure_drop = 1.0

        result = calculate_flow_rate_through_valve(
            cv=cv,
            pressure_drop=pressure_drop,
            unit_system="SI",
        )

        assert result["unit"] == "m³/h"
        # Q = Cv * sqrt(ΔP) = 360 * sqrt(1) = 360
        expected = cv * math.sqrt(pressure_drop)
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_flow_rate_inverse_of_cv_required(self):
        """Test that flow rate calculation is inverse of Cv required."""
        Q = 100.0
        dP = 10.0

        cv_result = calculate_cv_required(Q, dP, unit_system="US")
        cv = cv_result["value"]

        flow_result = calculate_flow_rate_through_valve(cv, dP, unit_system="US")
        Q_calculated = flow_result["value"]

        # Should recover original flow rate
        assert math.isclose(Q_calculated, Q, rel_tol=0.01)

    def test_flow_rate_invalid_cv(self):
        """Test validation of Cv values."""
        with pytest.raises(ValueError):
            calculate_flow_rate_through_valve(
                cv=0.0,
                pressure_drop=10.0,
                unit_system="US",
            )


class TestValveSizing:
    """Test valve sizing and selection."""

    def test_valve_sizing_basic(self):
        """Test basic valve sizing."""
        available_cvs = [10, 25, 50, 100, 150]

        result = calculate_valve_sizing(
            flow_rate=100.0,
            pressure_drop=10.0,
            valve_cv_options=available_cvs,
            unit_system="US",
        )

        assert "recommended_cv" in result
        assert result["recommended_cv"] in available_cvs
        assert result["recommended_percentage"] > 0

    def test_valve_sizing_opening_percentage(self):
        """Test that recommended valve opening is in reasonable range."""
        result = calculate_valve_sizing(
            flow_rate=100.0,
            pressure_drop=10.0,
            valve_cv_options=[25, 50, 100, 150, 200],
            unit_system="US",
        )

        # Recommended valve should ideally be 10-90% open
        if result["recommended_percentage"] >= 10:
            assert result["recommended_percentage"] <= 90

    def test_valve_sizing_no_suitable_warning(self):
        """Test warning when no valve in ideal range found."""
        result = calculate_valve_sizing(
            flow_rate=100.0,
            pressure_drop=10.0,
            valve_cv_options=[5, 10],  # All too small
            unit_system="US",
        )

        # Should find closest match but with warning
        assert len(result["warnings"]) > 0 or result["recommended_percentage"] < 10


class TestValveAuthority:
    """Test valve authority calculations."""

    def test_valve_authority_basic(self):
        """Test basic valve authority calculation."""
        result = calculate_valve_authority(
            valve_pressure_drop=10.0,
            system_pressure_drop=20.0,
        )

        # Authority = 10 / (10 + 20) = 0.333
        expected = 10.0 / 30.0
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_valve_authority_good_range(self):
        """Test valve authority in good operating range."""
        result = calculate_valve_authority(
            valve_pressure_drop=10.0,
            system_pressure_drop=15.0,  # Authority ≈ 0.4
        )

        assert 0.3 <= result["value"] <= 0.5
        assert "good" in result["assessment"].lower()

    def test_valve_authority_low(self):
        """Test low valve authority."""
        result = calculate_valve_authority(
            valve_pressure_drop=2.0,
            system_pressure_drop=50.0,  # Authority ≈ 0.038
        )

        assert result["value"] < 0.2
        assert "low" in result["assessment"].lower()

    def test_valve_authority_high(self):
        """Test high valve authority."""
        result = calculate_valve_authority(
            valve_pressure_drop=50.0,
            system_pressure_drop=10.0,  # Authority ≈ 0.833
        )

        assert result["value"] > 0.7
        assert "high" in result["assessment"].lower()
        assert len(result["warnings"]) > 0


class TestValveRangeability:
    """Test valve rangeability calculations."""

    def test_rangeability_basic(self):
        """Test basic rangeability calculation."""
        result = calculate_valve_rangeability(
            cv_min=1.0,
            cv_max=50.0,
        )

        # Rangeability = 50 / 1 = 50:1
        expected = 50.0 / 1.0
        assert math.isclose(result["value"], expected, rel_tol=0.01)
        assert result["value_ratio"] == "50.0:1"

    def test_rangeability_typical_globe(self):
        """Test rangeability for typical globe valve."""
        result = calculate_valve_rangeability(
            cv_min=2.0,
            cv_max=50.0,  # 25:1 rangeability
        )

        assert 20 <= result["value"] <= 30
        assert "good" in result["assessment"].lower()

    def test_rangeability_limited(self):
        """Test limited rangeability."""
        result = calculate_valve_rangeability(
            cv_min=5.0,
            cv_max=50.0,  # 10:1 rangeability
        )

        assert result["value"] == 10.0
        assert "limited" in result["assessment"].lower()
        assert len(result["warnings"]) > 0

    def test_rangeability_invalid_cv(self):
        """Test validation of Cv values."""
        with pytest.raises(ValueError):
            calculate_valve_rangeability(
                cv_min=100.0,
                cv_max=50.0,  # Min > Max
            )


class TestRelativeFlowCapacity:
    """Test relative flow capacity at different openings."""

    def test_linear_characteristic(self):
        """Test linear flow characteristic."""
        result_25 = calculate_relative_flow_capacity(25, "linear")
        result_50 = calculate_relative_flow_capacity(50, "linear")

        # Should be proportional
        assert math.isclose(result_25["value"], 0.25, rel_tol=0.01)
        assert math.isclose(result_50["value"], 0.50, rel_tol=0.01)

    def test_parabolic_characteristic(self):
        """Test parabolic flow characteristic."""
        result_25 = calculate_relative_flow_capacity(25, "parabolic")
        result_50 = calculate_relative_flow_capacity(50, "parabolic")

        # Should be proportional to opening squared
        assert math.isclose(result_25["value"], 0.0625, rel_tol=0.01)  # 0.25²
        assert math.isclose(result_50["value"], 0.25, rel_tol=0.01)  # 0.5²

    def test_equal_percentage_characteristic(self):
        """Test equal percentage flow characteristic."""
        result_10 = calculate_relative_flow_capacity(10, "equal_percentage")
        result_50 = calculate_relative_flow_capacity(50, "equal_percentage")

        # Flow should increase more gradually at low openings
        assert result_10["value"] < result_50["value"]

    def test_full_opening(self):
        """Test relative flow at full opening."""
        for characteristic in ["linear", "parabolic", "equal_percentage"]:
            result = calculate_relative_flow_capacity(100, characteristic)
            # At 100%, should be at or near maximum
            assert result["value"] > 0.95


class TestValvePerformanceAssessment:
    """Test comprehensive valve performance assessment."""

    def test_performance_good_conditions(self):
        """Test valve performance in good conditions."""
        result = assess_valve_performance(
            cv_at_design=25.0,
            cv_max=50.0,
            pressure_drop_design=10.0,
            system_pressure_drop=15.0,
        )

        assert 25 <= result["opening_percent"] <= 75
        assert "good" in result["opening_assessment"].lower() or "moderate" in result["opening_assessment"].lower()

    def test_performance_severely_throttled(self):
        """Test valve performance when severely throttled."""
        result = assess_valve_performance(
            cv_at_design=2.0,  # Very low opening
            cv_max=50.0,
            pressure_drop_design=20.0,
            system_pressure_drop=10.0,
        )

        assert result["opening_percent"] < 10
        assert "throttled" in result["opening_assessment"].lower()
        assert len(result["warnings"]) > 0

    def test_performance_nearly_wide_open(self):
        """Test valve performance when nearly wide open."""
        result = assess_valve_performance(
            cv_at_design=40.0,  # High opening
            cv_max=50.0,
            pressure_drop_design=5.0,
            system_pressure_drop=20.0,
        )

        assert result["opening_percent"] > 75
        assert "wide open" in result["opening_assessment"].lower()


class TestIntegrationValveSizing:
    """Integration tests for valve sizing."""

    def test_complete_valve_sizing_workflow(self):
        """Test complete valve sizing workflow."""
        # Required flow and pressure drop
        required_flow = 100.0  # gpm
        required_dp = 10.0  # psi

        # Available valves
        available_cvs = [25, 50, 75, 100, 150]

        # Step 1: Calculate required Cv
        cv_required = calculate_cv_required(
            required_flow, required_dp, unit_system="US"
        )
        assert cv_required["value"] > 0

        # Step 2: Select valve
        valve_selection = calculate_valve_sizing(
            required_flow, required_dp, available_cvs, unit_system="US"
        )
        selected_cv = valve_selection["recommended_cv"]
        assert selected_cv in available_cvs

        # Step 3: Verify flow
        actual_flow = calculate_flow_rate_through_valve(
            selected_cv, required_dp, unit_system="US"
        )
        assert actual_flow["value"] >= required_flow

        # Step 4: Assess authority
        authority = calculate_valve_authority(required_dp, 20.0)
        assert authority["value"] > 0

        # Step 5: Assess rangeability
        rangeability = calculate_valve_rangeability(
            cv_min=selected_cv * 0.05,  # Assume 5% minimum
            cv_max=selected_cv,
        )
        assert rangeability["value"] > 0

        # Step 6: Overall performance
        performance = assess_valve_performance(
            cv_at_design=selected_cv,
            cv_max=selected_cv,
            pressure_drop_design=required_dp,
            system_pressure_drop=20.0,
        )
        assert "assessment" in performance["overall_assessment"]
