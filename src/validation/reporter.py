"""Validation result reporting and analysis."""

import logging
from dataclasses import dataclass

from .models import ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    """Summary statistics for validation results."""

    total_tests: int
    passed_tests: int
    failed_tests: int
    z_factor_passed: int
    z_factor_failed: int
    fugacity_passed: int
    fugacity_failed: int
    min_z_deviation: float | None
    max_z_deviation: float | None
    avg_z_deviation: float | None
    min_fugacity_deviation: float | None
    max_fugacity_deviation: float | None
    avg_fugacity_deviation: float | None

    @property
    def overall_pass_rate(self) -> float:
        """Calculate overall pass rate."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100.0

    @property
    def z_factor_pass_rate(self) -> float:
        """Calculate Z factor pass rate."""
        total = self.z_factor_passed + self.z_factor_failed
        if total == 0:
            return 0.0
        return (self.z_factor_passed / total) * 100.0

    @property
    def fugacity_pass_rate(self) -> float:
        """Calculate fugacity pass rate."""
        total = self.fugacity_passed + self.fugacity_failed
        if total == 0:
            return 0.0
        return (self.fugacity_passed / total) * 100.0


class ValidationReporter:
    """Generate validation reports and statistics."""

    @staticmethod
    def generate_report(results: list[ValidationResult]) -> ValidationReport:
        """Generate summary report from validation results.

        Parameters
        ----------
        results : list[ValidationResult]
            List of validation results

        Returns
        -------
        ValidationReport
            Summary statistics
        """
        if not results:
            return ValidationReport(
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                z_factor_passed=0,
                z_factor_failed=0,
                fugacity_passed=0,
                fugacity_failed=0,
                min_z_deviation=None,
                max_z_deviation=None,
                avg_z_deviation=None,
                min_fugacity_deviation=None,
                max_fugacity_deviation=None,
                avg_fugacity_deviation=None,
            )

        # Count results
        passed = sum(1 for r in results if r.z_factor_passed or r.fugacity_passed)
        failed = len(results) - passed

        # Z factor analysis
        z_passed = sum(1 for r in results if r.z_factor_passed)
        z_failed = sum(
            1 for r in results if not r.z_factor_passed and r.calculated_z_factor is not None
        )

        z_deviations = [r.z_factor_deviation for r in results if r.z_factor_deviation is not None]
        min_z_dev = min(z_deviations) if z_deviations else None
        max_z_dev = max(z_deviations) if z_deviations else None
        avg_z_dev = sum(z_deviations) / len(z_deviations) if z_deviations else None

        # Fugacity analysis
        fug_passed = sum(1 for r in results if r.fugacity_passed)
        fug_failed = sum(
            1 for r in results if not r.fugacity_passed and r.calculated_fugacity is not None
        )

        fug_deviations = [r.fugacity_deviation for r in results if r.fugacity_deviation is not None]
        min_fug_dev = min(fug_deviations) if fug_deviations else None
        max_fug_dev = max(fug_deviations) if fug_deviations else None
        avg_fug_dev = sum(fug_deviations) / len(fug_deviations) if fug_deviations else None

        return ValidationReport(
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=failed,
            z_factor_passed=z_passed,
            z_factor_failed=z_failed,
            fugacity_passed=fug_passed,
            fugacity_failed=fug_failed,
            min_z_deviation=min_z_dev,
            max_z_deviation=max_z_dev,
            avg_z_deviation=avg_z_dev,
            min_fugacity_deviation=min_fug_dev,
            max_fugacity_deviation=max_fug_dev,
            avg_fugacity_deviation=avg_fug_dev,
        )

    @staticmethod
    def format_report(report: ValidationReport) -> str:
        """Format report as human-readable text.

        Parameters
        ----------
        report : ValidationReport
            Report to format

        Returns
        -------
        str
            Formatted report
        """
        lines = [
            "=" * 70,
            "NIST VALIDATION REPORT",
            "=" * 70,
            "",
            "Overall Results",
            f"  Total Tests:      {report.total_tests}",
            f"  Passed:           {report.passed_tests}",
            f"  Failed:           {report.failed_tests}",
            f"  Pass Rate:        {report.overall_pass_rate:.1f}%",
            "",
            "Z Factor Validation",
            f"  Passed:           {report.z_factor_passed}",
            f"  Failed:           {report.z_factor_failed}",
            f"  Pass Rate:        {report.z_factor_pass_rate:.1f}%",
        ]

        if report.min_z_deviation is not None:
            lines.extend(
                [
                    f"  Min Deviation:    {report.min_z_deviation:.4f} ({report.min_z_deviation * 100:.2f}%)",
                    f"  Max Deviation:    {report.max_z_deviation:.4f} ({report.max_z_deviation * 100:.2f}%)",
                    f"  Avg Deviation:    {report.avg_z_deviation:.4f} ({report.avg_z_deviation * 100:.2f}%)",
                ]
            )

        lines.extend(
            [
                "",
                "Fugacity Validation",
                f"  Passed:           {report.fugacity_passed}",
                f"  Failed:           {report.fugacity_failed}",
                f"  Pass Rate:        {report.fugacity_pass_rate:.1f}%",
            ]
        )

        if report.min_fugacity_deviation is not None:
            lines.extend(
                [
                    f"  Min Deviation:    {report.min_fugacity_deviation:.4f} ({report.min_fugacity_deviation * 100:.2f}%)",
                    f"  Max Deviation:    {report.max_fugacity_deviation:.4f} ({report.max_fugacity_deviation * 100:.2f}%)",
                    f"  Avg Deviation:    {report.avg_fugacity_deviation:.4f} ({report.avg_fugacity_deviation * 100:.2f}%)",
                ]
            )

        lines.extend(["", "=" * 70])

        return "\n".join(lines)

    @staticmethod
    def print_report(report: ValidationReport) -> None:
        """Print formatted report to logger.

        Parameters
        ----------
        report : ValidationReport
            Report to print
        """
        logger.info(ValidationReporter.format_report(report))
