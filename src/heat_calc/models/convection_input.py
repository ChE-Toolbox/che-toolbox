"""Input models for convection heat transfer calculations.

Defines Pydantic models for calculating convection coefficients for various
geometries and flow regimes.
"""

from typing import Literal

from pydantic import BaseModel, Field

from heat_calc.models.base import BaseCalculationInput


class FluidProperties(BaseModel):
    """Thermal and transport properties for convection calculations.

    Attributes
    ----------
    density : float
        Fluid density in kg/m³.
    dynamic_viscosity : float
        Dynamic viscosity in Pa·s.
    thermal_conductivity : float
        Thermal conductivity in W/(m·K).
    specific_heat : float
        Specific heat capacity in J/(kg·K).
    thermal_expansion_coefficient : float, optional
        Volumetric thermal expansion coefficient in 1/K.
        Required only for natural convection calculations.
    """

    model_config = {"arbitrary_types_allowed": True}

    density: float = Field(
        ...,
        description="Fluid density in kg/m³",
        gt=0,
        json_schema_extra={"unit": "kg/m³", "example": 1.2},
    )

    dynamic_viscosity: float = Field(
        ...,
        description="Dynamic viscosity in Pa·s",
        gt=0,
        json_schema_extra={"unit": "Pa·s", "example": 1.8e-5},
    )

    thermal_conductivity: float = Field(
        ...,
        description="Thermal conductivity in W/(m·K)",
        gt=0,
        json_schema_extra={"unit": "W/(m·K)", "example": 0.026},
    )

    specific_heat: float = Field(
        ...,
        description="Specific heat capacity in J/(kg·K)",
        gt=0,
        json_schema_extra={"unit": "J/(kg·K)", "example": 1005.0},
    )

    thermal_expansion_coefficient: float | None = Field(
        default=None,
        description="Volumetric thermal expansion coefficient in 1/K (for natural convection)",
        gt=0,
        json_schema_extra={"unit": "1/K", "example": 0.00333},
    )


class FlatPlateConvection(BaseCalculationInput):
    """Forced convection over a flat plate.

    Supports both laminar and turbulent flow regimes. The flow regime is
    determined automatically based on Reynolds number.

    Attributes
    ----------
    geometry_type : str
        Must be "flat_plate".
    length : float
        Characteristic length (plate length) in meters.
    flow_velocity : float
        Free stream velocity in m/s.
    surface_temperature : float
        Plate surface temperature in Kelvin.
    bulk_fluid_temperature : float
        Free stream fluid temperature in Kelvin.
    fluid_properties : FluidProperties
        Thermal and transport properties of the fluid.
    roughness : float, optional
        Relative surface roughness (dimensionless). Default is 0.0 (smooth).
    """

    model_config = {"arbitrary_types_allowed": True}

    geometry_type: Literal["flat_plate"] = Field(
        default="flat_plate",
        description="Geometry type identifier",
    )

    length: float = Field(
        ...,
        description="Characteristic length (plate length) in meters",
        gt=0,
        json_schema_extra={"unit": "m", "example": 1.0},
    )

    flow_velocity: float = Field(
        ...,
        description="Free stream velocity in m/s",
        gt=0,
        json_schema_extra={"unit": "m/s", "example": 5.0},
    )

    surface_temperature: float = Field(
        ...,
        description="Plate surface temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 350.0},
    )

    bulk_fluid_temperature: float = Field(
        ...,
        description="Free stream fluid temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 300.0},
    )

    fluid_properties: FluidProperties = Field(
        ...,
        description="Thermal and transport properties of the fluid",
    )

    roughness: float = Field(
        default=0.0,
        description="Relative surface roughness (dimensionless)",
        ge=0,
        json_schema_extra={"unit": "-", "example": 0.0},
    )


