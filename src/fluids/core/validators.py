"""
Input validation and physical reasonableness checks for calculations.
"""



class ValidationError(Exception):
    """Raised when validation fails."""

    pass


def validate_reynolds_components(
    density: float,
    velocity: float,
    diameter: float,
    viscosity: float,
) -> tuple[bool, str | None]:
    """
    Validate Reynolds number calculation inputs.

    Args:
        density: Fluid density in kg/m³
        velocity: Flow velocity in m/s
        diameter: Characteristic diameter in m
        viscosity: Dynamic viscosity in Pa·s

    Returns:
        Tuple of (is_valid, error_message)
    """
    if density <= 0:
        return False, "Density must be positive"
    if velocity < 0:
        return False, "Velocity must be non-negative"
    if diameter <= 0:
        return False, "Diameter must be positive"
    if viscosity <= 0:
        return False, "Viscosity must be positive"

    return True, None


def validate_flow_regime(reynolds_number: float) -> tuple[str, str | None]:
    """
    Classify flow regime and return warning if in transitional zone.

    Args:
        reynolds_number: Calculated Reynolds number

    Returns:
        Tuple of (regime, warning_message)
        regime: 'laminar', 'transitional', or 'turbulent'
        warning_message: None or warning string if in transitional zone
    """
    if reynolds_number < 2300:
        return "laminar", None
    elif reynolds_number <= 4000:
        return "transitional", (
            f"Reynolds {reynolds_number:.0f} in transitional zone (2300-4000). "
            "Using laminar friction factor as conservative estimate."
        )
    else:
        return "turbulent", None


def validate_pipe_geometry(
    diameter: float, length: float, roughness: float
) -> tuple[bool, str | None]:
    """
    Validate pipe geometry parameters.

    Args:
        diameter: Pipe diameter in m
        length: Pipe length in m
        roughness: Absolute roughness in m

    Returns:
        Tuple of (is_valid, error_message)
    """
    if diameter <= 0:
        return False, "Pipe diameter must be positive"
    if length <= 0:
        return False, "Pipe length must be positive"
    if roughness < 0:
        return False, "Absolute roughness cannot be negative"
    if roughness > diameter:
        return False, "Roughness cannot exceed pipe diameter"

    return True, None


def validate_pressure_drop_inputs(
    friction_factor: float,
    length: float,
    diameter: float,
    velocity: float,
    density: float,
) -> tuple[bool, str | None]:
    """
    Validate Darcy-Weisbach pressure drop inputs.

    Args:
        friction_factor: Dimensionless friction factor
        length: Pipe length in m
        diameter: Pipe diameter in m
        velocity: Flow velocity in m/s
        density: Fluid density in kg/m³

    Returns:
        Tuple of (is_valid, error_message)
    """
    if friction_factor <= 0:
        return False, "Friction factor must be positive"
    if length <= 0:
        return False, "Pipe length must be positive"
    if diameter <= 0:
        return False, "Pipe diameter must be positive"
    if velocity < 0:
        return False, "Velocity must be non-negative"
    if density <= 0:
        return False, "Density must be positive"

    return True, None


def validate_pump_head(
    static_head: float, dynamic_head: float, friction_losses: float
) -> tuple[bool, str | None]:
    """
    Validate pump head calculation inputs.

    Args:
        static_head: Static head in m
        dynamic_head: Dynamic head in m
        friction_losses: Friction losses in m

    Returns:
        Tuple of (is_valid, error_message)
    """
    if static_head < 0:
        return False, "Static head cannot be negative"
    if dynamic_head < 0:
        return False, "Dynamic head cannot be negative"
    if friction_losses < 0:
        return False, "Friction losses cannot be negative"

    return True, None


def validate_pump_power(
    flow_rate: float,
    density: float,
    head: float,
    efficiency: float,
) -> tuple[bool, str | None]:
    """
    Validate pump power calculation inputs.

    Args:
        flow_rate: Volumetric flow rate in m³/s
        density: Fluid density in kg/m³
        head: Pump head in m
        efficiency: Pump efficiency (0-1)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if flow_rate <= 0:
        return False, "Flow rate must be positive"
    if density <= 0:
        return False, "Density must be positive"
    if head < 0:
        return False, "Head cannot be negative"
    if efficiency <= 0 or efficiency > 1:
        return False, "Efficiency must be between 0 and 1"

    return True, None


def validate_valve_cv(
    flow_rate: float,
    pressure_drop: float,
    specific_gravity: float,
) -> tuple[bool, str | None]:
    """
    Validate valve Cv calculation inputs.

    Args:
        flow_rate: Volumetric flow rate in m³/s
        pressure_drop: Pressure drop across valve in Pa
        specific_gravity: Fluid specific gravity (dimensionless)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if flow_rate <= 0:
        return False, "Flow rate must be positive"
    if pressure_drop <= 0:
        return False, "Pressure drop must be positive"
    if specific_gravity <= 0:
        return False, "Specific gravity must be positive"

    return True, None


def validate_unit_system(unit_system: str) -> tuple[bool, str | None]:
    """
    Validate unit system specification.

    Args:
        unit_system: Unit system ('SI' or 'US')

    Returns:
        Tuple of (is_valid, error_message)
    """
    if unit_system not in ("SI", "US"):
        return False, f"Unknown unit system '{unit_system}'. Use 'SI' or 'US'."

    return True, None
