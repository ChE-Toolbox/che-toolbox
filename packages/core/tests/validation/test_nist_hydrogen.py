"""NIST validation tests for Hydrogen (H2) critical properties.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_hydrogen_critical_temperature() -> None:
    """Validate hydrogen critical temperature against NIST WebBook.

    NIST Value: 33.145 K
    Tolerance: ±0.01%
    """
    hydrogen = get_compound("hydrogen")
    assert hydrogen.critical_properties.temperature.magnitude == pytest.approx(33.145, rel=1e-4)


@pytest.mark.validation
def test_hydrogen_critical_pressure() -> None:
    """Validate hydrogen critical pressure against NIST WebBook.

    NIST Value: 1.2964 MPa = 1296400 Pa
    Tolerance: ±0.01%
    """
    hydrogen = get_compound("hydrogen")
    assert hydrogen.critical_properties.pressure.magnitude == pytest.approx(1296400, rel=1e-4)


@pytest.mark.validation
def test_hydrogen_acentric_factor() -> None:
    """Validate hydrogen acentric factor against NIST WebBook.

    NIST Value: -0.216
    CoolProp Value: -0.219
    Tolerance: ±2% (acentric factor has higher variance between correlations)
    """
    hydrogen = get_compound("hydrogen")
    assert hydrogen.critical_properties.acentric_factor == pytest.approx(-0.216, rel=0.02)
