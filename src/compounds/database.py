"""Compound database management."""

import json
from pathlib import Path

from .models import Compound


class CompoundDatabase:
    """Manages access to compound database."""

    def __init__(self, db_path: Path | str = "data/compounds.json") -> None:
        """Initialize compound database.

        Parameters
        ----------
        db_path : Path or str
            Path to compounds.json file
        """
        self.db_path = Path(db_path)
        self._compounds: dict[str, Compound] = {}
        self._load_database()

    def _load_database(self) -> None:
        """Load compound database from JSON file."""
        if not self.db_path.exists():
            return

        with self.db_path.open() as f:
            data = json.load(f)
            for compound_data in data:
                compound = Compound(**compound_data)
                self._compounds[compound.name.lower()] = compound

    def get(self, name: str) -> Compound | None:
        """Get compound by name.

        Parameters
        ----------
        name : str
            Compound name (case-insensitive)

        Returns
        -------
        Compound or None
            Compound object or None if not found
        """
        return self._compounds.get(name.lower())

    def get_by_cas(self, cas_number: str) -> Compound | None:
        """Get compound by CAS number.

        Parameters
        ----------
        cas_number : str
            CAS registry number

        Returns
        -------
        Compound or None
            Compound object or None if not found
        """
        for compound in self._compounds.values():
            if compound.cas_number == cas_number:
                return compound
        return None

    def list_compounds(self) -> list[str]:
        """List all available compound names.

        Returns
        -------
        list[str]
            List of compound names
        """
        return sorted(self._compounds.keys())

    def add_compound(self, compound: Compound) -> None:
        """Add compound to database.

        Parameters
        ----------
        compound : Compound
            Compound object to add
        """
        self._compounds[compound.name.lower()] = compound

    def save(self) -> None:
        """Save database to JSON file."""
        compounds_data = [
            c.model_dump() for c in sorted(self._compounds.values(), key=lambda c: c.name)
        ]
        with self.db_path.open("w") as f:
            json.dump(compounds_data, f, indent=2)
