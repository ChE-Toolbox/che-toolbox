"""Validation tests for insulation sizing calculations against literature references.

Tests insulation economic optimization and temperature-constrained calculations
against published reference cases from Incropera, Perry's, and ASHRAE.
"""

import json
import math
from pathlib import Path

import pytest

from heat_calc.insulation import calculate_insulation
from heat_calc.models.insulation_input import InsulationInput


# Load reference test cases
REFERENCE_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "reference_test_cases.json"


@pytest.fixture
def reference_cases():
    """Load insulation reference test cases from JSON file."""
    with open(REFERENCE_DATA_PATH, "r") as f:
        data = json.load(f)
    return data["insulation"]


class TestInsulationIncropera:
    """Validation tests against Incropera textbook examples."""

    def test_ins_001_economic_optimization(self, reference_cases):
        """Test INS_001: Economic optimization - Incropera Example 3.5.

        This test validates economic insulation thickness optimization
        matching Incropera's published example.
        """
        case = next(c for c in reference_cases if c["case_id"] == "INS_001")

        # Extract reference parameters
        expected_thickness = case["expected_optimal_thickness_m"]
        tolerance_percent = case["tolerance_percent"]

        # Note: INS_001 provides simplified parameters
        # We need to construct a full input matching the reference conditions
        # This is a conceptual test - parameters may need adjustment
        input_data = InsulationInput(
            pipe_diameter=case["outer_radius_m"] * 2.0,
            pipe_length=100.0,  # Assumed standard length
            T_surface_uninsulated=case["surface_temp_k"],
            T_ambient=case["ambient_temp_k"],
            h_ambient=10.0,  # Assumed natural convection
            insulation_material="reference_material",
            thermal_conductivity_insulation=case["thermal_conductivity_w_mk"],
            density_insulation=100.0,  # Assumed
            energy_cost=case["annual_cost_factor"],
            insulation_cost_per_thickness=case["cost_per_cubic_meter"],
        )

        result = calculate_insulation(input_data)

        assert result.success
        assert result.optimization_mode == "economic_payback"

        # Validate optimal thickness within tolerance
        thickness_error = abs(result.optimal_insulation_thickness - expected_thickness) / expected_thickness * 100
        assert thickness_error <= tolerance_percent, (
            f"Optimal thickness {result.optimal_insulation_thickness:.3f} m "
            f"does not match expected {expected_thickness:.3f} m "
            f"(error: {thickness_error:.1f}%, tolerance: {tolerance_percent}%)"
        )

    def test_ins_002_temperature_constraint(self, reference_cases):
        """Test INS_002: Temperature-constrained insulation sizing.

        Validates minimum insulation thickness to meet surface temperature
        safety requirements.
        """
        case = next(c for c in reference_cases if c["case_id"] == "INS_002")

        expected_thickness = case["expected_required_thickness_m"]
        tolerance_percent = case["tolerance_percent"]

        input_data = InsulationInput(
            pipe_diameter=case["outer_radius_m"] * 2.0,
            pipe_length=100.0,
            T_surface_uninsulated=case["pipe_temp_k"],
            T_ambient=case["ambient_temp_k"],
            h_ambient=15.0,
            insulation_material="reference_material",
            thermal_conductivity_insulation=case["thermal_conductivity_w_mk"],
            density_insulation=100.0,
            energy_cost=10.0,  # Not primary driver in temp-constrained mode
            insulation_cost_per_thickness=50.0,
            surface_temp_limit=case["max_surface_temp_k"],
        )

        result = calculate_insulation(input_data)

        assert result.success
        assert result.optimization_mode == "temperature_constraint"

        # Validate thickness meets temperature constraint
        assert result.T_surface_insulated <= case["max_surface_temp_k"] + 1.0  # 1K tolerance

        # Validate thickness is close to expected
        thickness_error = abs(result.optimal_insulation_thickness - expected_thickness) / expected_thickness * 100
        assert thickness_error <= tolerance_percent, (
            f"Required thickness {result.optimal_insulation_thickness:.3f} m "
            f"does not match expected {expected_thickness:.3f} m "
            f"(error: {thickness_error:.1f}%, tolerance: {tolerance_percent}%)"
        )

    def test_ins_003_heat_loss_reduction(self, reference_cases):
        """Test INS_003: Cylindrical insulation heat loss reduction.

        Validates heat loss reduction percentage for cylindrical insulation.
        """
        case = next(c for c in reference_cases if c["case_id"] == "INS_003")

        expected_reduction = case["expected_heat_loss_reduction_percent"]
        tolerance_percent = case["tolerance_percent"]

        # Create input with specified insulation thickness
        input_data = InsulationInput(
            pipe_diameter=case["pipe_radius_m"] * 2.0,
            pipe_length=case["pipe_length_m"],
            T_surface_uninsulated=case["pipe_temp_k"],
            T_ambient=case["ambient_temp_k"],
            h_ambient=15.0,
            insulation_material="reference_material",
            thermal_conductivity_insulation=case["thermal_conductivity_w_mk"],
            density_insulation=100.0,
            energy_cost=10.0,
            insulation_cost_per_thickness=50.0,
            # Override optimization to test at specified thickness
            insulation_thickness_min=case["insulation_thickness_m"],
            insulation_thickness_max=case["insulation_thickness_m"],
        )

        result = calculate_insulation(input_data)

        assert result.success

        # Validate heat loss reduction percentage
        reduction_error = abs(result.heat_loss_reduction_percent - expected_reduction)
        assert reduction_error <= tolerance_percent, (
            f"Heat loss reduction {result.heat_loss_reduction_percent:.1f}% "
            f"does not match expected {expected_reduction:.1f}% "
            f"(error: {reduction_error:.1f}%, tolerance: {tolerance_percent}%)"
        )


