from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.allure_flaky_stats import RunStats  # noqa: E402
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
                    "value": 12.0,
                },
                "avg_api_duration_sec": {
                    "direction": "maximum",
                    "value": 1.5,
                },
                "ui_run_duration_sec": {
                    "direction": "maximum",
                    "value": 300.0,
                },
                "api_run_duration_sec": {
                    "direction": "maximum",
                    "value": 75.0,
                },
                "suite_duration_sec": {
                    "direction": "maximum",
                    "value": 360.0,
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
                    "browser": "Chromium",
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
        self.assertIn("<th>Browser</th>", page)
        self.assertIn('"browser": "Chromium"', page)
        self.assertIn("31 Jul 2026 — 31 Jul 2026", page)
        self.assertEqual(page.count('<details class="panel calculation-details">'), 2)
        self.assertEqual(page.count("<summary>How Metrics Are Calculated</summary>"), 2)
        self.assertIn("<= 12.00s", page)
        self.assertIn("<= 360.00s", page)
        self.assertIn('href="coverage/"', page)
        self.assertIn('href="../reports/"', page)

    def test_ui_average_uses_only_ui_tests(self) -> None:
        row = RunStats(
            run_name="20260731_090000_1_allure-results.zip",
            total_tests=3,
            api_tests=1,
            ui_tests=2,
            flaky_tests=0,
            api_flaky_tests=0,
            ui_flaky_tests=0,
            passed_tests=3,
            failed_tests=0,
            broken_tests=0,
            total_duration_ms=25_000,
            api_duration_ms=1_000,
            ui_duration_ms=24_000,
            suite_duration_ms=30_000,
        )

        self.assertEqual(row.avg_duration_seconds, 12.0)


if __name__ == "__main__":
    unittest.main()
