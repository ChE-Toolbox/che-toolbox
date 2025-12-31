"""Unit tests for insulation sizing and economic optimization calculations.

Tests the calculate_insulation function with various optimization modes,
economic parameters, and edge cases.
"""

import pytest

from heat_calc.insulation import calculate_insulation
from heat_calc.models.insulation_input import InsulationInput
from heat_calc.models.insulation_results import InsulationResult


class TestEconomicOptimization:
    """Tests for economic payback optimization mode."""

    def test_basic_economic_optimization(self):
        """Test basic economic optimization for insulation thickness."""
        input_data = InsulationInput(
            pipe_diameter=0.1,  # 100 mm OD
            pipe_length=100.0,
            T_surface_uninsulated=423.15,  # 150°C
            T_ambient=298.15,  # 25°C
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
        )

        result = calculate_insulation(input_data)

        assert result.success
        assert result.optimization_mode == "economic_payback"
        assert result.optimal_insulation_thickness > 0
        assert result.optimal_insulation_thickness >= input_data.insulation_thickness_min
        assert result.optimal_insulation_thickness <= input_data.insulation_thickness_max
        assert result.Q_insulated < result.Q_uninsulated
        assert result.heat_loss_reduction_percent > 0
        assert result.payback_period_years > 0

    def test_economic_opt_high_energy_cost(self):
        """Test that higher energy costs lead to thicker insulation."""
        # Base case
        input_base = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=10.0,
            insulation_cost_per_thickness=50.0,
        )

        # High energy cost case
        input_high_energy = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=50.0,  # 5x higher
            insulation_cost_per_thickness=50.0,
        )

        result_base = calculate_insulation(input_base)
        result_high = calculate_insulation(input_high_energy)

        assert result_base.success
        assert result_high.success
        # Higher energy cost should lead to thicker insulation
        assert result_high.optimal_insulation_thickness > result_base.optimal_insulation_thickness

    def test_economic_opt_heat_loss_reduction(self):
        """Test that insulation reduces heat loss significantly."""
        input_data = InsulationInput(
            pipe_diameter=0.15,
            pipe_length=50.0,
            T_surface_uninsulated=473.15,  # 200°C
            T_ambient=298.15,
            h_ambient=20.0,
            insulation_material="fiberglass",
            thermal_conductivity_insulation=0.035,
            density_insulation=64.0,
            energy_cost=15.0,
            insulation_cost_per_thickness=45.0,
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Insulation should reduce heat loss by at least 70%
        assert result.heat_loss_reduction_percent >= 70.0
        assert result.Q_insulated < 0.3 * result.Q_uninsulated

    def test_payback_period_calculation(self):
        """Test payback period calculation accuracy."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
            analysis_period_years=10,
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Manual check: payback = total_cost / annual_savings
        expected_payback = result.total_insulation_cost / result.annual_cost_savings
        assert abs(result.payback_period_years - expected_payback) < 0.01

    def test_net_annual_savings_positive(self):
        """Test that optimal solution has positive net savings."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
            analysis_period_years=10,
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Net savings should be positive for economic optimum
        assert result.net_annual_savings > 0
        assert result.annual_cost_savings > result.annual_insulation_cost


class TestTemperatureConstraint:
    """Tests for temperature-constrained optimization mode."""

    def test_temperature_constraint_mode(self):
        """Test temperature-constrained optimization."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,  # 150°C
            T_ambient=298.15,  # 25°C
            h_ambient=15.0,
            insulation_material="fiberglass",
            thermal_conductivity_insulation=0.035,
            density_insulation=64.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=45.0,
            surface_temp_limit=333.15,  # 60°C max surface temp
        )

        result = calculate_insulation(input_data)

        assert result.success
        assert result.optimization_mode == "temperature_constraint"
        assert result.T_surface_insulated <= result.T_surface_required + 1.0  # 1K tolerance
        assert result.T_surface_insulated < input_data.T_surface_uninsulated

    def test_temperature_limit_met(self):
        """Test that surface temperature meets the specified limit."""
        input_data = InsulationInput(
            pipe_diameter=0.15,
            pipe_length=50.0,
            T_surface_uninsulated=473.15,  # 200°C
            T_ambient=298.15,
            h_ambient=20.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
            surface_temp_limit=323.15,  # 50°C limit
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Surface temperature should be at or below limit
        assert result.T_surface_insulated <= result.T_surface_required + 0.5
        # Should have significant thickness to meet this constraint
        assert result.optimal_insulation_thickness > 0.02


class TestMaterialQuantities:
    """Tests for material volume and mass calculations."""

    def test_material_volume_calculation(self):
        """Test insulation volume calculation."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
        )

        result = calculate_insulation(input_data)

        assert result.success
        assert result.insulation_volume > 0
        # Check that mass = volume × density
        expected_mass = result.insulation_volume * input_data.density_insulation
        assert abs(result.insulation_mass - expected_mass) < 0.1

    def test_material_mass_scales_with_density(self):
        """Test that material mass scales with density."""
        # Low density insulation
        input_low = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="low_density",
            thermal_conductivity_insulation=0.04,
            density_insulation=50.0,  # Low density
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
        )

        # High density insulation
        input_high = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="high_density",
            thermal_conductivity_insulation=0.04,
            density_insulation=150.0,  # High density
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
        )

        result_low = calculate_insulation(input_low)
        result_high = calculate_insulation(input_high)

        assert result_low.success
        assert result_high.success
        # Mass should scale approximately with density ratio
        density_ratio = input_high.density_insulation / input_low.density_insulation
        mass_ratio = result_high.insulation_mass / result_low.insulation_mass
        # Allow for small differences due to optimization differences
        assert abs(mass_ratio - density_ratio) < 0.3


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_min_thickness_constraint(self):
        """Test that thickness respects minimum constraint."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=323.15,  # Low temp (50°C)
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
            insulation_thickness_min=0.05,  # 50mm minimum
        )

        result = calculate_insulation(input_data)

        assert result.success
        assert result.optimal_insulation_thickness >= input_data.insulation_thickness_min

    def test_max_thickness_constraint(self):
        """Test that thickness respects maximum constraint."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=573.15,  # High temp (300°C)
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=100.0,  # Very high energy cost
            insulation_cost_per_thickness=10.0,  # Low insulation cost
            insulation_thickness_max=0.08,  # 80mm maximum
        )

        result = calculate_insulation(input_data)

        assert result.success
        assert result.optimal_insulation_thickness <= input_data.insulation_thickness_max

    def test_small_temperature_difference(self):
        """Test with small temperature difference."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=308.15,  # 35°C (small ΔT)
            T_ambient=298.15,  # 25°C
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Small ΔT means small heat loss, so thin insulation expected
        assert result.Q_uninsulated < 500.0  # Low heat loss

    def test_long_pipe_length(self):
        """Test with long pipe length."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=1000.0,  # 1 km pipe
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Longer pipe means more heat loss and more material
        assert result.Q_uninsulated > 10000.0  # Significant heat loss
        assert result.insulation_volume > 1.0  # Substantial material volume


