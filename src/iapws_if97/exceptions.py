"""Exception classes for IAPWS-IF97 steam property calculations.

Provides domain-specific exceptions with structured error messages for
input validation, numerical stability, and state errors.
"""


class SteamTableError(Exception):
    """Base exception for all IAPWS-IF97 calculations."""



class InputRangeError(ValueError, SteamTableError):
    """Raised when input pressure or temperature is outside valid range.

    Attributes:
        parameter: Name of invalid parameter ('pressure' or 'temperature')
        value: Value that was invalid
        min_value: Minimum valid value
        max_value: Maximum valid value
        message: Human-readable error message
    """

    def __init__(
        self,
        parameter: str,
        value: float,
        min_value: float,
        max_value: float,
    ) -> None:
        """Initialize InputRangeError with parameter details.

        Args:
            parameter: Name of parameter that is out of range
            value: The invalid value provided
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value
        """
        self.parameter = parameter
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        msg = (
            f"{parameter.capitalize()}: {value:.6e} outside valid range. "
            f"Valid: {min_value:.6e}–{max_value:.6e}"
        )
        super().__init__(msg)


class NumericalInstabilityError(RuntimeError, SteamTableError):
    """Raised when calculation cannot proceed due to singularity or convergence failure.

    Attributes:
        reason: Why calculation cannot proceed (e.g., "singularity", "no convergence")
        location: Where the problem occurs (e.g., "critical point")
        suggestion: User guidance (e.g., move away from critical point)
        message: Human-readable error message
    """

    def __init__(
        self,
        reason: str,
        location: str,
        suggestion: str,
    ) -> None:
        """Initialize NumericalInstabilityError with diagnostics.

        Args:
            reason: Reason for instability (e.g., "singularity")
            location: Where instability occurs
            suggestion: Recommended action to resolve
        """
        self.reason = reason
        self.location = location
        self.suggestion = suggestion
        msg = f"{reason} near {location}. Suggestion: {suggestion}"
        super().__init__(msg)


class InvalidStateError(ValueError, SteamTableError):
    """Raised when user attempts to use single-phase API on saturation line.

    Attributes:
        pressure: Input pressure
        temperature: Input temperature
        message: Guidance on correct API to use
    """

    def __init__(
        self,
        pressure: float,
        temperature: float,
    ) -> None:
        """Initialize InvalidStateError for two-phase conditions.

        Args:
            pressure: Input pressure in Pa
            temperature: Input temperature in K
        """
        self.pressure = pressure
        self.temperature = temperature
        msg = (
            f"Pressure {pressure:.6e} Pa, Temperature {temperature:.2f} K: "
            "On saturation line (two-phase region). "
            "Use T_sat(P) or P_sat(T) for saturation properties."
        )
        super().__init__(msg)
