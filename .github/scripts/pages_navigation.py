#!/usr/bin/env python3
"""Add consistent return navigation to published report pages."""

from __future__ import annotations

import html
import os
import re
from collections.abc import Iterable
from pathlib import Path

NAVIGATION_MARKER = "data-qa-pages-navigation"

NAVIGATION_CSS = """
<style data-qa-pages-navigation>
  [data-qa-pages-navigation-links] {
    all: initial;
    position: fixed;
    right: 16px;
    bottom: 16px;
    z-index: 2147483647;
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 6px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 10px;
    background: rgba(31, 35, 40, 0.92);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.24);
    backdrop-filter: blur(8px);
    font: 600 13px/1.25 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }
  [data-qa-pages-navigation-links] a {
    all: unset;
    display: inline-block;
    padding: 7px 10px;
    border-radius: 7px;
    color: #ffffff;
    cursor: pointer;
    white-space: nowrap;
  }
  [data-qa-pages-navigation-links] a:hover,
  [data-qa-pages-navigation-links] a:focus-visible {
    background: rgba(255, 255, 255, 0.14);
    text-decoration: none;
    outline: none;
  }
  @media (max-width: 520px) {
    [data-qa-pages-navigation-links] {
      right: 8px;
      bottom: 8px;
      max-width: calc(100vw - 16px);
      overflow-x: auto;
    }
  }
</style>
""".strip()


def relative_directory_url(page: Path, destination: Path) -> str:
    """Return a Pages-safe relative URL from an HTML page to a directory."""
    relative = os.path.relpath(destination, start=page.parent)
    return relative.replace(os.sep, "/").rstrip("/") + "/"


def inject_navigation(
    page: Path,
    links: Iterable[tuple[str, Path]],
) -> bool:
    """Inject fixed return links into one HTML page, once."""
    content = page.read_text(encoding="utf-8")
    if NAVIGATION_MARKER in content:
        return False

    rendered_links = "".join(
        (
            f'<a href="{html.escape(relative_directory_url(page, destination))}">'
            f"{html.escape(label)}</a>"
        )
        for label, destination in links
    )
    navigation = (
        f"\n{NAVIGATION_CSS}\n"
        f"<nav {NAVIGATION_MARKER} data-qa-pages-navigation-links "
        f'aria-label="QA report navigation">{rendered_links}</nav>\n'
    )
    closing_body = re.search(r"</body\s*>", content, flags=re.IGNORECASE)
    if closing_body is None:
        updated = content + navigation
    else:
        updated = (
            content[: closing_body.start()]
            + navigation
            + content[closing_body.start() :]
        )
    page.write_text(updated, encoding="utf-8")
    return True


def decorate_allure_reports(site_dir: Path) -> int:
    """Add QA and report-index links to every archived Allure SPA."""
    updated = 0
    for metadata_path in sorted((site_dir / "reports").glob("*/*/metadata.json")):
        suite = metadata_path.parent.parent.name
        if suite == "postgresql-regression":
            links = (
                ("← PostgreSQL metrics", site_dir / "quality" / "postgresql"),
                ("PR regression", site_dir / "quality"),
                ("All reports", site_dir / "reports"),
            )
        else:
            links = (
                ("← QA metrics", site_dir / "quality"),
                ("PostgreSQL nightly", site_dir / "quality" / "postgresql"),
                ("All reports", site_dir / "reports"),
            )
        index_path = metadata_path.parent / "index.html"
        if index_path.is_file() and inject_navigation(index_path, links):
            updated += 1
    return updated


def decorate_coverage_reports(site_dir: Path) -> int:
    """Add return links to every page in every archived coverage report."""
    updated = 0
    links = (
        ("← Coverage summary", site_dir / "quality" / "coverage"),
        ("QA metrics", site_dir / "quality"),
    )
    for metadata_path in sorted((site_dir / "coverage").glob("*/metadata.json")):
        html_dir = metadata_path.parent / "html"
        if not html_dir.is_dir():
            continue
        for html_path in sorted(html_dir.rglob("*.html")):
            if inject_navigation(html_path, links):
                updated += 1
    return updated


def decorate_published_reports(site_dir: Path) -> tuple[int, int]:
    """Decorate current and historical Allure and coverage pages."""
    return (
        decorate_allure_reports(site_dir),
        decorate_coverage_reports(site_dir),
    )