class TestInputValidation:
    """Tests for input validation and error handling."""

    def test_invalid_temp_difference(self):
        """Test that T_surface must be greater than T_ambient."""
        with pytest.raises(ValueError, match="T_surface_uninsulated.*must be greater than.*T_ambient"):
            InsulationInput(
                pipe_diameter=0.1,
                pipe_length=100.0,
                T_surface_uninsulated=298.15,  # Same as ambient
                T_ambient=298.15,
                h_ambient=15.0,
                insulation_material="mineral_wool",
                thermal_conductivity_insulation=0.04,
                density_insulation=100.0,
                energy_cost=12.0,
                insulation_cost_per_thickness=50.0,
            )

    def test_invalid_thickness_range(self):
        """Test that max thickness must be greater than min thickness."""
        with pytest.raises(ValueError, match="insulation_thickness_max.*must be greater than"):
            InsulationInput(
                pipe_diameter=0.1,
                pipe_length=100.0,
                T_surface_uninsulated=423.15,
                T_ambient=298.15,
                h_ambient=15.0,
                insulation_material="mineral_wool",
                thermal_conductivity_insulation=0.04,
                density_insulation=100.0,
                energy_cost=12.0,
                insulation_cost_per_thickness=50.0,
                insulation_thickness_min=0.10,
                insulation_thickness_max=0.05,  # Less than min
            )

    def test_invalid_surface_temp_limit(self):
        """Test that surface temp limit must be between ambient and uninsulated."""
        # Limit below ambient
        with pytest.raises(ValueError, match="surface_temp_limit.*must be greater than T_ambient"):
            InsulationInput(
                pipe_diameter=0.1,
                pipe_length=100.0,
                T_surface_uninsulated=423.15,
                T_ambient=298.15,
                h_ambient=15.0,
                insulation_material="mineral_wool",
                thermal_conductivity_insulation=0.04,
                density_insulation=100.0,
                energy_cost=12.0,
                insulation_cost_per_thickness=50.0,
                surface_temp_limit=290.15,  # Below ambient
            )

        # Limit above uninsulated surface temp
        with pytest.raises(ValueError, match="surface_temp_limit.*must be less than T_surface_uninsulated"):
            InsulationInput(
                pipe_diameter=0.1,
                pipe_length=100.0,
                T_surface_uninsulated=423.15,
                T_ambient=298.15,
                h_ambient=15.0,
                insulation_material="mineral_wool",
                thermal_conductivity_insulation=0.04,
                density_insulation=100.0,
                energy_cost=12.0,
                insulation_cost_per_thickness=50.0,
                surface_temp_limit=450.15,  # Above uninsulated
            )


class TestResultValidation:
    """Tests for result object validation."""

    def test_result_energy_balance(self):
        """Test that energy balance is internally consistent."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Check heat loss reduction calculation
        heat_loss_reduction = (result.Q_uninsulated - result.Q_insulated) / result.Q_uninsulated * 100
        assert abs(result.heat_loss_reduction_percent - heat_loss_reduction) < 0.1

    def test_result_economic_consistency(self):
        """Test that economic metrics are internally consistent."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
            analysis_period_years=10,
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Check net savings = cost savings - insulation cost
        expected_net = result.annual_cost_savings - result.annual_insulation_cost
        assert abs(result.net_annual_savings - expected_net) < 0.01
