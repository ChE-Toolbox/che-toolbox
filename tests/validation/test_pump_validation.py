"""
Validation tests for pump sizing calculations.

These tests validate pump calculations against engineering standards and
typical pump curves from manufacturer datasheets.
"""

import pytest
import math
from fluids.pump import (
    calculate_total_head,
    calculate_hydraulic_power,
    calculate_brake_power,
    calculate_motor_power,
    calculate_npsh_available,
    calculate_npsh_required,
    check_cavitation_risk,
)


class TestPumpHeadValidation:
    """Validate pump head calculations against engineering standards."""

    def test_head_calculation_units_consistency(self):
        """Test that SI and US unit results are consistent."""
        # SI calculation: 10 m elevation + 5000 Pa pressure drop + 2 m/s velocity
        si_result = calculate_total_head(
            elevation_change=10.0,  # m
            pressure_drop=5000,  # Pa
            velocity=2.0,  # m/s
            fluid_density=1000,  # kg/m³
        )

        # US customary equivalent
        # 10 m = 32.81 ft
        # 5000 Pa = 0.725 psi
        # 2 m/s = 6.56 ft/s
        us_result = calculate_total_head(
            elevation_change=32.81,  # ft
            pressure_drop=0.725,  # psi
            velocity=6.56,  # ft/s
            fluid_density=62.4,  # lb/ft³
            unit_system="US",
        )

        # Convert SI head to feet for comparison (1 m = 3.28084 ft)
        si_head_in_ft = si_result["value"] * 3.28084

        # Should be reasonably close (allowing for conversion rounding)
        assert math.isclose(si_head_in_ft, us_result["value"], rel_tol=0.05)

    def test_head_component_summation(self):
        """Test that total head equals sum of components."""
        elevation = 15.0
        pressure_drop = 10000
        velocity = 1.5

        result = calculate_total_head(
            elevation_change=elevation,
            pressure_drop=pressure_drop,
            velocity=velocity,
            fluid_density=1000,
        )

        # Verify component addition
        expected_total = result["static_head"] + result["dynamic_head"] + result["pressure_head"]
        assert math.isclose(result["value"], expected_total, rel_tol=0.01)

    def test_head_without_elevation(self):
        """Test head calculation with only pressure drop and velocity."""
        result = calculate_total_head(
            elevation_change=0.0,  # No elevation change
            pressure_drop=5000,  # Pa
            velocity=2.0,  # m/s
        )

        # Static head should be zero
        assert result["static_head"] == 0.0
        # Total should equal dynamic + pressure head
        assert math.isclose(
            result["value"],
            result["dynamic_head"] + result["pressure_head"],
            rel_tol=0.01,
        )

    def test_head_dynamic_component_formula(self):
        """Test dynamic head follows v²/(2g) formula."""
        velocity = 3.0  # m/s
        g = 9.81

        result = calculate_total_head(
            elevation_change=0.0,
            pressure_drop=0.0,
            velocity=velocity,
        )

        expected_dynamic_head = (velocity ** 2) / (2 * g)
        assert math.isclose(result["dynamic_head"], expected_dynamic_head, rel_tol=0.01)


