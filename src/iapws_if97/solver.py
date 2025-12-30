"""Root-finding and optimization solvers for IAPWS-IF97.

Wraps SciPy optimization functions for finding saturation properties,
region boundaries, and solving implicit equations in thermodynamic calculations.
"""

from typing import Callable, Tuple

from scipy.optimize import brentq


def find_root_brent(
    func: Callable[[float], float],
    bracket: Tuple[float, float],
    tolerance: float = 1e-6,
    max_iter: int = 100,
) -> float:
    """Find root of function using Brent's method.

    Robust root-finding method suitable for thermodynamic equations.
    Assumes func(bracket[0]) and func(bracket[1]) have opposite signs.

    Args:
        func: Function to find root of (must have different signs at bracket endpoints)
        bracket: (a, b) tuple where func(a) and func(b) have opposite signs
        tolerance: Absolute tolerance for convergence (default 1e-6)
        max_iter: Maximum iterations (default 100)

    Returns:
        Root of func within bracket to specified tolerance

    Raises:
        ValueError: If bracket doesn't bracket a root (same sign at endpoints)
        RuntimeError: If convergence not achieved after max_iter iterations
    """
    try:
        root = brentq(func, bracket[0], bracket[1], xtol=tolerance, rtol=tolerance, maxiter=max_iter)
        return root
    except ValueError as e:
        if "f(a) and f(b) must have different signs" in str(e):
            f_a = func(bracket[0])
            f_b = func(bracket[1])
            raise ValueError(
                f"Bracket does not contain root. "
                f"func({bracket[0]}) = {f_a:.6e}, func({bracket[1]}) = {f_b:.6e}"
            )
        raise
    except RuntimeError as e:
        raise RuntimeError(f"Root-finding failed to converge after {max_iter} iterations: {e}")


def find_root_newton(
    func: Callable[[float], float],
    derivative: Callable[[float], float],
    x0: float,
    tolerance: float = 1e-6,
    max_iter: int = 100,
) -> float:
    """Find root using Newton-Raphson method (stub for future use).

    Args:
        func: Function to find root of
        derivative: Derivative of func
        x0: Initial guess
        tolerance: Absolute tolerance for convergence
        max_iter: Maximum iterations

    Returns:
        Root to specified tolerance

    Note:
        Currently a stub. SciPy's brentq is preferred for thermodynamic equations.
    """
    x = x0
    for i in range(max_iter):
        f = func(x)
        if abs(f) < tolerance:
            return x
        df = derivative(x)
        if abs(df) < 1e-14:
            raise ValueError(f"Derivative too small at iteration {i}: {df}")
        x = x - f / df

    raise RuntimeError(f"Newton-Raphson failed to converge after {max_iter} iterations")


def verify_bracket(
    func: Callable[[float], float],
    bracket: Tuple[float, float],
    name: str = "bracket",
) -> bool:
    """Verify that bracket contains a root (function has opposite signs at endpoints).

    Args:
        func: Function to check
        bracket: (a, b) tuple
        name: Name of bracket for error messages

    Returns:
        True if bracket contains a root, False otherwise
    """
    f_a = func(bracket[0])
    f_b = func(bracket[1])
    return f_a * f_b < 0


__all__ = ["find_root_brent", "find_root_newton", "verify_bracket"]
