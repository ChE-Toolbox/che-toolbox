"""NIST validation tests for Helium (He) critical properties.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440597
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_helium_critical_temperature() -> None:
    """Validate helium critical temperature against NIST WebBook.

    NIST Value: 5.1953 K
    Tolerance: ±0.01%
    """
    helium = get_compound("helium")
    assert helium.critical_properties.temperature.magnitude == pytest.approx(5.1953, rel=1e-4)


@pytest.mark.validation
def test_helium_critical_pressure() -> None:
    """Validate helium critical pressure against NIST WebBook.

    NIST Value: 0.22746 MPa = 227460 Pa
    CoolProp Value: 228900 Pa
    Tolerance: ±1% (helium properties have higher variance)
    """
    helium = get_compound("helium")
    assert helium.critical_properties.pressure.magnitude == pytest.approx(227460, rel=0.01)


@pytest.mark.validation
def test_helium_acentric_factor() -> None:
    """Validate helium acentric factor against NIST WebBook.

    NIST Value: -0.382
    Tolerance: ±1%
    """
    helium = get_compound("helium")
    assert helium.critical_properties.acentric_factor == pytest.approx(-0.382, rel=0.01)