class TestPumpPowerValidation:
    """Validate pump power calculations."""

    def test_hydraulic_power_formula(self):
        """Test hydraulic power follows P = ρgQH/1000 (kW)."""
        flow_rate = 0.02  # m³/s (72 m³/h)
        head = 30.0  # m
        density = 1000  # kg/m³
        g = 9.81

        result = calculate_hydraulic_power(
            flow_rate=flow_rate,
            head=head,
            fluid_density=density,
            g=g,
        )

        # Expected: (1000 * 9.81 * 0.02 * 30) / 1000 = 5.886 kW
        expected = (density * g * flow_rate * head) / 1000
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_brake_power_higher_than_hydraulic(self):
        """Test that brake power always exceeds hydraulic power."""
        flow_rate = 0.01
        head = 25.0

        hydraulic = calculate_hydraulic_power(flow_rate, head)

        brake = calculate_brake_power(
            flow_rate=flow_rate,
            head=head,
            pump_efficiency=0.85,
        )

        # Brake power should be higher due to efficiency losses
        assert brake["value"] > hydraulic["value"]

    def test_brake_power_efficiency_effect(self):
        """Test brake power scales correctly with efficiency."""
        flow_rate = 0.01
        head = 25.0
        hydraulic_power = calculate_hydraulic_power(flow_rate, head)["value"]

        # Test with different efficiencies
        brake_75 = calculate_brake_power(
            flow_rate=flow_rate,
            head=head,
            pump_efficiency=0.75,
        )

        brake_85 = calculate_brake_power(
            flow_rate=flow_rate,
            head=head,
            pump_efficiency=0.85,
        )

        # Higher efficiency means lower brake power needed
        assert brake_75["value"] > brake_85["value"]

        # Verify formula: P_brake = P_hydraulic / efficiency
        assert math.isclose(brake_75["value"], hydraulic_power / 0.75, rel_tol=0.01)
        assert math.isclose(brake_85["value"], hydraulic_power / 0.85, rel_tol=0.01)

    def test_motor_power_typical_efficiency(self):
        """Test motor power with typical motor efficiency of 95%."""
        brake_power = 5.0  # kW

        result = calculate_motor_power(brake_power, motor_efficiency=0.95)

        # Expected: 5.0 / 0.95 ≈ 5.263 kW
        expected = brake_power / 0.95
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_complete_power_chain(self):
        """Test complete chain: hydraulic → brake → motor power."""
        flow_rate = 0.02
        head = 35.0
        pump_efficiency = 0.82
        motor_efficiency = 0.93

        # Hydraulic power (ideal)
        hydraulic = calculate_hydraulic_power(flow_rate, head)

        # Brake power (accounting for pump losses)
        brake = calculate_brake_power(
            flow_rate=flow_rate,
            head=head,
            pump_efficiency=pump_efficiency,
        )

        # Motor power (accounting for motor losses)
        motor = calculate_motor_power(brake["value"], motor_efficiency)

        # Verify relationships
        assert brake["value"] > hydraulic["value"]
        assert motor["value"] > brake["value"]

        # Verify overall efficiency
        overall_efficiency = hydraulic["value"] / motor["value"]
        expected_overall = pump_efficiency * motor_efficiency
        assert math.isclose(overall_efficiency, expected_overall, rel_tol=0.05)


class TestNPSHValidation:
    """Validate NPSH calculations."""

    def test_npsh_available_at_sea_level(self):
        """Test NPSH available with standard sea level conditions."""
        # Standard sea level: P_atm = 101,325 Pa, P_vapor_water_20C = 2,340 Pa
        atmospheric = 101325
        vapor_pressure = 2340
        suction_head = 1.0  # m (flooded suction)

        result = calculate_npsh_available(
            atmospheric_pressure=atmospheric,
            vapor_pressure=vapor_pressure,
            suction_head=suction_head,
            fluid_density=1000,
        )

        # NPSHA = (P_atm - P_vapor)/(ρg) + h_suction
        # = (101325 - 2340) / (1000 * 9.81) + 1.0
        # ≈ 10.1 + 1.0 = 11.1 m
        assert result["value"] > 10.0
        assert result["unit"] == "m"

    def test_npsh_available_with_lift(self):
        """Test NPSH available with pump above fluid (lift condition)."""
        result = calculate_npsh_available(
            atmospheric_pressure=101325,
            vapor_pressure=2340,
            suction_head=-2.0,  # Negative: pump is 2m above source
            fluid_density=1000,
        )

        # Should warn about lift
        assert len(result["warnings"]) > 0
        # NPSHA should be reduced due to negative head
        assert result["value"] < 10.0

    def test_npsh_required_flow_effect(self):
        """Test NPSH required increases with flow (square relationship)."""
        design_flow = 0.01
        npshr_design = 1.0

        # At design flow
        at_design = calculate_npsh_required(
            pump_design_point_flow=design_flow,
            actual_flow=design_flow,
            npsh_required_at_design=npshr_design,
        )

        # At 50% flow (0.5 ratio)
        at_50_percent = calculate_npsh_required(
            pump_design_point_flow=design_flow,
            actual_flow=design_flow * 0.5,
            npsh_required_at_design=npshr_design,
        )

        # At 150% flow (1.5 ratio)
        at_150_percent = calculate_npsh_required(
            pump_design_point_flow=design_flow,
            actual_flow=design_flow * 1.5,
            npsh_required_at_design=npshr_design,
        )

        # Verify square relationship
        # At 50%: ratio = 0.5, NPSHR_required = 1.0 * (0.5)² = 0.25
        assert math.isclose(at_50_percent["value"], 0.25, rel_tol=0.01)

        # At 150%: ratio = 1.5, NPSHR_required = 1.0 * (1.5)² = 2.25
        assert math.isclose(at_150_percent["value"], 2.25, rel_tol=0.01)

    def test_npsh_required_at_design_equals_input(self):
        """Test that NPSH required at design flow equals input value."""
        design_flow = 0.015
        npshr_design = 1.5

        result = calculate_npsh_required(
            pump_design_point_flow=design_flow,
            actual_flow=design_flow,
            npsh_required_at_design=npshr_design,
        )

        assert math.isclose(result["value"], npshr_design, rel_tol=0.01)


