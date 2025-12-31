"""Compound registry with in-memory indexing for fast lookups.

This module provides a CompoundRegistry class that loads compound data and indexes
it for efficient retrieval by CAS number, name, formula, or aliases.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from chemeng_core.compounds.exceptions import CompoundNotFoundError
from chemeng_core.compounds.loader import JSONCompoundLoader

if TYPE_CHECKING:
    from chemeng_core.compounds.models import CompoundDTO, DatabaseMetadataDTO


class CompoundRegistry:
    """Registry for compound data with multi-key indexing.

    This class loads compound data from a JSON file and creates in-memory indexes
    for fast lookups by various identifiers (CAS, name, formula, aliases).

    The design allows for future tiered access:
    - Tier 1: Core compounds from JSON (current implementation)
    - Tier 2: Extended compounds from CoolProp (future)
    - Tier 3: User-added compounds (future)

    Attributes:
        loader: JSONCompoundLoader instance
        compounds: List of all loaded compounds
        metadata: Database metadata
        _cas_index: CAS number -> compound mapping
        _name_index: lowercase name -> compound mapping
    """

    def __init__(self, data_path: Path | str) -> None:
        """Initialize registry with path to compound data file.

        Args:
            data_path: Path to compounds.json file
        """
        self.loader = JSONCompoundLoader(data_path)
        self.compounds: list[CompoundDTO] = []
        self.metadata: DatabaseMetadataDTO | None = None
        self._cas_index: dict[str, CompoundDTO] = {}
        self._name_index: dict[str, CompoundDTO] = {}
        self._loaded = False

    def load(self) -> None:
        """Load compound data and build indexes.

        This method must be called before any lookup operations.

        Raises:
            ValidationError: If data fails validation
        """
        if self._loaded:
            return  # Already loaded

        database = self.loader.load()
        self.compounds = list(database.compounds)
        self.metadata = database.metadata

        # Build indexes
        self._build_indexes()
        self._loaded = True

    def _build_indexes(self) -> None:
        """Build in-memory indexes for fast lookups."""
        for compound in self.compounds:
            # CAS index (primary key)
            self._cas_index[compound.cas_number] = compound

            # Name index (case-insensitive)
            self._name_index[compound.name.lower()] = compound
            self._name_index[compound.formula.lower()] = compound
            self._name_index[compound.coolprop_name.lower()] = compound

            # Alias index
            for alias in compound.aliases:
                self._name_index[alias.lower()] = compound

    def get_by_cas(self, cas_number: str) -> CompoundDTO:
        """Get compound by CAS Registry Number.

        Args:
            cas_number: CAS number (e.g., "7732-18-5")

        Returns:
            CompoundDTO instance

        Raises:
            CompoundNotFoundError: If compound not found

        Examples:
            >>> registry = CompoundRegistry("compounds.json")
            >>> registry.load()
            >>> water = registry.get_by_cas("7732-18-5")
            >>> print(water.name)
            Water
        """
        if not self._loaded:
            self.load()

        compound = self._cas_index.get(cas_number)
        if compound is None:
            raise CompoundNotFoundError(cas_number)
        return compound

    def get_by_name(self, name: str) -> CompoundDTO:
        """Get compound by name, formula, or alias (case-insensitive).

        Args:
            name: Compound name, formula, or alias

        Returns:
            CompoundDTO instance

        Raises:
            CompoundNotFoundError: If compound not found

        Examples:
            >>> registry = CompoundRegistry("compounds.json")
            >>> registry.load()
            >>> water = registry.get_by_name("water")
            >>> h2o = registry.get_by_name("H2O")
            >>> assert water.cas_number == h2o.cas_number
        """
        if not self._loaded:
            self.load()

        compound = self._name_index.get(name.lower())
        if compound is None:
            raise CompoundNotFoundError(name)
        return compound

    def get_by_formula(self, formula: str) -> CompoundDTO:
        """Get compound by chemical formula (case-insensitive).

        Args:
            formula: Chemical formula (e.g., "H2O", "CO2")

        Returns:
            CompoundDTO instance

        Raises:
            CompoundNotFoundError: If compound not found

        Examples:
            >>> registry = CompoundRegistry("compounds.json")
            >>> registry.load()
            >>> water = registry.get_by_formula("H2O")
        """
        return self.get_by_name(formula)  # Formula is in name index

    def search(self, query: str) -> list[CompoundDTO]:
        """Search for compounds by partial name/formula match.

        Args:
            query: Search query string

        Returns:
            List of matching compounds (empty if no matches)

        Examples:
            >>> registry = CompoundRegistry("compounds.json")
            >>> registry.load()
            >>> results = registry.search("meth")
            >>> print([c.name for c in results])
            ['Methane']
        """
        if not self._loaded:
            self.load()

        query_lower = query.lower()
        results = []

        for compound in self.compounds:
            # Check if query matches name, formula, or aliases
            if (
                query_lower in compound.name.lower()
                or query_lower in compound.formula.lower()
                or any(query_lower in alias.lower() for alias in compound.aliases)
            ):
                results.append(compound)

        return results

    def list_all(self) -> list[CompoundDTO]:
        """Get list of all compounds in registry.

        Returns:
            List of all CompoundDTO instances

        Examples:
            >>> registry = CompoundRegistry("compounds.json")
            >>> registry.load()
            >>> compounds = registry.list_all()
            >>> len(compounds)
            10
        """
        if not self._loaded:
            self.load()
        return list(self.compounds)
