"""Unit tests for compound database."""

import json
import tempfile
from pathlib import Path

import pytest

from src.compounds.database import CompoundDatabase
from src.compounds.models import Compound


class TestCompoundDatabase:
    """Test CompoundDatabase class."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create a temporary database file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            compounds_data = [
                {
                    "name": "methane",
                    "cas_number": "74-82-8",
                    "molecular_weight": 16.043,
                    "tc": 190.564,
                    "pc": 4599200.0,
                    "acentric_factor": 0.011,
                },
                {
                    "name": "ethane",
                    "cas_number": "74-84-0",
                    "molecular_weight": 30.070,
                    "tc": 305.322,
                    "pc": 4872200.0,
                    "acentric_factor": 0.099,
                },
            ]
            json.dump(compounds_data, f)
            temp_path = Path(f.name)

        yield temp_path

        # Cleanup
        temp_path.unlink()

    def test_load_database(self, temp_db: Path) -> None:
        """Test loading compounds from database."""
        db = CompoundDatabase(temp_db)
        assert "methane" in db.list_compounds()
        assert "ethane" in db.list_compounds()

    def test_get_compound(self, temp_db: Path) -> None:
        """Test getting a compound by name."""
        db = CompoundDatabase(temp_db)
        methane = db.get("methane")
        assert methane is not None
        assert methane.name == "methane"
        assert methane.tc == 190.564

    def test_get_compound_case_insensitive(self, temp_db: Path) -> None:
        """Test that compound lookup is case-insensitive."""
        db = CompoundDatabase(temp_db)
        methane_lower = db.get("methane")
        methane_upper = db.get("METHANE")
        assert methane_lower == methane_upper

    def test_get_nonexistent_compound(self, temp_db: Path) -> None:
        """Test getting a nonexistent compound returns None."""
        db = CompoundDatabase(temp_db)
        compound = db.get("nonexistent")
        assert compound is None

    def test_get_by_cas(self, temp_db: Path) -> None:
        """Test getting a compound by CAS number."""
        db = CompoundDatabase(temp_db)
        methane = db.get_by_cas("74-82-8")
        assert methane is not None
        assert methane.name == "methane"

    def test_get_by_cas_nonexistent(self, temp_db: Path) -> None:
        """Test getting a nonexistent CAS number returns None."""
        db = CompoundDatabase(temp_db)
        compound = db.get_by_cas("999-99-9")
        assert compound is None

    def test_list_compounds(self, temp_db: Path) -> None:
        """Test listing all compounds."""
        db = CompoundDatabase(temp_db)
        compounds = db.list_compounds()
        assert len(compounds) == 2
        assert "ethane" in compounds
        assert "methane" in compounds
        # Should be sorted
        assert compounds == sorted(compounds)

    def test_add_compound(self, temp_db: Path) -> None:
        """Test adding a new compound."""
        db = CompoundDatabase(temp_db)
        propane = Compound(
            name="propane",
            cas_number="74-98-6",
            molecular_weight=44.096,
            tc=369.83,
            pc=4248400.0,
            acentric_factor=0.152,
        )
        db.add_compound(propane)
        assert db.get("propane") == propane

    def test_save_database(self, temp_db: Path) -> None:
        """Test saving database to file."""
        db = CompoundDatabase(temp_db)

        # Add a new compound
        propane = Compound(
            name="propane",
            cas_number="74-98-6",
            molecular_weight=44.096,
            tc=369.83,
            pc=4248400.0,
            acentric_factor=0.152,
        )
        db.add_compound(propane)
        db.save()

        # Load in a new instance
        db2 = CompoundDatabase(temp_db)
        assert db2.get("propane") is not None
        assert len(db2.list_compounds()) == 3

    def test_missing_database(self) -> None:
        """Test that missing database file doesn't raise error."""
        db = CompoundDatabase("nonexistent_path.json")
        assert db.list_compounds() == []
