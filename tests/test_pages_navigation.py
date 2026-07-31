from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parents[1] / ".github" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from pages_navigation import decorate_published_reports  # noqa: E402


def write_html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "<!doctype html><html><body><main>Report</main></body></html>",
        encoding="utf-8",
    )


class PagesNavigationTest(unittest.TestCase):
    def test_decorates_allure_and_every_coverage_html_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            site_dir = Path(temp_dir)
            allure_dir = site_dir / "reports" / "regression" / "123-attempt-1"
            write_html(allure_dir / "index.html")
            (allure_dir / "metadata.json").write_text("{}", encoding="utf-8")

            coverage_dir = site_dir / "coverage" / "123-attempt-1"
            write_html(coverage_dir / "html" / "index.html")
            write_html(coverage_dir / "html" / "pkg" / "module.html")
            (coverage_dir / "metadata.json").write_text("{}", encoding="utf-8")

            allure_pages, coverage_pages = decorate_published_reports(site_dir)

            self.assertEqual((allure_pages, coverage_pages), (1, 2))
            allure_html = (allure_dir / "index.html").read_text(encoding="utf-8")
            coverage_index = (coverage_dir / "html" / "index.html").read_text(
                encoding="utf-8"
            )
            coverage_module = (coverage_dir / "html" / "pkg" / "module.html").read_text(
                encoding="utf-8"
            )

            self.assertIn('href="../../../quality/"', allure_html)
            self.assertIn('href="../../"', allure_html)
            self.assertIn('href="../../../quality/coverage/"', coverage_index)
            self.assertIn('href="../../../quality/"', coverage_index)
            self.assertIn('href="../../../../quality/coverage/"', coverage_module)
            self.assertIn('href="../../../../quality/"', coverage_module)

    def test_navigation_refresh_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            site_dir = Path(temp_dir)
            allure_dir = site_dir / "reports" / "smoke" / "456-attempt-2"
            write_html(allure_dir / "index.html")
            (allure_dir / "metadata.json").write_text("{}", encoding="utf-8")

            self.assertEqual(decorate_published_reports(site_dir), (1, 0))
            first_content = (allure_dir / "index.html").read_text(encoding="utf-8")

            self.assertEqual(decorate_published_reports(site_dir), (0, 0))
            self.assertEqual(
                (allure_dir / "index.html").read_text(encoding="utf-8"),
                first_content,
            )


if __name__ == "__main__":
    unittest.main()
