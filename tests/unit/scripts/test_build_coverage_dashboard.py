from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from scripts import build_coverage_dashboard as dashboard

NOW = datetime(2026, 7, 28, 12, tzinfo=UTC)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def coverage_payload(
    *,
    covered_lines: int,
    statements: int,
    covered_branches: int,
    branches: int,
) -> dict[str, object]:
    return {
        "meta": {"branch_coverage": True},
        "totals": {
            "covered_lines": covered_lines,
            "num_statements": statements,
            "missing_lines": statements - covered_lines,
            "excluded_lines": 0,
            "covered_branches": covered_branches,
            "num_branches": branches,
            "missing_branches": branches - covered_branches,
        },
        "files": {
            "src/main/api/client.py": {
                "summary": {
                    "covered_lines": covered_lines,
                    "num_statements": statements,
                    "covered_branches": covered_branches,
                    "num_branches": branches,
                },
                "missing_lines": [3, 4, 5, 10],
            }
        },
    }


def write_report(
    site_dir: Path,
    *,
    run_id: int,
    attempt: int,
    generated_at: str,
    coverage: dict[str, object],
) -> None:
    report_id = f"{run_id}-attempt-{attempt}"
    report_dir = site_dir / "coverage" / report_id
    write_json(
        report_dir / "metadata.json",
        {
            "branch": "main",
            "generated_at": generated_at,
            "report_id": report_id,
            "run_url": f"https://github.test/actions/runs/{run_id}",
            "sha": "abc123456789",
            "source": "src/main/api",
        },
    )
    write_json(report_dir / "coverage.json", coverage)


def test_load_reports_keeps_latest_attempt_for_each_run(tmp_path: Path) -> None:
    write_report(
        tmp_path,
        run_id=100,
        attempt=1,
        generated_at="2026-07-27T10:00:00Z",
        coverage=coverage_payload(
            covered_lines=4,
            statements=10,
            covered_branches=1,
            branches=4,
        ),
    )
    write_report(
        tmp_path,
        run_id=100,
        attempt=2,
        generated_at="2026-07-28T10:00:00Z",
        coverage=coverage_payload(
            covered_lines=8,
            statements=10,
            covered_branches=3,
            branches=4,
        ),
    )

    reports = dashboard.load_coverage_reports(
        tmp_path,
        window_start_at=dashboard.window_start(NOW, 7),
        window_end=NOW,
    )

    assert [(report.run_id, report.attempt) for report in reports] == [(100, 2)]


def test_metrics_calculate_line_branch_and_previous_report_delta(
    tmp_path: Path,
) -> None:
    write_report(
        tmp_path,
        run_id=100,
        attempt=1,
        generated_at="2026-07-27T10:00:00Z",
        coverage=coverage_payload(
            covered_lines=6,
            statements=10,
            covered_branches=2,
            branches=4,
        ),
    )
    write_report(
        tmp_path,
        run_id=200,
        attempt=1,
        generated_at="2026-07-28T10:00:00Z",
        coverage=coverage_payload(
            covered_lines=8,
            statements=10,
            covered_branches=3,
            branches=4,
        ),
    )
    reports = dashboard.load_coverage_reports(
        tmp_path,
        window_start_at=dashboard.window_start(NOW, 7),
        window_end=NOW,
    )

    metrics = dashboard.build_metrics(reports, now=NOW, days=7)

    assert metrics["latest"]["line_rate"] == 80
    assert metrics["latest"]["branch_rate"] == 75
    assert metrics["delta"] == {"line_rate": 20, "branch_rate": 25}
    assert metrics["modules"][0]["missing"] == "3–5, 10"
    assert metrics["trend"][-1]["line_rate"] == 80


def test_compact_line_numbers_keeps_complete_ranges() -> None:
    assert (
        dashboard.compact_line_numbers(
            [1, 2, 5, 8, 9, 12, 15, 18, 21],
            limit=3,
        )
        == "1–2, 5, 8–9, …"
    )


def test_main_writes_detail_page_and_metrics_json(
    tmp_path: Path,
    monkeypatch,
) -> None:
    write_report(
        tmp_path,
        run_id=100,
        attempt=1,
        generated_at="2026-07-28T10:00:00Z",
        coverage=coverage_payload(
            covered_lines=8,
            statements=10,
            covered_branches=3,
            branches=4,
        ),
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_coverage_dashboard.py",
            "--site-dir",
            str(tmp_path),
            "--days",
            "7",
            "--now",
            NOW.isoformat(),
        ],
    )

    dashboard.main()

    page = (tmp_path / "quality" / "coverage" / "index.html").read_text(
        encoding="utf-8"
    )
    metrics = json.loads(
        (tmp_path / "quality" / "coverage" / "metrics.json").read_text(encoding="utf-8")
    )
    assert "API test framework coverage" in page
    assert "../../coverage/100-attempt-1/html/" in page
    assert metrics["latest"]["line_rate"] == 80


def test_main_writes_empty_page_when_no_reports_exist(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_coverage_dashboard.py",
            "--site-dir",
            str(tmp_path),
            "--now",
            NOW.isoformat(),
        ],
    )

    dashboard.main()

    page = (tmp_path / "quality" / "coverage" / "index.html").read_text(
        encoding="utf-8"
    )
    assert "No coverage reports published yet." in page
