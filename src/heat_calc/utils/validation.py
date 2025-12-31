"""Input validation helpers for heat exchanger calculations."""

import math

from pint import Quantity


def validate_temperature(value: float | Quantity, param_name: str = "temperature") -> float:
    """Validate and convert temperature to Kelvin.

    Parameters
    ----------
    value : Union[float, Quantity]
        Temperature value with or without units (Pint Quantity).
    param_name : str
        Name of parameter for error messages.

    Returns
    -------
    float
        Temperature in Kelvin.

    Raises
    ------
    ValueError
        If temperature is invalid (NaN, Inf, below 0 K).
    TypeError
        If value type is unsupported.
    """
    if isinstance(value, Quantity):
        temp_k = value.to("kelvin").magnitude
    elif isinstance(value, (int, float)):
        temp_k = float(value)
    else:
        raise TypeError(f"{param_name} must be float or Pint Quantity, got {type(value)}")

    if math.isnan(temp_k) or math.isinf(temp_k):
        raise ValueError(f"{param_name} cannot be NaN or Inf")

    if temp_k < 0:
        raise ValueError(f"{param_name} must be >= 0 K, got {temp_k} K")

    return temp_k


def validate_pressure(value: float | Quantity, param_name: str = "pressure") -> float:
    """Validate and convert pressure to Pascal.

    Parameters
    ----------
    value : Union[float, Quantity]
        Pressure value with or without units (Pint Quantity).
    param_name : str
        Name of parameter for error messages.

    Returns
    -------
    float
        Pressure in Pascal.

    Raises
    ------
    ValueError
        If pressure is invalid (NaN, Inf, negative).
    TypeError
        If value type is unsupported.
    """
    if isinstance(value, Quantity):
        pressure_pa = value.to("pascal").magnitude
    elif isinstance(value, (int, float)):
        pressure_pa = float(value)
    else:
        raise TypeError(f"{param_name} must be float or Pint Quantity, got {type(value)}")

    if math.isnan(pressure_pa) or math.isinf(pressure_pa):
        raise ValueError(f"{param_name} cannot be NaN or Inf")

    if pressure_pa < 0:
        raise ValueError(f"{param_name} must be >= 0 Pa, got {pressure_pa} Pa")

    return pressure_pa


def validate_positive_float(value: float, param_name: str, allow_zero: bool = False) -> float:
    """Validate that a float is positive (optionally allow zero).

    Parameters
    ----------
    value : float
        The value to validate.
    param_name : str
        Name of parameter for error messages.
    allow_zero : bool
        If True, allows value == 0; otherwise requires value > 0.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    ValueError
        If value is invalid (NaN, Inf, or not positive).
    TypeError
        If value is not numeric.
    """
    try:
        val = float(value)
    except (TypeError, ValueError) as e:
        raise TypeError(f"{param_name} must be numeric, got {type(value)}") from e

    if math.isnan(val) or math.isinf(val):
        raise ValueError(f"{param_name} cannot be NaN or Inf")

    if allow_zero:
        if val < 0:
            raise ValueError(f"{param_name} must be >= 0, got {val}")
    else:
        if val <= 0:
            raise ValueError(f"{param_name} must be > 0, got {val}")

    return val


def validate_range(value: float, min_val: float, max_val: float, param_name: str) -> float:
    """Validate that a value is within a specified range.

    Parameters
    ----------
    value : float
        The value to validate.
    min_val : float
        Minimum allowed value (inclusive).
    max_val : float
        Maximum allowed value (inclusive).
    param_name : str
        Name of parameter for error messages.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    ValueError
        If value is outside the range.
    """
    if not (min_val <= value <= max_val):
        raise ValueError(f"{param_name} must be between {min_val} and {max_val}, got {value}")
    return value


def check_nan_inf(value: float, param_name: str) -> None:
    """Check that a float is neither NaN nor Inf.

    Parameters
    ----------
    value : float
        The value to check.
    param_name : str
        Name of parameter for error messages.

    Raises
    ------
    ValueError
        If value is NaN or Inf.
    """
    if math.isnan(value):
        raise ValueError(f"{param_name} is NaN")
    if math.isinf(value):
        raise ValueError(f"{param_name} is Inf")
