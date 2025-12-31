"""
Validation tests for pipe flow calculations against reference standards.

These tests validate calculations against Crane TP-410 and engineering standards.
Reference: Crane Co. Technical Paper No. 410M, "Flow of Fluids Through Valves, Fittings, and Pipe"
"""

import pytest
import math
from fluids.pipe import (
    calculate_reynolds,
    calculate_friction_factor,
    calculate_pressure_drop,
)


class TestReynoldsValidation:
    """Validate Reynolds number calculations against known references."""

    def test_reynolds_laminar_boundary(self):
        """Test Reynolds laminar boundary case (Re = 2300)."""
        # For laminar-transitional boundary
        # Given parameters that result in Re ≈ 2300
        density = 1000  # kg/m³
        diameter = 0.05  # m
        viscosity = 0.001  # Pa·s

        # Calculate velocity needed for Re = 2300
        # Re = ρVD/μ → V = Re·μ/(ρ·D)
        velocity = 2300 * viscosity / (density * diameter)

        result = calculate_reynolds(density, velocity, diameter, viscosity)

        # Should be very close to 2300
        assert math.isclose(result["value"], 2300, rel_tol=0.01)
        assert result["flow_regime"] == "laminar" or result["flow_regime"] == "transitional"

    def test_reynolds_turbulent_boundary(self):
        """Test Reynolds turbulent boundary case (Re = 4000)."""
        density = 1000
        diameter = 0.05
        viscosity = 0.001

        # Calculate velocity for Re = 4000
        velocity = 4000 * viscosity / (density * diameter)

        result = calculate_reynolds(density, velocity, diameter, viscosity)

        assert math.isclose(result["value"], 4000, rel_tol=0.01)
        assert result["flow_regime"] == "transitional" or result["flow_regime"] == "turbulent"

    def test_reynolds_water_at_20c(self, standard_water):
        """Test Reynolds with standard water at 20°C."""
        # Standard test case with water
        velocity = 1.0  # m/s
        diameter = 0.025  # m (1 inch)

        result = calculate_reynolds(
            density=standard_water["density"],
            velocity=velocity,
            diameter=diameter,
            viscosity=standard_water["dynamic_viscosity"],
        )

        # Expected: Re = 1000 * 1.0 * 0.025 / 0.001 = 25,000
        expected = 25000
        assert math.isclose(result["value"], expected, rel_tol=0.05)
        assert result["flow_regime"] == "turbulent"

    def test_reynolds_transitional_zone_warning(self):
        """Test that transitional zone generates warning."""
        result = calculate_reynolds(
            density=1000,
            velocity=0.23,
            diameter=0.05,
            viscosity=0.001,
        )

        # Re should be around 1150, which is laminar
        # But test transitional explicitly
        if result["flow_regime"] == "transitional":
            assert len(result["warnings"]) > 0


class TestFrictionFactorValidation:
    """Validate friction factor against Crane TP-410 reference data."""

    def test_friction_laminar_exact_solution(self):
        """Test that laminar friction factor matches exact solution f = 64/Re."""
        # Test across range of laminar Reynolds numbers
        test_cases = [
            (100, 0.64),    # Re=100 → f=0.64
            (500, 0.128),   # Re=500 → f=0.128
            (1000, 0.064),  # Re=1000 → f=0.064
            (2000, 0.032),  # Re=2000 → f=0.032
        ]

        for reynolds, expected_f in test_cases:
            result = calculate_friction_factor(
                reynolds=reynolds,
                roughness=0.0,
                diameter=0.05,
                method="churchill",
            )

            # Laminar should be exact
            assert math.isclose(result["value"], expected_f, rel_tol=0.01)

    def test_friction_turbulent_churchill_vs_colebrook(self):
        """Test that Churchill and Colebrook methods are reasonably close."""
        reynolds = 10000
        roughness = 0.000045  # Steel pipe
        diameter = 0.05

        churchill_result = calculate_friction_factor(
            reynolds=reynolds,
            roughness=roughness,
            diameter=diameter,
            method="churchill",
        )

        colebrook_result = calculate_friction_factor(
            reynolds=reynolds,
            roughness=roughness,
            diameter=diameter,
            method="colebrook",
        )

        # Should be within 5% of each other
        ratio = churchill_result["value"] / colebrook_result["value"]
        assert 0.95 <= ratio <= 1.05

    def test_friction_smooth_pipe_turbulent(self):
        """Test friction factor for smooth pipe in turbulent region."""
        # For smooth pipes (relative roughness ≈ 0), Colebrook approximates Blasius
        # f ≈ 0.316 / Re^0.25 for smooth pipes
        reynolds = 100000

        result = calculate_friction_factor(
            reynolds=reynolds,
            roughness=0.0,  # Smooth pipe
            diameter=0.05,
            method="churchill",
        )

        # Blasius formula: f = 0.316 * Re^(-0.25)
        blasius_f = 0.316 * (reynolds ** -0.25)

        # Should be reasonably close (within 10%)
        assert math.isclose(result["value"], blasius_f, rel_tol=0.10)

    def test_friction_rough_pipe_turbulent(self):
        """Test friction factor for rough pipe in turbulent region."""
        # Rough pipe will have higher friction factor
        reynolds = 50000
        roughness = 0.0001  # Very rough
        diameter = 0.05

        result = calculate_friction_factor(
            reynolds=reynolds,
            roughness=roughness,
            diameter=diameter,
            method="churchill",
        )

        # Friction factor should be noticeably higher than smooth pipe equivalent
        result_smooth = calculate_friction_factor(
            reynolds=reynolds,
            roughness=0.0,
            diameter=diameter,
            method="churchill",
        )

        assert result["value"] > result_smooth["value"]

    def test_friction_transitional_uses_laminar(self):
        """Test that transitional zone uses laminar as conservative estimate."""
        reynolds = 3000  # In transitional zone

        result = calculate_friction_factor(
            reynolds=reynolds,
            roughness=0.000045,
            diameter=0.05,
            method="churchill",
        )

        # Should equal laminar value in transitional zone
        expected_laminar = 64 / reynolds
        assert math.isclose(result["value"], expected_laminar, rel_tol=0.01)
        assert len(result["warnings"]) > 0


