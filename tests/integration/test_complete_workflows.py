"""
End-to-end integration tests for complete engineering workflows.

These tests verify that all three user stories work together seamlessly.
"""

import pytest
import math
from fluids.pipe import calculate_reynolds, calculate_friction_factor, calculate_pressure_drop
from fluids.pump import (
    calculate_total_head,
    calculate_hydraulic_power,
    calculate_brake_power,
    calculate_motor_power,
    calculate_npsh_available,
    calculate_npsh_required,
    check_cavitation_risk,
)
from fluids.valve import (
    calculate_cv_required,
    calculate_valve_sizing,
    calculate_valve_authority,
    assess_valve_performance,
)


class TestCompleteSystemDesign:
    """Test complete system design workflow: Pipe → Pump → Valve."""

    def test_industrial_water_pump_system(self, standard_water, standard_pipe):
        """
        Design a water circulation system for an industrial process.

        System Requirements:
        - Flow: 50 m³/h (0.01389 m³/s)
        - Elevation: 20 m
        - Pipe length: 150 m
        - System includes pump, piping, and control valve
        """
        # System parameters
        elevation = 20.0  # m
        pipe_length = 150.0  # m
        flow_rate_m3s = 0.01389  # m³/s (50 m³/h)

        # Fluid properties (standard water at 20°C)
        density = standard_water["density"]
        viscosity = standard_water["dynamic_viscosity"]

        # Pipe properties
        diameter = standard_pipe["diameter"]  # 0.05 m (2 inches)
        roughness = standard_pipe["absolute_roughness"]

        # ============ STEP 1: Pipe Flow Analysis ============
        # Calculate velocity
        area = math.pi * (diameter / 2) ** 2
        velocity = flow_rate_m3s / area

        # Calculate Reynolds number
        re_result = calculate_reynolds(density, velocity, diameter, viscosity)
        assert re_result["flow_regime"] == "turbulent"

        # Calculate friction factor
        ff_result = calculate_friction_factor(
            reynolds=re_result["value"],
            roughness=roughness,
            diameter=diameter,
            method="churchill",
        )
        assert 0.01 < ff_result["value"] < 0.1

        # Calculate pressure drop in piping
        dp_result = calculate_pressure_drop(
            friction_factor=ff_result["value"],
            length=pipe_length,
            diameter=diameter,
            velocity=velocity,
            density=density,
        )
        friction_loss = dp_result["value"]

        # ============ STEP 2: Pump Sizing ============
        # Calculate total head required
        head_result = calculate_total_head(
            elevation_change=elevation,
            pressure_drop=friction_loss,
            velocity=velocity,
            fluid_density=density,
        )
        total_head = head_result["value"]
        assert total_head > elevation  # Must be more than elevation alone

        # Calculate hydraulic power
        hydraulic = calculate_hydraulic_power(
            flow_rate=flow_rate_m3s,
            head=total_head,
            fluid_density=density,
        )

        # Select pump with typical efficiency
        pump_efficiency = 0.82
        brake = calculate_brake_power(
            flow_rate=flow_rate_m3s,
            head=total_head,
            pump_efficiency=pump_efficiency,
            fluid_density=density,
        )

        # Calculate motor size needed
        motor_efficiency = 0.93
        motor = calculate_motor_power(brake["value"], motor_efficiency)

        # Check NPSH conditions (flooded suction, water at 20°C)
        npsh_available = calculate_npsh_available(
            atmospheric_pressure=101325,  # Pa
            vapor_pressure=2340,  # Pa for water at 20°C
            suction_head=1.5,  # m (flooded suction)
            suction_losses=300,  # Pa
        )

        npsh_required = calculate_npsh_required(
            pump_design_point_flow=flow_rate_m3s,
            actual_flow=flow_rate_m3s,
            npsh_required_at_design=0.8,  # m
        )

        cavitation = check_cavitation_risk(
            npsh_available=npsh_available["value"],
            npsh_required=npsh_required["value"],
        )

        # ============ STEP 3: Valve Sizing ============
        # Pressure drop available for control valve (50% of system)
        valve_pressure_drop = friction_loss / 2  # Pa
        system_pressure_drop = friction_loss / 2  # Rest of system

        # Calculate required Cv for control valve
        # Convert to US units for valve sizing (more common)
        flow_rate_gpm = flow_rate_m3s * 951.92  # Convert m³/s to gpm
        pressure_drop_psi = valve_pressure_drop / 6894.76  # Convert Pa to psi

        cv_required = calculate_cv_required(
            flow_rate=flow_rate_gpm,
            pressure_drop=pressure_drop_psi,
            unit_system="US",
        )

        # Select valve from standard sizes
        standard_sizes = [10, 25, 35, 50, 75, 100]
        valve_selection = calculate_valve_sizing(
            flow_rate=flow_rate_gpm,
            pressure_drop=pressure_drop_psi,
            valve_cv_options=standard_sizes,
            unit_system="US",
        )

        # Assess valve authority
        authority = calculate_valve_authority(
            valve_pressure_drop=valve_pressure_drop,
            system_pressure_drop=system_pressure_drop,
        )

        performance = assess_valve_performance(
            cv_at_design=valve_selection["recommended_cv"],
            cv_max=valve_selection["recommended_cv"],
            pressure_drop_design=valve_pressure_drop,
            system_pressure_drop=system_pressure_drop,
        )

        # ============ VERIFICATION ============
        # Verify all calculations are consistent
        assert re_result["value"] > 4000  # Turbulent
        assert 0 < ff_result["value"] < 0.1
        assert friction_loss > 0
        assert total_head > 0
        assert hydraulic["value"] > 0
        assert brake["value"] > hydraulic["value"]  # Accounting for efficiency
        assert motor["value"] > brake["value"]
        assert npsh_available["value"] > npsh_required["value"]
        assert cavitation["cavitation_risk"] in ["safe", "marginal"]
        assert cv_required["value"] > 0
        assert valve_selection["recommended_cv"] in standard_sizes
        assert 10 < valve_selection["recommended_percentage"] < 90
        assert 0.2 <= authority["value"] <= 0.6  # Good valve authority

        # ============ SYSTEM SUMMARY ============
        print(f"\n=== COMPLETE SYSTEM DESIGN SUMMARY ===")
        print(f"Flow Rate: {flow_rate_m3s:.4f} m³/s ({flow_rate_gpm:.1f} gpm)")
        print(f"Elevation: {elevation:.1f} m")
        print(f"Pipe Length: {pipe_length:.1f} m")
        print(f"\nPipe Flow Analysis:")
        print(f"  Reynolds: {re_result['value']:.0f} ({re_result['flow_regime']})")
        print(f"  Friction Factor: {ff_result['value']:.4f}")
        print(f"  Pressure Drop: {friction_loss/6894.76:.2f} psi")
        print(f"\nPump Requirements:")
        print(f"  Total Head: {total_head:.2f} m")
        print(f"  Hydraulic Power: {hydraulic['value']:.2f} kW")
        print(f"  Brake Power (82% eff): {brake['value']:.2f} kW")
        print(f"  Motor Power (93% eff): {motor['value']:.2f} kW")
        print(f"  NPSH Available: {npsh_available['value']:.2f} m")
        print(f"  NPSH Required: {npsh_required['value']:.2f} m")
        print(f"  Cavitation Risk: {cavitation['cavitation_risk']}")
        print(f"\nValve Sizing:")
        print(f"  Cv Required: {cv_required['value']:.2f}")
        print(f"  Selected Valve: {valve_selection['recommended_cv']}")
        print(f"  Opening: {valve_selection['recommended_percentage']:.1f}%")
        print(f"  Authority: {authority['value_percentage']}")
        print(f"  Authority Assessment: {authority['assessment']}")


