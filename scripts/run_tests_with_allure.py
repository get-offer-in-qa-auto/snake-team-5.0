#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_RESULTS_DIR = Path("artifacts/allure-results")
DEFAULT_REPORT_DIR = Path("artifacts/allure-report")


def has_files(path: Path) -> bool:
    return path.is_dir() and any(item.is_file() for item in path.rglob("*"))


def run_pytest(marker: str | None, results_dir: Path, pytest_args: list[str]) -> int:
    command = [
        sys.executable,
        "-m",
        "pytest",
        f"--alluredir={results_dir}",
        "--clean-alluredir",
    ]

    if marker:
        command.extend(["-m", marker])

    command.extend(pytest_args or ["tests"])

    return subprocess.run(command, check=False).returncode


def generate_allure_report(results_dir: Path, report_dir: Path) -> int:
    allure_command = shutil.which("allure")
    if allure_command is None:
        print(
            "Allure commandline is not installed. "
            "Install it and run: allure generate "
            f"{results_dir} --clean -o {report_dir}",
            file=sys.stderr,
        )
        return 0

    if not has_files(results_dir):
        print(f"No Allure results found in {results_dir}; report generation skipped.")
        return 0

    return subprocess.run(
        [
            allure_command,
            "generate",
            str(results_dir),
            "--clean",
            "-o",
            str(report_dir),
        ],
        check=False,
    ).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run pytest and immediately generate an Allure HTML report."
    )
    parser.add_argument(
        "-m",
        "--marker",
        help="Pytest marker expression, for example: smoke or regression.",
    )
    parser.add_argument(
        "--allure-results",
        default=str(DEFAULT_RESULTS_DIR),
        help="Directory with Allure result files created by pytest.",
    )
    parser.add_argument(
        "--allure-report",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory where the generated Allure HTML report will be saved.",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Extra pytest arguments. Use '--' before arguments when needed.",
    )
    args = parser.parse_args()

    pytest_args = args.pytest_args
    if pytest_args[:1] == ["--"]:
        pytest_args = pytest_args[1:]

    results_dir = Path(args.allure_results)
    report_dir = Path(args.allure_report)

    pytest_exit_code = run_pytest(args.marker, results_dir, pytest_args)
    report_exit_code = generate_allure_report(
        results_dir,
        report_dir,
    )

    return pytest_exit_code or report_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