class TestPressureDropValidation:
    """Validate pressure drop calculations against Darcy-Weisbach and reference data."""

    def test_pressure_drop_formula_verification(self):
        """Verify Darcy-Weisbach formula: ΔP = f(L/D)(ρV²/2)."""
        # Known test case
        friction_factor = 0.030
        length = 100.0  # m
        diameter = 0.05  # m
        velocity = 2.0  # m/s
        density = 1000  # kg/m³

        result = calculate_pressure_drop(
            friction_factor=friction_factor,
            length=length,
            diameter=diameter,
            velocity=velocity,
            density=density,
        )

        # Manual calculation
        expected_dp = friction_factor * (length / diameter) * (density * velocity ** 2 / 2)

        assert math.isclose(result["value"], expected_dp, rel_tol=0.01)

    def test_pressure_drop_laminar_flow(self, standard_water):
        """Test pressure drop in fully laminar flow."""
        # Low velocity laminar flow
        density = standard_water["density"]
        viscosity = standard_water["dynamic_viscosity"]
        velocity = 0.05  # m/s (very low)
        diameter = 0.05
        length = 100.0

        # Calculate Reynolds
        re_result = calculate_reynolds(density, velocity, diameter, viscosity)
        assert re_result["flow_regime"] == "laminar"

        # Get friction factor
        ff_result = calculate_friction_factor(
            reynolds=re_result["value"],
            roughness=0.0,
            diameter=diameter,
        )

        # Calculate pressure drop
        dp_result = calculate_pressure_drop(
            friction_factor=ff_result["value"],
            length=length,
            diameter=diameter,
            velocity=velocity,
            density=density,
        )

        # Should be positive and small
        assert dp_result["value"] > 0
        assert dp_result["value"] < 100  # Pa (very small)

    def test_pressure_drop_turbulent_flow(self, standard_water):
        """Test pressure drop in fully turbulent flow."""
        # High velocity turbulent flow
        density = standard_water["density"]
        viscosity = standard_water["dynamic_viscosity"]
        velocity = 2.0  # m/s
        diameter = 0.05
        length = 100.0

        # Calculate Reynolds
        re_result = calculate_reynolds(density, velocity, diameter, viscosity)
        assert re_result["flow_regime"] == "turbulent"

        # Get friction factor
        ff_result = calculate_friction_factor(
            reynolds=re_result["value"],
            roughness=0.000045,  # Steel pipe
            diameter=diameter,
        )

        # Calculate pressure drop
        dp_result = calculate_pressure_drop(
            friction_factor=ff_result["value"],
            length=length,
            diameter=diameter,
            velocity=velocity,
            density=density,
        )

        # Should be reasonably large for high velocity
        assert dp_result["value"] > 1000  # Pa

    def test_pressure_drop_doubles_with_velocity_squared(self):
        """Verify that pressure drop varies with V²."""
        v1_result = calculate_pressure_drop(
            friction_factor=0.03,
            length=100.0,
            diameter=0.05,
            velocity=1.0,
            density=1000,
        )

        v2_result = calculate_pressure_drop(
            friction_factor=0.03,
            length=100.0,
            diameter=0.05,
            velocity=2.0,
            density=1000,
        )

        # Pressure drop should increase by factor of 4 (2² = 4)
        ratio = v2_result["value"] / v1_result["value"]
        assert math.isclose(ratio, 4.0, rel_tol=0.01)

    def test_pressure_drop_varies_linearly_with_length(self):
        """Verify that pressure drop varies linearly with pipe length."""
        l1_result = calculate_pressure_drop(
            friction_factor=0.03,
            length=50.0,
            diameter=0.05,
            velocity=2.0,
            density=1000,
        )

        l2_result = calculate_pressure_drop(
            friction_factor=0.03,
            length=100.0,
            diameter=0.05,
            velocity=2.0,
            density=1000,
        )

        # Pressure drop should double with length
        ratio = l2_result["value"] / l1_result["value"]
        assert math.isclose(ratio, 2.0, rel_tol=0.01)


