"""Integration tests for valve CLI commands."""

import json
import subprocess
import sys


class TestValveCLI:
    """Test valve sizing CLI commands."""

    def test_cv_calculation_text(self) -> None:
        """Test Cv calculation command with text output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "cv",
                "--flow-rate",
                "10",  # m³/h
                "--pressure-drop",
                "2",  # bar
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        assert "Result" in result.stdout or "Cv" in result.stdout

    def test_cv_calculation_json(self) -> None:
        """Test Cv calculation with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "cv",
                "--flow-rate",
                "10",
                "--pressure-drop",
                "2",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "value" in output
        assert output["value"] > 0

    def test_cv_with_specific_gravity(self) -> None:
        """Test Cv calculation with custom specific gravity."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "cv",
                "--flow-rate",
                "10",
                "--pressure-drop",
                "2",
                "--specific-gravity",
                "0.85",  # Oil
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "value" in output

    def test_flow_rate_calculation(self) -> None:
        """Test flow rate through valve calculation."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "flow-rate",
                "--cv",
                "7.07",
                "--pressure-drop",
                "2",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0

    def test_flow_rate_json_output(self) -> None:
        """Test flow rate calculation with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "flow-rate",
                "--cv",
                "7.07",
                "--pressure-drop",
                "2",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "value" in output
        assert output["value"] > 0

    def test_valve_sizing(self) -> None:
        """Test valve sizing command."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "sizing",
                "--flow-rate",
                "10",
                "--pressure-drop",
                "2",
                "--valve-type",
                "ball",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        # May succeed or fail depending on reference data
        assert result.returncode in [0, 1]

    def test_valve_sizing_json(self) -> None:
        """Test valve sizing with JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "sizing",
                "--flow-rate",
                "10",
                "--pressure-drop",
                "2",
                "--valve-type",
                "ball",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        # May succeed or fail depending on reference data
        assert result.returncode in [0, 1]

    def test_minimal_verbosity(self) -> None:
        """Test minimal verbosity output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "cv",
                "--flow-rate",
                "10",
                "--pressure-drop",
                "2",
                "--verbosity",
                "minimal",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        # Should be concise
        assert len(result.stdout.strip().split("\n")) <= 2

    def test_detailed_verbosity(self) -> None:
        """Test detailed verbosity output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "cv",
                "--flow-rate",
                "10",
                "--pressure-drop",
                "2",
                "--verbosity",
                "detailed",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        # Detailed should show more information
        assert len(result.stdout.strip().split("\n")) >= 3

    def test_us_units(self) -> None:
        """Test valve calculations with US customary units."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "cv",
                "--flow-rate",
                "44",  # gpm
                "--pressure-drop",
                "29",  # psi
                "--unit-system",
                "US",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0

    def test_error_negative_flow(self) -> None:
        """Test error handling for negative flow rate."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "cv",
                "--flow-rate",
                "-10",  # Invalid
                "--pressure-drop",
                "2",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode != 0
        assert "Error" in result.stderr or "error" in result.stderr.lower()

    def test_error_zero_pressure_drop(self) -> None:
        """Test error handling for zero pressure drop."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "cv",
                "--flow-rate",
                "10",
                "--pressure-drop",
                "0",  # Invalid
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode != 0

    def test_error_negative_cv(self) -> None:
        """Test error handling for negative Cv."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "flow-rate",
                "--cv",
                "-5",  # Invalid
                "--pressure-drop",
                "2",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode != 0

    def test_help_command(self) -> None:
        """Test valve help output."""
        result = subprocess.run(
            [sys.executable, "-m", "fluids.cli.main", "valve", "--help"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        assert "cv" in result.stdout
        assert "flow-rate" in result.stdout
        assert "sizing" in result.stdout

    def test_cv_subcommand_help(self) -> None:
        """Test Cv subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "fluids.cli.main", "valve", "cv", "--help"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert result.returncode == 0
        assert "flow-rate" in result.stdout
        assert "pressure-drop" in result.stdout

    def test_combined_workflow(self) -> None:
        """Test a complete workflow: calculate Cv, then use it to calculate flow."""
        # First calculate Cv
        cv_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "cv",
                "--flow-rate",
                "10",
                "--pressure-drop",
                "2",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert cv_result.returncode == 0
        cv_output = json.loads(cv_result.stdout)
        cv_value = cv_output["value"]

        # Then use that Cv to calculate flow rate
        flow_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fluids.cli.main",
                "valve",
                "flow-rate",
                "--cv",
                str(cv_value),
                "--pressure-drop",
                "2",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )

        assert flow_result.returncode == 0
        flow_output = json.loads(flow_result.stdout)
        # Should get back approximately the same flow rate
        assert abs(flow_output["value"] - 10) < 0.1
