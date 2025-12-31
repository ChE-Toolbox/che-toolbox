"""
Unit tests for pump sizing calculations.

Tests pump head, power, and NPSH calculations.
"""

import math

import pytest

from fluids.pump import (
    calculate_brake_power,
    calculate_dynamic_head,
    calculate_hydraulic_power,
    calculate_motor_power,
    calculate_npsh_available,
    calculate_npsh_required,
    calculate_static_head,
    calculate_total_head,
    check_cavitation_risk,
)


class TestHeadCalculations:
    """Test pump head calculations."""

    def test_total_head_basic(self):
        """Test basic total head calculation."""
        result = calculate_total_head(
            elevation_change=10.0,
            pressure_drop=5000,
            velocity=2.0,
        )

        assert "value" in result
        assert result["unit"] == "m"
        assert result["value"] > 0
        assert "static_head" in result
        assert "dynamic_head" in result
        assert "pressure_head" in result

    def test_static_head_basic(self):
        """Test static head calculation."""
        result = calculate_static_head(elevation_change=5.0)

        assert result["value"] == 5.0
        assert result["unit"] == "m"

    def test_static_head_zero(self):
        """Test static head with zero elevation."""
        result = calculate_static_head(elevation_change=0.0)

        assert result["value"] == 0.0
        assert len(result["warnings"]) > 0

    def test_dynamic_head_basic(self):
        """Test dynamic head calculation (velocity head)."""
        velocity = 2.0
        result = calculate_dynamic_head(velocity=velocity)

        # H_velocity = V²/(2g) = 4/(2*9.81) ≈ 0.204 m
        expected = (velocity ** 2) / (2 * 9.81)
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_dynamic_head_zero_velocity(self):
        """Test dynamic head at zero velocity."""
        result = calculate_dynamic_head(velocity=0.0)

        assert result["value"] == 0.0
        assert len(result["warnings"]) > 0

    def test_total_head_components(self):
        """Test that total head equals sum of components."""
        elev = 10.0
        dp = 5000
        vel = 2.0
        rho = 1000.0

        result = calculate_total_head(
            elevation_change=elev,
            pressure_drop=dp,
            velocity=vel,
            fluid_density=rho,
        )

        # Check that components add up
        expected_total = result["static_head"] + result["dynamic_head"] + result["pressure_head"]
        assert math.isclose(result["value"], expected_total, rel_tol=0.01)

    def test_total_head_us_units(self):
        """Test total head calculation in US customary units."""
        result = calculate_total_head(
            elevation_change=30.0,  # ft
            pressure_drop=10.0,  # psi
            velocity=5.0,  # ft/s
            unit_system="US",
        )

        assert result["unit"] == "ft"
        assert result["value"] > 0

    def test_total_head_invalid_elevation(self):
        """Test validation of negative elevation."""
        with pytest.raises(ValueError):
            calculate_total_head(
                elevation_change=-5.0,
                pressure_drop=1000,
                velocity=1.0,
            )

    def test_total_head_invalid_velocity(self):
        """Test validation of negative velocity."""
        with pytest.raises(ValueError):
            calculate_total_head(
                elevation_change=5.0,
                pressure_drop=1000,
                velocity=-1.0,
            )


