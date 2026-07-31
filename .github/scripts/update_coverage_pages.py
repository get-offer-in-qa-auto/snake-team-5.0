#!/usr/bin/env python3
"""Add one coverage.py report to the persistent GitHub Pages site."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

from pages_navigation import decorate_published_reports

SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")


def safe_id(value: str) -> str:
    if not SAFE_ID_PATTERN.fullmatch(value):
        raise ValueError(
            "report id must contain only letters, numbers, '.', '_', or '-'"
        )
    return value


def copy_coverage_report(source: Path, destination: Path) -> None:
    required_files = (
        source / "coverage.json",
        source / "coverage.xml",
        source / "html" / "index.html",
    )
    missing = [path.name for path in required_files if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "coverage artifact is incomplete; missing: " + ", ".join(missing)
        )
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def append_github_output(report_path: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            output.write(f"coverage_report_path={report_path}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", required=True, type=Path)
    parser.add_argument("--coverage-dir", required=True, type=Path)
    parser.add_argument("--report-id", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--event", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--source", default="src/main/api")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_id = safe_id(args.report_id)
    report_path = f"coverage/{report_id}"
    destination = args.site_dir / report_path
    copy_coverage_report(args.coverage_dir, destination)

    metadata = {
        "branch": args.branch,
        "event": args.event,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "report_id": report_id,
        "run_url": args.run_url,
        "sha": args.sha,
        "source": args.source,
        "workflow": args.workflow,
    }
    destination.joinpath("metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.site_dir / ".nojekyll").touch()
    allure_pages, coverage_pages = decorate_published_reports(args.site_dir)
    append_github_output(report_path)
    print(f"Coverage report path: {report_path}")
    print(
        "Return navigation refreshed: "
        f"{allure_pages} Allure pages, {coverage_pages} coverage pages."
    )


if __name__ == "__main__":
    main()
