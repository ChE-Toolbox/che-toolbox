"""Custom exceptions for compound database operations."""


class CompoundNotFoundError(Exception):
    """Exception raised when a compound cannot be found in the database.

    Attributes:
        identifier: The identifier (CAS, name, formula, etc.) that was searched
    """

    def __init__(self, identifier: str) -> None:
        """Initialize with the identifier that was not found.

        Args:
            identifier: The compound identifier that was searched
        """
        self.identifier = identifier
        super().__init__(f"Compound not found: identifier='{identifier}'")


class ValidationError(Exception):
    """Exception raised when compound data fails validation.

    This is raised when data doesn't match the expected schema or
    contains invalid values.
    """

    pass


class DimensionalityError(Exception):
    """Exception raised when unit conversions have incompatible dimensions.

    This is re-exported from units.handler for convenience.
    """

    pass
