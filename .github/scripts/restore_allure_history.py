#!/usr/bin/env python3
"""Restore Allure history from the latest published report for one suite."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-").lower()
    if not slug:
        raise ValueError("slug value must contain at least one safe character")
    return slug


def load_suite_reports(site_dir: Path, suite: str) -> list[dict[str, str]]:
    reports: list[dict[str, str]] = []
    suite_dir = site_dir / "reports" / suite
    if not suite_dir.is_dir():
        return reports

    for metadata_path in sorted(suite_dir.glob("*/metadata.json")):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        metadata["path"] = metadata_path.parent.as_posix()
        reports.append(metadata)

    return sorted(
        reports,
        key=lambda item: (item.get("generated_at", ""), item.get("report_id", "")),
        reverse=True,
    )


def restore_history(site_dir: Path, suite: str, results_dir: Path) -> bool:
    for report in load_suite_reports(site_dir, suite):
        history_dir = Path(report["path"]) / "history"
        if history_dir.is_dir():
            destination = results_dir / "history"
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(history_dir, destination)
            print(f"Restored Allure history from {history_dir}")
            return True

    print(f"No previous Allure history found for suite '{suite}'.")
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", required=True, type=Path)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--results-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    restore_history(
        site_dir=args.site_dir,
        suite=slugify(args.suite),
        results_dir=args.results_dir,
    )


if __name__ == "__main__":
    main()
