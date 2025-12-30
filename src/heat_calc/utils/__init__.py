"""Utility functions and constants for heat exchanger calculations.

This module provides:
- validation: Input validation helpers (unit checking, range checks, NaN/Inf guards)
- constants: Physical constants and reference correlation metadata
"""

from heat_calc.utils import constants, validation

__all__ = ["constants", "validation"]