class TestCavitationRiskValidation:
    """Validate cavitation risk assessment."""

    def test_cavitation_risk_safe_margin(self):
        """Test safe cavitation margin (>20%)."""
        result = check_cavitation_risk(
            npsh_available=3.0,
            npsh_required=1.5,
        )

        assert result["cavitation_risk"] == "safe"
        # Margin = 3.0 - 1.5 = 1.5 m
        # Margin % = 1.5 / 1.5 = 100% ✓
        assert result["npsh_margin"] > 0
        assert "adequate" in result["recommendation"].lower()

    def test_cavitation_risk_marginal_margin(self):
        """Test marginal cavitation margin (10-20%)."""
        result = check_cavitation_risk(
            npsh_available=1.15,
            npsh_required=1.0,
        )

        assert result["cavitation_risk"] == "marginal"
        # Margin = 1.15 - 1.0 = 0.15 m
        # Margin % = 0.15 / 1.0 = 15% ✓
        assert "minimal" in result["recommendation"].lower()

    def test_cavitation_risk_danger_margin(self):
        """Test danger cavitation margin (<10%)."""
        result = check_cavitation_risk(
            npsh_available=1.05,
            npsh_required=1.0,
        )

        assert result["cavitation_risk"] == "danger"
        # Margin = 0.05 m = 5%
        assert "very low" in result["recommendation"].lower()

    def test_cavitation_risk_critical(self):
        """Test critical cavitation condition."""
        result = check_cavitation_risk(
            npsh_available=0.8,
            npsh_required=1.0,
        )

        assert result["cavitation_risk"] == "critical"
        assert result["npsh_margin"] < 0
        assert "will occur" in result["recommendation"].lower()


class TestIntegrationPumpSizing:
    """Integration tests for complete pump sizing workflow."""

    def test_system_design_workflow(self):
        """Test complete pump sizing for a system design."""
        # System specs
        elevation_gain = 20.0  # m
        pipe_friction_loss = 8000  # Pa
        flow_rate = 0.025  # m³/s
        velocity = 3.0  # m/s
        density = 1000  # kg/m³

        # Step 1: Calculate total head required
        head_result = calculate_total_head(
            elevation_change=elevation_gain,
            pressure_drop=pipe_friction_loss,
            velocity=velocity,
            fluid_density=density,
        )

        assert head_result["value"] > elevation_gain

        # Step 2: Calculate hydraulic power needed
        hydraulic = calculate_hydraulic_power(
            flow_rate=flow_rate,
            head=head_result["value"],
            fluid_density=density,
        )

        assert hydraulic["value"] > 0

        # Step 3: Select pump with typical efficiency
        pump_efficiency = 0.82  # Typical centrifugal pump

        brake = calculate_brake_power(
            flow_rate=flow_rate,
            head=head_result["value"],
            pump_efficiency=pump_efficiency,
            fluid_density=density,
        )

        assert brake["value"] > hydraulic["value"]

        # Step 4: Calculate motor size (includes motor efficiency)
        motor_efficiency = 0.92  # Typical electric motor

        motor = calculate_motor_power(
            brake_power=brake["value"],
            motor_efficiency=motor_efficiency,
        )

        assert motor["value"] > brake["value"]

        # Step 5: Check NPSH conditions (water at 20°C)
        npsh_available = calculate_npsh_available(
            atmospheric_pressure=101325,
            vapor_pressure=2340,
            suction_head=1.5,  # Flooded suction
            suction_losses=500,
        )

        # Typical pump NPSH required is 10-30% of design head
        npsh_required = calculate_npsh_required(
            pump_design_point_flow=flow_rate,
            actual_flow=flow_rate,
            npsh_required_at_design=0.8,
        )

        cavitation = check_cavitation_risk(
            npsh_available=npsh_available["value"],
            npsh_required=npsh_required["value"],
        )

        assert cavitation["cavitation_risk"] in ["safe", "marginal"]

    def test_high_altitude_design(self):
        """Test pump sizing at high altitude with lower atmospheric pressure."""
        # High altitude: atmospheric pressure reduced
        altitude_pressure = 70000  # Pa at ~3000m elevation
        vapor_pressure = 2340  # Assuming same fluid

        result = calculate_npsh_available(
            atmospheric_pressure=altitude_pressure,
            vapor_pressure=vapor_pressure,
            suction_head=1.0,
            fluid_density=1000,
        )

        # Should have lower NPSHA due to lower atmospheric pressure
        sea_level = calculate_npsh_available(
            atmospheric_pressure=101325,
            vapor_pressure=vapor_pressure,
            suction_head=1.0,
            fluid_density=1000,
        )

        assert result["value"] < sea_level["value"]
