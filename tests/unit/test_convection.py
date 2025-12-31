"""Unit tests for convection heat transfer calculations.

Tests the calculate_convection function for all supported geometries:
- Flat plate (forced convection, laminar/turbulent)
- Pipe flow (internal forced convection)
- Cylinder in crossflow (external forced convection)
- Vertical plate (natural convection)
"""

import pytest

from heat_calc.convection import calculate_convection
from heat_calc.models.convection_input import (
    CylinderCrossflowConvection,
    FlatPlateConvection,
    FluidProperties,
    PipeFlowConvection,
    VerticalPlateNaturalConvection,
)


class TestFlatPlateConvection:
    """Tests for flat plate forced convection."""

    def test_flat_plate_laminar_air(self):
        """Test laminar flow over flat plate with air."""
        # Air properties at 300 K
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        input_data = FlatPlateConvection(
            length=1.0,
            flow_velocity=2.0,  # Low velocity for laminar
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        assert result.Reynolds > 0
        assert result.Reynolds < 5e5  # Should be laminar
        assert result.flow_regime == "laminar"
        assert result.Prandtl > 0
        assert result.Nusselt > 0
        assert result.geometry_type == "flat_plate"

    def test_flat_plate_turbulent_air(self):
        """Test turbulent flow over flat plate with air."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        input_data = FlatPlateConvection(
            length=1.0,
            flow_velocity=50.0,  # High velocity for turbulent
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        assert result.Reynolds >= 5e5  # Should be turbulent
        assert result.flow_regime == "turbulent"

    def test_flat_plate_water(self):
        """Test flat plate convection with water."""
        water_props = FluidProperties(
            density=997.0,
            dynamic_viscosity=8.9e-4,
            thermal_conductivity=0.613,
            specific_heat=4179.0,
        )

        input_data = FlatPlateConvection(
            length=0.5,
            flow_velocity=1.0,
            surface_temperature=320.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=water_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        # Water has higher Pr than air
        assert result.Prandtl > 1.0


class TestPipeFlowConvection:
    """Tests for pipe flow forced convection."""

    def test_pipe_flow_laminar(self):
        """Test laminar pipe flow."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        input_data = PipeFlowConvection(
            diameter=0.1,
            length=10.0,
            flow_velocity=0.1,  # Low velocity for laminar
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        assert result.Reynolds < 2300  # Should be laminar
        assert result.flow_regime == "laminar"
        assert result.Nusselt == pytest.approx(3.66, rel=0.01)  # Fully developed laminar

    def test_pipe_flow_turbulent_dittus_boelter(self):
        """Test turbulent pipe flow with Dittus-Boelter correlation."""
        water_props = FluidProperties(
            density=997.0,
            dynamic_viscosity=8.9e-4,
            thermal_conductivity=0.613,
            specific_heat=4179.0,
        )

        input_data = PipeFlowConvection(
            diameter=0.05,
            length=10.0,
            flow_velocity=2.0,  # High velocity for turbulent
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=water_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        assert result.Reynolds >= 10000  # Should be turbulent
        assert result.flow_regime == "turbulent"
        assert result.Nusselt > 10  # Much higher than laminar

    def test_pipe_flow_transitional(self):
        """Test transitional regime pipe flow."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        input_data = PipeFlowConvection(
            diameter=0.05,
            length=10.0,
            flow_velocity=3.0,  # Transitional regime
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        assert 2300 <= result.Reynolds < 10000  # Transitional range
        assert result.flow_regime == "transitional"


class TestCylinderCrossflowConvection:
    """Tests for cylinder in crossflow convection."""

    def test_cylinder_crossflow_air(self):
        """Test cylinder in crossflow with air."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        input_data = CylinderCrossflowConvection(
            diameter=0.1,
            flow_velocity=10.0,
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        assert result.Reynolds > 0
        assert result.Prandtl > 0
        assert result.Nusselt > 0
        assert result.geometry_type == "cylinder_crossflow"
        assert result.correlation_equation in ["Churchill-Bernstein", "Churchill-Bernstein (simplified)"]

    def test_cylinder_crossflow_water(self):
        """Test cylinder in crossflow with water."""
        water_props = FluidProperties(
            density=997.0,
            dynamic_viscosity=8.9e-4,
            thermal_conductivity=0.613,
            specific_heat=4179.0,
        )

        input_data = CylinderCrossflowConvection(
            diameter=0.05,
            flow_velocity=5.0,
            surface_temperature=320.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=water_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        # Water should have higher h than air due to higher thermal conductivity
        assert result.h > 100  # Water typically > 100 W/(m²·K)

    def test_cylinder_low_reynolds(self):
        """Test cylinder at low Reynolds number (creeping flow)."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        input_data = CylinderCrossflowConvection(
            diameter=0.001,  # Small diameter
            flow_velocity=0.01,  # Very low velocity
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        assert result.Reynolds < 1
        assert result.flow_regime == "creeping"


class TestNaturalConvection:
    """Tests for natural convection on vertical plate."""

    def test_natural_convection_laminar(self):
        """Test laminar natural convection on vertical plate."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
            thermal_expansion_coefficient=1.0 / 300.0,  # ~1/T for ideal gas
        )

        input_data = VerticalPlateNaturalConvection(
            height=0.5,  # Small height for laminar
            surface_temperature=320.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        assert result.Grashof is not None
        assert result.Rayleigh is not None
        assert result.Grashof > 0
        assert result.Rayleigh > 0
        assert result.Rayleigh < 1e9  # Laminar regime
        assert result.flow_regime == "natural_laminar"
        assert result.geometry_type == "vertical_plate_natural"

    def test_natural_convection_turbulent(self):
        """Test turbulent natural convection on vertical plate."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
            thermal_expansion_coefficient=1.0 / 300.0,
        )

        input_data = VerticalPlateNaturalConvection(
            height=3.0,  # Large height for turbulent
            surface_temperature=350.0,  # Larger temperature difference
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        assert result.Rayleigh >= 1e9  # Turbulent regime
        assert result.flow_regime == "natural_turbulent"

    def test_natural_convection_without_beta(self):
        """Test natural convection when beta not provided (should use 1/T approximation)."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
            # thermal_expansion_coefficient not provided
        )

        input_data = VerticalPlateNaturalConvection(
            height=1.0,
            surface_temperature=320.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.h > 0
        # Should still work using 1/T approximation
        assert result.Rayleigh > 0


class TestCorrelationRangeValidation:
    """Test correlation range checking."""

    def test_within_range_flag(self):
        """Test that is_within_correlation_range flag is set correctly."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        # Test with normal conditions (should be within range)
        input_data = FlatPlateConvection(
            length=1.0,
            flow_velocity=10.0,
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert isinstance(result.is_within_correlation_range, bool)
        assert "Re" in result.applicable_range
        assert "Pr" in result.applicable_range


class TestIntermediateValues:
    """Test that intermediate values are correctly stored."""

    def test_intermediate_values_present(self):
        """Test that intermediate values dictionary is populated."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        input_data = FlatPlateConvection(
            length=1.0,
            flow_velocity=5.0,
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert len(result.intermediate_values) > 0
        assert "characteristic_length_m" in result.intermediate_values
        assert "flow_velocity_m_s" in result.intermediate_values