class TestPowerCalculations:
    """Test pump power calculations."""

    def test_hydraulic_power_basic(self):
        """Test basic hydraulic power calculation."""
        result = calculate_hydraulic_power(
            flow_rate=0.01,  # m³/s
            head=20.0,  # m
        )

        assert result["unit"] == "kW"
        assert result["value"] > 0
        # P = ρ * g * Q * H / 1000 = 1000 * 9.81 * 0.01 * 20 / 1000 ≈ 1.962 kW
        expected = 1000 * 9.81 * 0.01 * 20 / 1000
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_hydraulic_power_zero_flow(self):
        """Test hydraulic power at zero flow."""
        result = calculate_hydraulic_power(
            flow_rate=0.0,
            head=20.0,
        )

        assert result["value"] == 0.0
        assert len(result["warnings"]) > 0

    def test_hydraulic_power_zero_head(self):
        """Test hydraulic power at zero head."""
        result = calculate_hydraulic_power(
            flow_rate=0.01,
            head=0.0,
        )

        assert result["value"] == 0.0
        assert len(result["warnings"]) > 0

    def test_brake_power_basic(self):
        """Test brake power calculation."""
        flow_rate = 0.01
        head = 20.0
        efficiency = 0.80

        result = calculate_brake_power(
            flow_rate=flow_rate,
            head=head,
            pump_efficiency=efficiency,
        )

        assert result["unit"] == "kW"
        assert result["value"] > 0
        # Brake power should be greater than hydraulic power
        assert result["value"] > result["hydraulic_power"]
        # Check that power_loss is positive
        assert result["power_loss"] > 0

    def test_brake_power_high_efficiency(self):
        """Test brake power with high efficiency."""
        result = calculate_brake_power(
            flow_rate=0.01,
            head=20.0,
            pump_efficiency=0.95,
        )

        assert result["value"] > 0
        # Power loss should be small relative to hydraulic power
        loss_ratio = result["power_loss"] / result["hydraulic_power"]
        assert loss_ratio < 0.1

    def test_brake_power_low_efficiency_warning(self):
        """Test brake power with low efficiency generates warning."""
        result = calculate_brake_power(
            flow_rate=0.01,
            head=20.0,
            pump_efficiency=0.40,
        )

        assert len(result["warnings"]) > 0

    def test_brake_power_invalid_efficiency(self):
        """Test validation of pump efficiency."""
        with pytest.raises(ValueError):
            calculate_brake_power(
                flow_rate=0.01,
                head=20.0,
                pump_efficiency=1.5,  # > 1.0
            )

    def test_motor_power_basic(self):
        """Test motor power calculation."""
        brake_power = 2.0
        motor_efficiency = 0.95

        result = calculate_motor_power(
            brake_power=brake_power,
            motor_efficiency=motor_efficiency,
        )

        assert result["value"] > 0
        assert result["value"] > brake_power  # Motor power > brake power
        # Expected: 2.0 / 0.95 ≈ 2.105 kW
        expected = brake_power / motor_efficiency
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_motor_power_zero_brake(self):
        """Test motor power at zero brake power."""
        result = calculate_motor_power(
            brake_power=0.0,
            motor_efficiency=0.95,
        )

        assert result["value"] == 0.0
        assert len(result["warnings"]) > 0

    def test_motor_power_low_efficiency_warning(self):
        """Test motor power with low efficiency generates warning."""
        result = calculate_motor_power(
            brake_power=2.0,
            motor_efficiency=0.80,
        )

        assert len(result["warnings"]) > 0


class TestNPSHCalculations:
    """Test NPSH calculations."""

    def test_npsh_available_basic(self):
        """Test basic NPSH available calculation."""
        result = calculate_npsh_available(
            atmospheric_pressure=101325,  # Pa
            vapor_pressure=2340,  # Pa for water at 20°C
            suction_head=2.0,  # m (flooded suction)
        )

        assert result["unit"] == "m"
        assert result["value"] > 0
        assert "pressure_head" in result
        assert "suction_head" in result

    def test_npsh_available_negative_suction_head(self):
        """Test NPSH available with lift (negative suction head)."""
        result = calculate_npsh_available(
            atmospheric_pressure=101325,
            vapor_pressure=2340,
            suction_head=-1.0,  # Lift condition
        )

        assert len(result["warnings"]) > 0
        assert "lift" in result["warnings"][0].lower() or "above" in result["warnings"][0].lower()

    def test_npsh_available_with_suction_losses(self):
        """Test NPSH available accounting for suction line losses."""
        result_no_loss = calculate_npsh_available(
            atmospheric_pressure=101325,
            vapor_pressure=2340,
            suction_head=2.0,
            suction_losses=0.0,
        )

        result_with_loss = calculate_npsh_available(
            atmospheric_pressure=101325,
            vapor_pressure=2340,
            suction_head=2.0,
            suction_losses=1000,  # Some loss in Pa
        )

        assert result_no_loss["value"] > result_with_loss["value"]

    def test_npsh_available_us_units(self):
        """Test NPSH available in US customary units."""
        result = calculate_npsh_available(
            atmospheric_pressure=14.7,  # psi
            vapor_pressure=0.35,  # psi for water at 68°F
            suction_head=5.0,  # ft
            unit_system="US",
        )

        assert result["unit"] == "ft"
        assert result["value"] > 0

    def test_npsh_required_basic(self):
        """Test NPSH required calculation."""
        design_flow = 0.01  # m³/s
        actual_flow = 0.008  # m³/s (80% of design)
        npshr_design = 1.0  # m

        result = calculate_npsh_required(
            pump_design_point_flow=design_flow,
            actual_flow=actual_flow,
            npsh_required_at_design=npshr_design,
        )

        # NPSHR = 1.0 * (0.008/0.01)² = 1.0 * 0.64 = 0.64 m
        expected = npshr_design * (actual_flow / design_flow) ** 2
        assert math.isclose(result["value"], expected, rel_tol=0.01)

    def test_npsh_required_at_design_point(self):
        """Test NPSH required at design flow equals design value."""
        design_flow = 0.01
        npshr_design = 1.0

        result = calculate_npsh_required(
            pump_design_point_flow=design_flow,
            actual_flow=design_flow,  # Operating at design point
            npsh_required_at_design=npshr_design,
        )

        assert math.isclose(result["value"], npshr_design, rel_tol=0.01)

    def test_npsh_required_high_flow_warning(self):
        """Test NPSH required with high flow generates warning."""
        result = calculate_npsh_required(
            pump_design_point_flow=0.01,
            actual_flow=0.013,  # 130% of design
            npsh_required_at_design=1.0,
        )

        assert len(result["warnings"]) > 0

    def test_npsh_required_low_flow_warning(self):
        """Test NPSH required with low flow generates warning."""
        result = calculate_npsh_required(
            pump_design_point_flow=0.01,
            actual_flow=0.004,  # 40% of design
            npsh_required_at_design=1.0,
        )

        assert len(result["warnings"]) > 0


