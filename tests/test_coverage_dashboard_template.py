from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.build_coverage_dashboard import render_dashboard  # noqa: E402


class CoverageDashboardTemplateTest(unittest.TestCase):
    def test_uses_quality_dashboard_visual_language(self) -> None:
        metrics = {
            "generated_at": "2026-07-31T09:00:00+00:00",
            "reports": 1,
            "latest": {
                "run_id": 1,
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

        self.assertIn("API Framework Code Coverage", page)
        self.assertIn("1️⃣ Coverage Summary", page)
        self.assertIn("2️⃣ Coverage Details", page)
        self.assertEqual(page.count('<section class="group">'), 2)
        self.assertIn("--background: #f4efe7", page)
        self.assertIn('"Avenir Next", "Segoe UI", sans-serif', page)
        self.assertIn("radial-gradient(1200px 400px", page)
        self.assertIn('class="qa-report-links"', page)
        self.assertIn('href="../"', page)
        self.assertIn('href="../../coverage/1-attempt-1/html/"', page)


if __name__ == "__main__":
    unittest.main()
