"""Validation tests for IAPWS-IF97 saturation line calculations.

Tests saturation property calculations against IAPWS reference tables
with ±0.1% accuracy tolerance as specified in IAPWS-IF97 standard.
"""

import pytest

from src.iapws_if97 import SteamTable, ureg
from src.iapws_if97.exceptions import InputRangeError


@pytest.mark.validation
class TestSaturationValidation:
    """Validate saturation calculations against IAPWS reference data."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize SteamTable for all tests."""
        self.steam = SteamTable()
        self.tolerance = 0.001  # ±0.1% as per IAPWS-IF97 spec

    def test_saturation_reference_data_exists(self, saturation_reference_points):
        """Verify that IAPWS saturation reference data is loaded."""
        assert saturation_reference_points is not None
        assert len(saturation_reference_points) > 0
        print(f"\nLoaded {len(saturation_reference_points)} saturation reference points")

    def test_T_sat_against_reference_data(self, saturation_reference_points):
        """Validate T_sat(P) calculations against IAPWS reference tables."""
        failures = []

        for point in saturation_reference_points:
            P_pa = point["pressure_Pa"]
            expected_T_K = point["temperature_K"]

            try:
                # Calculate saturation properties
                sat_props = self.steam.T_sat(P_pa * ureg.Pa)

                # Extract temperature
                calculated_T_K = sat_props.saturation_temperature.to("K").magnitude

                # Calculate relative error
                rel_error = abs(calculated_T_K - expected_T_K) / expected_T_K

                if rel_error > self.tolerance:
                    failures.append(
                        {
                            "point_id": point.get("point_id", "unknown"),
                            "pressure_Pa": P_pa,
                            "expected_T_K": expected_T_K,
                            "calculated_T_K": calculated_T_K,
                            "rel_error": rel_error * 100,
                        }
                    )
            except Exception as e:
                failures.append(
                    {
                        "point_id": point.get("point_id", "unknown"),
                        "pressure_Pa": P_pa,
                        "error": str(e),
                    }
                )

        if failures:
            print(f"\n{len(failures)} T_sat validation failures:")
            for fail in failures[:5]:  # Show first 5 failures
                print(f"  {fail}")

        assert len(failures) == 0, (
            f"{len(failures)}/{len(saturation_reference_points)} T_sat points failed validation"
        )

    def test_P_sat_against_reference_data(self, saturation_reference_points):
        """Validate P_sat(T) calculations against IAPWS reference tables."""
        failures = []

        for point in saturation_reference_points:
            T_K = point["temperature_K"]
            expected_P_pa = point["pressure_Pa"]

            try:
                # Calculate saturation properties
                sat_props = self.steam.P_sat(T_K * ureg.K)

                # Extract pressure
                calculated_P_pa = sat_props.saturation_pressure.to("Pa").magnitude

                # Calculate relative error
                rel_error = abs(calculated_P_pa - expected_P_pa) / expected_P_pa

                if rel_error > self.tolerance:
                    failures.append(
                        {
                            "point_id": point.get("point_id", "unknown"),
                            "temperature_K": T_K,
                            "expected_P_Pa": expected_P_pa,
                            "calculated_P_Pa": calculated_P_pa,
                            "rel_error": rel_error * 100,
                        }
                    )
            except Exception as e:
                failures.append(
                    {
                        "point_id": point.get("point_id", "unknown"),
                        "temperature_K": T_K,
                        "error": str(e),
                    }
                )

        if failures:
            print(f"\n{len(failures)} P_sat validation failures:")
            for fail in failures[:5]:
                print(f"  {fail}")

        assert len(failures) == 0, (
            f"{len(failures)}/{len(saturation_reference_points)} P_sat points failed validation"
        )

    def test_saturation_enthalpy_liquid_validation(self, saturation_reference_points):
        """Validate liquid enthalpy h_f at saturation against reference data."""
        failures = []

        for point in saturation_reference_points:
            P_pa = point["pressure_Pa"]
            expected_h_f = point["enthalpy_liquid_kJ_per_kg"]

            try:
                sat_props = self.steam.T_sat(P_pa * ureg.Pa)
                calculated_h_f = sat_props.enthalpy_liquid.to("kJ/kg").magnitude

                rel_error = abs(calculated_h_f - expected_h_f) / abs(expected_h_f)

                if rel_error > self.tolerance:
                    failures.append(
                        {
                            "point_id": point.get("point_id", "unknown"),
                            "pressure_Pa": P_pa,
                            "expected_h_f": expected_h_f,
                            "calculated_h_f": calculated_h_f,
                            "rel_error": rel_error * 100,
                        }
                    )
            except Exception as e:
                failures.append(
                    {
                        "point_id": point.get("point_id", "unknown"),
                        "pressure_Pa": P_pa,
                        "error": str(e),
                    }
                )

        if failures:
            print(f"\n{len(failures)} h_f validation failures:")
            for fail in failures[:5]:
                print(f"  {fail}")

        assert len(failures) == 0, (
            f"{len(failures)}/{len(saturation_reference_points)} h_f points failed"
        )

    def test_saturation_enthalpy_vapor_validation(self, saturation_reference_points):
        """Validate vapor enthalpy h_g at saturation against reference data."""
        failures = []

        for point in saturation_reference_points:
            P_pa = point["pressure_Pa"]
            expected_h_g = point["enthalpy_vapor_kJ_per_kg"]

            try:
                sat_props = self.steam.T_sat(P_pa * ureg.Pa)
                calculated_h_g = sat_props.enthalpy_vapor.to("kJ/kg").magnitude

                rel_error = abs(calculated_h_g - expected_h_g) / abs(expected_h_g)

                if rel_error > self.tolerance:
                    failures.append(
                        {
                            "point_id": point.get("point_id", "unknown"),
                            "pressure_Pa": P_pa,
                            "expected_h_g": expected_h_g,
                            "calculated_h_g": calculated_h_g,
                            "rel_error": rel_error * 100,
                        }
                    )
            except Exception as e:
                failures.append(
                    {
                        "point_id": point.get("point_id", "unknown"),
                        "pressure_Pa": P_pa,
                        "error": str(e),
                    }
                )

        if failures:
            print(f"\n{len(failures)} h_g validation failures:")
            for fail in failures[:5]:
                print(f"  {fail}")

        assert len(failures) == 0, (
            f"{len(failures)}/{len(saturation_reference_points)} h_g points failed"
        )

    def test_saturation_entropy_liquid_validation(self, saturation_reference_points):
        """Validate liquid entropy s_f at saturation against reference data."""
        failures = []

        for point in saturation_reference_points:
            P_pa = point["pressure_Pa"]
            expected_s_f = point["entropy_liquid_kJ_per_kg_K"]

            try:
                sat_props = self.steam.T_sat(P_pa * ureg.Pa)
                calculated_s_f = sat_props.entropy_liquid.to("kJ/(kg*K)").magnitude

                rel_error = abs(calculated_s_f - expected_s_f) / abs(expected_s_f)

                if rel_error > self.tolerance:
                    failures.append(
                        {
                            "point_id": point.get("point_id", "unknown"),
                            "pressure_Pa": P_pa,
                            "expected_s_f": expected_s_f,
                            "calculated_s_f": calculated_s_f,
                            "rel_error": rel_error * 100,
                        }
                    )
            except Exception as e:
                failures.append(
                    {
                        "point_id": point.get("point_id", "unknown"),
                        "pressure_Pa": P_pa,
                        "error": str(e),
                    }
                )

        if failures:
            print(f"\n{len(failures)} s_f validation failures:")
            for fail in failures[:5]:
                print(f"  {fail}")

        assert len(failures) == 0, (
            f"{len(failures)}/{len(saturation_reference_points)} s_f points failed"
        )

    def test_saturation_entropy_vapor_validation(self, saturation_reference_points):
        """Validate vapor entropy s_g at saturation against reference data."""
        failures = []

        for point in saturation_reference_points:
            P_pa = point["pressure_Pa"]
            expected_s_g = point["entropy_vapor_kJ_per_kg_K"]

            try:
                sat_props = self.steam.T_sat(P_pa * ureg.Pa)
                calculated_s_g = sat_props.entropy_vapor.to("kJ/(kg*K)").magnitude

                rel_error = abs(calculated_s_g - expected_s_g) / abs(expected_s_g)

                if rel_error > self.tolerance:
                    failures.append(
                        {
                            "point_id": point.get("point_id", "unknown"),
                            "pressure_Pa": P_pa,
                            "expected_s_g": expected_s_g,
                            "calculated_s_g": calculated_s_g,
                            "rel_error": rel_error * 100,
                        }
                    )
            except Exception as e:
                failures.append(
                    {
                        "point_id": point.get("point_id", "unknown"),
                        "pressure_Pa": P_pa,
                        "error": str(e),
                    }
                )

        if failures:
            print(f"\n{len(failures)} s_g validation failures:")
            for fail in failures[:5]:
                print(f"  {fail}")

        assert len(failures) == 0, (
            f"{len(failures)}/{len(saturation_reference_points)} s_g points failed"
        )

    def test_saturation_density_liquid_validation(self, saturation_reference_points):
        """Validate liquid density rho_f at saturation against reference data."""
        failures = []

        for point in saturation_reference_points:
            P_pa = point["pressure_Pa"]
            expected_rho_f = point["density_liquid_kg_per_m3"]

            try:
                sat_props = self.steam.T_sat(P_pa * ureg.Pa)
                calculated_rho_f = sat_props.density_liquid.to("kg/m**3").magnitude

                rel_error = abs(calculated_rho_f - expected_rho_f) / abs(expected_rho_f)

                if rel_error > self.tolerance:
                    failures.append(
                        {
                            "point_id": point.get("point_id", "unknown"),
                            "pressure_Pa": P_pa,
                            "expected_rho_f": expected_rho_f,
                            "calculated_rho_f": calculated_rho_f,
                            "rel_error": rel_error * 100,
                        }
                    )
            except Exception as e:
                failures.append(
                    {
                        "point_id": point.get("point_id", "unknown"),
                        "pressure_Pa": P_pa,
                        "error": str(e),
                    }
                )

        if failures:
            print(f"\n{len(failures)} rho_f validation failures:")
            for fail in failures[:5]:
                print(f"  {fail}")

        assert len(failures) == 0, (
            f"{len(failures)}/{len(saturation_reference_points)} rho_f points failed"
        )

    def test_saturation_density_vapor_validation(self, saturation_reference_points):
        """Validate vapor density rho_g at saturation against reference data."""
        failures = []

        for point in saturation_reference_points:
            P_pa = point["pressure_Pa"]
            expected_rho_g = point["density_vapor_kg_per_m3"]

            try:
                sat_props = self.steam.T_sat(P_pa * ureg.Pa)
                calculated_rho_g = sat_props.density_vapor.to("kg/m**3").magnitude

                rel_error = abs(calculated_rho_g - expected_rho_g) / abs(expected_rho_g)

                if rel_error > self.tolerance:
                    failures.append(
                        {
                            "point_id": point.get("point_id", "unknown"),
                            "pressure_Pa": P_pa,
                            "expected_rho_g": expected_rho_g,
                            "calculated_rho_g": calculated_rho_g,
                            "rel_error": rel_error * 100,
                        }
                    )
            except Exception as e:
                failures.append(
                    {
                        "point_id": point.get("point_id", "unknown"),
                        "pressure_Pa": P_pa,
                        "error": str(e),
                    }
                )

        if failures:
            print(f"\n{len(failures)} rho_g validation failures:")
            for fail in failures[:5]:
                print(f"  {fail}")

        assert len(failures) == 0, (
            f"{len(failures)}/{len(saturation_reference_points)} rho_g points failed"
        )

    def test_heat_of_vaporization_calculation(self, saturation_reference_points):
        """Validate heat of vaporization h_fg = h_g - h_f calculation."""
        for point in saturation_reference_points:
            P_pa = point["pressure_Pa"]

            sat_props = self.steam.T_sat(P_pa * ureg.Pa)

            # Calculate h_fg from method
            h_fg_method = sat_props.heat_of_vaporization().to("kJ/kg").magnitude

            # Calculate h_fg manually
            h_g = sat_props.enthalpy_vapor.to("kJ/kg").magnitude
            h_f = sat_props.enthalpy_liquid.to("kJ/kg").magnitude
            h_fg_manual = h_g - h_f

            # Should match exactly (both use same calculation)
            assert abs(h_fg_method - h_fg_manual) < 1e-6, (
                f"h_fg calculation mismatch at P={P_pa} Pa: {h_fg_method} vs {h_fg_manual}"
            )

    def test_saturation_pressure_range_validation(self):
        """Test saturation calculations at pressure boundaries."""
        # Minimum saturation pressure (triple point)
        min_P = 611.657  # Pa
        sat_low = self.steam.T_sat(min_P * ureg.Pa)
        assert sat_low.saturation_temperature.to("K").magnitude > 273.0

        # Maximum saturation pressure (near critical point)
        max_P = 22.064e6  # Pa (critical pressure)
        sat_high = self.steam.T_sat(max_P * ureg.Pa)
        assert sat_high.saturation_temperature.to("K").magnitude > 640.0

    def test_saturation_temperature_range_validation(self):
        """Test saturation calculations at temperature boundaries."""
        # Minimum saturation temperature (triple point)
        min_T = 273.16  # K
        sat_low = self.steam.P_sat(min_T * ureg.K)
        assert sat_low.saturation_pressure.to("Pa").magnitude > 600.0

        # Maximum saturation temperature (near critical point)
        max_T = 647.096  # K (critical temperature)
        sat_high = self.steam.P_sat(max_T * ureg.K)
        assert sat_high.saturation_pressure.to("MPa").magnitude > 20.0

    def test_invalid_saturation_pressure_raises_error(self):
        """Test that invalid saturation pressures raise InputRangeError."""
        # Negative pressure
        with pytest.raises(InputRangeError):
            self.steam.T_sat(-1000 * ureg.Pa)

        # Pressure above critical point
        with pytest.raises(InputRangeError):
            self.steam.T_sat(25e6 * ureg.Pa)

    def test_invalid_saturation_temperature_raises_error(self):
        """Test that invalid saturation temperatures raise InputRangeError."""
        # Below triple point
        with pytest.raises(InputRangeError):
            self.steam.P_sat(200 * ureg.K)

        # Above critical temperature
        with pytest.raises(InputRangeError):
            self.steam.P_sat(700 * ureg.K)