class TestCavitationRisk:
    """Test cavitation risk assessment."""

    def test_cavitation_safe(self):
        """Test safe cavitation margin."""
        result = check_cavitation_risk(
            npsh_available=5.0,
            npsh_required=1.0,
        )

        assert result["cavitation_risk"] == "safe"
        assert result["npsh_margin"] > 0
        assert "adequate" in result["recommendation"].lower()

    def test_cavitation_marginal(self):
        """Test marginal cavitation margin."""
        result = check_cavitation_risk(
            npsh_available=1.15,
            npsh_required=1.0,  # 15% margin
        )

        assert result["cavitation_risk"] == "marginal"
        assert "minimal" in result["recommendation"].lower()

    def test_cavitation_danger(self):
        """Test danger cavitation margin."""
        result = check_cavitation_risk(
            npsh_available=1.05,
            npsh_required=1.0,  # 5% margin
        )

        assert result["cavitation_risk"] == "danger"
        assert "very low" in result["recommendation"].lower()

    def test_cavitation_critical(self):
        """Test critical cavitation condition."""
        result = check_cavitation_risk(
            npsh_available=0.5,
            npsh_required=1.0,  # Negative margin
        )

        assert result["cavitation_risk"] == "critical"
        assert "will occur" in result["recommendation"].lower()


class TestIntegrationPumpSizing:
    """Integration tests for pump sizing."""

    def test_complete_pump_sizing_analysis(self, standard_water, standard_pipe):
        """Test complete pump sizing analysis."""
        # System parameters
        elevation_change = 15.0  # m
        pipe_length = 200.0  # m
        flow_rate = 0.015  # m³/s
        velocity = 2.0  # m/s

        # Calculate pressure drop (use a friction factor)
        pressure_drop = 0.03 * (pipe_length / standard_pipe["diameter"]) * (
            standard_water["density"] * velocity ** 2 / 2
        )

        # Calculate total head required
        head_result = calculate_total_head(
            elevation_change=elevation_change,
            pressure_drop=pressure_drop,
            velocity=velocity,
            fluid_density=standard_water["density"],
        )

        assert head_result["value"] > 0

        # Calculate hydraulic power
        hydraulic_power = calculate_hydraulic_power(
            flow_rate=flow_rate,
            head=head_result["value"],
            fluid_density=standard_water["density"],
        )

        assert hydraulic_power["value"] > 0

        # Calculate brake power with typical pump efficiency
        brake_power = calculate_brake_power(
            flow_rate=flow_rate,
            head=head_result["value"],
            pump_efficiency=0.80,
            fluid_density=standard_water["density"],
        )

        assert brake_power["value"] > hydraulic_power["value"]

        # Calculate NPSH available
        npsh_available = calculate_npsh_available(
            atmospheric_pressure=101325,
            vapor_pressure=2340,  # Water at 20°C
            suction_head=2.0,
            suction_losses=500,
        )

        assert npsh_available["value"] > 0

        # Check NPSH required and cavitation risk
        npsh_required = calculate_npsh_required(
            pump_design_point_flow=flow_rate,
            actual_flow=flow_rate,
            npsh_required_at_design=1.2,
        )

        cavitation = check_cavitation_risk(
            npsh_available=npsh_available["value"],
            npsh_required=npsh_required["value"],
        )

        assert cavitation["cavitation_risk"] in ["safe", "marginal", "danger", "critical"]
