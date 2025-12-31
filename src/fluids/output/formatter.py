"""
Output formatting for calculation results with configurable verbosity.

Supports minimal, standard, and detailed output formats in both text and JSON.
"""

from typing import Any, Literal


def format_calculation(
    result: dict[str, Any],
    verbosity: Literal["minimal", "standard", "detailed"] = "standard",
    output_format: Literal["text", "json"] = "text",
) -> str | dict[str, Any]:
    """
    Format calculation result based on verbosity and output format.

    Args:
        result: Calculation result dictionary with keys: value, unit, formula_used,
                intermediate_values, warnings, source
        verbosity: Output verbosity level ('minimal', 'standard', 'detailed')
        output_format: Output format ('text' or 'json')

    Returns:
        Formatted output as string (text) or dict (JSON)
    """
    if output_format == "json":
        return _format_json(result, verbosity)
    else:
        return _format_text(result, verbosity)


def _format_json(
    result: dict[str, Any],
    verbosity: Literal["minimal", "standard", "detailed"],
) -> dict[str, Any]:
    """Format result as JSON."""
    if verbosity == "minimal":
        return {
            "value": result.get("value"),
            "unit": result.get("unit"),
        }
    elif verbosity == "standard":
        return {
            "value": result.get("value"),
            "unit": result.get("unit"),
            "formula": result.get("formula_used"),
            "intermediate_values": result.get("intermediate_values", {}),
            "warnings": result.get("warnings", []),
        }
    else:  # detailed
        return result


def _format_text(
    result: dict[str, Any],
    verbosity: Literal["minimal", "standard", "detailed"],
) -> str:
    """Format result as human-readable text."""
    lines: list[str] = []

    if verbosity == "minimal":
        # Just the result
        value = result.get("value")
        unit = result.get("unit", "")
        lines.append(f"{value} {unit}".strip())

    elif verbosity == "standard":
        # Result + formula + intermediate values
        value = result.get("value")
        unit = result.get("unit", "")
        lines.append(f"Result: {value} {unit}".strip())
        lines.append("")

        if result.get("formula_used"):
            lines.append(f"Formula: {result['formula_used']}")

        if result.get("intermediate_values"):
            lines.append("Intermediate values:")
            for key, val in result["intermediate_values"].items():
                lines.append(f"  {key}: {val}")

        if result.get("warnings"):
            lines.append("")
            lines.append("Warnings:")
            for warning in result["warnings"]:
                if isinstance(warning, dict):
                    lines.append(f"  ⚠️  {warning.get('message', warning)}")
                else:
                    lines.append(f"  ⚠️  {warning}")

    else:  # detailed
        # Everything
        lines.append("=== CALCULATION RESULT ===")
        lines.append(f"Result: {result.get('value')} {result.get('unit', '')}")
        lines.append("")

        if result.get("formula_used"):
            lines.append(f"Formula: {result['formula_used']}")
            lines.append("")

        if result.get("intermediate_values"):
            lines.append("Calculation steps:")
            for key, val in result["intermediate_values"].items():
                lines.append(f"  {key}: {val}")
            lines.append("")

        if result.get("warnings"):
            lines.append("Warnings and Notes:")
            for warning in result["warnings"]:
                if isinstance(warning, dict):
                    severity = warning.get("severity", "INFO")
                    lines.append(f"  [{severity}] {warning.get('message', warning)}")
                else:
                    lines.append(f"  [INFO] {warning}")
            lines.append("")

        if result.get("source"):
            lines.append(f"Source: {result['source']}")

        if result.get("reference_data"):
            lines.append(f"Reference: {result['reference_data']}")

    return "\n".join(lines)


def create_result(
    value: float,
    unit: str,
    formula_used: str = "",
    intermediate_values: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    source: str = "",
    reference_data: str = "",
) -> dict[str, Any]:
    """
    Create a standardized calculation result dictionary.

    Args:
        value: Calculated value
        unit: Unit of the value
        formula_used: Formula or method used for calculation
        intermediate_values: Dictionary of intermediate calculation values
        warnings: List of warnings or informational messages
        source: Source of calculation (e.g., 'Crane TP-410')
        reference_data: Reference data used for validation

    Returns:
        Standardized result dictionary
    """
    return {
        "value": value,
        "unit": unit,
        "formula_used": formula_used,
        "intermediate_values": intermediate_values or {},
        "warnings": warnings or [],
        "source": source,
        "reference_data": reference_data,
    }
