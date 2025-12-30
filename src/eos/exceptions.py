"""Custom exceptions for EOS calculations."""


class ConvergenceWarning(Warning):
    """Warning raised when convergence fails but a best estimate is available."""

    def __init__(
        self,
        message: str,
        best_estimate: float | None = None,
        residual: float | None = None,
    ) -> None:
        """Initialize convergence warning.

        Parameters
        ----------
        message : str
            Warning message
        best_estimate : float, optional
            Best estimate found before convergence failed
        residual : float, optional
            Residual at best estimate
        """
        super().__init__(message)
        self.best_estimate = best_estimate
        self.residual = residual
