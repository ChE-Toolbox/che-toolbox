"""
Pump power requirement calculations.

Provides calculations for:
- Hydraulic power (ideal power with no losses)
- Brake power (actual power required accounting for pump efficiency)
- Motor power (including motor efficiency)
"""

from typing import Dict, Any


def calculate_hydraulic_power(
    flow_rate: float,
    head: float,
    fluid_density: float = 1000.0,
    g: float = 9.81,
    unit_system: str = "SI",
) -> Dict[str, Any]:
    """
    Calculate hydraulic power (ideal power without losses).

    Hydraulic power is the theoretical minimum power required to move fluid
    through the system. Actual brake power will be higher due to pump inefficiency.

    Power = ρ * g * Q * H / 1000 (in kW)
    or Power = ρ * g * Q * H / 550 (in hp, for US customary)

    Parameters
    ----------
    flow_rate : float
        Volumetric flow rate in m³/s (SI) or ft³/s (US)
    head : float
        Pump head in meters (SI) or feet (US)
    fluid_density : float, optional
        Fluid density in kg/m³ (SI) or lb/ft³ (US), default 1000.0
    g : float, optional
        Gravitational acceleration, default 9.81 m/s² (SI)
    unit_system : str, optional
        Unit system: 'SI' or 'US', default 'SI'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Hydraulic power
        - 'unit': Unit of power measurement ('kW' for SI, 'hp' for US)
        - 'formula_used': Description of calculation method
        - 'warnings': List of warnings if any
        - 'intermediate_values': Dict of intermediate values
        - 'source': Reference information

    Raises
    ------
    ValueError
        If any required input is invalid
    """
    from fluids.core.validators import validate_unit_system

    is_valid, error_msg = validate_unit_system(unit_system)
    if not is_valid:
        raise ValueError(error_msg)

    if flow_rate < 0:
        raise ValueError("Flow rate cannot be negative")
    if head < 0:
        raise ValueError("Head cannot be negative")
    if fluid_density <= 0:
        raise ValueError("Fluid density must be positive")

    warnings = []

    if flow_rate == 0:
        warnings.append("Zero flow rate: hydraulic power is zero")
        return {
            "value": 0.0,
            "unit": "kW" if unit_system == "SI" else "hp",
            "formula_used": "P_hydraulic = ρ * g * Q * H / conversion_factor",
            "warnings": warnings,
            "intermediate_values": {
                "flow_rate": flow_rate,
                "head": head,
                "density": fluid_density,
            },
            "source": "Hydraulic power calculation",
        }

    if head == 0:
        warnings.append("Zero head: hydraulic power is zero")
        return {
            "value": 0.0,
            "unit": "kW" if unit_system == "SI" else "hp",
            "formula_used": "P_hydraulic = ρ * g * Q * H / conversion_factor",
            "warnings": warnings,
            "intermediate_values": {
                "flow_rate": flow_rate,
                "head": head,
                "density": fluid_density,
            },
            "source": "Hydraulic power calculation",
        }

    # Calculate hydraulic power
    if unit_system == "SI":
        # Power = ρ * g * Q * H / 1000 (kW)
        power = (fluid_density * g * flow_rate * head) / 1000.0
        unit = "kW"
        conversion = 1000.0
    else:  # US customary
        # Power = ρ * g * Q * H / 550 (hp)
        # With ρ in lb/ft³, g = 32.174 ft/s², Q in ft³/s, H in ft
        # But we use a conversion constant
        power = (fluid_density * 32.174 * flow_rate * head) / 550.0
        unit = "hp"
        conversion = 550.0

    return {
        "value": power,
        "unit": unit,
        "formula_used": f"P_hydraulic = ρ * g * Q * H / {conversion}",
        "warnings": warnings,
        "intermediate_values": {
            "flow_rate": flow_rate,
            "head": head,
            "fluid_density": fluid_density,
            "gravitational_acceleration": g,
        },
        "source": "Hydraulic power calculation (ideal power)",
    }


