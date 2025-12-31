"""Logging configuration for IAPWS-IF97 library.

Provides DEBUG-level logging for:
- Region assignment
- Convergence information for saturation calculations
- Numerical stability checks
- Performance diagnostics

Users can enable logging by setting the logging level:
    import logging
    logging.basicConfig(level=logging.DEBUG)
"""

import logging

# Create logger for this package
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler with formatter
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler.setFormatter(formatter)

# Add handler to logger (only if not already added)
if not logger.handlers:
    logger.addHandler(console_handler)


def log_region_assignment(
    pressure_pa: float, temperature_k: float, region_name: str, diagnostic: str = ""
):
    """Log region assignment decision.

    Args:
        pressure_pa: Pressure in Pa
        temperature_k: Temperature in K
        region_name: Assigned region name (Region1, Region2, Region3, Saturation)
        diagnostic: Optional diagnostic information
    """
    logger.debug(
        f"Region assignment: P={pressure_pa / 1e6:.4f} MPa, T={temperature_k:.2f} K → {region_name} {diagnostic}"
    )


def log_convergence(method: str, iterations: int, final_error: float, converged: bool):
    """Log convergence information for iterative calculations.

    Args:
        method: Name of the method (e.g., "T_sat", "P_sat")
        iterations: Number of iterations taken
        final_error: Final residual error
        converged: Whether convergence was achieved
    """
    status = "CONVERGED" if converged else "FAILED"
    logger.debug(
        f"{method}: {status} after {iterations} iterations, final error = {final_error:.2e}"
    )


def log_singularity_check(
    pressure_pa: float, temperature_k: float, distance_from_critical: float, within_threshold: bool
):
    """Log singularity proximity check near critical point.

    Args:
        pressure_pa: Pressure in Pa
        temperature_k: Temperature in K
        distance_from_critical: Normalized distance from critical point
        within_threshold: Whether within singularity threshold
    """
    status = "WITHIN THRESHOLD" if within_threshold else "SAFE"
    logger.debug(
        f"Singularity check: P={pressure_pa / 1e6:.4f} MPa, T={temperature_k:.2f} K, "
        f"distance={distance_from_critical:.2%}, status={status}"
    )


def log_property_calculation(region: str, property_name: str, value: float, units: str):
    """Log calculated property value.

    Args:
        region: Region name
        property_name: Name of the property (h, s, u, rho)
        value: Calculated value
        units: Units of the value
    """
    logger.debug(f"{region} calculation: {property_name} = {value:.6f} {units}")


def log_performance(operation: str, duration_ms: float):
    """Log performance metrics.

    Args:
        operation: Description of the operation
        duration_ms: Duration in milliseconds
    """
    logger.debug(f"Performance: {operation} took {duration_ms:.3f} ms")


def log_input_validation(
    parameter_name: str, value: float, valid_min: float, valid_max: float, is_valid: bool
):
    """Log input validation results.

    Args:
        parameter_name: Name of the parameter being validated
        value: Parameter value
        valid_min: Minimum valid value
        valid_max: Maximum valid value
        is_valid: Whether the value is valid
    """
    status = "VALID" if is_valid else "INVALID"
    logger.debug(
        f"Input validation: {parameter_name} = {value:.2e}, "
        f"range=[{valid_min:.2e}, {valid_max:.2e}], status={status}"
    )


# Example usage documentation
__doc_examples__ = """
# Enable logging in your application:

import logging
from iapws_if97 import SteamTable

# Configure logging at DEBUG level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now all library operations will log diagnostic information
steam = SteamTable()
h = steam.h_pt(10 * ureg.MPa, 500 * ureg.K)

# Example output:
# 2025-12-30 12:00:00 - iapws_if97.logging_config - DEBUG - Region assignment: P=10.0000 MPa, T=500.00 K → Region1
# 2025-12-30 12:00:00 - iapws_if97.logging_config - DEBUG - Region1 calculation: h = 975.123456 kJ/kg
"""