class TestInsulationEconomics:
    """Economic analysis validation tests."""

    def test_payback_period_consistency(self):
        """Test payback period calculation against manual calculation."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,  # 150°C
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=12.0,  # $/MWh
            insulation_cost_per_thickness=50.0,
            analysis_period_years=10,
        )

        result = calculate_insulation(input_data)

        assert result.success

        # Manual payback calculation
        expected_payback = result.total_insulation_cost / result.annual_cost_savings

        # Validate payback period accuracy
        assert abs(result.payback_period_years - expected_payback) < 0.01, (
            f"Payback period {result.payback_period_years:.2f} years "
            f"does not match manual calculation {expected_payback:.2f} years"
        )

    def test_energy_cost_impact_on_thickness(self):
        """Test that higher energy costs lead to thicker optimal insulation."""
        base_input = InsulationInput(
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

        high_energy_input = InsulationInput(
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

        result_base = calculate_insulation(base_input)
        result_high = calculate_insulation(high_energy_input)

        assert result_base.success
        assert result_high.success

        # Higher energy cost should justify thicker insulation
        assert result_high.optimal_insulation_thickness > result_base.optimal_insulation_thickness, (
            f"High energy cost case ({result_high.optimal_insulation_thickness:.3f} m) "
            f"should have thicker insulation than base case ({result_base.optimal_insulation_thickness:.3f} m)"
        )

        # Higher energy cost should also reduce payback period
        assert result_high.payback_period_years < result_base.payback_period_years, (
            f"High energy cost case should have shorter payback period "
            f"({result_high.payback_period_years:.1f} vs {result_base.payback_period_years:.1f} years)"
        )

    def test_insulation_cost_impact_on_thickness(self):
        """Test that higher insulation costs lead to thinner optimal thickness."""
        base_input = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=15.0,
            insulation_cost_per_thickness=40.0,
        )

        high_cost_input = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=423.15,
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="mineral_wool",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=15.0,
            insulation_cost_per_thickness=100.0,  # 2.5x higher
        )

        result_base = calculate_insulation(base_input)
        result_high = calculate_insulation(high_cost_input)

        assert result_base.success
        assert result_high.success

        # Higher insulation cost should lead to thinner optimal thickness
        assert result_high.optimal_insulation_thickness < result_base.optimal_insulation_thickness, (
            f"High insulation cost case ({result_high.optimal_insulation_thickness:.3f} m) "
            f"should have thinner insulation than base case ({result_base.optimal_insulation_thickness:.3f} m)"
        )


class TestHeatLossCalculations:
    """Heat loss calculation validation tests."""

    def test_heat_loss_monotonic_decrease(self):
        """Test that heat loss decreases monotonically with insulation thickness."""
        # Test with manual thickness progression
        thicknesses = [0.01, 0.03, 0.05, 0.07, 0.10]
        heat_losses = []

        for thickness in thicknesses:
            input_data = InsulationInput(
                pipe_diameter=0.1,
                pipe_length=100.0,
                T_surface_uninsulated=423.15,
                T_ambient=298.15,
                h_ambient=15.0,
                insulation_material="test",
                thermal_conductivity_insulation=0.04,
                density_insulation=100.0,
                energy_cost=12.0,
                insulation_cost_per_thickness=50.0,
                insulation_thickness_min=thickness,
                insulation_thickness_max=thickness,
            )

            result = calculate_insulation(input_data)
            assert result.success
            heat_losses.append(result.Q_insulated)

        # Verify monotonic decrease
        for i in range(len(heat_losses) - 1):
            assert heat_losses[i] > heat_losses[i + 1], (
                f"Heat loss should decrease with thickness: "
                f"{heat_losses[i]:.1f} W at {thicknesses[i]:.3f} m > "
                f"{heat_losses[i+1]:.1f} W at {thicknesses[i+1]:.3f} m"
            )

    def test_cylindrical_resistance_formula(self):
        """Validate cylindrical thermal resistance calculation."""
        # Known analytical case
        pipe_diameter = 0.1  # 100 mm
        insulation_thickness = 0.05  # 50 mm
        pipe_length = 1.0  # 1 meter for unit calculation
        k_insulation = 0.04  # W/(m·K)
        T_pipe = 423.15  # K
        T_ambient = 298.15  # K
        h_ambient = 15.0  # W/(m²·K)

        # Manual calculation of thermal resistance
        r1 = pipe_diameter / 2.0
        r2 = r1 + insulation_thickness

        # R_cond = ln(r2/r1) / (2πLk)
        R_cond = math.log(r2 / r1) / (2.0 * math.pi * pipe_length * k_insulation)

        # R_conv = 1 / (h × A_outer)
        A_outer = 2.0 * math.pi * r2 * pipe_length
        R_conv = 1.0 / (h_ambient * A_outer)

        # Total resistance
        R_total = R_cond + R_conv

        # Expected heat loss
        expected_q = (T_pipe - T_ambient) / R_total

        # Calculate using library function
        input_data = InsulationInput(
            pipe_diameter=pipe_diameter,
            pipe_length=pipe_length,
            T_surface_uninsulated=T_pipe,
            T_ambient=T_ambient,
            h_ambient=h_ambient,
            insulation_material="test",
            thermal_conductivity_insulation=k_insulation,
            density_insulation=100.0,
            energy_cost=12.0,
            insulation_cost_per_thickness=50.0,
            insulation_thickness_min=insulation_thickness,
            insulation_thickness_max=insulation_thickness,
        )

        result = calculate_insulation(input_data)

        assert result.success

        # Validate heat loss calculation
        heat_loss_error = abs(result.Q_insulated - expected_q) / expected_q * 100
        assert heat_loss_error < 1.0, (
            f"Heat loss calculation error {heat_loss_error:.2f}% exceeds 1% tolerance. "
            f"Calculated: {result.Q_insulated:.2f} W, Expected: {expected_q:.2f} W"
        )


class TestTemperatureProfile:
    """Surface temperature calculation validation tests."""

    def test_surface_temp_between_limits(self):
        """Test that insulated surface temperature is between ambient and pipe temp."""
        input_data = InsulationInput(
            pipe_diameter=0.1,
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

        # Surface temperature should be between ambient and pipe surface
        assert result.T_surface_insulated > input_data.T_ambient, (
            f"Surface temp {result.T_surface_insulated:.1f} K should be above ambient {input_data.T_ambient:.1f} K"
        )
        assert result.T_surface_insulated < input_data.T_surface_uninsulated, (
            f"Surface temp {result.T_surface_insulated:.1f} K should be below pipe temp "
            f"{input_data.T_surface_uninsulated:.1f} K"
        )

    def test_surface_temp_decreases_with_thickness(self):
        """Test that surface temperature decreases with increasing insulation thickness."""
        thicknesses = [0.02, 0.05, 0.10]
        surface_temps = []

        for thickness in thicknesses:
            input_data = InsulationInput(
                pipe_diameter=0.1,
                pipe_length=100.0,
                T_surface_uninsulated=473.15,  # 200°C
                T_ambient=298.15,
                h_ambient=15.0,
                insulation_material="test",
                thermal_conductivity_insulation=0.04,
                density_insulation=100.0,
                energy_cost=12.0,
                insulation_cost_per_thickness=50.0,
                insulation_thickness_min=thickness,
                insulation_thickness_max=thickness,
            )

            result = calculate_insulation(input_data)
            assert result.success
            surface_temps.append(result.T_surface_insulated)

        # Verify surface temperature decreases with thickness
        for i in range(len(surface_temps) - 1):
            assert surface_temps[i] > surface_temps[i + 1], (
                f"Surface temp should decrease with thickness: "
                f"{surface_temps[i]:.1f} K at {thicknesses[i]:.3f} m > "
                f"{surface_temps[i+1]:.1f} K at {thicknesses[i+1]:.3f} m"
            )

    def test_temp_constraint_satisfaction(self):
        """Test that temperature constraint mode satisfies the specified limit."""
        surface_temp_limits = [333.15, 323.15, 313.15]  # 60°C, 50°C, 40°C

        for temp_limit in surface_temp_limits:
            input_data = InsulationInput(
                pipe_diameter=0.1,
                pipe_length=100.0,
                T_surface_uninsulated=473.15,  # 200°C
                T_ambient=298.15,
                h_ambient=15.0,
                insulation_material="test",
                thermal_conductivity_insulation=0.04,
                density_insulation=100.0,
                energy_cost=12.0,
                insulation_cost_per_thickness=50.0,
                surface_temp_limit=temp_limit,
            )

            result = calculate_insulation(input_data)

            assert result.success
            assert result.optimization_mode == "temperature_constraint"

            # Surface temperature should meet constraint (with small tolerance)
            assert result.T_surface_insulated <= temp_limit + 1.0, (
                f"Surface temp {result.T_surface_insulated:.1f} K exceeds limit {temp_limit:.1f} K"
            )


class TestBoundaryConditions:
    """Edge case and boundary condition tests."""

    def test_minimum_thickness_binding(self):
        """Test case where optimal thickness hits minimum constraint."""
        # Very low energy cost makes thin insulation optimal
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=323.15,  # Low temp (50°C)
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="test",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=1.0,  # Very low energy cost
            insulation_cost_per_thickness=100.0,  # High insulation cost
            insulation_thickness_min=0.02,
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Optimal thickness may hit minimum constraint
        assert result.optimal_insulation_thickness >= input_data.insulation_thickness_min

    def test_maximum_thickness_binding(self):
        """Test case where optimal thickness hits maximum constraint."""
        # Very high energy cost makes thick insulation optimal
        input_data = InsulationInput(
            pipe_diameter=0.1,
            pipe_length=100.0,
            T_surface_uninsulated=573.15,  # High temp (300°C)
            T_ambient=298.15,
            h_ambient=15.0,
            insulation_material="test",
            thermal_conductivity_insulation=0.04,
            density_insulation=100.0,
            energy_cost=100.0,  # Very high energy cost
            insulation_cost_per_thickness=10.0,  # Low insulation cost
            insulation_thickness_max=0.08,
        )

        result = calculate_insulation(input_data)

        assert result.success
        # Optimal thickness may hit maximum constraint
        assert result.optimal_insulation_thickness <= input_data.insulation_thickness_max
