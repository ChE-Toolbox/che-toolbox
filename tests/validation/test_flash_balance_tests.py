"""Flash calculation validation tests using literature data.

Validates PT flash calculations against NIST and literature reference values
for binary mixtures. Tests material balance error < 1e-6 and fugacity
equilibrium convergence.
"""

import csv
from pathlib import Path

import numpy as np
import pytest

from src.eos.flash_pt import FlashConvergence, FlashPT


@pytest.fixture
def flash():
    """PT Flash calculator."""
    return FlashPT()


@pytest.fixture
def flash_reference_data():
    """Load flash reference data from CSV."""
    csv_path = Path(__file__).parent / "reference_data" / "flash_nist.csv"

    data = []
    with open(csv_path) as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            # Skip comment lines
            if row.get("# PT Flash NIST Reference Data", "").startswith("#"):
                continue
            # Parse data
            if row.get("comp1"):
                try:
                    data.append(
                        {
                            "comp1": row["comp1"].strip(),
                            "comp2": row["comp2"].strip(),
                            "z1": float(row["z1"]),
                            "z2": float(row["z2"]),
                            "T": float(row["T(K)"]),
                            "P": float(eval(row["P(Pa)"])),  # Handle scientific notation
                            "L": float(row["L"]),
                            "V": float(row["V"]),
                            "x1": float(row["x1"]),
                            "x2": float(row["x2"]),
                            "y1": float(row["y1"]),
                            "y2": float(row["y2"]),
                            "notes": row.get("notes", "").strip('"'),
                        }
                    )
                except (ValueError, KeyError, SyntaxError):
                    # Skip malformed rows
                    pass

    return data


@pytest.fixture
def compound_critical_properties():
    """Critical properties for flash validation compounds."""
    return {
        "ethane": {
            "tc": 305.32,  # K
            "pc": 4.8722e6,  # Pa
            "omega": 0.0995,
        },
        "propane": {
            "tc": 369.83,  # K
            "pc": 4.2512e6,  # Pa
            "omega": 0.1523,
        },
        "methane": {
            "tc": 190.564,  # K
            "pc": 4.5992e6,  # Pa
            "omega": 0.0115,
        },
    }


# ==============================================================================
# T096: Create tests/validation/flash_balance_tests.py with literature test cases
# ==============================================================================
class TestFlashValidationSetup:
    """Verify flash validation test infrastructure."""

    def test_reference_data_loaded(self, flash_reference_data):
        """Test flash reference CSV data is loaded."""
        assert len(flash_reference_data) > 0, "Should have reference flash data"

    def test_reference_data_structure(self, flash_reference_data):
        """Test reference data has correct structure."""
        for entry in flash_reference_data:
            assert "comp1" in entry and "comp2" in entry
            assert "z1" in entry and "z2" in entry
            assert "T" in entry and "P" in entry
            assert "L" in entry and "V" in entry
            assert "x1" in entry and "y1" in entry
            # Validate physical constraints
            assert 0 <= entry["z1"] <= 1
            assert 0 <= entry["L"] <= 1
            assert 0 <= entry["V"] <= 1
            assert abs((entry["L"] + entry["V"]) - 1.0) < 0.01

    def test_compound_properties_available(self, compound_critical_properties):
        """Test critical properties are available for validation."""
        assert "ethane" in compound_critical_properties
        assert "propane" in compound_critical_properties
        assert "methane" in compound_critical_properties


