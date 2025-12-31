"""
Core fluid mechanics calculations for engineering design.

This module provides:
- Pipe flow analysis (Reynolds number, friction factor, pressure drop)
- Pump sizing (head, power, NPSH calculations)
- Valve sizing (Cv calculations, flow coefficients)

All calculations use SI units with Pint for dimensional analysis and validation.
"""

from fluids.pipe import (
    calculate_friction_factor,
    calculate_pressure_drop,
    calculate_reynolds,
)
from fluids.pump import (
    calculate_brake_power,
    calculate_dynamic_head,
    calculate_hydraulic_power,
    calculate_motor_power,
    calculate_npsh_available,
    calculate_npsh_required,
    calculate_static_head,
    calculate_total_head,
    check_cavitation_risk,
)
from fluids.valve import (
    assess_valve_performance,
    calculate_cv_required,
    calculate_flow_rate_through_valve,
    calculate_relative_flow_capacity,
    calculate_valve_authority,
    calculate_valve_rangeability,
    calculate_valve_sizing,
)

__version__ = "0.1.0"

__all__ = [
    # Pipe flow functions
    "calculate_reynolds",
    "calculate_friction_factor",
    "calculate_pressure_drop",
    # Pump sizing functions - Head
    "calculate_total_head",
    "calculate_static_head",
    "calculate_dynamic_head",
    # Pump sizing functions - Power
    "calculate_hydraulic_power",
    "calculate_brake_power",
    "calculate_motor_power",
    # Pump sizing functions - NPSH
    "calculate_npsh_available",
    "calculate_npsh_required",
    "check_cavitation_risk",
    # Valve sizing functions - Cv and Flow
    "calculate_cv_required",
    "calculate_flow_rate_through_valve",
    "calculate_valve_sizing",
    # Valve performance functions
    "calculate_valve_authority",
    "calculate_valve_rangeability",
    "calculate_relative_flow_capacity",
    "assess_valve_performance",
]
