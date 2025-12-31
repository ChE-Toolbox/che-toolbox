"""Utility functions for IAPWS-IF97 calculations.

Provides polynomial evaluation, numerical helpers, and common mathematical
operations used across region calculations.
"""


import numpy as np


def horner_polynomial(coefficients: list[float], x: float) -> float:
    """Evaluate polynomial using Horner's method.

    Evaluates polynomial: a[0] + a[1]*x + a[2]*x^2 + ... + a[n]*x^n
    Using Horner's method for numerical stability: a[0] + x*(a[1] + x*(a[2] + ...))

    Args:
        coefficients: List of polynomial coefficients [a0, a1, a2, ..., an]
        x: Evaluation point

    Returns:
        Polynomial value at x
    """
    result = 0.0
    for coeff in reversed(coefficients):
        result = result * x + coeff
    return result


def multidimensional_polynomial(
    coefficients: np.ndarray,
    x: float,
    y: float,
) -> float:
    """Evaluate 2D polynomial in x and y.

    Evaluates polynomial of form: sum(c_ij * x^i * y^j)
    where c_ij are coefficients arranged in matrix form.

    Args:
        coefficients: 2D array of coefficients indexed by (power_of_x, power_of_y)
        x: First variable
        y: Second variable

    Returns:
        Polynomial value
    """
    result = 0.0
    for i, row in enumerate(coefficients):
        for j, coeff in enumerate(row):
            result += coeff * (x**i) * (y**j)
    return result


def dimensionless_pi(pressure_pa: float, reference_pressure_pa: float) -> float:
    """Calculate dimensionless pressure (pi).

    Used in IAPWS-IF97 equations where pressure is normalized by reference.

    Args:
        pressure_pa: Pressure in Pa
        reference_pressure_pa: Reference pressure in Pa (typically 16.53 MPa or 1 MPa)

    Returns:
        Dimensionless pressure pi = P / P_ref
    """
    return pressure_pa / reference_pressure_pa


def dimensionless_tau(temperature_k: float, reference_temperature_k: float) -> float:
    """Calculate dimensionless temperature (tau).

    Used in IAPWS-IF97 equations where temperature is normalized by reference.

    Args:
        temperature_k: Temperature in Kelvin
        reference_temperature_k: Reference temperature in K (typically 1386 K or 647.096 K)

    Returns:
        Dimensionless temperature tau = T_ref / T
    """
    return reference_temperature_k / temperature_k


def inverse_tau(tau: float, reference_temperature_k: float) -> float:
    """Convert dimensionless tau back to temperature.

    Args:
        tau: Dimensionless temperature tau = T_ref / T
        reference_temperature_k: Reference temperature in K

    Returns:
        Temperature in Kelvin
    """
    if tau == 0:
        raise ValueError("tau must be non-zero")
    return reference_temperature_k / tau


def safe_power(base: float, exponent: float) -> float:
    """Safely compute x^y with bounds checking.

    Handles edge cases like 0^0 and prevents overflow/underflow.

    Args:
        base: Base value
        exponent: Exponent

    Returns:
        Result of base^exponent
    """
    if base == 0 and exponent == 0:
        return 1.0  # Convention: 0^0 = 1
    if base == 0 and exponent < 0:
        raise ValueError("Cannot raise 0 to negative power")
    if base < 0 and not float(exponent).is_integer():
        raise ValueError("Cannot raise negative number to fractional power")

    try:
        return float(base**exponent)
    except (OverflowError, ValueError) as e:
        raise ArithmeticError(f"Error computing {base}^{exponent}: {e}")


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range [min_val, max_val].

    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def normalize_array(arr: np.ndarray) -> np.ndarray:
    """Normalize NumPy array to [0, 1] range.

    Args:
        arr: Input array

    Returns:
        Normalized array (arr - min) / (max - min)
    """
    arr_min = np.min(arr)
    arr_max = np.max(arr)
    if arr_max == arr_min:
        return np.zeros_like(arr)
    return (arr - arr_min) / (arr_max - arr_min)