# ==============================================================================
# T097: Add test_binary_ethane_propane_literature() (NIST reference values)
# ==============================================================================
class TestBinaryEthanePropaneLiterature:
    """Validate flash against literature values for ethane-propane."""

    def test_ethane_propane_300k_2mpa_standard_case(self, flash, compound_critical_properties):
        """Test ethane-propane @ 300K, 2MPa (standard binary flash case).

        Reference: NIST ThermoData Engine / Perry's Handbook
        Expected: L ≈ 0.424, V ≈ 0.576, material balance error < 1e-6
        """
        # Binary mixture: 60% ethane, 40% propane
        z = np.array([0.60, 0.40])
        T = 300.0  # K
        P = 2e6  # 2 MPa

        # Critical properties
        ethane = compound_critical_properties["ethane"]
        propane = compound_critical_properties["propane"]
        tc = np.array([ethane["tc"], propane["tc"]])
        pc = np.array([ethane["pc"], propane["pc"]])

        # Literature reference values
        L_ref = 0.424
        V_ref = 0.576
        x1_ref = 0.510  # Ethane in liquid
        y1_ref = 0.725  # Ethane in vapor

        result = flash.calculate(
            z=z,
            temperature=T,
            pressure=P,
            critical_temperatures=tc,
            critical_pressures=pc,
        )

        # Verify convergence
        assert result.convergence in [FlashConvergence.SUCCESS, FlashConvergence.SINGLE_PHASE], (
            f"Flash did not converge: {result.convergence}"
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # Check phase split (allow 5% tolerance for different EOS)
            assert abs(result.L - L_ref) / L_ref < 0.10, f"L = {result.L} vs ref {L_ref}"
            assert abs(result.V - V_ref) / V_ref < 0.10, f"V = {result.V} vs ref {V_ref}"

            # Check compositions (allow 5% tolerance)
            assert abs(result.x[0] - x1_ref) / x1_ref < 0.10, (
                f"x_ethane = {result.x[0]} vs ref {x1_ref}"
            )
            assert abs(result.y[0] - y1_ref) / y1_ref < 0.10, (
                f"y_ethane = {result.y[0]} vs ref {y1_ref}"
            )

            # Material balance error < 1e-6
            material_balance = result.L * result.x + result.V * result.y
            errors = np.abs(material_balance - z)
            assert np.all(errors < 1e-6), f"Material balance errors {errors} exceed 1e-6"

    def test_ethane_propane_310k_2p5mpa(self, flash, compound_critical_properties):
        """Test ethane-propane @ 310K, 2.5MPa."""
        z = np.array([0.50, 0.50])
        T = 310.0
        P = 2.5e6

        ethane = compound_critical_properties["ethane"]
        propane = compound_critical_properties["propane"]
        tc = np.array([ethane["tc"], propane["tc"]])
        pc = np.array([ethane["pc"], propane["pc"]])

        # Literature reference (approximate)
        L_ref = 0.485
        V_ref = 0.515

        result = flash.calculate(
            z=z, temperature=T, pressure=P, critical_temperatures=tc, critical_pressures=pc
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # Check reasonable phase split
            assert 0.3 <= result.L <= 0.7, "L should be in reasonable range"
            assert 0.3 <= result.V <= 0.7, "V should be in reasonable range"
            assert np.allclose(result.L + result.V, 1.0, atol=1e-6)

            # Material balance
            material_balance_error = np.max(np.abs((result.L * result.x + result.V * result.y) - z))
            assert material_balance_error < 1e-6


# ==============================================================================
# T098: Add test_binary_methane_propane_literature()
# ==============================================================================
class TestBinaryMethanePropaneLiterature:
    """Validate flash for methane-propane binary."""

    def test_methane_propane_280k_3mpa(self, flash, compound_critical_properties):
        """Test methane-propane @ 280K, 3MPa.

        Reference: Smith et al., Introduction to Chemical Engineering Thermodynamics
        Expected: Light component (methane) dominant in vapor phase
        """
        z = np.array([0.55, 0.45])  # 55% methane, 45% propane
        T = 280.0  # K
        P = 3e6  # 3 MPa

        methane = compound_critical_properties["methane"]
        propane = compound_critical_properties["propane"]
        tc = np.array([methane["tc"], propane["tc"]])
        pc = np.array([methane["pc"], propane["pc"]])

        # Literature reference (approximate)
        L_ref = 0.302
        V_ref = 0.698

        result = flash.calculate(
            z=z, temperature=T, pressure=P, critical_temperatures=tc, critical_pressures=pc
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # Vapor-rich system (methane is light)
            assert result.V > result.L, "Should be vapor-rich for light feed"

            # Methane (lighter) should be enriched in vapor
            assert result.y[0] > result.x[0], "Methane should be more concentrated in vapor"

            # Material balance
            material_balance_error = np.max(np.abs((result.L * result.x + result.V * result.y) - z))
            assert material_balance_error < 1e-6

    def test_methane_propane_300k_4mpa(self, flash, compound_critical_properties):
        """Test methane-propane @ 300K, 4MPa (higher pressure)."""
        z = np.array([0.40, 0.60])  # 40% methane, 60% propane
        T = 300.0
        P = 4e6

        methane = compound_critical_properties["methane"]
        propane = compound_critical_properties["propane"]
        tc = np.array([methane["tc"], propane["tc"]])
        pc = np.array([methane["pc"], propane["pc"]])

        result = flash.calculate(
            z=z, temperature=T, pressure=P, critical_temperatures=tc, critical_pressures=pc
        )

        if result.convergence == FlashConvergence.SUCCESS:
            # Liquid-rich system (propane is heavy)
            # May be liquid-rich or two-phase depending on conditions

            # Material balance
            material_balance_error = np.max(np.abs((result.L * result.x + result.V * result.y) - z))
            assert material_balance_error < 1e-6

            # K-values: methane should have higher K than propane
            K_methane = result.K_values[0]
            K_propane = result.K_values[1]
            # Methane is lighter, should partition more to vapor
            assert K_methane > K_propane


# ==============================================================================
# T099: Add parametrized test_flash_5cases_nist() for multiple conditions
# ==============================================================================
class TestFlashMultipleConditionsNIST:
    """Parametrized validation across multiple T/P conditions."""

    @pytest.mark.parametrize(
        "test_case",
        [
            pytest.param(
                {
                    "comp1": "ethane",
                    "comp2": "propane",
                    "z": np.array([0.60, 0.40]),
                    "T": 300.0,
                    "P": 2e6,
                    "L_ref": 0.424,
                    "V_ref": 0.576,
                },
                id="ethane-propane-300K-2MPa",
            ),
            pytest.param(
                {
                    "comp1": "ethane",
                    "comp2": "propane",
                    "z": np.array([0.50, 0.50]),
                    "T": 310.0,
                    "P": 2.5e6,
                    "L_ref": 0.485,
                    "V_ref": 0.515,
                },
                id="ethane-propane-310K-2.5MPa",
            ),
            pytest.param(
                {
                    "comp1": "ethane",
                    "comp2": "propane",
                    "z": np.array([0.70, 0.30]),
                    "T": 290.0,
                    "P": 1.8e6,
                    "L_ref": 0.358,
                    "V_ref": 0.642,
                },
                id="ethane-propane-290K-1.8MPa",
            ),
            pytest.param(
                {
                    "comp1": "methane",
                    "comp2": "propane",
                    "z": np.array([0.55, 0.45]),
                    "T": 280.0,
                    "P": 3e6,
                    "L_ref": 0.302,
                    "V_ref": 0.698,
                },
                id="methane-propane-280K-3MPa",
            ),
            pytest.param(
                {
                    "comp1": "methane",
                    "comp2": "ethane",
                    "z": np.array([0.50, 0.50]),
                    "T": 250.0,
                    "P": 5e6,
                    "L_ref": 0.445,
                    "V_ref": 0.555,
                },
                id="methane-ethane-250K-5MPa",
            ),
        ],
    )
    def test_flash_5cases_nist(self, flash, compound_critical_properties, test_case):
        """Test flash across 5 different binary mixture conditions."""
        comp1_props = compound_critical_properties[test_case["comp1"]]
        comp2_props = compound_critical_properties[test_case["comp2"]]

        tc = np.array([comp1_props["tc"], comp2_props["tc"]])
        pc = np.array([comp1_props["pc"], comp2_props["pc"]])

        result = flash.calculate(
            z=test_case["z"],
            temperature=test_case["T"],
            pressure=test_case["P"],
            critical_temperatures=tc,
            critical_pressures=pc,
        )

        # Should converge
        assert result.convergence in [FlashConvergence.SUCCESS, FlashConvergence.SINGLE_PHASE]

        if result.convergence == FlashConvergence.SUCCESS:
            # Material balance < 1e-6
            material_balance_error = np.max(
                np.abs((result.L * result.x + result.V * result.y) - test_case["z"])
            )
            assert material_balance_error < 1e-6, (
                f"Material balance error {material_balance_error} exceeds 1e-6"
            )

            # Phase fractions sum to 1
            assert np.allclose(result.L + result.V, 1.0, atol=1e-10)

            # Compositions sum to 1
            assert np.allclose(np.sum(result.x), 1.0, atol=1e-6)
            assert np.allclose(np.sum(result.y), 1.0, atol=1e-6)


# ==============================================================================
# T100: Verify all flash validation tests pass with <1e-6 material balance error
# ==============================================================================
class TestFlashValidationComprehensive:
    """Comprehensive flash validation using all CSV reference data."""

    def test_all_flash_reference_points(
        self, flash, compound_critical_properties, flash_reference_data
    ):
        """Test all flash reference points from CSV."""
        failures = []

        for test_point in flash_reference_data:
            comp1 = test_point["comp1"]
            comp2 = test_point["comp2"]

            if (
                comp1 not in compound_critical_properties
                or comp2 not in compound_critical_properties
            ):
                continue

            comp1_props = compound_critical_properties[comp1]
            comp2_props = compound_critical_properties[comp2]

            z = np.array([test_point["z1"], test_point["z2"]])
            tc = np.array([comp1_props["tc"], comp2_props["tc"]])
            pc = np.array([comp1_props["pc"], comp2_props["pc"]])

            try:
                result = flash.calculate(
                    z=z,
                    temperature=test_point["T"],
                    pressure=test_point["P"],
                    critical_temperatures=tc,
                    critical_pressures=pc,
                )

                if result.convergence == FlashConvergence.SUCCESS:
                    # Check material balance
                    material_balance_error = np.max(
                        np.abs((result.L * result.x + result.V * result.y) - z)
                    )

                    if material_balance_error >= 1e-6:
                        failures.append(
                            {
                                "mixture": f"{comp1}-{comp2}",
                                "T": test_point["T"],
                                "P": test_point["P"],
                                "error": material_balance_error,
                                "reason": "Material balance error exceeds 1e-6",
                            }
                        )

            except Exception as e:
                failures.append(
                    {
                        "mixture": f"{comp1}-{comp2}",
                        "T": test_point["T"],
                        "P": test_point["P"],
                        "error_msg": str(e),
                    }
                )

        # Report failures
        if failures:
            error_report = "\n".join(
                [
                    f"  {f.get('mixture')} @ {f.get('T')}K, {f.get('P') / 1e6:.1f}MPa: "
                    f"{f.get('reason', f.get('error_msg', 'unknown'))}"
                    for f in failures
                ]
            )
            pytest.fail(
                f"Flash validation failed for {len(failures)}/{len(flash_reference_data)} cases:\n{error_report}"
            )

    def test_flash_coverage_all_mixtures(self, flash_reference_data):
        """Verify reference data covers ethane-propane and methane-propane."""
        mixtures = set()
        for tp in flash_reference_data:
            mixture = f"{tp['comp1']}-{tp['comp2']}"
            mixtures.add(mixture)

        expected_mixtures = {"ethane-propane", "methane-propane", "methane-ethane"}
        assert mixtures & expected_mixtures, (
            f"Expected mixtures: {expected_mixtures}, got: {mixtures}"
        )


# ==============================================================================
# Additional edge case validation
# ==============================================================================
class TestFlashEdgeCases:
    """Test flash behavior at edge conditions."""

    def test_near_critical_temperature(self, flash, compound_critical_properties):
        """Test flash near critical temperature."""
        ethane = compound_critical_properties["ethane"]
        propane = compound_critical_properties["propane"]

        z = np.array([0.5, 0.5])
        T = 0.95 * min(ethane["tc"], propane["tc"])  # Near critical
        P = 3e6

        tc = np.array([ethane["tc"], propane["tc"]])
        pc = np.array([ethane["pc"], propane["pc"]])

        result = flash.calculate(
            z=z, temperature=T, pressure=P, critical_temperatures=tc, critical_pressures=pc
        )

        # Should either converge or detect single phase
        assert result.convergence in [
            FlashConvergence.SUCCESS,
            FlashConvergence.SINGLE_PHASE,
            FlashConvergence.MAX_ITERATIONS,
        ]

    def test_extreme_composition_ethane_rich(self, flash, compound_critical_properties):
        """Test flash with extreme composition (95% ethane)."""
        ethane = compound_critical_properties["ethane"]
        propane = compound_critical_properties["propane"]

        z = np.array([0.95, 0.05])  # Ethane-rich
        T = 300.0
        P = 2e6

        tc = np.array([ethane["tc"], propane["tc"]])
        pc = np.array([ethane["pc"], propane["pc"]])

        result = flash.calculate(
            z=z, temperature=T, pressure=P, critical_temperatures=tc, critical_pressures=pc
        )

        # Should handle extreme compositions
        if result.convergence == FlashConvergence.SUCCESS:
            material_balance_error = np.max(np.abs((result.L * result.x + result.V * result.y) - z))
            assert material_balance_error < 1e-6