def calculate_brake_power(
    flow_rate: float,
    head: float,
    pump_efficiency: float,
    fluid_density: float = 1000.0,
    g: float = 9.81,
    unit_system: str = "SI",
) -> Dict[str, Any]:
    """
    Calculate brake power (actual power required from pump).

    Brake power accounts for pump inefficiency.
    P_brake = P_hydraulic / η_pump

    Parameters
    ----------
    flow_rate : float
        Volumetric flow rate in m³/s (SI) or ft³/s (US)
    head : float
        Pump head in meters (SI) or feet (US)
    pump_efficiency : float
        Pump efficiency as fraction (0 < η ≤ 1)
    fluid_density : float, optional
        Fluid density in kg/m³ (SI) or lb/ft³ (US), default 1000.0
    g : float, optional
        Gravitational acceleration, default 9.81 m/s²
    unit_system : str, optional
        Unit system: 'SI' or 'US', default 'SI'

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Brake power
        - 'unit': Unit of power measurement
        - 'hydraulic_power': Ideal power without losses
        - 'pump_efficiency': Input efficiency
        - 'formula_used': Description of calculation
        - 'warnings': List of warnings if any
        - 'source': Reference information

    Raises
    ------
    ValueError
        If any required input is invalid
    """
    from fluids.core.validators import validate_unit_system

    is_valid, error_msg = validate_unit_system(unit_system)
    if not is_valid:
        raise ValueError(error_msg)

    if pump_efficiency <= 0 or pump_efficiency > 1:
        raise ValueError("Pump efficiency must be between 0 and 1")

    # Calculate hydraulic power first
    hydraulic_result = calculate_hydraulic_power(
        flow_rate, head, fluid_density, g, unit_system
    )
    hydraulic_power = hydraulic_result["value"]

    warnings = []
    if pump_efficiency < 0.5:
        warnings.append(
            f"Pump efficiency {pump_efficiency:.2%} is unusually low; verify input"
        )
    if pump_efficiency > 0.95:
        warnings.append(
            f"Pump efficiency {pump_efficiency:.2%} is very high; verify input"
        )

    # Calculate brake power
    brake_power = hydraulic_power / pump_efficiency

    return {
        "value": brake_power,
        "unit": hydraulic_result["unit"],
        "hydraulic_power": hydraulic_power,
        "pump_efficiency": pump_efficiency,
        "power_loss": brake_power - hydraulic_power,
        "formula_used": f"P_brake = P_hydraulic / η_pump",
        "warnings": warnings,
        "intermediate_values": {
            "flow_rate": flow_rate,
            "head": head,
            "pump_efficiency": pump_efficiency,
            "fluid_density": fluid_density,
        },
        "source": "Brake power calculation (actual pump power)",
    }


def calculate_motor_power(
    brake_power: float,
    motor_efficiency: float = 0.95,
) -> Dict[str, Any]:
    """
    Calculate motor power (electrical power input to motor).

    Motor power accounts for motor losses.
    P_motor = P_brake / η_motor

    Parameters
    ----------
    brake_power : float
        Brake power (mechanical power output from motor) in kW or hp
    motor_efficiency : float, optional
        Motor efficiency as fraction (0 < η ≤ 1), default 0.95

    Returns
    -------
    dict
        Result dictionary with keys:
        - 'value': Motor electrical power
        - 'unit': Unit of power (same as input brake_power unit)
        - 'brake_power': Input brake power
        - 'motor_efficiency': Input efficiency
        - 'power_loss': Power lost in motor
        - 'formula_used': Description of calculation
        - 'warnings': List of warnings if any
        - 'source': Reference information

    Raises
    ------
    ValueError
        If any required input is invalid
    """
    if brake_power < 0:
        raise ValueError("Brake power cannot be negative")
    if motor_efficiency <= 0 or motor_efficiency > 1:
        raise ValueError("Motor efficiency must be between 0 and 1")

    warnings = []
    if motor_efficiency < 0.85:
        warnings.append(
            f"Motor efficiency {motor_efficiency:.2%} is unusually low; verify input"
        )
    if brake_power == 0:
        warnings.append("Zero brake power: motor power is zero")

    # Calculate motor power
    motor_power = brake_power / motor_efficiency
    power_loss = motor_power - brake_power

    return {
        "value": motor_power,
        "unit": "kW or hp (same as brake_power input)",
        "brake_power": brake_power,
        "motor_efficiency": motor_efficiency,
        "power_loss": power_loss,
        "efficiency_percentage": f"{motor_efficiency * 100:.1f}%",
        "formula_used": "P_motor = P_brake / η_motor",
        "warnings": warnings,
        "source": "Motor power calculation (electrical power input)",
    }
