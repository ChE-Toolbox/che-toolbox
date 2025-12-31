"""JSON-based compound data loader.

This module provides functionality to load and validate compound data from JSON files.
The loader uses Pydantic models for schema validation and ensures data integrity.
"""

from __future__ import annotations

import json
from pathlib import Path

from chemeng_core.compounds.exceptions import ValidationError
from chemeng_core.compounds.models import CompoundDatabaseDTO, CompoundDTO
from chemeng_core.compounds.validation import validate_compound_json


class JSONCompoundLoader:
    """Load and validate compound data from JSON files.

    This class handles loading compound databases from JSON format, with full
    schema validation using Pydantic models.

    Attributes:
        data_path: Path to the compound JSON file
        database: Loaded and validated database (after load())
    """

    def __init__(self, data_path: Path | str) -> None:
        """Initialize loader with path to compound data file.

        Args:
            data_path: Path to compounds.json file
        """
        self.data_path = Path(data_path)
        self.database: CompoundDatabaseDTO | None = None

    def load(self) -> CompoundDatabaseDTO:
        """Load and validate compound database from JSON file.

        This method reads the JSON file, validates its structure, and parses
        it into Pydantic models for type safety and validation.

        Returns:
            Validated CompoundDatabaseDTO instance

        Raises:
            ValidationError: If data fails validation
            FileNotFoundError: If data file doesn't exist

        Examples:
            >>> loader = JSONCompoundLoader("packages/core/src/chemeng_core/data/compounds/compounds.json")
            >>> database = loader.load()
            >>> print(database.metadata.compound_count)
            10
        """
        # Validate JSON structure
        raw_data = validate_compound_json(self.data_path)

        # Parse into Pydantic models
        try:
            self.database = CompoundDatabaseDTO.model_validate(raw_data)
        except Exception as e:
            raise ValidationError(f"Failed to parse compound database: {e}") from e

        # Additional validation: compound count consistency
        actual_count = len(self.database.compounds)
        expected_count = self.database.metadata.compound_count
        if actual_count != expected_count:
            raise ValidationError(
                f"Compound count mismatch: metadata says {expected_count}, "
                f"but found {actual_count} compounds"
            )

        return self.database

    def validate(self) -> bool:
        """Validate that data has been loaded and is valid.

        Returns:
            True if database is loaded and valid

        Raises:
            ValidationError: If database not loaded
        """
        if self.database is None:
            raise ValidationError("Database not loaded. Call load() first.")
        return True

    def get_compound_by_cas(self, cas_number: str) -> CompoundDTO | None:
        """Get compound by CAS number.

        Args:
            cas_number: CAS Registry Number

        Returns:
            CompoundDTO if found, None otherwise

        Raises:
            ValidationError: If database not loaded
        """
        self.validate()
        assert self.database is not None  # For type checker

        for compound in self.database.compounds:
            if compound.cas_number == cas_number:
                return compound
        return None

    def get_compound_by_name(self, name: str) -> CompoundDTO | None:
        """Get compound by name (case-insensitive).

        Searches both the primary name and aliases.

        Args:
            name: Compound name (e.g., "water", "H2O")

        Returns:
            CompoundDTO if found, None otherwise

        Raises:
            ValidationError: If database not loaded
        """
        self.validate()
        assert self.database is not None  # For type checker

        name_lower = name.lower()
        for compound in self.database.compounds:
            # Check primary name
            if compound.name.lower() == name_lower:
                return compound
            # Check formula
            if compound.formula.lower() == name_lower:
                return compound
            # Check CoolProp name
            if compound.coolprop_name.lower() == name_lower:
                return compound
            # Check aliases
            if any(alias.lower() == name_lower for alias in compound.aliases):
                return compound

        return None

    def list_all_compounds(self) -> list[CompoundDTO]:
        """Get list of all compounds in database.

        Returns:
            List of all CompoundDTO instances

        Raises:
            ValidationError: If database not loaded
        """
        self.validate()
        assert self.database is not None  # For type checker
        return list(self.database.compounds)


def add_compound_to_database(
    compound: CompoundDTO, database_path: Path | str, check_duplicates: bool = True
) -> None:
    """Add a new compound to the database JSON file.

    This function loads the existing database, validates the new compound,
    checks for duplicates, appends the compound, and saves the updated database.

    Args:
        compound: CompoundDTO instance to add
        database_path: Path to compounds.json file
        check_duplicates: If True, raise error if CAS number already exists

    Raises:
        ValidationError: If compound is invalid or duplicate exists
        FileNotFoundError: If database file doesn't exist

    Examples:
        >>> from chemeng_core.compounds.extractor import CoolPropDataExtractor
        >>> extractor = CoolPropDataExtractor("Argon")
        >>> argon = extractor.extract_compound_data(
        ...     cas_number="7440-37-1",
        ...     name="Argon",
        ...     formula="Ar",
        ...     iupac_name="argon",
        ...     aliases=["argon", "Ar"]
        ... )
        >>> add_compound_to_database(argon, "compounds.json")
    """
    database_path = Path(database_path)

    # Load existing database
    loader = JSONCompoundLoader(database_path)
    database = loader.load()

    # Check for duplicates
    if check_duplicates:
        for existing_compound in database.compounds:
            if existing_compound.cas_number == compound.cas_number:
                raise ValidationError(
                    f"Compound with CAS number {compound.cas_number} "
                    f"already exists in database: {existing_compound.name}"
                )

    # Add new compound
    updated_compounds = list(database.compounds) + [compound]

    # Update metadata
    updated_metadata = database.metadata.model_copy(
        update={
            "compound_count": len(updated_compounds),
            "retrieved_date": compound.source.retrieved_date,
        }
    )

    # Create updated database
    updated_database = CompoundDatabaseDTO(metadata=updated_metadata, compounds=updated_compounds)

    # Write to file
    with database_path.open("w") as f:
        json.dump(
            updated_database.model_dump(mode="python"),
            f,
            indent=2,
            default=str,  # Handle date serialization
        )
        f.write("\n")  # Add trailing newline
