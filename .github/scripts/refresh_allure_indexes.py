#!/usr/bin/env python3
"""Refresh Allure Pages indexes after adding non-report content."""

from __future__ import annotations

import argparse
from pathlib import Path

from update_allure_pages import load_reports, write_indexes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    write_indexes(args.site_dir, load_reports(args.site_dir))
    print("Refreshed Allure indexes.")


if __name__ == "__main__":
    main()
