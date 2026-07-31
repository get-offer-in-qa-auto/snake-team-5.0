from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.allure_flaky_stats import RunStats  # noqa: E402
from scripts.build_quality_dashboard import (  # noqa: E402
    load_workflow_runs,
    render_dashboard,
)


class QualityDashboardTemplateTest(unittest.TestCase):
    def test_loads_postgresql_suite_completeness(self) -> None:
        payload = [
            {
                "id": 42,
                "run_attempt": 1,
                "run_number": 7,
                "status": "completed",
                "conclusion": "failure",
                "event": "schedule",
                "head_branch": "main",
                "html_url": "https://example.test/actions/runs/42",
                "created_at": "2026-07-31T05:35:29Z",
                "run_started_at": "2026-07-31T05:35:32Z",
                "updated_at": "2026-07-31T05:41:08Z",
                "test_duration_seconds": 336,
                "test_suite_complete": False,
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            runs_path = Path(temp_dir) / "runs.json"
            runs_path.write_text(json.dumps(payload), encoding="utf-8")
            runs = load_workflow_runs(
                runs_path,
                window_start=datetime(2026, 7, 25, tzinfo=UTC),
                window_end=datetime(2026, 7, 31, 12, tzinfo=UTC),
            )

        self.assertEqual(len(runs), 1)
        self.assertFalse(runs[0].test_suite_complete)
        self.assertEqual(runs[0].duration_seconds, 336)

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
                    "report_url": "reports/regression/1-attempt-1/",
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
                    "report_url": "reports/regression/1-attempt-1/",
                }
            ],
            "slowest_api_tests": [
                {
                    "run_label": "2026-07-31 09:00",
                    "test_name": "tests.api.test_endpoint",
                    "duration_sec": 0.1,
                    "status": "passed",
                    "report_url": "reports/regression/1-attempt-1/",
                }
            ],
            "browser_runs": [
                {
                    "run_id": 1,
                    "run_label": "31 Jul 09:00",
                    "report_url": "reports/regression/1-attempt-1/",
                    "browser": "Chromium",
                    "pass_rate": 100.0,
                    "avg_duration_sec": 1.0,
                },
                {
                    "run_id": 1,
                    "run_label": "31 Jul 09:00",
                    "report_url": "reports/regression/1-attempt-1/",
                    "browser": "Firefox",
                    "pass_rate": 100.0,
                    "avg_duration_sec": 1.2,
                },
                {
                    "run_id": 1,
                    "run_label": "31 Jul 09:00",
                    "report_url": "reports/regression/1-attempt-1/",
                    "browser": "WebKit",
                    "pass_rate": 100.0,
                    "avg_duration_sec": 1.4,
                },
            ],
            "browser_summary": [
                {
                    "browser": browser,
                    "runs": 1,
                    "total_tests": 5,
                    "failed_tests": 0,
                    "pass_rate": 100.0,
                    "flaky_rate": 0.0,
                    "avg_duration_sec": duration,
                    "p95_duration_sec": duration + 0.5,
                    "p90_run_duration_sec": duration * 5,
                    "avg_target_sec": target,
                    "run_target_sec": run_target,
                    "status": "ok",
                    "status_label": "OK",
                }
                for browser, duration, target, run_target in (
                    ("Chromium", 1.0, 11.0, 100.0),
                    ("Firefox", 1.2, 13.0, 115.0),
                    ("WebKit", 1.4, 14.0, 120.0),
                )
            ],
            "browser_coverage": {
                "common_tests": 5,
                "unique_tests": 5,
                "coverage_rate": 100.0,
                "by_browser": {
                    "Chromium": 5,
                    "Firefox": 5,
                    "WebKit": 5,
                },
            },
            "browser_failures": [
                {
                    "browser": "Firefox",
                    "test_name": "tests.ui.test_page",
                    "failed_results": 1,
                    "failed_runs": 1,
                    "latest_run": "2026-07-31 09:00",
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

        self.assertEqual(page.count("<canvas id="), 12)
        self.assertIn("1️⃣ Test Result Distribution", page)
        self.assertIn("2️⃣ Speed Metrics", page)
        self.assertIn("3️⃣ Cross-Browser UI", page)
        self.assertIn("Browser Coverage", page)
        self.assertIn("Browser-Specific Failures", page)
        self.assertIn('id="browser-pass-trend"', page)
        self.assertIn('id="browser-duration-trend"', page)
        self.assertIn("Total UI Test Time", page)
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
        self.assertIn('href="../quality/">PR Regression</a>', page)
        self.assertIn(
            'href="../quality/postgresql/">PostgreSQL Nightly</a>',
            page,
        )
        self.assertIn(
            '"report_url": "../reports/regression/1-attempt-1/"',
            page,
        )
        self.assertIn('class="run-report-link"', page)
        self.assertIn(
            'target="_blank" rel="noopener noreferrer">Allure Reports</a>',
            page,
        )
        self.assertIn("Open Allure report for", page)
        self.assertIn("function enablePointLinks(canvas, points)", page)
        self.assertIn(
            "window.open(point.d.report_url, '_blank', 'noopener,noreferrer')",
            page,
        )
        self.assertIn(
            'target="_blank" rel="noopener noreferrer"',
            page,
        )
        self.assertEqual(
            page.count('"report_url": "../reports/regression/1-attempt-1/"'),
            6,
        )

        archived_page = render_dashboard(
            metrics,
            root_prefix="../../../",
            coverage_url="../../coverage/",
            periods=[],
        )
        self.assertIn(
            '"report_url": "../../../reports/regression/1-attempt-1/"',
            archived_page,
        )

        metrics["pipeline"] = {
            "completed": 2,
            "successful": 1,
            "success_rate": 50.0,
            "p95_duration_seconds": 220.0,
        }
        metrics["data_quality"] = {
            "published_reports": 2,
            "metric_reports": 1,
            "incomplete_runs": 1,
            "incomplete_reports": 1,
            "runs_without_report": 0,
        }
        metrics["recent_runs"] = [
            {
                "id": 2,
                "number": 2,
                "attempt": 1,
                "conclusion": "failure",
                "event": "schedule",
                "branch": "main",
                "created_at": "2026-07-31T10:00:00+00:00",
                "duration_seconds": 180.0,
                "run_url": "https://example.test/actions/runs/2",
                "report_url": "reports/postgresql-regression/2-attempt-1/",
                "test_suite_complete": False,
            }
        ]
        postgresql_page = render_dashboard(
            metrics,
            root_prefix="../../",
            coverage_url="../coverage/",
            periods=[],
            report_title="TeamCity PostgreSQL Nightly Metrics",
            report_subtitle=(
                "Nightly quality metrics on the PostgreSQL TeamCity stand"
            ),
            dashboard_kind="postgresql",
        )
        self.assertIn("TeamCity PostgreSQL Nightly Metrics", postgresql_page)
        self.assertIn("PostgreSQL nightly execution status", postgresql_page)
        self.assertIn("Complete Runs Used", postgresql_page)
        self.assertIn('Nightly executions</div><div class="value">2', postgresql_page)
        self.assertIn(
            'Workflow stability</div><div class="value">50.00%', postgresql_page
        )
        self.assertIn("Incomplete nightly runs (1)", postgresql_page)
        self.assertIn(
            'href="../../reports/postgresql-regression/2-attempt-1/" '
            'target="_blank" rel="noopener noreferrer"',
            postgresql_page,
        )
        self.assertIn(
            'class="active" href="../../quality/postgresql/"',
            postgresql_page,
        )

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
