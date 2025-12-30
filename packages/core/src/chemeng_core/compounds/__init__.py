"""Chemical compound database module.

This module provides access to thermophysical properties of chemical compounds,
sourced from CoolProp and validated against NIST WebBook data.

Public API:
    - get_compound: Convenience function to get a compound by any identifier
    - create_registry: Factory function to create a CompoundRegistry
    - CompoundRegistry: Main registry class for compound lookups
    - CompoundDTO: Compound data model
    - CompoundNotFoundError: Exception for missing compounds
"""

from __future__ import annotations

from pathlib import Path

from chemeng_core.compounds.exceptions import CompoundNotFoundError
from chemeng_core.compounds.models import CompoundDTO
from chemeng_core.compounds.registry import CompoundRegistry

# Default data path (relative to this file)
_DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "compounds" / "compounds.json"

# Global registry instance (lazy-loaded)
_global_registry: CompoundRegistry | None = None


def create_registry(data_path: Path | str | None = None) -> CompoundRegistry:
    """Create and load a CompoundRegistry instance.

    Args:
        data_path: Optional custom path to compounds.json.
                   If None, uses default bundled data.

    Returns:
        Loaded CompoundRegistry instance

    Examples:
        >>> registry = create_registry()
        >>> water = registry.get_by_name("water")
        >>> print(water.name)
        Water
    """
    if data_path is None:
        data_path = _DEFAULT_DATA_PATH

    registry = CompoundRegistry(data_path)
    registry.load()
    return registry


def get_compound(identifier: str, data_path: Path | str | None = None) -> CompoundDTO:
    """Get a compound by any identifier (CAS, name, formula, alias).

    This is a convenience function that automatically creates or reuses a
    global registry and attempts to find the compound by any identifier type.

    Args:
        identifier: CAS number, name, formula, or alias
        data_path: Optional custom path to compounds.json

    Returns:
        CompoundDTO instance

    Raises:
        CompoundNotFoundError: If compound not found

    Examples:
        >>> water = get_compound("water")
        >>> h2o = get_compound("H2O")
        >>> by_cas = get_compound("7732-18-5")
        >>> assert water.cas_number == h2o.cas_number == by_cas.cas_number
    """
    global _global_registry

    # Create or reuse global registry
    if _global_registry is None or data_path is not None:
        _global_registry = create_registry(data_path)

    # Try to get compound (registry will raise CompoundNotFoundError if not found)
    try:
        # Try as CAS number first (exact match)
        return _global_registry.get_by_cas(identifier)
    except CompoundNotFoundError:
        pass

    # Try as name/formula/alias
    return _global_registry.get_by_name(identifier)


__all__ = [
    "CompoundDTO",
    "CompoundNotFoundError",
    "CompoundRegistry",
    "create_registry",
    "get_compound",
]