class PipeFlowConvection(BaseCalculationInput):
    """Forced convection in pipe flow.

    Uses Dittus-Boelter or Gnielinski correlation depending on flow regime.

    Attributes
    ----------
    geometry_type : str
        Must be "pipe_flow".
    diameter : float
        Pipe inner diameter in meters.
    length : float
        Pipe length in meters.
    flow_velocity : float
        Mean flow velocity in m/s.
    surface_temperature : float
        Pipe wall temperature in Kelvin.
    bulk_fluid_temperature : float
        Bulk fluid temperature in Kelvin.
    fluid_properties : FluidProperties
        Thermal and transport properties of the fluid.
    """

    model_config = {"arbitrary_types_allowed": True}

    geometry_type: Literal["pipe_flow"] = Field(
        default="pipe_flow",
        description="Geometry type identifier",
    )

    diameter: float = Field(
        ...,
        description="Pipe inner diameter in meters",
        gt=0,
        json_schema_extra={"unit": "m", "example": 0.05},
    )

    length: float = Field(
        ...,
        description="Pipe length in meters",
        gt=0,
        json_schema_extra={"unit": "m", "example": 10.0},
    )

    flow_velocity: float = Field(
        ...,
        description="Mean flow velocity in m/s",
        gt=0,
        json_schema_extra={"unit": "m/s", "example": 2.0},
    )

    surface_temperature: float = Field(
        ...,
        description="Pipe wall temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 350.0},
    )

    bulk_fluid_temperature: float = Field(
        ...,
        description="Bulk fluid temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 300.0},
    )

    fluid_properties: FluidProperties = Field(
        ...,
        description="Thermal and transport properties of the fluid",
    )


class CylinderCrossflowConvection(BaseCalculationInput):
    """Forced convection over a cylinder in crossflow.

    Uses Churchill-Bernstein or similar correlations for external flow.

    Attributes
    ----------
    geometry_type : str
        Must be "cylinder_crossflow".
    diameter : float
        Cylinder diameter in meters.
    flow_velocity : float
        Free stream velocity in m/s.
    surface_temperature : float
        Cylinder surface temperature in Kelvin.
    bulk_fluid_temperature : float
        Free stream fluid temperature in Kelvin.
    fluid_properties : FluidProperties
        Thermal and transport properties of the fluid.
    """

    model_config = {"arbitrary_types_allowed": True}

    geometry_type: Literal["cylinder_crossflow"] = Field(
        default="cylinder_crossflow",
        description="Geometry type identifier",
    )

    diameter: float = Field(
        ...,
        description="Cylinder diameter in meters",
        gt=0,
        json_schema_extra={"unit": "m", "example": 0.1},
    )

    flow_velocity: float = Field(
        ...,
        description="Free stream velocity in m/s",
        gt=0,
        json_schema_extra={"unit": "m/s", "example": 5.0},
    )

    surface_temperature: float = Field(
        ...,
        description="Cylinder surface temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 350.0},
    )

    bulk_fluid_temperature: float = Field(
        ...,
        description="Free stream fluid temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 300.0},
    )

    fluid_properties: FluidProperties = Field(
        ...,
        description="Thermal and transport properties of the fluid",
    )


class VerticalPlateNaturalConvection(BaseCalculationInput):
    """Natural convection on a vertical plate.

    Uses Rayleigh number-based correlations for natural convection.

    Attributes
    ----------
    geometry_type : str
        Must be "vertical_plate_natural".
    height : float
        Plate height (characteristic length) in meters.
    surface_temperature : float
        Plate surface temperature in Kelvin.
    bulk_fluid_temperature : float
        Ambient fluid temperature in Kelvin.
    fluid_properties : FluidProperties
        Thermal and transport properties of the fluid.
        Must include thermal_expansion_coefficient.
    pressure : float, optional
        Ambient pressure in Pascals. Default is 101325 Pa (1 atm).
    """

    model_config = {"arbitrary_types_allowed": True}

    geometry_type: Literal["vertical_plate_natural"] = Field(
        default="vertical_plate_natural",
        description="Geometry type identifier",
    )

    height: float = Field(
        ...,
        description="Plate height (characteristic length) in meters",
        gt=0,
        json_schema_extra={"unit": "m", "example": 1.0},
    )

    surface_temperature: float = Field(
        ...,
        description="Plate surface temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 350.0},
    )

    bulk_fluid_temperature: float = Field(
        ...,
        description="Ambient fluid temperature in Kelvin",
        gt=0,
        json_schema_extra={"unit": "K", "example": 300.0},
    )

    fluid_properties: FluidProperties = Field(
        ...,
        description="Thermal and transport properties of the fluid",
    )

    pressure: float = Field(
        default=101325.0,
        description="Ambient pressure in Pascals",
        gt=0,
        json_schema_extra={"unit": "Pa", "example": 101325.0},
    )
