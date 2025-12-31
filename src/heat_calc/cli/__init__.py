"""CLI interface for heat exchanger calculations.

Provides command-line tools for:
- calculate-lmtd: LMTD method calculations
- calculate-ntu: NTU method calculations
- calculate-convection: Convection correlations
- calculate-insulation: Insulation sizing

Each command accepts JSON/YAML input and supports multiple output formats.
"""

from heat_calc.cli.main import cli

__all__ = ["cli"]
