from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from scripts import build_quality_dashboard as dashboard

NOW = datetime(2026, 7, 28, 12, tzinfo=UTC)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def workflow_run(
    run_id: int,
    *,
    attempt: int = 1,
    conclusion: str = "success",
    created_at: str = "2026-07-28T09:00:00Z",
) -> dict[str, object]:
    return {
        "id": run_id,
        "run_attempt": attempt,
        "run_number": run_id,
        "status": "completed",
        "conclusion": conclusion,
        "event": "pull_request",
        "head_branch": "feature/metrics",
        "html_url": f"https://github.test/actions/runs/{run_id}",
        "created_at": created_at,
        "run_started_at": created_at,
        "updated_at": "2026-07-28T09:10:00Z",
    }


def make_test_case(
    uid: str,
    scope: str,
    status: str,
    *,
    retries: int = 0,
    duration_ms: int = 1_000,
) -> dict[str, object]:
    return {
        "uid": uid,
        "historyId": f"history-{uid}",
        "name": f"test_{uid}",
        "fullName": f"tests.test_{uid}",
        "status": status,
        "retriesCount": retries,
        "labels": [{"name": "parentSuite", "value": scope}],
        "time": {"duration": duration_ms},
    }


def write_report(
    site_dir: Path,
    *,
    run_id: int,
    attempt: int,
    generated_at: str,
    tests: list[dict[str, object]],
) -> None:
    report_id = f"{run_id}-attempt-{attempt}"
    report_dir = site_dir / "reports" / "regression" / report_id
    write_json(
        report_dir / "metadata.json",
        {
            "report_id": report_id,
            "generated_at": generated_at,
            "run_url": f"https://github.test/actions/runs/{run_id}",
        },
    )
    write_json(report_dir / "widgets" / "summary.json", {"statistic": {}})
    for test in tests:
        write_json(report_dir / "data" / "test-cases" / f"{test['uid']}.json", test)


def test_load_workflow_runs_keeps_latest_attempt_and_filters_window(
    tmp_path: Path,
) -> None:
    runs_path = tmp_path / "runs.json"
    write_json(
        runs_path,
        [
            workflow_run(100, attempt=1),
            workflow_run(100, attempt=2),
            workflow_run(
                99,
                created_at="2026-07-20T09:00:00Z",
            ),
        ],
    )

    runs = dashboard.load_workflow_runs(
        runs_path,
        window_start=dashboard.window_start(NOW, 7),
        window_end=NOW,
    )

    assert [(run.id, run.attempt) for run in runs] == [(100, 2)]


def test_load_published_reports_deduplicates_latest_attempt(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    write_report(
        site_dir,
        run_id=100,
        attempt=1,
        generated_at="2026-07-27T10:00:00Z",
        tests=[make_test_case("old", "API", "failed")],
    )
    write_report(
        site_dir,
        run_id=100,
        attempt=2,
        generated_at="2026-07-28T10:00:00Z",
        tests=[make_test_case("new", "API", "passed")],
    )

    reports = dashboard.load_published_reports(
        site_dir,
        "regression",
        window_start=dashboard.window_start(NOW, 7),
        window_end=NOW,
        latest_attempts={},
    )

    assert [(report.run_id, report.attempt) for report in reports] == [(100, 2)]
    assert reports[0].tests[0]["uid"] == "new"


def test_metrics_include_pipeline_failures_and_test_flakiness(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    runs_path = tmp_path / "runs.json"
    write_json(
        runs_path,
        [
            workflow_run(100, attempt=2),
            workflow_run(200, conclusion="failure"),
        ],
    )
    write_report(
        site_dir,
        run_id=100,
        attempt=2,
        generated_at="2026-07-28T10:00:00Z",
        tests=[
            make_test_case("api", "API", "passed"),
            make_test_case("chromium", "UI · Chromium", "passed", retries=1),
            make_test_case("firefox", "UI · Firefox", "failed"),
            make_test_case("webkit", "UI · WebKit", "passed"),
        ],
    )
    runs = dashboard.load_workflow_runs(
        runs_path,
        window_start=dashboard.window_start(NOW, 7),
        window_end=NOW,
    )
    reports = dashboard.load_published_reports(
        site_dir,
        "regression",
        window_start=dashboard.window_start(NOW, 7),
        window_end=NOW,
        latest_attempts={run.id: run.attempt for run in runs},
    )

    metrics = dashboard.build_metrics(runs, reports, now=NOW, days=7)

    assert metrics["pipeline"]["success_rate"] == 50
    assert metrics["data_quality"] == {
        "completed_runs": 2,
        "published_reports": 1,
        "runs_without_report": 1,
    }
    assert metrics["tests"]["pass_rate"] == 75
    assert metrics["tests"]["flaky"] == 1
    assert metrics["tests"]["retry_rate"] == 20
    assert [suite["name"] for suite in metrics["suites"]] == [
        "API",
        "UI · Chromium",
        "UI · Firefox",
        "UI · WebKit",
    ]


def test_main_writes_dashboard_and_machine_readable_metrics(
    tmp_path: Path,
    monkeypatch,
) -> None:
    site_dir = tmp_path / "site"
    runs_path = tmp_path / "runs.json"
    write_json(runs_path, [workflow_run(100)])
    write_report(
        site_dir,
        run_id=100,
        attempt=1,
        generated_at="2026-07-28T10:00:00Z",
        tests=[make_test_case("api", "API", "passed")],
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_quality_dashboard.py",
            "--site-dir",
            str(site_dir),
            "--runs-json",
            str(runs_path),
            "--days",
            "7",
            "--now",
            NOW.isoformat(),
        ],
    )

    dashboard.main()

    html = (site_dir / "quality" / "index.html").read_text(encoding="utf-8")
    metrics = json.loads(
        (site_dir / "quality" / "metrics.json").read_text(encoding="utf-8")
    )
    assert "TeamCity QA metrics" in html
    assert 'style="--days: 7"' in html
    assert "../reports/regression/100-attempt-1/" in html
    assert metrics["window"]["start"] == "2026-07-22T00:00:00+00:00"
