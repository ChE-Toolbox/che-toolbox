"""NIST validation tests for Nitrogen (N2) critical properties.

Reference: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379
"""

import pytest

from chemeng_core.compounds import get_compound


@pytest.mark.validation
def test_nitrogen_critical_temperature() -> None:
    """Validate nitrogen critical temperature against NIST WebBook.

    NIST Value: 126.192 K
    Tolerance: ±0.01%
    """
    nitrogen = get_compound("nitrogen")
    assert nitrogen.critical_properties.temperature.magnitude == pytest.approx(126.192, rel=1e-4)


@pytest.mark.validation
def test_nitrogen_critical_pressure() -> None:
    """Validate nitrogen critical pressure against NIST WebBook.

    NIST Value: 3.3958 MPa = 3395800 Pa
    Tolerance: ±0.01%
    """
    nitrogen = get_compound("nitrogen")
    assert nitrogen.critical_properties.pressure.magnitude == pytest.approx(3395800, rel=1e-4)


@pytest.mark.validation
def test_nitrogen_acentric_factor() -> None:
    """Validate nitrogen acentric factor against NIST WebBook.

    NIST Value: 0.0372
    Tolerance: ±1%
    """
    nitrogen = get_compound("nitrogen")
    assert nitrogen.critical_properties.acentric_factor == pytest.approx(0.0372, rel=0.01)
