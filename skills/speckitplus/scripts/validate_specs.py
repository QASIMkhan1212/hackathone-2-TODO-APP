#!/usr/bin/env python3
"""Validate SpecKit Plus specifications for consistency and completeness."""

import argparse
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class SpecValidation:
    """Overall specification validation results."""
    file: Path
    results: list[ValidationResult]

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results if r.severity == "error")

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if not r.passed and r.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for r in self.results if not r.passed and r.severity == "warning")


def check_frontmatter(content: str) -> ValidationResult:
    """Check if specification has proper frontmatter."""
    if content.startswith("# "):
        return ValidationResult(True, "Has title heading")
    return ValidationResult(False, "Missing title heading (# Title)")


def check_user_stories(content: str) -> ValidationResult:
    """Check for properly formatted user stories."""
    pattern = r"\*\*As a\*\*.*\*\*I want\*\*.*\*\*So that\*\*"
    if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
        return ValidationResult(True, "Contains user story format")
    return ValidationResult(
        False,
        "Missing user stories (As a... I want... So that...)",
        severity="warning"
    )


def check_acceptance_criteria(content: str) -> ValidationResult:
    """Check for acceptance criteria."""
    if "Acceptance Criteria" in content or "- [ ]" in content:
        return ValidationResult(True, "Contains acceptance criteria")
    return ValidationResult(
        False,
        "Missing acceptance criteria checkboxes",
        severity="warning"
    )


def check_overview(content: str) -> ValidationResult:
    """Check for overview section."""
    if "## Overview" in content or "## Description" in content:
        return ValidationResult(True, "Has overview section")
    return ValidationResult(
        False,
        "Missing overview/description section",
        severity="warning"
    )


def check_dependencies(content: str) -> ValidationResult:
    """Check for dependencies section."""
    if "## Dependencies" in content or "## Depends on" in content:
        return ValidationResult(True, "Has dependencies section")
    return ValidationResult(
        False,
        "Consider adding dependencies section",
        severity="info"
    )


def check_empty_placeholders(content: str) -> ValidationResult:
    """Check for unfilled placeholders."""
    placeholders = re.findall(r'\[.*?\]', content)
    unfilled = [p for p in placeholders if p not in ['[ ]', '[x]', '[X]']]
    template_markers = [p for p in unfilled if 'TODO' in p.upper() or p == '[...]']

    if template_markers:
        return ValidationResult(
            False,
            f"Contains unfilled placeholders: {', '.join(template_markers[:3])}",
            severity="warning"
        )
    return ValidationResult(True, "No unfilled template placeholders")


def validate_specification(file_path: Path) -> SpecValidation:
    """Validate a single specification file."""
    content = file_path.read_text(encoding="utf-8")

    results = [
        check_frontmatter(content),
        check_user_stories(content),
        check_acceptance_criteria(content),
        check_overview(content),
        check_dependencies(content),
        check_empty_placeholders(content),
    ]

    return SpecValidation(file=file_path, results=results)


def validate_project(project_path: Path) -> list[SpecValidation]:
    """Validate all specifications in a project."""
    spec_path = project_path / ".speckit" / "specifications"

    if not spec_path.exists():
        print(f"Error: No specifications directory found at {spec_path}")
        return []

    validations = []
    for spec_file in spec_path.glob("**/*.md"):
        validations.append(validate_specification(spec_file))

    return validations


def print_results(validations: list[SpecValidation]) -> None:
    """Print validation results."""
    total_errors = 0
    total_warnings = 0

    for validation in validations:
        print(f"\n{'=' * 50}")
        print(f"File: {validation.file}")
        print(f"{'=' * 50}")

        for result in validation.results:
            if result.passed:
                icon = "[PASS]"
            elif result.severity == "error":
                icon = "[FAIL]"
                total_errors += 1
            elif result.severity == "warning":
                icon = "[WARN]"
                total_warnings += 1
            else:
                icon = "[INFO]"

            print(f"  {icon} {result.message}")

    print(f"\n{'=' * 50}")
    print(f"Summary: {len(validations)} files validated")
    print(f"  Errors: {total_errors}")
    print(f"  Warnings: {total_warnings}")

    if total_errors == 0:
        print("\nValidation PASSED")
    else:
        print("\nValidation FAILED")


def main():
    parser = argparse.ArgumentParser(
        description="Validate SpecKit Plus specifications"
    )
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path.cwd(),
        help="Project path or specification file (default: current directory)"
    )

    args = parser.parse_args()
    path = args.path

    if path.is_file():
        validations = [validate_specification(path)]
    else:
        validations = validate_project(path)

    if validations:
        print_results(validations)
    else:
        print("No specifications found to validate.")


if __name__ == "__main__":
    main()
