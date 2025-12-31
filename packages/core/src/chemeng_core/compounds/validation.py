"""JSON schema validation for compound data using Pydantic.

This module provides validation utilities for compound database files,
ensuring data integrity and schema compliance.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from chemeng_core.compounds.exceptions import ValidationError


def validate_compound_json(json_path: Path | str) -> dict[str, Any]:
    """Validate compound JSON file against schema.

    This function reads a JSON file and validates its structure before
    parsing it into Pydantic models. This provides early error detection
    for malformed data files.

    Args:
        json_path: Path to compound JSON file

    Returns:
        Validated JSON data as dictionary

    Raises:
        ValidationError: If JSON is malformed or doesn't match expected structure
        FileNotFoundError: If file doesn't exist

    Examples:
        >>> data = validate_compound_json("compounds.json")
        >>> print(data["metadata"]["version"])
        '1.0.0'
    """
    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(f"Compound data file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in {path}: {e}") from e

    # Basic structure validation
    if not isinstance(data, dict):
        raise ValidationError(f"Expected dict at root level, got {type(data).__name__}")

    if "metadata" not in data:
        raise ValidationError("Missing required 'metadata' field")

    if "compounds" not in data:
        raise ValidationError("Missing required 'compounds' field")

    if not isinstance(data["compounds"], list):
        raise ValidationError(
            f"Expected 'compounds' to be a list, got {type(data['compounds']).__name__}"
        )

    return data


def validate_pydantic_model(model_class: type, data: dict[str, Any]) -> Any:
    """Validate data against a Pydantic model.

    Args:
        model_class: Pydantic model class
        data: Dictionary data to validate

    Returns:
        Validated model instance

    Raises:
        ValidationError: If data doesn't match model schema
    """
    try:
        return model_class.model_validate(data)
    except PydanticValidationError as e:
        raise ValidationError(f"Pydantic validation failed: {e}") from e
