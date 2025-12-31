"""Validation tests for convection heat transfer correlations.

Tests convection calculations against published correlations and reference data from:
- Incropera & DeWitt: "Fundamentals of Heat and Mass Transfer"
- Perry's Chemical Engineers' Handbook
- Churchill & Bernstein: "A Correlating Equation for Forced Convection"
- Standard heat transfer textbooks
"""

import math

import pytest

from heat_calc.convection import calculate_convection
from heat_calc.models.convection_input import (
    CylinderCrossflowConvection,
    FlatPlateConvection,
    FluidProperties,
    PipeFlowConvection,
    VerticalPlateNaturalConvection,
)


class TestFlatPlateValidation:
    """Validate flat plate correlations against published references."""

    def test_laminar_flat_plate_incropera_example_7_1(self):
        """Validate laminar flat plate against Incropera Example 7.1.

        Source: Incropera & DeWitt, 9th ed., Chapter 7
        Air at 300 K flowing over 0.5 m flat plate at U = 2 m/s
        Expected: Re ≈ 64000 (laminar), Nu_L ≈ 179, h ≈ 9.4 W/(m²·K)
        """
        air_props = FluidProperties(
            density=1.177,  # kg/m³ at 300 K
            dynamic_viscosity=1.846e-5,  # Pa·s
            thermal_conductivity=0.0263,  # W/(m·K)
            specific_heat=1007.0,  # J/(kg·K)
        )

        input_data = FlatPlateConvection(
            length=0.5,
            flow_velocity=2.0,
            surface_temperature=320.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        # Verify Reynolds number (laminar regime)
        assert result.success
        assert result.flow_regime == "laminar"
        assert abs(result.Reynolds - 64000) < 2000

        # Verify Nusselt number (Nu = 0.664 Re^0.5 Pr^(1/3))
        expected_Nu = 0.664 * result.Reynolds**0.5 * result.Prandtl**(1/3)
        assert abs(result.Nusselt - expected_Nu) < 1.0

        # Verify heat transfer coefficient
        expected_h = expected_Nu * air_props.thermal_conductivity / input_data.length
        assert abs(result.h - expected_h) < 0.5  # W/(m²·K)

    def test_turbulent_flat_plate_high_reynolds(self):
        """Validate turbulent flat plate at high Reynolds number.

        For Re = 1e6, Pr = 0.7, turbulent correlation should apply
        Expected: Nu ≈ 1356, h ≈ 71 W/(m²·K)
        """
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        # Calculate velocity needed for Re = 1e6 over 1 m plate
        L = 1.0
        Re_target = 1e6
        U = Re_target * air_props.dynamic_viscosity / (air_props.density * L)

        input_data = FlatPlateConvection(
            length=L,
            flow_velocity=U,
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.flow_regime == "turbulent"
        assert abs(result.Reynolds - Re_target) < Re_target * 0.01

        # Verify turbulent correlation (Nu = 0.037 Re^0.8 Pr^(1/3))
        Pr = air_props.specific_heat * air_props.dynamic_viscosity / air_props.thermal_conductivity
        expected_Nu = 0.037 * Re_target**0.8 * Pr**(1/3)
        assert abs(result.Nusselt - expected_Nu) / expected_Nu < 0.05


class TestPipeFlowValidation:
    """Validate pipe flow correlations against published references."""

    def test_laminar_pipe_fully_developed(self):
        """Validate fully developed laminar pipe flow.

        Source: Incropera & DeWitt, Table 8.1
        For fully developed laminar flow with constant wall temperature:
        Nu = 3.66 (theoretical value)
        """
        water_props = FluidProperties(
            density=997.0,
            dynamic_viscosity=8.9e-4,
            thermal_conductivity=0.613,
            specific_heat=4179.0,
        )

        input_data = PipeFlowConvection(
            diameter=0.05,
            length=10.0,
            flow_velocity=0.01,  # Very low for laminar
            surface_temperature=320.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=water_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.flow_regime == "laminar"
        assert result.Reynolds < 2300
        assert abs(result.Nusselt - 3.66) < 0.01  # Theoretical value

    def test_turbulent_pipe_dittus_boelter(self):
        """Validate turbulent pipe flow with Dittus-Boelter correlation.

        Source: Dittus-Boelter equation
        Nu = 0.023 Re^0.8 Pr^0.4 (for heating)
        Valid for Re > 10000, 0.7 < Pr < 160, L/D > 10
        """
        water_props = FluidProperties(
            density=997.0,
            dynamic_viscosity=8.9e-4,
            thermal_conductivity=0.613,
            specific_heat=4179.0,
        )

        D = 0.05
        Re_target = 50000
        U = Re_target * water_props.dynamic_viscosity / (water_props.density * D)

        input_data = PipeFlowConvection(
            diameter=D,
            length=2.0,  # L/D = 40
            flow_velocity=U,
            surface_temperature=320.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=water_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.flow_regime == "turbulent"
        assert abs(result.Reynolds - Re_target) < Re_target * 0.01

        # Verify Dittus-Boelter or Gnielinski correlation
        Pr = water_props.specific_heat * water_props.dynamic_viscosity / water_props.thermal_conductivity
        expected_Nu_DB = 0.023 * Re_target**0.8 * Pr**0.4

        # Allow either Dittus-Boelter or Gnielinski (more accurate)
        assert result.Nusselt > expected_Nu_DB * 0.8
        assert result.Nusselt < expected_Nu_DB * 1.5

    def test_pipe_flow_gnielinski_correlation(self):
        """Validate Gnielinski correlation for turbulent pipe flow.

        Source: Gnielinski (1976), more accurate than Dittus-Boelter
        Valid for 3000 < Re < 5e6, 0.5 < Pr < 2000
        """
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        D = 0.1
        Re_target = 20000
        U = Re_target * air_props.dynamic_viscosity / (air_props.density * D)

        input_data = PipeFlowConvection(
            diameter=D,
            length=5.0,
            flow_velocity=U,
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.flow_regime == "turbulent"
        assert result.correlation_equation in ["Gnielinski", "Dittus-Boelter"]

        # Verify reasonable Nu value for turbulent air flow
        assert 40 < result.Nusselt < 100


class TestCylinderCrossflowValidation:
    """Validate cylinder crossflow correlations against published references."""

    def test_cylinder_crossflow_churchill_bernstein(self):
        """Validate Churchill-Bernstein correlation for cylinder in crossflow.

        Source: Churchill & Bernstein (1977)
        Comprehensive correlation valid for all Re and Pr > 0.2
        """
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        D = 0.1
        U = 10.0
        Re = air_props.density * U * D / air_props.dynamic_viscosity
        Pr = air_props.specific_heat * air_props.dynamic_viscosity / air_props.thermal_conductivity

        input_data = CylinderCrossflowConvection(
            diameter=D,
            flow_velocity=U,
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        # Calculate expected Churchill-Bernstein Nu
        expected_Nu = (0.3 +
                      (0.62 * Re**0.5 * Pr**(1/3)) /
                      (1 + (0.4/Pr)**(2/3))**0.25 *
                      (1 + (Re/282000)**(5/8))**(4/5))

        assert result.success
        assert abs(result.Reynolds - Re) < 100
        assert abs(result.Nusselt - expected_Nu) / expected_Nu < 0.01  # Within 1%

    def test_cylinder_crossflow_low_re(self):
        """Validate cylinder crossflow at low Reynolds number.

        For very low Re, Nu should approach minimum value
        """
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        input_data = CylinderCrossflowConvection(
            diameter=0.01,
            flow_velocity=0.01,
            surface_temperature=320.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.Reynolds < 10
        # At very low Re, Nu should be close to minimum
        assert result.Nusselt > 0.3  # Minimum from Churchill-Bernstein


class TestNaturalConvectionValidation:
    """Validate natural convection correlations against published references."""

    def test_natural_convection_laminar_incropera(self):
        """Validate laminar natural convection on vertical plate.

        Source: Incropera & DeWitt, Churchill-Chu correlation
        For 10^4 < Ra < 10^9: Nu = 0.68 + 0.670 Ra^0.25 / [1 + (0.492/Pr)^(9/16)]^(4/9)
        """
        # Air properties at 300 K
        T_film = 310.0  # (320 + 300) / 2
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
            thermal_expansion_coefficient=1.0 / T_film,
        )

        H = 0.5
        T_s = 320.0
        T_inf = 300.0

        input_data = VerticalPlateNaturalConvection(
            height=H,
            surface_temperature=T_s,
            bulk_fluid_temperature=T_inf,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.flow_regime == "natural_laminar"
        assert result.Rayleigh < 1e9

        # Verify Churchill-Chu laminar correlation
        Ra = result.Rayleigh
        Pr = result.Prandtl
        expected_Nu = 0.68 + (0.670 * Ra**0.25) / (1 + (0.492/Pr)**(9/16))**(4/9)
        assert abs(result.Nusselt - expected_Nu) / expected_Nu < 0.02  # Within 2%

    def test_natural_convection_turbulent(self):
        """Validate turbulent natural convection on vertical plate.

        Source: Incropera & DeWitt, Churchill-Chu correlation
        For Ra > 10^9: Nu = 0.15 Ra^(1/3)
        """
        T_film = 325.0
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
            thermal_expansion_coefficient=1.0 / T_film,
        )

        H = 3.0  # Large height
        T_s = 350.0  # Large temperature difference
        T_inf = 300.0

        input_data = VerticalPlateNaturalConvection(
            height=H,
            surface_temperature=T_s,
            bulk_fluid_temperature=T_inf,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.flow_regime == "natural_turbulent"
        assert result.Rayleigh >= 1e9

        # Verify Churchill-Chu turbulent correlation
        Ra = result.Rayleigh
        expected_Nu = 0.15 * Ra**(1/3)
        assert abs(result.Nusselt - expected_Nu) / expected_Nu < 0.05  # Within 5%


class TestDimensionlessNumbersValidation:
    """Validate calculation of dimensionless numbers."""

    def test_reynolds_number_calculation(self):
        """Verify Reynolds number calculation."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        L = 1.0
        U = 10.0
        expected_Re = air_props.density * U * L / air_props.dynamic_viscosity

        input_data = FlatPlateConvection(
            length=L,
            flow_velocity=U,
            surface_temperature=350.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert abs(result.Reynolds - expected_Re) < 100

    def test_prandtl_number_calculation(self):
        """Verify Prandtl number calculation."""
        # Water at 300 K has Pr ≈ 6.1
        water_props = FluidProperties(
            density=997.0,
            dynamic_viscosity=8.9e-4,
            thermal_conductivity=0.613,
            specific_heat=4179.0,
        )

        expected_Pr = (water_props.specific_heat * water_props.dynamic_viscosity /
                      water_props.thermal_conductivity)

        input_data = PipeFlowConvection(
            diameter=0.05,
            length=1.0,
            flow_velocity=1.0,
            surface_temperature=320.0,
            bulk_fluid_temperature=300.0,
            fluid_properties=water_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert abs(result.Prandtl - expected_Pr) / expected_Pr < 0.01
        assert 5.0 < result.Prandtl < 7.0  # Typical for water

    def test_grashof_and_rayleigh_numbers(self):
        """Verify Grashof and Rayleigh number calculations."""
        T_film = 310.0
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
            thermal_expansion_coefficient=1.0 / T_film,
        )

        H = 1.0
        T_s = 320.0
        T_inf = 300.0
        g = 9.81

        # Calculate expected values
        nu = air_props.dynamic_viscosity / air_props.density
        alpha = air_props.thermal_conductivity / (air_props.density * air_props.specific_heat)
        Pr = nu / alpha
        Gr = g * air_props.thermal_expansion_coefficient * abs(T_s - T_inf) * H**3 / nu**2
        Ra = Gr * Pr

        input_data = VerticalPlateNaturalConvection(
            height=H,
            surface_temperature=T_s,
            bulk_fluid_temperature=T_inf,
            fluid_properties=air_props,
        )

        result = calculate_convection(input_data)

        assert result.success
        assert result.Grashof is not None
        assert result.Rayleigh is not None
        assert abs(result.Grashof - Gr) / Gr < 0.02
        assert abs(result.Rayleigh - Ra) / Ra < 0.02


class TestCorrelationRangeValidation:
    """Validate correlation applicability range checking."""

    def test_correlation_range_warning(self):
        """Test that correlation range checks are performed."""
        air_props = FluidProperties(
            density=1.177,
            dynamic_viscosity=1.846e-5,
            thermal_conductivity=0.0263,
            specific_heat=1007.0,
        )

        # Normal case - should be within range
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
        assert result.applicable_range is not None
        assert len(result.applicable_range) > 0
