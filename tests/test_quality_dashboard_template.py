from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.build_quality_dashboard import render_dashboard  # noqa: E402


class QualityDashboardTemplateTest(unittest.TestCase):
    def test_reference_template_keeps_ten_metric_charts_and_navigation(
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
                "fail_rate": {"direction": "maximum", "value": 2.0},
                "broken_rate": {"direction": "maximum", "value": 1.0},
                "flaky_rate": {"direction": "maximum", "value": 2.0},
                "stability_rate": {"direction": "minimum", "value": 95.0},
                "avg_duration_sec": {
                    "direction": "maximum",
                    "value": 3.0,
                },
                "avg_api_duration_sec": {
                    "direction": "maximum",
                    "value": 0.2,
                },
                "ui_run_duration_sec": {
                    "direction": "maximum",
                    "value": 240.0,
                },
                "api_run_duration_sec": {
                    "direction": "maximum",
                    "value": 20.0,
                },
                "suite_duration_sec": {
                    "direction": "maximum",
                    "value": 240.0,
                },
            },
            "metric_runs": [
                {
                    "run_id": 1,
                    "generated_at": "2026-07-31T09:00:00+00:00",
                    "total_tests": 10,
                    "api_tests": 5,
                    "ui_tests": 5,
                    "passed_tests": 10,
                    "failed_tests": 0,
                    "broken_tests": 0,
                    "flaky_tests": 0,
                    "api_flaky_tests": 0,
                    "ui_flaky_tests": 0,
                    "avg_duration_sec": 1.0,
                    "avg_api_duration_sec": 0.1,
                    "ui_run_duration_sec": 8.0,
                    "api_run_duration_sec": 0.5,
                    "suite_duration_sec": 200.0,
                }
            ],
            "slowest_ui_tests": [
                {
                    "run_label": "2026-07-31 09:00",
                    "test_name": "tests.ui.test_page",
                    "duration_sec": 2.0,
                    "status": "passed",
                }
            ],
            "slowest_api_tests": [
                {
                    "run_label": "2026-07-31 09:00",
                    "test_name": "tests.api.test_endpoint",
                    "duration_sec": 0.1,
                    "status": "passed",
                }
            ],
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

        self.assertEqual(page.count("<canvas id="), 10)
        self.assertIn("1️⃣ Test Result Distribution", page)
        self.assertIn("2️⃣ Speed Metrics", page)
        self.assertIn("Average Pass Rate Trend", page)
        self.assertIn("Slowest tests API", page)
        self.assertIn("31 Jul 2026 — 31 Jul 2026", page)
        self.assertIn('href="coverage/"', page)
        self.assertIn('href="../reports/"', page)


if __name__ == "__main__":
    unittest.main()