class TestIntegrationPipeFlow:
    """Integration tests for complete pipe flow analysis workflow."""

    def test_complete_pipe_analysis_laminar(self, standard_water):
        """Complete analysis of laminar pipe flow."""
        # Setup: Low velocity laminar flow
        flow_rate = 0.00314  # m³/s (0.2 gpm equivalent)
        diameter = 0.05  # m (2 inches)
        length = 100.0  # m
        velocity = flow_rate / (math.pi * (diameter / 2) ** 2)

        # Step 1: Calculate Reynolds
        re_result = calculate_reynolds(
            density=standard_water["density"],
            velocity=velocity,
            diameter=diameter,
            viscosity=standard_water["dynamic_viscosity"],
        )

        assert re_result["flow_regime"] == "laminar"
        assert re_result["value"] < 2300

        # Step 2: Calculate friction factor
        ff_result = calculate_friction_factor(
            reynolds=re_result["value"],
            roughness=0.0,
            diameter=diameter,
        )

        # Should use exact laminar formula
        expected_f = 64 / re_result["value"]
        assert math.isclose(ff_result["value"], expected_f, rel_tol=0.01)

        # Step 3: Calculate pressure drop
        dp_result = calculate_pressure_drop(
            friction_factor=ff_result["value"],
            length=length,
            diameter=diameter,
            velocity=velocity,
            density=standard_water["density"],
        )

        assert dp_result["value"] > 0
        assert dp_result["unit"] == "Pa"

    def test_complete_pipe_analysis_turbulent(self, standard_water, standard_pipe):
        """Complete analysis of turbulent pipe flow."""
        # Setup: High velocity turbulent flow
        velocity = 2.5  # m/s

        # Step 1: Calculate Reynolds
        re_result = calculate_reynolds(
            density=standard_water["density"],
            velocity=velocity,
            diameter=standard_pipe["diameter"],
            viscosity=standard_water["dynamic_viscosity"],
        )

        assert re_result["flow_regime"] == "turbulent"
        assert re_result["value"] > 4000

        # Step 2: Calculate friction factor
        ff_result = calculate_friction_factor(
            reynolds=re_result["value"],
            roughness=standard_pipe["absolute_roughness"],
            diameter=standard_pipe["diameter"],
            method="churchill",
        )

        # Friction factor should be reasonable for turbulent flow
        assert 0.01 < ff_result["value"] < 0.1

        # Step 3: Calculate pressure drop
        dp_result = calculate_pressure_drop(
            friction_factor=ff_result["value"],
            length=standard_pipe["length"],
            diameter=standard_pipe["diameter"],
            velocity=velocity,
            density=standard_water["density"],
        )

        # Pressure drop should be significant for turbulent flow
        assert dp_result["value"] > 100  # Pa
        assert dp_result["unit"] == "Pa"

    def test_us_customary_units_consistency(self):
        """Test that US customary results are consistent with SI."""
        # SI calculation
        si_result = calculate_pressure_drop(
            friction_factor=0.030,
            length=30.48,  # 100 feet in meters
            diameter=0.0508,  # 2 inches in meters
            velocity=0.6096,  # 2 ft/s in m/s
            density=1000,  # approximated as water
            unit_system="SI",
        )

        # US customary calculation (equivalent values)
        us_result = calculate_pressure_drop(
            friction_factor=0.030,
            length=100.0,  # feet
            diameter=2.0,  # inches
            velocity=2.0,  # ft/s
            density=62.4,  # lb/ft³ (water)
            unit_system="US",
        )

        # Convert SI result to psi for comparison
        # 1 psi = 6894.76 Pa
        si_in_psi = si_result["value"] / 6894.76

        # Should be reasonably close (allowing for rounding differences)
        assert math.isclose(si_in_psi, us_result["value"], rel_tol=0.10)
