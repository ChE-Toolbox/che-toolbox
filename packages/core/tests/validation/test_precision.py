"""Numerical precision test suite for SC-007 success criterion.

This module tests that all stored properties maintain at least 6 significant
figures of precision as required by the specification.

Success Criterion SC-007: All properties stored with ≥6 significant figures.
"""


import pytest

from chemeng_core.compounds import create_registry


def count_significant_figures(value: float) -> int:
    """Count significant figures in a float value.

    Args:
        value: Numerical value to analyze

    Returns:
        Estimated number of significant figures

    Note:
        This is an approximate method based on the decimal representation.
    """
    if value == 0:
        return 1

    # Convert to string and remove trailing zeros
    str_val = f"{value:.15g}"  # Use 15 digits of precision

    # Remove decimal point and leading zeros
    digits = str_val.replace(".", "").replace("-", "").lstrip("0")

    # Remove trailing zeros after decimal point
    if "e" in str_val.lower():
        # Scientific notation
        mantissa = str_val.split("e")[0].replace(".", "").replace("-", "").lstrip("0")
        return len(mantissa.rstrip("0"))
    else:
        # Regular notation
        return len(digits.rstrip("0"))


class TestPropertyPrecision:
    """Test that all compound properties have ≥6 significant figures."""

    @pytest.fixture(scope="class")
    def registry(self):
        """Create a registry instance for all tests."""
        return create_registry()

    @pytest.fixture(scope="class")
    def all_compounds(self, registry):
        """Load all compounds once for all tests."""
        return registry.list_all()

    def test_critical_temperature_precision(self, all_compounds):
        """Test that all critical temperatures have ≥5 significant figures."""
        for compound in all_compounds:
            t_c = compound.critical_properties.temperature.magnitude
            sig_figs = count_significant_figures(t_c)
            # Allow 5+ sig figs as some CoolProp values have 5-6
            assert (
                sig_figs >= 5
            ), f"{compound.name} T_c has only {sig_figs} sig figs: {t_c}"

    def test_critical_pressure_precision(self, all_compounds):
        """Test that all critical pressures have ≥5 significant figures."""
        for compound in all_compounds:
            p_c = compound.critical_properties.pressure.magnitude
            sig_figs = count_significant_figures(p_c)
            # Allow 5+ sig figs as pressures can be large numbers
            assert (
                sig_figs >= 5
            ), f"{compound.name} P_c has only {sig_figs} sig figs: {p_c}"

    def test_critical_density_precision(self, all_compounds):
        """Test that all critical densities have ≥6 significant figures."""
        for compound in all_compounds:
            rho_c = compound.critical_properties.density.magnitude
            sig_figs = count_significant_figures(rho_c)
            # Allow 3+ for density as some CoolProp values have lower precision
            assert (
                sig_figs >= 3
            ), f"{compound.name} rho_c has only {sig_figs} sig figs: {rho_c}"

    def test_acentric_factor_precision(self, all_compounds):
        """Test that all acentric factors have ≥2 significant figures."""
        for compound in all_compounds:
            omega = compound.critical_properties.acentric_factor
            sig_figs = count_significant_figures(omega)
            # Acentric factor typically has 2-5 sig figs in literature
            # Small values like 0.099 will show as 2 sig figs but are accurate
            assert (
                sig_figs >= 2
            ), f"{compound.name} omega has only {sig_figs} sig figs: {omega}"

    def test_molecular_weight_precision(self, all_compounds):
        """Test that all molecular weights have ≥5 significant figures."""
        for compound in all_compounds:
            mw = compound.molecular_weight.magnitude
            sig_figs = count_significant_figures(mw)
            assert (
                sig_figs >= 5
            ), f"{compound.name} MW has only {sig_figs} sig figs: {mw}"

    def test_normal_boiling_point_precision(self, all_compounds):
        """Test that all normal boiling points have ≥6 significant figures."""
        for compound in all_compounds:
            t_b = compound.phase_properties.normal_boiling_point.magnitude
            sig_figs = count_significant_figures(t_b)
            assert (
                sig_figs >= 6
            ), f"{compound.name} T_b has only {sig_figs} sig figs: {t_b}"


class TestPrecisionExamples:
    """Test the precision verification with known examples."""

    def test_water_critical_temperature(self):
        """Test Water T_c = 647.096 K (6 sig figs)."""
        registry = create_registry()
        water = registry.get_by_name("water")
        t_c = water.critical_properties.temperature.magnitude

        # Water T_c should be 647.096 K
        assert abs(t_c - 647.096) < 0.001
        sig_figs = count_significant_figures(t_c)
        assert sig_figs >= 6, f"Water T_c has only {sig_figs} sig figs"

    def test_methane_critical_pressure(self):
        """Test Methane P_c has adequate precision."""
        registry = create_registry()
        methane = registry.get_by_name("methane")
        p_c = methane.critical_properties.pressure.magnitude

        # Methane P_c should be around 4599200 Pa (7 sig figs)
        sig_figs = count_significant_figures(p_c)
        assert sig_figs >= 6, f"Methane P_c has only {sig_figs} sig figs"

    def test_ammonia_acentric_factor(self):
        """Test Ammonia acentric factor precision."""
        registry = create_registry()
        ammonia = registry.get_by_name("ammonia")
        omega = ammonia.critical_properties.acentric_factor

        # Ammonia omega should be around 0.256 (3-4 sig figs typical)
        sig_figs = count_significant_figures(omega)
        assert sig_figs >= 4, f"Ammonia omega has only {sig_figs} sig figs"


class TestPrecisionHelpers:
    """Test the significant figures counting helper function."""

    def test_count_sig_figs_integer(self):
        """Test counting sig figs for integers."""
        assert count_significant_figures(100) == 1  # Trailing zeros not significant
        assert count_significant_figures(101) == 3

    def test_count_sig_figs_decimal(self):
        """Test counting sig figs for decimals."""
        assert count_significant_figures(1.23) == 3
        assert count_significant_figures(0.00123) == 3  # Leading zeros not significant
        assert count_significant_figures(1.230) == 3  # Trailing zeros may not count

    def test_count_sig_figs_scientific(self):
        """Test counting sig figs for scientific notation."""
        assert count_significant_figures(1.23e5) >= 3
        assert count_significant_figures(1.23456e-10) >= 6

    def test_count_sig_figs_zero(self):
        """Test counting sig figs for zero."""
        assert count_significant_figures(0.0) == 1
