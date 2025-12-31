"""
Unit tests for pipe flow calculations.

Tests Reynolds number, friction factor, and pressure drop calculations.
"""

import math

import pytest

from fluids.pipe import (
    calculate_friction_factor,
    calculate_pressure_drop,
    calculate_reynolds,
)


class TestReynolds:
    """Test Reynolds number calculation."""

    def test_reynolds_calculation_basic(self, standard_water):
        """Test basic Reynolds number calculation."""
        result = calculate_reynolds(
            density=standard_water["density"],
            velocity=2.0,
            diameter=0.05,
            viscosity=standard_water["dynamic_viscosity"],
        )

        assert "value" in result
        assert "flow_regime" in result
        assert result["value"] > 0
        assert result["unit"] == "dimensionless"

    def test_reynolds_laminar(self):
        """Test laminar flow regime (Re < 2300)."""
        result = calculate_reynolds(
            density=1000,
            velocity=0.04,
            diameter=0.05,
            viscosity=0.001,
        )
        assert result["flow_regime"] == "laminar"
        assert result["value"] < 2300

    def test_reynolds_turbulent(self):
        """Test turbulent flow regime (Re > 4000)."""
        result = calculate_reynolds(
            density=1000,
            velocity=2.0,
            diameter=0.05,
            viscosity=0.001,
        )
        assert result["flow_regime"] == "turbulent"
        assert result["value"] > 4000

    def test_reynolds_transitional_warning(self):
        """Test transitional zone warning."""
        result = calculate_reynolds(
            density=1000,
            velocity=0.23,
            diameter=0.05,
            viscosity=0.001,
        )
        assert result["flow_regime"] == "transitional"
        assert len(result["warnings"]) > 0

    def test_reynolds_invalid_density(self):
        """Test validation of negative density."""
        with pytest.raises(ValueError):
            calculate_reynolds(
                density=-1000,
                velocity=1.0,
                diameter=0.05,
                viscosity=0.001,
            )

    def test_reynolds_invalid_diameter(self):
        """Test validation of zero diameter."""
        with pytest.raises(ValueError):
            calculate_reynolds(
                density=1000,
                velocity=1.0,
                diameter=0.0,
                viscosity=0.001,
            )


class TestFrictionFactor:
    """Test friction factor calculation."""

    def test_friction_laminar_exact(self):
        """Test friction factor for laminar flow (exact solution)."""
        re = 1000
        result = calculate_friction_factor(
            reynolds=re,
            roughness=0.0,
            diameter=0.05,
            method="churchill",
        )

        expected_f = 64 / re
        assert math.isclose(result["value"], expected_f, rel_tol=0.01)

    def test_friction_turbulent_churchill(self):
        """Test friction factor for turbulent flow (Churchill method)."""
        result = calculate_friction_factor(
            reynolds=10000,
            roughness=0.000045,
            diameter=0.05,
            method="churchill",
        )

        assert result["value"] > 0
        assert result["value"] < 0.1
        assert "churchill" in result["formula_used"].lower()

    def test_friction_turbulent_colebrook(self):
        """Test friction factor for turbulent flow (Colebrook method)."""
        result = calculate_friction_factor(
            reynolds=10000,
            roughness=0.000045,
            diameter=0.05,
            method="colebrook",
        )

        assert result["value"] > 0
        assert result["value"] < 0.1

    def test_friction_transitional_warning(self):
        """Test transitional zone uses laminar as conservative."""
        result = calculate_friction_factor(
            reynolds=3000,  # In transitional zone
            roughness=0.000045,
            diameter=0.05,
            method="churchill",
        )

        assert len(result["warnings"]) > 0
        assert "transitional" in result["warnings"][0].lower()

    def test_friction_zero_velocity(self):
        """Test friction factor at zero Reynolds (zero velocity)."""
        result = calculate_friction_factor(
            reynolds=0.0,
            roughness=0.0,
            diameter=0.05,
            method="churchill",
        )

        # At Re=0, we expect f = 64/Re → ∞, but we handle as 64.0
        assert result["value"] > 0
        assert len(result["warnings"]) > 0

    def test_friction_invalid_reynolds_negative(self):
        """Test validation of negative Reynolds number."""
        with pytest.raises(ValueError):
            calculate_friction_factor(
                reynolds=-1000,
                roughness=0.0,
                diameter=0.05,
            )


class TestPressureDrop:
    """Test Darcy-Weisbach pressure drop calculation."""

    def test_pressure_drop_basic(self):
        """Test basic pressure drop calculation."""
        result = calculate_pressure_drop(
            friction_factor=0.03,
            length=100.0,
            diameter=0.05,
            velocity=2.0,
            density=1000,
        )

        assert "value" in result
        assert result["value"] > 0
        assert result["unit"] == "Pa"

    def test_pressure_drop_zero_velocity(self):
        """Test pressure drop at zero velocity."""
        result = calculate_pressure_drop(
            friction_factor=0.03,
            length=100.0,
            diameter=0.05,
            velocity=0.0,
            density=1000,
        )

        assert result["value"] == 0.0

    def test_pressure_drop_formula(self):
        """Test pressure drop matches Darcy-Weisbach formula."""
        f = 0.03
        L = 100.0
        D = 0.05
        V = 2.0
        rho = 1000

        result = calculate_pressure_drop(f, L, D, V, rho)

        # Expected: ΔP = f × (L/D) × (ρV²/2)
        expected_dp = f * (L / D) * (rho * V**2 / 2)

        assert math.isclose(result["value"], expected_dp, rel_tol=0.01)

    def test_pressure_drop_invalid_friction(self):
        """Test validation of invalid friction factor."""
        with pytest.raises(ValueError):
            calculate_pressure_drop(
                friction_factor=-0.03,
                length=100.0,
                diameter=0.05,
                velocity=2.0,
                density=1000,
            )

    def test_pressure_drop_unit_conversion_us(self):
        """Test pressure drop calculation in US units."""
        result = calculate_pressure_drop(
            friction_factor=0.03,
            length=100.0,  # ft in US
            diameter=0.05,  # ft in US
            velocity=2.0,  # ft/s in US
            density=1000,  # lb/ft³ in US (approximate)
            unit_system="US",
        )

        assert result["unit"] == "psi"


class TestIntegration:
    """Integration tests for pipe flow analysis."""

    def test_complete_pipe_flow_analysis(self, standard_water, standard_pipe):
        """Test complete pipe flow analysis with water."""
        # Given conditions
        velocity = 2.0  # m/s
        flow_area = math.pi * (standard_pipe["diameter"] / 2) ** 2
        _flow_rate = velocity * flow_area

        # Calculate Reynolds
        re_result = calculate_reynolds(
            density=standard_water["density"],
            velocity=velocity,
            diameter=standard_pipe["diameter"],
            viscosity=standard_water["dynamic_viscosity"],
        )

        assert re_result["flow_regime"] in ["laminar", "transitional", "turbulent"]

        # Calculate friction factor
        ff_result = calculate_friction_factor(
            reynolds=re_result["value"],
            roughness=standard_pipe["absolute_roughness"],
            diameter=standard_pipe["diameter"],
        )

        assert ff_result["value"] > 0

        # Calculate pressure drop
        pd_result = calculate_pressure_drop(
            friction_factor=ff_result["value"],
            length=standard_pipe["length"],
            diameter=standard_pipe["diameter"],
            velocity=velocity,
            density=standard_water["density"],
        )

        assert pd_result["value"] >= 0
        assert pd_result["unit"] == "Pa"
