from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.build_quality_dashboard import render_dashboard  # noqa: E402


class QualityDashboardTemplateTest(unittest.TestCase):
    def test_graphical_template_keeps_four_metric_charts_and_navigation(
        self,
    ) -> None:
        metrics = {
            "generated_at": "2026-07-31T09:00:00+00:00",
            "window": {
                "days": 7,
                "start": "2026-07-25T00:00:00+00:00",
                "end": "2026-07-31T09:00:00+00:00",
            },
            "pipeline": {
                "completed": 1,
                "successful": 1,
                "success_rate": 100.0,
                "p95_duration_seconds": 200.0,
            },
            "tests": {
                "total": 10,
                "failed": 0,
                "pass_rate": 100.0,
                "flaky": 0,
                "retries": 0,
                "retry_rate": 0.0,
            },
            "data_quality": {
                "published_reports": 1,
                "runs_without_report": 0,
            },
            "quality_targets": {
                "pass_rate": {"direction": "minimum", "value": 98.0},
                "stability_rate": {"direction": "minimum", "value": 95.0},
                "suite_duration_sec": {
                    "direction": "maximum",
                    "value": 240.0,
                },
            },
            "run_trends": [
                {
                    "run_number": 1,
                    "label": "31 Jul 09:00",
                    "run_url": "https://example.test/actions/runs/1",
                    "test_pass_rate": 100.0,
                    "pipeline_success_rate": 100.0,
                    "workflow_duration_seconds": 200.0,
                    "flaky_results": 0,
                }
            ],
            "suites": [],
            "attention": [],
            "recent_runs": [],
            "coverage": {
                "latest": {
                    "line_rate": 90.0,
                    "branch_rate": 80.0,
                }
            },
        }

        page = render_dashboard(
            metrics,
            root_prefix="../",
            coverage_url="coverage/",
            periods=[(7, "periods/7/"), (14, "periods/14/")],
        )

        self.assertEqual(page.count('<svg class="line-chart"'), 4)
        self.assertIn("Metric history", page)
        self.assertIn("Where instability is", page)
        self.assertIn("Needs attention", page)
        self.assertIn("Recent regression runs", page)
        self.assertIn('href="coverage/"', page)
        self.assertIn('href="../reports/"', page)


if __name__ == "__main__":
    unittest.main()
