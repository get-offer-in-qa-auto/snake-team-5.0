from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.build_coverage_dashboard import render_dashboard  # noqa: E402


class CoverageDashboardTemplateTest(unittest.TestCase):
    def test_replaces_only_the_black_page_theme(self) -> None:
        metrics = {
            "generated_at": "2026-07-31T09:00:00+00:00",
            "reports": 1,
            "latest": {
                "run_id": 1,
                "run_url": "https://example.test/actions/runs/1",
                "generated_at": "2026-07-31T09:00:00+00:00",
                "branch": "main",
                "sha": "1234567890",
                "html_url": "coverage/1-attempt-1/html/",
                "line_rate": 90.0,
                "branch_rate": 60.0,
                "covered_lines": 90,
                "num_statements": 100,
                "missing_lines": 10,
                "covered_branches": 6,
                "num_branches": 10,
                "missing_branches": 4,
            },
            "latest_context": {
                "label": "Today at 09:00 UTC",
            },
            "files": {
                "total": 2,
                "with_coverage": 2,
                "with_coverage_rate": 100.0,
                "full": 1,
                "full_rate": 50.0,
                "partial": 1,
                "partial_rate": 50.0,
                "empty": 0,
                "empty_rate": 0.0,
            },
            "modules": [
                {
                    "path": "src/main/api/client.py",
                    "line_rate": 90.0,
                    "branch_rate": 60.0,
                    "covered_lines": 90,
                    "num_statements": 100,
                    "missing": "91–100",
                }
            ],
        }

        page = render_dashboard(
            metrics,
            root_prefix="../../",
            quality_url="../",
        )

        self.assertIn("⚙ API Coverage Analysis", page)
        self.assertIn('class="topbar"', page)
        self.assertIn('class="donut-grid"', page)
        self.assertIn("Coverage by File", page)
        self.assertIn("Latest coverage measurement", page)
        self.assertIn("Measured: 31 Jul 2026 09:00 UTC", page)
        self.assertIn("GitHub Actions run #1", page)
        self.assertIn("Branch: main", page)
        self.assertIn("Commit: 12345678", page)
        self.assertIn('href="https://example.test/actions/runs/1"', page)
        self.assertIn(
            "This page uses the latest published coverage measurement.",
            page,
        )
        self.assertNotIn("does not average or aggregate coverage", page)
        self.assertIn("--background: #f4efe7", page)
        self.assertNotIn("@media (prefers-color-scheme: dark)", page)
        self.assertNotIn('class="group"', page)
        self.assertIn('href="../"', page)
        self.assertIn('href="../../coverage/1-attempt-1/html/"', page)

    def test_explains_pull_request_merge_ref(self) -> None:
        metrics = {
            "generated_at": "2026-07-31T09:00:00+00:00",
            "reports": 1,
            "latest": {
                "run_id": 1,
                "run_url": "https://example.test/actions/runs/1",
                "generated_at": "2026-07-31T09:00:00+00:00",
                "branch": "69/merge",
                "sha": "1234567890",
                "html_url": "coverage/1-attempt-1/html/",
                "line_rate": 90.0,
                "branch_rate": 60.0,
                "covered_lines": 90,
                "num_statements": 100,
                "missing_lines": 10,
                "covered_branches": 6,
                "num_branches": 10,
                "missing_branches": 4,
            },
            "latest_context": {"label": "Today at 09:00 UTC"},
            "files": {
                "total": 0,
                "with_coverage": 0,
                "with_coverage_rate": None,
                "full": 0,
                "full_rate": None,
                "partial": 0,
                "partial_rate": None,
                "empty": 0,
                "empty_rate": None,
            },
            "modules": [],
        }

        page = render_dashboard(metrics, root_prefix="../../", quality_url="../")

        self.assertIn("Pull request #69 · merge ref", page)


if __name__ == "__main__":
    unittest.main()