class TestMultipleUnitsConsistency:
    """Test that SI and US customary units produce consistent results."""

    def test_si_vs_us_calculations(self, standard_water):
        """Verify SI and US results are equivalent."""

        # SI calculation
        re_si = calculate_reynolds(
            density=1000,  # kg/m³
            velocity=2.0,  # m/s
            diameter=0.05,  # m
            viscosity=0.001,  # Pa·s
        )

        # US equivalent (with proper conversions)
        # 1000 kg/m³ = 62.4 lb/ft³
        # 2.0 m/s = 6.56 ft/s
        # 0.05 m = 0.164 ft
        # 0.001 Pa·s = 0.0671 lbf·s/ft²

        re_us_input = (62.4 * 6.56 * 0.164) / 0.0671
        re_us = re_us_input  # Reynolds is dimensionless

        # Results should match (within conversion error)
        assert math.isclose(re_si["value"], re_us, rel_tol=0.05)


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error conditions."""

    def test_zero_flow_rate(self):
        """Test system with zero flow (pump off)."""
        power = calculate_hydraulic_power(
            flow_rate=0.0,
            head=20.0,
        )
        assert power["value"] == 0.0
        assert len(power["warnings"]) > 0

    def test_very_small_flow(self, standard_water):
        """Test system with very small flow (control valve near closed)."""
        re = calculate_reynolds(
            density=standard_water["density"],
            velocity=0.01,  # Very low velocity
            diameter=0.05,
            viscosity=standard_water["dynamic_viscosity"],
        )
        assert re["flow_regime"] == "laminar"

    def test_very_high_flow(self, standard_water):
        """Test system with very high flow (near maximum)."""
        re = calculate_reynolds(
            density=standard_water["density"],
            velocity=10.0,  # Very high velocity
            diameter=0.05,
            viscosity=standard_water["dynamic_viscosity"],
        )
        assert re["flow_regime"] == "turbulent"
        assert re["value"] > 100000

    def test_cavitation_risk_evaluation(self):
        """Test cavitation risk at different margins."""
        # Safe condition
        safe = check_cavitation_risk(5.0, 1.0)
        assert safe["cavitation_risk"] == "safe"

        # Danger condition
        danger = check_cavitation_risk(1.05, 1.0)
        assert danger["cavitation_risk"] == "danger"

        # Critical condition
        critical = check_cavitation_risk(0.5, 1.0)
        assert critical["cavitation_risk"] == "critical"
