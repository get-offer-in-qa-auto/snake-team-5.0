#!/usr/bin/env python3
"""Build a rolling QA metrics dashboard from Actions runs and Allure Pages."""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from scripts.allure_flaky_stats import RunStats
    from scripts.reference_metrics_dashboard import (
        DEFAULT_GATES as REFERENCE_DEFAULT_GATES,
    )
    from scripts.reference_metrics_dashboard import (
        build_html as build_reference_dashboard_html,
    )
except ModuleNotFoundError:
    from allure_flaky_stats import RunStats  # type: ignore[import-not-found, no-redef]
    from reference_metrics_dashboard import (
        DEFAULT_GATES as REFERENCE_DEFAULT_GATES,
    )  # type: ignore[import-not-found, no-redef]
    from reference_metrics_dashboard import (
        build_html as build_reference_dashboard_html,
    )  # type: ignore[import-not-found, no-redef]

REPORT_ID_PATTERN = re.compile(r"^(?P<run_id>\d+)-attempt-(?P<attempt>\d+)$")
FAILED_STATUSES = {"failed", "broken"}
COMPLETED_TEST_STATUSES = {"passed", "failed", "broken", "skipped", "unknown"}
UI_SCOPE_ORDER = ("API", "UI · Chromium", "UI · Firefox", "UI · WebKit")
BROWSER_NAMES = ("Chromium", "Firefox", "WebKit")
DEFAULT_BROWSER_TARGETS = {
    "Chromium": {"avg_duration_sec": 11.0, "run_duration_sec": 100.0},
    "Firefox": {"avg_duration_sec": 13.0, "run_duration_sec": 115.0},
    "WebKit": {"avg_duration_sec": 14.0, "run_duration_sec": 120.0},
}
QUALITY_TARGET_KEYS = (
    "pass_rate",
    "fail_rate",
    "broken_rate",
    "flaky_rate",
    "stability_rate",
    "avg_duration_sec",
    "avg_api_duration_sec",
    "ui_run_duration_sec",
    "api_run_duration_sec",
    "suite_duration_sec",
)
QUALITY_TARGET_DIRECTIONS = {"minimum", "maximum"}
PERCENTAGE_TARGET_KEYS = {
    "pass_rate",
    "fail_rate",
    "broken_rate",
    "flaky_rate",
    "stability_rate",
}


@dataclass(frozen=True)
class WorkflowRun:
    id: int
    attempt: int
    number: int
    conclusion: str
    event: str
    branch: str
    url: str
    created_at: datetime
    started_at: datetime
    updated_at: datetime
    test_duration_seconds: float | None = None
    test_suite_complete: bool = True

    @property
    def duration_seconds(self) -> float:
        if self.test_duration_seconds is not None:
            return max(0.0, self.test_duration_seconds)
        return max(0.0, (self.updated_at - self.started_at).total_seconds())


@dataclass(frozen=True)
class PublishedReport:
    run_id: int
    attempt: int
    report_id: str
    path: str
    generated_at: datetime
    run_url: str
    summary: dict[str, Any]
    tests: tuple[dict[str, Any], ...]


def parse_datetime(value: str | None) -> datetime:
    if not value:
        raise ValueError("datetime value is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def percentile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def percentage(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator * 100 / denominator, 2)


def window_start(now: datetime, days: int) -> datetime:
    """Return the UTC midnight starting an inclusive calendar-day window."""
    return (now - timedelta(days=days - 1)).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def load_workflow_runs(
    runs_path: Path, *, window_start: datetime, window_end: datetime
) -> list[WorkflowRun]:
    payload = json.loads(runs_path.read_text(encoding="utf-8"))
    raw_runs = (
        payload.get("workflow_runs", []) if isinstance(payload, dict) else payload
    )
    if not isinstance(raw_runs, list):
        raise ValueError("workflow runs JSON must contain a list")

    latest_attempts: dict[int, WorkflowRun] = {}
    for item in raw_runs:
        if not isinstance(item, dict) or item.get("status") != "completed":
            continue
        created_at = parse_datetime(item.get("created_at"))
        if created_at < window_start or created_at > window_end:
            continue
        started_at = parse_datetime(
            item.get("run_started_at") or item.get("created_at")
        )
        updated_at = parse_datetime(item.get("updated_at") or item.get("created_at"))
        run = WorkflowRun(
            id=int(item["id"]),
            attempt=int(item.get("run_attempt") or 1),
            number=int(item.get("run_number") or 0),
            conclusion=str(item.get("conclusion") or "unknown"),
            event=str(item.get("event") or "unknown"),
            branch=str(item.get("head_branch") or "unknown"),
            url=str(item.get("html_url") or "#"),
            created_at=created_at,
            started_at=started_at,
            updated_at=updated_at,
            test_duration_seconds=(
                float(item["test_duration_seconds"])
                if item.get("test_duration_seconds") is not None
                else None
            ),
            test_suite_complete=(
                bool(item["test_suite_complete"])
                if item.get("test_suite_complete") is not None
                else True
            ),
        )
        previous = latest_attempts.get(run.id)
        if previous is None or run.attempt >= previous.attempt:
            latest_attempts[run.id] = run

    return sorted(latest_attempts.values(), key=lambda run: run.created_at)


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def load_quality_targets(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    if payload is None:
        raise ValueError(f"quality targets config is missing or invalid: {path}")

    targets: dict[str, dict[str, Any]] = {}
    for key in QUALITY_TARGET_KEYS:
        raw_target = payload.get(key)
        if not isinstance(raw_target, dict):
            raise ValueError(f"quality target {key!r} must be an object")
        direction = str(raw_target.get("direction") or "")
        if direction not in QUALITY_TARGET_DIRECTIONS:
            raise ValueError(
                f"quality target {key!r} direction must be one of "
                f"{sorted(QUALITY_TARGET_DIRECTIONS)}"
            )
        try:
            value = float(raw_target["value"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                f"quality target {key!r} value must be a number"
            ) from error
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"quality target {key!r} value must be non-negative")
        if key in PERCENTAGE_TARGET_KEYS and value > 100:
            raise ValueError(
                f"quality target {key!r} value must not be greater than 100"
            )
        targets[key] = {
            "direction": direction,
            "value": value,
            "name": str(raw_target.get("name") or key.replace("_", " ").title()),
            "recommendation": str(raw_target.get("recommendation") or ""),
        }
    return targets


def load_browser_targets(path: Path) -> dict[str, dict[str, float]]:
    payload = load_json(path)
    if payload is None:
        raise ValueError(f"quality targets config is missing or invalid: {path}")
    raw_targets = payload.get("browser_targets", DEFAULT_BROWSER_TARGETS)
    if not isinstance(raw_targets, dict):
        raise ValueError("browser_targets must be an object")

    targets: dict[str, dict[str, float]] = {}
    for browser in BROWSER_NAMES:
        raw_target = raw_targets.get(browser, DEFAULT_BROWSER_TARGETS[browser])
        if not isinstance(raw_target, dict):
            raise ValueError(f"browser target {browser!r} must be an object")
        try:
            avg_duration = float(raw_target["avg_duration_sec"])
            run_duration = float(raw_target["run_duration_sec"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                f"browser target {browser!r} durations must be numbers"
            ) from error
        if (
            not math.isfinite(avg_duration)
            or not math.isfinite(run_duration)
            or avg_duration <= 0
            or run_duration <= 0
        ):
            raise ValueError(f"browser target {browser!r} durations must be positive")
        targets[browser] = {
            "avg_duration_sec": avg_duration,
            "run_duration_sec": run_duration,
        }
    return targets


def load_published_reports(
    site_dir: Path,
    suite: str,
    *,
    window_start: datetime,
    window_end: datetime,
    latest_attempts: dict[int, int],
) -> list[PublishedReport]:
    reports_by_run: dict[int, PublishedReport] = {}
    suite_dir = site_dir / "reports" / suite
    if not suite_dir.is_dir():
        return []

    for metadata_path in sorted(suite_dir.glob("*/metadata.json")):
        metadata = load_json(metadata_path)
        if metadata is None:
            continue
        report_id = str(metadata.get("report_id") or metadata_path.parent.name)
        match = REPORT_ID_PATTERN.fullmatch(report_id)
        if match is None:
            continue
        run_id = int(match.group("run_id"))
        attempt = int(match.group("attempt"))
        expected_attempt = latest_attempts.get(run_id)
        if expected_attempt is not None and attempt != expected_attempt:
            continue

        try:
            generated_at = parse_datetime(str(metadata.get("generated_at") or ""))
        except ValueError:
            continue
        if generated_at < window_start or generated_at > window_end:
            continue

        summary = load_json(metadata_path.parent / "widgets" / "summary.json")
        if summary is None:
            continue

        tests: list[dict[str, Any]] = []
        for test_path in sorted(
            (metadata_path.parent / "data" / "test-cases").glob("*.json")
        ):
            test = load_json(test_path)
            if test is not None:
                tests.append(test)

        report = PublishedReport(
            run_id=run_id,
            attempt=attempt,
            report_id=report_id,
            path=metadata_path.parent.relative_to(site_dir).as_posix(),
            generated_at=generated_at,
            run_url=str(metadata.get("run_url") or "#"),
            summary=summary,
            tests=tuple(tests),
        )
        previous = reports_by_run.get(run_id)
        if previous is None or report.attempt >= previous.attempt:
            reports_by_run[run_id] = report

    return sorted(reports_by_run.values(), key=lambda report: report.generated_at)


def test_scope(test: dict[str, Any]) -> str:
    for label in test.get("labels", []):
        if (
            isinstance(label, dict)
            and label.get("name") == "parentSuite"
            and label.get("value")
        ):
            return str(label["value"])

    name = str(test.get("name") or "").lower()
    for browser in ("chromium", "firefox", "webkit"):
        if f"[{browser}]" in name:
            return f"UI · {browser.title()}"
    return "Other"


def test_retry_count(test: dict[str, Any]) -> int:
    try:
        return max(0, int(test.get("retriesCount") or 0))
    except (TypeError, ValueError):
        return 0


def test_duration_ms(test: dict[str, Any]) -> float:
    time_payload = test.get("time")
    if not isinstance(time_payload, dict):
        return 0.0
    try:
        return max(0.0, float(time_payload.get("duration") or 0))
    except (TypeError, ValueError):
        return 0.0


def test_identity(test: dict[str, Any]) -> str:
    return str(
        test.get("historyId")
        or test.get("fullName")
        or test.get("name")
        or test.get("uid")
        or "unknown"
    )


def browser_name(test: dict[str, Any]) -> str | None:
    scope = test_scope(test)
    if not scope.startswith("UI ·"):
        return None
    candidate = scope.split("·", maxsplit=1)[1].strip()
    return candidate if candidate in BROWSER_NAMES else None


def logical_ui_test_identity(test: dict[str, Any]) -> str:
    identity = str(
        test.get("fullName") or test.get("name") or test_identity(test)
    ).strip()
    return re.sub(
        r"\[(?:chromium|firefox|webkit)\](?=($|\s))",
        "",
        identity,
        flags=re.IGNORECASE,
    ).strip()


def status_counts(reports: list[PublishedReport]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for report in reports:
        for test in report.tests:
            status = str(test.get("status") or "unknown")
            if status not in COMPLETED_TEST_STATUSES:
                status = "unknown"
            counts[status] += 1
    return counts


def report_metrics(report: PublishedReport) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    flaky_results = 0
    for test in report.tests:
        status = str(test.get("status") or "unknown")
        if status not in COMPLETED_TEST_STATUSES:
            status = "unknown"
        counts[status] += 1
        if bool(test.get("flaky")) or test_retry_count(test) > 0:
            flaky_results += 1

    total = sum(counts.values())
    return {
        "test_pass_rate": percentage(counts["passed"], total),
        "flaky_results": flaky_results,
        "test_total": total,
        "test_failed": counts["failed"] + counts["broken"],
    }


def aggregate_run_trends(
    runs: list[WorkflowRun],
    reports: list[PublishedReport],
    *,
    published_reports: list[PublishedReport] | None = None,
) -> list[dict[str, Any]]:
    reports_by_run = {report.run_id: report for report in reports}
    published_by_run = {
        report.run_id: report for report in (published_reports or reports)
    }
    points: list[dict[str, Any]] = []
    for run in runs:
        report = reports_by_run.get(run.id)
        published_report = published_by_run.get(run.id)
        report_values = report_metrics(report) if report else {}
        points.append(
            {
                "run_id": run.id,
                "run_number": run.number,
                "attempt": run.attempt,
                "label": run.created_at.strftime("%d %b %H:%M"),
                "created_at": run.created_at.isoformat(timespec="seconds"),
                "run_url": run.url,
                "report_url": (
                    f"{published_report.path}/" if published_report else None
                ),
                "conclusion": run.conclusion,
                "test_suite_complete": run.test_suite_complete,
                "test_pass_rate": report_values.get("test_pass_rate"),
                "pipeline_success_rate": (
                    100.0 if run.conclusion == "success" else 0.0
                ),
                "workflow_duration_seconds": round(run.duration_seconds, 1),
                "flaky_results": report_values.get("flaky_results"),
                "test_total": report_values.get("test_total"),
                "test_failed": report_values.get("test_failed"),
            }
        )
    return points


def aggregate_daily(
    reports: list[PublishedReport], *, window_end: datetime, days: int
) -> list[dict[str, Any]]:
    daily: dict[date, Counter[str]] = defaultdict(Counter)
    for report in reports:
        report_day = report.generated_at.date()
        for test in report.tests:
            status = str(test.get("status") or "unknown")
            if status not in COMPLETED_TEST_STATUSES:
                status = "unknown"
            retries = test_retry_count(test)
            is_flaky = bool(test.get("flaky")) or retries > 0
            if status == "passed" and is_flaky:
                daily[report_day]["flaky"] += 1
            else:
                daily[report_day][status] += 1

    result: list[dict[str, Any]] = []
    first_day = window_end.date() - timedelta(days=days - 1)
    for offset in range(days):
        current_day = first_day + timedelta(days=offset)
        counts = daily[current_day]
        passed = counts["passed"] + counts["flaky"]
        total = sum(counts.values())
        result.append(
            {
                "date": current_day.isoformat(),
                "label": current_day.strftime("%d %b"),
                "passed": counts["passed"],
                "failed": counts["failed"] + counts["broken"],
                "flaky": counts["flaky"],
                "skipped": counts["skipped"] + counts["unknown"],
                "total": total,
                "pass_rate": percentage(passed, total),
            }
        )
    return result


def aggregate_pipeline_daily(
    runs: list[WorkflowRun], *, window_end: datetime, days: int
) -> dict[str, dict[str, Any]]:
    runs_by_day: dict[date, list[WorkflowRun]] = defaultdict(list)
    for run in runs:
        runs_by_day[run.created_at.date()].append(run)

    result: dict[str, dict[str, Any]] = {}
    first_day = window_end.date() - timedelta(days=days - 1)
    for offset in range(days):
        current_day = first_day + timedelta(days=offset)
        daily_runs = runs_by_day[current_day]
        successful = sum(run.conclusion == "success" for run in daily_runs)
        result[current_day.isoformat()] = {
            "pipeline_runs": len(daily_runs),
            "pipeline_success_rate": percentage(successful, len(daily_runs)),
            "pipeline_p95_duration_seconds": (
                round(
                    percentile(
                        [run.duration_seconds for run in daily_runs],
                        0.95,
                    ),
                    1,
                )
                if daily_runs
                else None
            ),
        }
    return result


def merge_daily_metrics(
    runs: list[WorkflowRun],
    reports: list[PublishedReport],
    *,
    window_end: datetime,
    days: int,
) -> list[dict[str, Any]]:
    test_daily = aggregate_daily(reports, window_end=window_end, days=days)
    pipeline_daily = aggregate_pipeline_daily(
        runs,
        window_end=window_end,
        days=days,
    )
    for day in test_daily:
        day.update(pipeline_daily[day["date"]])
    return test_daily


def aggregate_suites(reports: list[PublishedReport]) -> list[dict[str, Any]]:
    suites: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "counts": Counter(),
            "durations": [],
            "flaky_ids": set(),
            "test_ids": set(),
        }
    )
    for report in reports:
        for test in report.tests:
            scope = test_scope(test)
            aggregate = suites[scope]
            status = str(test.get("status") or "unknown")
            if status not in COMPLETED_TEST_STATUSES:
                status = "unknown"
            aggregate["counts"][status] += 1
            aggregate["durations"].append(test_duration_ms(test))
            identity = test_identity(test)
            aggregate["test_ids"].add(identity)
            if bool(test.get("flaky")) or test_retry_count(test) > 0:
                aggregate["flaky_ids"].add(identity)

    ordered_names = list(UI_SCOPE_ORDER)
    ordered_names.extend(sorted(set(suites) - set(ordered_names)))
    result: list[dict[str, Any]] = []
    for name in ordered_names:
        if name not in suites:
            continue
        aggregate = suites[name]
        counts: Counter[str] = aggregate["counts"]
        total = sum(counts.values())
        result.append(
            {
                "name": name,
                "passed": counts["passed"],
                "failed": counts["failed"] + counts["broken"],
                "skipped": counts["skipped"] + counts["unknown"],
                "total": total,
                "pass_rate": percentage(counts["passed"], total),
                "flaky_tests": len(aggregate["flaky_ids"]),
                "unique_tests": len(aggregate["test_ids"]),
                "p95_duration_ms": round(percentile(aggregate["durations"], 0.95), 1),
            }
        )
    return result


def aggregate_browser_metrics(
    reports: list[PublishedReport],
    *,
    browser_targets: dict[str, dict[str, float]],
    quality_targets: dict[str, dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    list[dict[str, Any]],
]:
    browser_runs: list[dict[str, Any]] = []
    all_durations: dict[str, list[float]] = defaultdict(list)
    identities: dict[str, set[str]] = defaultdict(set)
    failures: dict[tuple[str, str], dict[str, Any]] = {}

    for report in sorted(reports, key=lambda item: item.generated_at):
        tests_by_browser: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for test in report.tests:
            browser = browser_name(test)
            if browser is None:
                continue
            tests_by_browser[browser].append(test)
            identity = logical_ui_test_identity(test)
            identities[browser].add(identity)
            status = str(test.get("status") or "unknown").lower()
            if status in FAILED_STATUSES:
                key = (browser, identity)
                aggregate = failures.setdefault(
                    key,
                    {
                        "browser": browser,
                        "test_name": identity,
                        "failed_results": 0,
                        "runs": set(),
                        "latest_run": "",
                    },
                )
                aggregate["failed_results"] += 1
                aggregate["runs"].add(report.run_id)
                aggregate["latest_run"] = report.generated_at.strftime("%Y-%m-%d %H:%M")

        for browser in BROWSER_NAMES:
            browser_tests = tests_by_browser.get(browser, [])
            if not browser_tests:
                continue
            counts: Counter[str] = Counter(
                str(test.get("status") or "unknown").lower() for test in browser_tests
            )
            durations = [test_duration_ms(test) / 1000 for test in browser_tests]
            all_durations[browser].extend(durations)
            total = len(browser_tests)
            flaky = sum(
                bool(test.get("flaky")) or test_retry_count(test) > 0
                for test in browser_tests
            )
            browser_runs.append(
                {
                    "run_id": report.run_id,
                    "run_label": report.generated_at.strftime("%d %b %H:%M"),
                    "generated_at": report.generated_at.isoformat(timespec="seconds"),
                    "report_url": f"{report.path}/",
                    "browser": browser,
                    "total_tests": total,
                    "passed_tests": counts["passed"],
                    "failed_tests": counts["failed"],
                    "broken_tests": counts["broken"],
                    "pass_rate": ratio_percent(counts["passed"], total),
                    "fail_rate": ratio_percent(counts["failed"], total),
                    "broken_rate": ratio_percent(counts["broken"], total),
                    "flaky_rate": ratio_percent(flaky, total),
                    "avg_duration_sec": average(durations),
                    "run_duration_sec": round(sum(durations), 2),
                    "avg_target_sec": browser_targets[browser]["avg_duration_sec"],
                    "run_target_sec": browser_targets[browser]["run_duration_sec"],
                }
            )

    summary: list[dict[str, Any]] = []
    pass_target = float(quality_targets["pass_rate"]["value"])
    flaky_target = float(quality_targets["flaky_rate"]["value"])
    for browser in BROWSER_NAMES:
        rows = [row for row in browser_runs if row["browser"] == browser]
        total = sum(int(row["total_tests"]) for row in rows)
        passed = sum(int(row["passed_tests"]) for row in rows)
        failed = sum(
            int(row["failed_tests"]) + int(row["broken_tests"]) for row in rows
        )
        avg_duration = average([float(row["avg_duration_sec"]) for row in rows])
        flaky_rate = (
            sum(float(row["flaky_rate"]) * int(row["total_tests"]) for row in rows)
            / total
            if total
            else 0.0
        )
        p90_run = round(
            percentile([float(row["run_duration_sec"]) for row in rows], 0.90),
            2,
        )
        avg_target = browser_targets[browser]["avg_duration_sec"]
        run_target = browser_targets[browser]["run_duration_sec"]
        passed_gate = (
            ratio_percent(passed, total) >= pass_target
            and flaky_rate <= flaky_target
            and avg_duration <= avg_target
            and p90_run <= run_target
        )
        summary.append(
            {
                "browser": browser,
                "runs": len(rows),
                "total_tests": total,
                "failed_tests": failed,
                "pass_rate": round(ratio_percent(passed, total), 2),
                "flaky_rate": round(flaky_rate, 2),
                "avg_duration_sec": avg_duration,
                "p95_duration_sec": round(percentile(all_durations[browser], 0.95), 2),
                "p90_run_duration_sec": p90_run,
                "avg_target_sec": avg_target,
                "run_target_sec": run_target,
                "status": "ok" if passed_gate else "fail",
                "status_label": "OK" if passed_gate else "Failed",
            }
        )

    union = set().union(*(identities[browser] for browser in BROWSER_NAMES))
    common = (
        set.intersection(*(identities[browser] for browser in BROWSER_NAMES))
        if all(identities[browser] for browser in BROWSER_NAMES)
        else set()
    )
    coverage = {
        "common_tests": len(common),
        "unique_tests": len(union),
        "coverage_rate": round(ratio_percent(len(common), len(union)), 2),
        "by_browser": {browser: len(identities[browser]) for browser in BROWSER_NAMES},
    }
    failure_rows = [
        {
            **{key: value for key, value in aggregate.items() if key != "runs"},
            "failed_runs": len(aggregate["runs"]),
        }
        for aggregate in failures.values()
    ]
    failure_rows.sort(
        key=lambda item: (
            int(item["failed_results"]),
            int(item["failed_runs"]),
            str(item["latest_run"]),
        ),
        reverse=True,
    )
    return browser_runs, summary, coverage, failure_rows[:10]


def aggregate_tests(reports: list[PublishedReport]) -> list[dict[str, Any]]:
    aggregates: dict[str, dict[str, Any]] = {}
    for report in reports:
        for test in report.tests:
            identity = test_identity(test)
            aggregate = aggregates.setdefault(
                identity,
                {
                    "identity": identity,
                    "name": str(test.get("name") or identity),
                    "full_name": str(test.get("fullName") or identity),
                    "scope": test_scope(test),
                    "statuses": set(),
                    "failed_runs": 0,
                    "runs": 0,
                    "retries": 0,
                    "allure_flaky": False,
                    "durations": [],
                    "last_seen": report.generated_at,
                    "latest_report_path": report.path,
                    "latest_uid": str(test.get("uid") or ""),
                },
            )
            status = str(test.get("status") or "unknown")
            aggregate["statuses"].add(status)
            aggregate["runs"] += 1
            if status in FAILED_STATUSES:
                aggregate["failed_runs"] += 1
            aggregate["retries"] += test_retry_count(test)
            aggregate["allure_flaky"] = aggregate["allure_flaky"] or bool(
                test.get("flaky")
            )
            aggregate["durations"].append(test_duration_ms(test))
            if report.generated_at >= aggregate["last_seen"]:
                aggregate["last_seen"] = report.generated_at
                aggregate["latest_report_path"] = report.path
                aggregate["latest_uid"] = str(test.get("uid") or "")

    result: list[dict[str, Any]] = []
    for aggregate in aggregates.values():
        statuses: set[str] = aggregate["statuses"]
        mixed_status = "passed" in statuses and bool(statuses & FAILED_STATUSES)
        flaky = aggregate["allure_flaky"] or aggregate["retries"] > 0 or mixed_status
        if aggregate["failed_runs"] > 0 and mixed_status:
            signal = "Intermittent failure"
        elif aggregate["failed_runs"] > 0:
            signal = "Failing"
        elif flaky:
            signal = "Flaky"
        else:
            signal = "Slow"

        latest_uid = aggregate["latest_uid"]
        report_link = f"{aggregate['latest_report_path']}/"
        if latest_uid:
            report_link += f"#testresult/{latest_uid}"
        result.append(
            {
                "identity": aggregate["identity"],
                "name": aggregate["name"],
                "full_name": aggregate["full_name"],
                "scope": aggregate["scope"],
                "failed_runs": aggregate["failed_runs"],
                "runs": aggregate["runs"],
                "retries": aggregate["retries"],
                "flaky": flaky,
                "signal": signal,
                "p95_duration_ms": round(percentile(aggregate["durations"], 0.95), 1),
                "last_seen": aggregate["last_seen"].isoformat(timespec="seconds"),
                "report_link": report_link,
            }
        )

    problem_tests = [
        item for item in result if item["failed_runs"] > 0 or item["flaky"]
    ]
    problem_tests.sort(
        key=lambda item: (
            item["failed_runs"],
            int(item["flaky"]),
            item["retries"],
            item["p95_duration_ms"],
        ),
        reverse=True,
    )
    selected = problem_tests[:10]
    if len(selected) < 5:
        selected_ids = {item["identity"] for item in selected}
        slow_tests = sorted(
            (item for item in result if item["identity"] not in selected_ids),
            key=lambda item: item["p95_duration_ms"],
            reverse=True,
        )
        selected.extend(slow_tests[: 5 - len(selected)])
    return selected


def average(values: list[float]) -> float:
    return round(sum(values) / len(values), 2) if values else 0.0


def ratio_percent(numerator: int, denominator: int) -> float:
    return numerator / denominator * 100 if denominator else 0.0


def is_api_test(test: dict[str, Any]) -> bool:
    scope = test_scope(test).lower()
    full_name = str(test.get("fullName") or test.get("name") or "").lower()
    return scope == "api" or ".api." in full_name


def is_ui_test(test: dict[str, Any]) -> bool:
    scope = test_scope(test).lower()
    full_name = str(test.get("fullName") or test.get("name") or "").lower()
    return scope.startswith("ui") or ".ui." in full_name


def report_wall_clock_seconds(report: PublishedReport) -> float:
    bounds: list[tuple[float, float]] = []
    for test in report.tests:
        time_payload = test.get("time")
        if not isinstance(time_payload, dict):
            continue
        try:
            started_at = float(time_payload["start"])
            stopped_at = float(time_payload["stop"])
        except (KeyError, TypeError, ValueError):
            continue
        if stopped_at >= started_at:
            bounds.append((started_at, stopped_at))
    if not bounds:
        return 0.0
    return (max(stop for _, stop in bounds) - min(start for start, _ in bounds)) / 1000


def reference_run_metrics(
    runs: list[WorkflowRun],
    reports: list[PublishedReport],
    quality_targets: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build one row per Allure report using the reference dashboard formulas."""
    runs_by_id = {run.id: run for run in runs}
    rows: list[dict[str, Any]] = []
    distribution_keys = ("pass_rate", "fail_rate", "broken_rate")

    for report in sorted(reports, key=lambda item: item.generated_at):
        counts: Counter[str] = Counter()
        api_duration_ms = 0.0
        ui_duration_ms = 0.0
        api_tests = 0
        ui_tests = 0
        api_flaky_tests = 0
        ui_flaky_tests = 0

        for test in report.tests:
            status = str(test.get("status") or "unknown").lower()
            counts[status] += 1
            duration_ms = test_duration_ms(test)
            flaky = bool(test.get("flaky"))
            if is_api_test(test):
                api_tests += 1
                api_duration_ms += duration_ms
                api_flaky_tests += int(flaky)
            if is_ui_test(test):
                ui_tests += 1
                ui_duration_ms += duration_ms
                ui_flaky_tests += int(flaky)

        total_tests = sum(counts.values())
        passed_tests = counts["passed"]
        failed_tests = counts["failed"]
        broken_tests = counts["broken"]
        flaky_tests = api_flaky_tests + ui_flaky_tests
        run = runs_by_id.get(report.run_id)
        suite_duration_seconds = (
            run.duration_seconds
            if run is not None
            else report_wall_clock_seconds(report)
        )

        row: dict[str, Any] = {
            "run_id": report.run_id,
            "run_number": run.number if run is not None else report.run_id,
            "attempt": report.attempt,
            "run_label": report.generated_at.strftime("%Y-%m-%d %H:%M"),
            "generated_at": report.generated_at.isoformat(timespec="seconds"),
            "run_url": run.url if run is not None else report.run_url,
            "report_url": f"{report.path}/",
            "total_tests": total_tests,
            "api_tests": api_tests,
            "ui_tests": ui_tests,
            "passed_tests": passed_tests,
            "pass_rate": ratio_percent(passed_tests, total_tests),
            "failed_tests": failed_tests,
            "fail_rate": ratio_percent(failed_tests, total_tests),
            "broken_tests": broken_tests,
            "broken_rate": ratio_percent(broken_tests, total_tests),
            "flaky_tests": flaky_tests,
            "flaky_rate": ratio_percent(flaky_tests, total_tests),
            "ui_flaky_tests": ui_flaky_tests,
            "ui_flaky_rate": ratio_percent(ui_flaky_tests, ui_tests),
            "api_flaky_tests": api_flaky_tests,
            "api_flaky_rate": ratio_percent(api_flaky_tests, api_tests),
            "run_success": total_tests > 0 and passed_tests == total_tests,
            "avg_duration_sec": ui_duration_ms / ui_tests / 1000 if ui_tests else 0.0,
            "avg_api_duration_sec": api_duration_ms / api_tests / 1000
            if api_tests
            else 0.0,
            "ui_run_duration_sec": ui_duration_ms / 1000,
            "api_run_duration_sec": api_duration_ms / 1000,
            "suite_duration_sec": suite_duration_seconds,
        }
        passed_gates = sum(
            target_passed(float(row[key]), quality_targets[key])
            for key in distribution_keys
        )
        row["quality_gates_passed"] = passed_gates
        row["quality_gates_failed"] = len(distribution_keys) - passed_gates
        row["quality_gate_status"] = (
            "OK" if row["quality_gates_failed"] == 0 else "Failed"
        )
        rows.append(row)

    return rows


def average_formula(
    label: str,
    rows: list[dict[str, Any]],
    field: str,
    unit: str,
) -> str:
    if not rows:
        return f"{label} = n/a"
    series = " + ".join(f"{float(row[field]):.2f}" for row in rows)
    value = average([float(row[field]) for row in rows])
    return f"{label} = ({series}) / {len(rows)} = {value:.2f}{unit}"


def build_quality_gates(
    rows: list[dict[str, Any]],
    quality_targets: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    total_runs = len(rows)
    total_tests = sum(int(row["total_tests"]) for row in rows)
    total_flaky = sum(int(row["flaky_tests"]) for row in rows)
    successful_runs = sum(bool(row["run_success"]) for row in rows)
    values = {
        "pass_rate": average([float(row["pass_rate"]) for row in rows]),
        "fail_rate": average([float(row["fail_rate"]) for row in rows]),
        "broken_rate": average([float(row["broken_rate"]) for row in rows]),
        "flaky_rate": percentage(total_flaky, total_tests) or 0.0,
        "stability_rate": percentage(successful_runs, total_runs) or 0.0,
        "avg_duration_sec": average([float(row["avg_duration_sec"]) for row in rows]),
        "avg_api_duration_sec": average(
            [float(row["avg_api_duration_sec"]) for row in rows]
        ),
        "ui_run_duration_sec": average(
            [float(row["ui_run_duration_sec"]) for row in rows]
        ),
        "api_run_duration_sec": average(
            [float(row["api_run_duration_sec"]) for row in rows]
        ),
        "suite_duration_sec": average(
            [float(row["suite_duration_sec"]) for row in rows]
        ),
        "ui_flaky_rate": average([float(row["ui_flaky_rate"]) for row in rows]),
        "api_flaky_rate": average([float(row["api_flaky_rate"]) for row in rows]),
    }
    formulas = {
        "pass_rate": average_formula("average pass rate", rows, "pass_rate", "%"),
        "fail_rate": average_formula("average fail rate", rows, "fail_rate", "%"),
        "broken_rate": average_formula("average broken rate", rows, "broken_rate", "%"),
        "flaky_rate": (
            f"flaky rate = {total_flaky} / {total_tests} = {values['flaky_rate']:.2f}%"
        ),
        "stability_rate": (
            f"stability = {successful_runs} / {total_runs} = "
            f"{values['stability_rate']:.2f}%"
        ),
        "avg_duration_sec": average_formula(
            "average UI test duration", rows, "avg_duration_sec", "s"
        ),
        "avg_api_duration_sec": average_formula(
            "average API test duration", rows, "avg_api_duration_sec", "s"
        ),
        "ui_run_duration_sec": average_formula(
            "total UI test time", rows, "ui_run_duration_sec", "s"
        ),
        "api_run_duration_sec": average_formula(
            "average API run duration", rows, "api_run_duration_sec", "s"
        ),
        "suite_duration_sec": average_formula(
            "average pipeline duration", rows, "suite_duration_sec", "s"
        ),
        "ui_flaky_rate": average_formula(
            "average UI flaky rate", rows, "ui_flaky_rate", "%"
        ),
        "api_flaky_rate": average_formula(
            "average API flaky rate", rows, "api_flaky_rate", "%"
        ),
    }
    descriptions = {
        "pass_rate": "Unweighted average of the final pass rate of every published run.",
        "fail_rate": "Unweighted average of the final failed-test rate of every published run.",
        "broken_rate": "Unweighted average of the final broken-test rate of every published run.",
        "flaky_rate": "All flaky API and UI results divided by all final test results.",
        "stability_rate": "Published runs where every final test result passed, divided by all published runs.",
        "avg_duration_sec": "Unweighted average of each run's mean UI-test duration.",
        "avg_api_duration_sec": "Unweighted average of each run's mean API-test duration.",
        "ui_run_duration_sec": "Unweighted average of the summed UI test duration in each run.",
        "api_run_duration_sec": "Unweighted average of the summed API test duration in each run.",
        "suite_duration_sec": "Unweighted average of the GitHub Actions test-stage duration.",
        "ui_flaky_rate": "Unweighted average of the UI flaky rate of every published run.",
        "api_flaky_rate": "Unweighted average of the API flaky rate of every published run.",
    }

    gate_order = (
        "pass_rate",
        "fail_rate",
        "broken_rate",
        "flaky_rate",
        "ui_flaky_rate",
        "api_flaky_rate",
        "stability_rate",
        "avg_duration_sec",
        "avg_api_duration_sec",
        "ui_run_duration_sec",
        "api_run_duration_sec",
        "suite_duration_sec",
    )
    gates: list[dict[str, Any]] = []
    for key in gate_order:
        target_key = "flaky_rate" if key in {"ui_flaky_rate", "api_flaky_rate"} else key
        target = quality_targets[target_key]
        direction = str(target["direction"])
        threshold = float(target["value"])
        value = float(values[key])
        passed = value >= threshold if direction == "minimum" else value <= threshold
        default_name = key.replace("_", " ").title()
        name = (
            "Average UI Flaky Rate"
            if key == "ui_flaky_rate"
            else "Average API Flaky Rate"
            if key == "api_flaky_rate"
            else str(target.get("name") or default_name)
        )
        gates.append(
            {
                "key": key,
                "name": name,
                "value": value,
                "unit": "%" if key.endswith("_rate") else "s",
                "target": threshold,
                "direction": direction,
                "threshold": (
                    f">= {threshold:.2f}"
                    if direction == "minimum"
                    else f"<= {threshold:.2f}"
                ),
                "status": "ok" if passed else "fail",
                "status_label": "OK" if passed else "Failed",
                "formula": formulas[key],
                "description": descriptions[key],
                "recommendation": str(target.get("recommendation") or ""),
            }
        )

    summary = {
        "published_runs": total_runs,
        "successful_runs": successful_runs,
        "total_tests": total_tests,
        "total_flaky": total_flaky,
        **values,
    }
    return summary, gates


def slowest_tests(
    reports: list[PublishedReport], *, ui: bool, limit: int = 4
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for report in reports:
        for test in report.tests:
            if is_ui_test(test) if ui else is_api_test(test):
                duration_seconds = round(test_duration_ms(test) / 1000, 2)
                if duration_seconds <= 0:
                    continue
                scope = test_scope(test)
                browser = (
                    scope.split("·", maxsplit=1)[1].strip()
                    if scope.startswith("UI ·")
                    else scope
                )
                records.append(
                    {
                        "run_id": report.run_id,
                        "run_label": report.generated_at.strftime("%Y-%m-%d %H:%M"),
                        "browser": browser,
                        "test_name": str(
                            test.get("fullName")
                            or test.get("name")
                            or test.get("uid")
                            or "unknown"
                        ),
                        "duration_sec": duration_seconds,
                        "status": str(test.get("status") or "unknown"),
                        "report_url": (
                            f"{report.path}/#testresult/{test['uid']}"
                            if test.get("uid")
                            else f"{report.path}/"
                        ),
                    }
                )
    records.sort(key=lambda item: float(item["duration_sec"]), reverse=True)
    return records[:limit]


def build_metrics(
    runs: list[WorkflowRun],
    reports: list[PublishedReport],
    *,
    now: datetime,
    days: int,
    quality_targets: dict[str, dict[str, Any]],
    browser_targets: dict[str, dict[str, float]] | None = None,
    coverage: dict[str, Any] | None = None,
    published_reports: list[PublishedReport] | None = None,
) -> dict[str, Any]:
    if browser_targets is None:
        browser_targets = DEFAULT_BROWSER_TARGETS
    report_inventory = published_reports if published_reports is not None else reports
    reference_rows = reference_run_metrics(runs, reports, quality_targets)
    reference_summary, quality_gates = build_quality_gates(
        reference_rows,
        quality_targets,
    )
    counts = status_counts(reports)
    test_total = sum(counts.values())
    test_passed = counts["passed"]
    tests_by_identity: dict[str, set[str]] = defaultdict(set)
    retries_by_identity: Counter[str] = Counter()
    allure_flaky_ids: set[str] = set()
    for report in reports:
        for test in report.tests:
            identity = test_identity(test)
            tests_by_identity[identity].add(str(test.get("status") or "unknown"))
            retries = test_retry_count(test)
            retries_by_identity[identity] += retries
            if bool(test.get("flaky")) or retries > 0:
                allure_flaky_ids.add(identity)

    historical_flaky_ids = {
        identity
        for identity, statuses in tests_by_identity.items()
        if "passed" in statuses and bool(statuses & FAILED_STATUSES)
    }
    flaky_ids = allure_flaky_ids | historical_flaky_ids
    retry_count = sum(retries_by_identity.values())
    successful_runs = sum(run.conclusion == "success" for run in runs)
    report_by_run = {report.run_id: report for report in report_inventory}
    incomplete_run_ids = {run.id for run in runs if not run.test_suite_complete}

    recent_runs = []
    for run in sorted(runs, key=lambda item: item.created_at, reverse=True):
        report = report_by_run.get(run.id)
        recent_runs.append(
            {
                "id": run.id,
                "number": run.number,
                "attempt": run.attempt,
                "conclusion": run.conclusion,
                "event": run.event,
                "branch": run.branch,
                "created_at": run.created_at.isoformat(timespec="seconds"),
                "duration_seconds": round(run.duration_seconds, 1),
                "run_url": run.url,
                "report_url": f"{report.path}/" if report else None,
                "test_suite_complete": run.test_suite_complete,
            }
        )

    (
        browser_runs,
        browser_summary,
        browser_coverage,
        browser_failures,
    ) = aggregate_browser_metrics(
        reports,
        browser_targets=browser_targets,
        quality_targets=quality_targets,
    )

    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "window": {
            "days": days,
            "start": window_start(now, days).isoformat(timespec="seconds"),
            "end": now.isoformat(timespec="seconds"),
        },
        "data_quality": {
            "completed_runs": len(runs),
            "published_reports": len(report_inventory),
            "metric_reports": len(reports),
            "incomplete_runs": sum(not run.test_suite_complete for run in runs),
            "incomplete_reports": sum(
                report.run_id in incomplete_run_ids for report in report_inventory
            ),
            "runs_without_report": sum(run.id not in report_by_run for run in runs),
        },
        "pipeline": {
            "completed": len(runs),
            "successful": successful_runs,
            "unsuccessful": len(runs) - successful_runs,
            "success_rate": percentage(successful_runs, len(runs)),
            "p95_duration_seconds": round(
                percentile([run.duration_seconds for run in runs], 0.95), 1
            ),
        },
        "tests": {
            "total": test_total,
            "passed": test_passed,
            "failed": counts["failed"] + counts["broken"],
            "skipped": counts["skipped"] + counts["unknown"],
            "pass_rate": percentage(test_passed, test_total),
            "unique": len(tests_by_identity),
            "flaky": len(flaky_ids),
            "retries": retry_count,
            "retry_rate": percentage(retry_count, test_total + retry_count),
        },
        "daily": merge_daily_metrics(
            runs,
            reports,
            window_end=now,
            days=days,
        ),
        "run_trends": aggregate_run_trends(
            runs,
            reports,
            published_reports=report_inventory,
        ),
        "quality_targets": quality_targets,
        "reference_summary": reference_summary,
        "quality_gates": quality_gates,
        "metric_runs": reference_rows,
        "slowest_ui_tests": slowest_tests(reports, ui=True),
        "slowest_api_tests": slowest_tests(reports, ui=False),
        "browser_runs": browser_runs,
        "browser_summary": browser_summary,
        "browser_coverage": browser_coverage,
        "browser_failures": browser_failures,
        "browser_targets": browser_targets,
        "suites": aggregate_suites(reports),
        "attention": aggregate_tests(reports),
        "recent_runs": recent_runs,
        "coverage": coverage,
    }


def format_percent(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f}%"


def format_duration(seconds: float) -> str:
    rounded = max(0, round(seconds))
    minutes, remaining_seconds = divmod(rounded, 60)
    if minutes:
        return f"{minutes}m {remaining_seconds:02d}s"
    return f"{remaining_seconds}s"


def target_passed(value: float, target: dict[str, Any]) -> bool:
    threshold = float(target["value"])
    if target["direction"] == "minimum":
        return value >= threshold
    return value <= threshold


def chart_target(metrics: dict[str, Any], field: str) -> dict[str, Any]:
    target_keys = {
        "test_pass_rate": "pass_rate",
        "pipeline_success_rate": "stability_rate",
        "workflow_duration_seconds": "suite_duration_sec",
    }
    if field == "flaky_results":
        return {"direction": "maximum", "value": 0.0}
    return metrics["quality_targets"][target_keys[field]]


def format_target(
    target: dict[str, Any],
    formatter: Callable[[float], str],
) -> str:
    operator = "≥" if target["direction"] == "minimum" else "≤"
    return f"{operator} {formatter(float(target['value']))}"


def render_line_chart(
    metrics: dict[str, Any],
    *,
    field: str,
    title: str,
    formatter: Callable[[float], str],
    css_class: str,
    percentage_scale: bool = False,
) -> str:
    points = metrics["run_trends"]
    target = chart_target(metrics, field)
    values = [
        float(point[field]) if point.get(field) is not None else None
        for point in points
    ]
    available = [value for value in values if value is not None]
    target_text = format_target(target, formatter)
    if not available:
        return (
            '<article class="chart-card">'
            '<div class="chart-head">'
            f"<h3>{html.escape(title)}</h3>"
            f'<span class="target-badge">Target {html.escape(target_text)}</span>'
            "</div>"
            '<p class="empty-state">No data in this period.</p>'
            "</article>"
        )

    lower = 0.0
    if percentage_scale:
        upper = 100.0
    else:
        upper = max(max(available), float(target["value"])) * 1.15
    if math.isclose(lower, upper):
        upper = 1.0

    width = 720.0
    height = 250.0
    left = 54.0
    right = 18.0
    top = 24.0
    bottom = 62.0
    plot_width = width - left - right
    plot_height = height - top - bottom

    def point(index: int, value: float) -> tuple[float, float]:
        x = left
        if len(values) > 1:
            x += index * plot_width / (len(values) - 1)
        y = top + (upper - value) * plot_height / (upper - lower)
        return x, y

    segments: list[list[str]] = []
    current: list[str] = []
    circles: list[str] = []
    for index, value in enumerate(values):
        if value is None:
            if current:
                segments.append(current)
                current = []
            continue
        x, y = point(index, value)
        current.append(f"{x:.1f},{y:.1f}")
        state = "ok" if target_passed(value, target) else "fail"
        label = (
            f"Run #{points[index]['run_number']} · {points[index]['label']}: "
            f"{formatter(value)} · target {target_text}"
        )
        circles.append(
            f'<a href="{html.escape(points[index]["run_url"])}">'
            f'<circle class="chart-point chart-point-{state}" '
            f'cx="{x:.1f}" cy="{y:.1f}" r="4">'
            f"<title>{html.escape(label)}</title></circle></a>"
        )
    if current:
        segments.append(current)

    lines = "".join(
        f'<polyline class="chart-line {css_class}" points="{" ".join(segment)}"/>'
        for segment in segments
        if len(segment) > 1
    )
    latest_index = max(index for index, value in enumerate(values) if value is not None)
    latest_value = values[latest_index]
    assert latest_value is not None
    latest_state = "ok" if target_passed(latest_value, target) else "fail"
    target_y = point(0, float(target["value"]))[1]

    grid_lines: list[str] = []
    for grid_index in range(5):
        ratio = grid_index / 4
        y = top + plot_height * ratio
        grid_value = upper - (upper - lower) * ratio
        grid_lines.append(
            f'<line class="chart-grid" x1="{left}" y1="{y:.1f}" '
            f'x2="{width - right}" y2="{y:.1f}"/>'
            f'<text class="chart-axis chart-axis-y" x="{left - 8}" '
            f'y="{y + 4:.1f}">{html.escape(formatter(grid_value))}</text>'
        )

    label_count = min(6, len(points))
    if label_count <= 1:
        label_indices = {0}
    else:
        label_indices = {
            round(index * (len(points) - 1) / (label_count - 1))
            for index in range(label_count)
        }
    x_labels: list[str] = []
    for index in sorted(label_indices):
        x = point(index, lower)[0]
        x_labels.append(
            f'<text class="chart-axis chart-axis-x" '
            f'transform="translate({x:.1f} {height - 30:.1f}) rotate(-22)">'
            f"{html.escape(str(points[index]['label']))}</text>"
        )

    return f"""
    <article class="chart-card">
      <div class="chart-head">
        <div>
          <h3>{html.escape(title)}</h3>
          <span class="target-badge">Target {html.escape(target_text)}</span>
        </div>
        <div class="chart-latest">
          <strong>{html.escape(formatter(latest_value))}</strong>
          <span class="target-status target-status-{latest_state}">
            {"On target" if latest_state == "ok" else "Off target"}
          </span>
        </div>
      </div>
      <svg class="line-chart" viewBox="0 0 {width:.0f} {height:.0f}" role="img"
           aria-label="{html.escape(title)} by workflow run over {metrics["window"]["days"]} days">
        {"".join(grid_lines)}
        <line class="target-line" x1="{left}" y1="{target_y:.1f}"
              x2="{width - right}" y2="{target_y:.1f}"/>
        <text class="target-label" x="{left + 6}" y="{max(13.0, target_y - 7):.1f}">
          Target {html.escape(target_text)}
        </text>
        {lines}
        {"".join(circles)}
        {"".join(x_labels)}
      </svg>
    </article>
    """


def render_metric_charts(metrics: dict[str, Any]) -> str:
    return "\n".join(
        (
            render_line_chart(
                metrics,
                field="test_pass_rate",
                title="Test pass rate",
                formatter=lambda value: f"{value:.1f}%",
                css_class="chart-green",
                percentage_scale=True,
            ),
            render_line_chart(
                metrics,
                field="pipeline_success_rate",
                title="Pipeline result",
                formatter=lambda value: f"{value:.0f}%",
                css_class="chart-blue",
                percentage_scale=True,
            ),
            render_line_chart(
                metrics,
                field="workflow_duration_seconds",
                title="Workflow duration",
                formatter=format_duration,
                css_class="chart-purple",
            ),
            render_line_chart(
                metrics,
                field="flaky_results",
                title="Flaky test results",
                formatter=lambda value: str(round(value)),
                css_class="chart-orange",
            ),
        )
    )


def render_suite_cards(metrics: dict[str, Any]) -> str:
    cards: list[str] = []
    pass_rate_target = metrics["quality_targets"]["pass_rate"]
    for suite in metrics["suites"]:
        rate = suite["pass_rate"]
        width = 0 if rate is None else max(0, min(100, rate))
        state = (
            "healthy"
            if rate is not None and target_passed(rate, pass_rate_target)
            else "warning"
        )
        cards.append(
            '<article class="suite">'
            f"<h3>{html.escape(suite['name'])}</h3>"
            f'<strong class="suite-value">{html.escape(format_percent(rate))}</strong>'
            f'<div class="progress"><span class="{state}" '
            f'style="width: {width:.1f}%"></span></div>'
            "<p>"
            f"{suite['flaky_tests']} flaky · "
            f"p95 {html.escape(format_duration(suite['p95_duration_ms'] / 1000))}"
            "</p>"
            "</article>"
        )
    if cards:
        return "\n".join(cards)
    return '<p class="empty-state">No published test results in this window.</p>'


def render_attention_rows(metrics: dict[str, Any], *, root_prefix: str) -> str:
    rows: list[str] = []
    for test in metrics["attention"]:
        rows.append(
            "<tr>"
            f'<td><a href="{html.escape(root_prefix + test["report_link"])}">'
            f"{html.escape(test['name'])}</a></td>"
            f'<td><span class="badge">{html.escape(test["signal"])}</span></td>'
            f'<td class="number">{test["failed_runs"]} / {test["runs"]}</td>'
            f'<td class="number">{test["retries"]}</td>'
            f"<td>{html.escape(test['scope'])}</td>"
            f'<td class="number">'
            f"{html.escape(format_duration(test['p95_duration_ms'] / 1000))}</td>"
            "</tr>"
        )
    if rows:
        return "\n".join(rows)
    return '<tr><td colspan="6" class="empty-state">No test data available.</td></tr>'


def render_run_rows(metrics: dict[str, Any], *, root_prefix: str) -> str:
    rows: list[str] = []
    for run in metrics["recent_runs"]:
        report_link = (
            f'<a href="{html.escape(root_prefix + run["report_url"])}">Allure</a>'
            if run["report_url"]
            else '<span class="muted">No report</span>'
        )
        rows.append(
            "<tr>"
            f'<td><a href="{html.escape(run["run_url"])}">#{run["number"]}</a></td>'
            f'<td><span class="status status-{html.escape(run["conclusion"])}">'
            f"{html.escape(run['conclusion'])}</span></td>"
            f"<td>{html.escape(run['event'])}</td>"
            f"<td>{html.escape(run['branch'])}</td>"
            f'<td class="number">{html.escape(format_duration(run["duration_seconds"]))}</td>'
            f"<td>{report_link}</td>"
            "</tr>"
        )
    if rows:
        return "\n".join(rows)
    return '<tr><td colspan="6" class="empty-state">No completed runs found.</td></tr>'


LINEAR_REPORT_CSS = """
:root {
  color-scheme: light;
  --background: #f6f8fa;
  --surface: #ffffff;
  --text: #1f2328;
  --muted: #59636e;
  --border: #d0d7de;
  --primary: #0969da;
  --ok: #1a7f37;
  --ok-soft: #dafbe1;
  --fail: #cf222e;
  --fail-soft: #ffebe9;
  --neutral-soft: #eaeef2;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--background);
  color: var(--text);
  font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
.page { width: min(1320px, 100%); margin: 0 auto; padding: 28px 20px 56px; }
.topbar {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 20px; flex-wrap: wrap;
}
h1 { margin: 0 0 4px; font-size: 30px; }
h2 { margin: 0; font-size: 21px; }
h3 { margin: 18px 0 8px; font-size: 16px; }
p { margin: 0; }
.muted, .section-note { color: var(--muted); }
.top-actions, .period-links, .contents { display: flex; gap: 8px; flex-wrap: wrap; }
.period-link, .contents a {
  display: inline-block; padding: 6px 10px; border: 1px solid var(--border);
  border-radius: 6px; background: var(--surface); color: var(--text);
}
.period-link.active { border-color: var(--primary); color: var(--primary); font-weight: 600; }
.window {
  margin-top: 14px; padding: 12px 14px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 8px;
}
.contents { margin-top: 14px; }
.section { margin-top: 28px; scroll-margin-top: 12px; }
.section-head {
  display: flex; justify-content: space-between; gap: 12px;
  align-items: baseline; flex-wrap: wrap; margin-bottom: 10px;
}
.table-wrap {
  overflow-x: auto; background: var(--surface);
  border: 1px solid var(--border); border-radius: 8px;
}
table { width: 100%; border-collapse: collapse; }
th, td {
  padding: 9px 11px; text-align: left; vertical-align: top;
  border-bottom: 1px solid var(--border);
}
th { background: var(--background); color: var(--muted); font-size: 13px; }
tr:last-child td { border-bottom: 0; }
.number { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
.formula {
  min-width: 320px; color: var(--muted);
  font: 12px/1.45 ui-monospace, SFMono-Regular, Consolas, monospace;
  overflow-wrap: anywhere;
}
.description { min-width: 240px; }
.status {
  display: inline-block; padding: 2px 7px; border-radius: 999px;
  font-weight: 700; white-space: nowrap;
}
.status-ok, .status-success { color: var(--ok); background: var(--ok-soft); }
.status-fail, .status-failure, .status-broken, .status-timed_out {
  color: var(--fail); background: var(--fail-soft);
}
.status-cancelled, .status-skipped, .status-neutral, .status-unknown {
  color: var(--muted); background: var(--neutral-soft);
}
.summary {
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px; margin-top: 16px;
}
.summary article {
  padding: 14px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 8px;
}
.summary strong { display: block; margin-top: 3px; font-size: 25px; }
.empty-state { padding: 14px; color: var(--muted); }
.footer {
  display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
  margin-top: 28px; color: var(--muted); font-size: 13px;
}
@media (max-width: 860px) {
  .summary { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 520px) {
  .page { padding: 20px 12px 40px; }
  .summary { grid-template-columns: 1fr; }
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --background: #0d1117; --surface: #161b22; --text: #e6edf3;
    --muted: #8b949e; --border: #30363d; --primary: #58a6ff;
    --ok: #3fb950; --ok-soft: #12261a;
    --fail: #f85149; --fail-soft: #32191c; --neutral-soft: #21262d;
  }
}
"""


GRAPH_DASHBOARD_CSS = """
:root {
  color-scheme: light;
  --background: #f6f8fa;
  --surface: #ffffff;
  --text: #1f2328;
  --muted: #636c76;
  --border: #d0d7de;
  --primary: #0969da;
  --healthy: #1a7f37;
  --healthy-soft: #dafbe1;
  --warning: #bf8700;
  --warning-soft: #fff8c5;
  --danger: #cf222e;
  --danger-soft: #ffebe9;
  --track: #eaeef2;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--background);
  color: var(--text);
  font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
.page { width: min(1180px, 100%); margin: 0 auto; padding: 28px 20px 48px; }
.topbar {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 18px; flex-wrap: wrap; margin-bottom: 20px;
}
h1 { font-size: 28px; line-height: 1.2; margin: 0 0 4px; }
h2 { font-size: 19px; margin: 0; }
h3 { font-size: 15px; margin: 0; }
p { margin: 0; }
.muted, .section-note, .suite p { color: var(--muted); }
.top-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.period {
  display: inline-flex; align-items: center; gap: 8px; padding: 6px 10px;
  background: var(--surface); border: 1px solid var(--border); border-radius: 999px;
}
.period-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--healthy); }
.period-links { display: flex; gap: 6px; flex-wrap: wrap; }
.period-link {
  display: inline-block; padding: 5px 9px; border: 1px solid var(--border);
  border-radius: 999px; background: var(--surface); color: var(--text);
}
.period-link.active {
  border-color: var(--primary); color: var(--primary); font-weight: 600;
}
.stats {
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px;
}
.card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px;
}
.stat-label { color: var(--muted); }
.stat-value {
  display: block; font-size: 30px; line-height: 1.2; margin: 4px 0;
}
.stat-context {
  display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap;
}
.badge {
  display: inline-block; padding: 2px 7px; border-radius: 999px;
  background: var(--track); color: var(--text); white-space: nowrap;
}
.section { margin-top: 22px; }
.section-head {
  display: flex; justify-content: space-between; gap: 12px; align-items: baseline;
  flex-wrap: wrap; margin-bottom: 10px;
}
.chart-grid-layout {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
}
.chart-card {
  min-width: 0; padding: 14px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 12px;
}
.chart-head {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 12px; margin-bottom: 8px;
}
.chart-head strong { font-size: 18px; }
.chart-head > div:first-child { display: grid; gap: 3px; }
.target-badge { color: var(--muted); font-size: 12px; }
.chart-latest {
  display: flex; align-items: flex-end; flex-direction: column; gap: 3px;
  text-align: right;
}
.target-status {
  display: inline-block; padding: 2px 7px; border-radius: 999px;
  font-size: 11px; font-weight: 600; white-space: nowrap;
}
.target-status-ok { color: var(--healthy); background: var(--healthy-soft); }
.target-status-fail { color: var(--danger); background: var(--danger-soft); }
.line-chart { display: block; width: 100%; height: auto; overflow: visible; }
.chart-grid { stroke: var(--border); stroke-width: 1; }
.chart-axis { fill: var(--muted); font-size: 11px; }
.chart-axis-y, .chart-axis-x { text-anchor: end; }
.target-line {
  stroke: var(--muted); stroke-width: 1.5; stroke-dasharray: 6 5;
}
.target-label { fill: var(--muted); font-size: 11px; font-weight: 600; }
.chart-line {
  fill: none; stroke: currentColor; stroke-width: 3;
  stroke-linecap: round; stroke-linejoin: round;
}
.chart-point { fill: var(--surface); stroke-width: 2.5; }
.chart-point-ok { stroke: var(--healthy); }
.chart-point-fail { stroke: var(--danger); }
.chart-green { color: var(--healthy); }
.chart-blue { color: var(--primary); }
.chart-purple { color: #8250df; }
.chart-orange { color: #bc4c00; }
.healthy { background: var(--healthy); }
.warning { background: var(--warning); }
.danger { background: var(--danger); }
.empty { background: var(--track); }
.trend-label { font-weight: 600; white-space: nowrap; }
.trend-detail { font-size: 12px; white-space: nowrap; }
.suites {
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0;
}
.suite { padding: 4px 16px 6px 0; }
.suite + .suite {
  border-left: 1px solid var(--border); padding-left: 16px;
}
.suite-value { display: block; font-size: 22px; margin: 3px 0; }
.progress {
  height: 7px; border-radius: 999px; overflow: hidden;
  background: var(--track); margin: 7px 0;
}
.progress span { display: block; height: 100%; border-radius: inherit; }
.table-wrap {
  overflow-x: auto; background: var(--surface);
  border: 1px solid var(--border); border-radius: 12px;
}
table { width: 100%; border-collapse: collapse; }
th, td {
  padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border);
}
th { color: var(--muted); font-size: 13px; font-weight: 600; }
tr:last-child td { border-bottom: 0; }
.number {
  text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums;
}
.status {
  display: inline-block; padding: 2px 7px; border-radius: 999px; font-weight: 600;
}
.status-success { color: var(--healthy); background: var(--healthy-soft); }
.status-failure, .status-timed_out, .status-action_required {
  color: var(--danger); background: var(--danger-soft);
}
.status-cancelled, .status-skipped, .status-neutral, .status-unknown {
  color: var(--warning); background: var(--warning-soft);
}
.empty-state { color: var(--muted); padding: 14px; }
.footer {
  display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
  color: var(--muted); margin-top: 24px; font-size: 13px;
}
@media (max-width: 760px) {
  .stats { grid-template-columns: 1fr; }
  .suites { grid-template-columns: 1fr 1fr; gap: 14px; }
  .suite + .suite { border-left: 0; padding-left: 0; }
  .chart-grid-layout { grid-template-columns: 1fr; }
}
@media (min-width: 761px) and (max-width: 980px) {
  .stats { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
  .page { padding: 20px 12px 36px; }
  .suites { grid-template-columns: 1fr; }
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --background: #0d1117; --surface: #161b22; --text: #e6edf3;
    --muted: #8b949e; --border: #30363d; --primary: #58a6ff;
    --healthy: #3fb950; --healthy-soft: #12261a;
    --warning: #d29922; --warning-soft: #2d250d;
    --danger: #f85149; --danger-soft: #32191c; --track: #30363d;
  }
}
"""


def gate_by_key(metrics: dict[str, Any], key: str) -> dict[str, Any]:
    return next(gate for gate in metrics["quality_gates"] if gate["key"] == key)


def render_gate_rows(metrics: dict[str, Any], keys: tuple[str, ...]) -> str:
    rows: list[str] = []
    for key in keys:
        gate = gate_by_key(metrics, key)
        rows.append(
            "<tr>"
            f"<td><strong>{html.escape(gate['name'])}</strong></td>"
            f'<td class="number">{float(gate["value"]):.2f}{html.escape(gate["unit"])}</td>'
            f'<td class="number">{html.escape(gate["threshold"])}{html.escape(gate["unit"])}</td>'
            f'<td><span class="status status-{gate["status"]}">{gate["status_label"]}</span></td>'
            f'<td class="formula">{html.escape(gate["formula"])}</td>'
            f'<td class="description">{html.escape(gate["description"])}'
            + (
                f'<br><span class="muted">Action: {html.escape(gate["recommendation"])}</span>'
                if gate["recommendation"]
                else ""
            )
            + "</td></tr>"
        )
    return "\n".join(rows)


def render_distribution_rows(metrics: dict[str, Any], *, root_prefix: str) -> str:
    rows: list[str] = []
    for run in metrics["metric_runs"]:
        rows.append(
            "<tr>"
            f'<td><a href="{html.escape(run["run_url"])}">{html.escape(run["run_label"])}</a>'
            f'<br><a class="muted" href="{html.escape(root_prefix + run["report_url"])}">'
            f"Allure · run #{run['run_number']}</a></td>"
            f'<td class="number">{run["total_tests"]}</td>'
            f'<td class="number">{run["passed_tests"]} / {float(run["pass_rate"]):.2f}%</td>'
            f'<td class="number">{run["failed_tests"]} / {float(run["fail_rate"]):.2f}%</td>'
            f'<td class="number">{run["broken_tests"]} / {float(run["broken_rate"]):.2f}%</td>'
            f'<td><span class="status status-{"ok" if run["quality_gate_status"] == "OK" else "fail"}">'
            f"{run['quality_gate_status']}</span><br>"
            f'<span class="muted">{run["quality_gates_passed"]} passed / '
            f"{run['quality_gates_failed']} failed</span></td>"
            "</tr>"
        )
    return (
        "\n".join(rows)
        or '<tr><td colspan="6" class="empty-state">No published reports.</td></tr>'
    )


def render_flaky_rows(metrics: dict[str, Any], *, root_prefix: str) -> str:
    rows: list[str] = []
    for run in metrics["metric_runs"]:
        rows.append(
            "<tr>"
            f'<td><a href="{html.escape(root_prefix + run["report_url"])}">'
            f"{html.escape(run['run_label'])}</a></td>"
            f'<td class="number">{run["flaky_tests"]} / {float(run["flaky_rate"]):.2f}%</td>'
            f'<td class="number">{run["ui_flaky_tests"]} / {run["ui_tests"]} / '
            f"{float(run['ui_flaky_rate']):.2f}%</td>"
            f'<td class="number">{run["api_flaky_tests"]} / {run["api_tests"]} / '
            f"{float(run['api_flaky_rate']):.2f}%</td>"
            "</tr>"
        )
    return (
        "\n".join(rows)
        or '<tr><td colspan="4" class="empty-state">No published reports.</td></tr>'
    )


def render_stability_rows(metrics: dict[str, Any]) -> str:
    rows: list[str] = []
    for run in metrics["metric_runs"]:
        state = "ok" if run["run_success"] else "fail"
        label = "Successful" if run["run_success"] else "Unstable"
        rows.append(
            "<tr>"
            f'<td><a href="{html.escape(run["run_url"])}">{html.escape(run["run_label"])}</a></td>'
            f'<td class="number">{run["passed_tests"]} / {run["total_tests"]}</td>'
            f'<td><span class="status status-{state}">{label}</span></td>'
            "</tr>"
        )
    return (
        "\n".join(rows)
        or '<tr><td colspan="3" class="empty-state">No published reports.</td></tr>'
    )


def render_duration_rows(metrics: dict[str, Any]) -> str:
    rows: list[str] = []
    duration_fields = (
        ("avg_duration_sec", "avg_duration_sec"),
        ("avg_api_duration_sec", "avg_api_duration_sec"),
        ("ui_run_duration_sec", "ui_run_duration_sec"),
        ("api_run_duration_sec", "api_run_duration_sec"),
        ("suite_duration_sec", "suite_duration_sec"),
    )
    for run in metrics["metric_runs"]:
        cells = [
            f'<td><a href="{html.escape(run["run_url"])}">{html.escape(run["run_label"])}</a></td>'
        ]
        for field, gate_key in duration_fields:
            value = float(run[field])
            gate = gate_by_key(metrics, gate_key)
            direction = gate["direction"]
            target = float(gate["target"])
            passed = value >= target if direction == "minimum" else value <= target
            cells.append(
                f'<td class="number">{value:.2f}s '
                f'<span class="status status-{"ok" if passed else "fail"}">'
                f"{'OK' if passed else 'Failed'}</span></td>"
            )
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        "\n".join(rows)
        or '<tr><td colspan="6" class="empty-state">No published reports.</td></tr>'
    )


def render_slowest_rows(
    metrics: dict[str, Any], *, key: str, gate_key: str, root_prefix: str
) -> str:
    gate = gate_by_key(metrics, gate_key)
    target = float(gate["target"])
    rows: list[str] = []
    for test in metrics[key]:
        duration = float(test["duration_sec"])
        rows.append(
            "<tr>"
            f'<td><a href="{html.escape(root_prefix + test["report_url"])}">'
            f"{html.escape(test['run_label'])}</a></td>"
            f"<td>{html.escape(test['test_name'])}</td>"
            f'<td class="number">{duration:.2f}s</td>'
            f'<td class="number">&lt;= {target:.2f}s</td>'
            f'<td><span class="status status-{"ok" if duration <= target else "fail"}">'
            f"{'OK' if duration <= target else 'Failed'}</span></td>"
            "</tr>"
        )
    return (
        "\n".join(rows)
        or '<tr><td colspan="5" class="empty-state">No duration data.</td></tr>'
    )


def render_period_links(
    periods: list[tuple[int, str]],
    *,
    current_days: int,
) -> str:
    return "".join(
        (
            f'<a class="period-link{" active" if days == current_days else ""}" '
            f'href="{html.escape(link)}">{days} days</a>'
        )
        for days, link in periods
    )


def render_linear_dashboard(
    metrics: dict[str, Any],
    *,
    root_prefix: str,
    coverage_url: str,
    periods: list[tuple[int, str]],
) -> str:
    quality = metrics["data_quality"]
    coverage = metrics.get("coverage")
    summary = metrics["reference_summary"]
    generated_at = parse_datetime(metrics["generated_at"])
    window_start = parse_datetime(metrics["window"]["start"])
    window_end = parse_datetime(metrics["window"]["end"])
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TeamCity QA metrics report</title>
    <style>{LINEAR_REPORT_CSS}</style>
  </head>
  <body>
    <main class="page">
      <header class="topbar">
        <div>
          <h1>TeamCity QA metrics report</h1>
          <p class="muted">Every metric, target and calculation for TeamCity Regression</p>
        </div>
        <div class="top-actions">
          <div class="period-links" aria-label="Saved metric periods">
            {render_period_links(periods, current_days=metrics["window"]["days"])}
          </div>
          <a class="period-link" href="{html.escape(coverage_url)}">Code coverage</a>
          <a class="period-link" href="{html.escape(root_prefix + "reports/")}">All reports</a>
        </div>
      </header>

      <div class="window">
        <strong>Period:</strong> {metrics["window"]["days"]} UTC calendar days,
        {window_start.strftime("%d %b %Y %H:%M")}–{window_end.strftime("%d %b %Y %H:%M")}.
        Metrics use published Allure reports; workflow runs without a report are listed separately
        and do not enter test calculations.
      </div>

      <nav class="contents" aria-label="Report sections">
        <a href="#distribution">Test distribution</a>
        <a href="#reliability">Flaky tests</a>
        <a href="#stability">Stability</a>
        <a href="#speed">Speed</a>
        <a href="#coverage">Coverage</a>
        <a href="#workflow-runs">Workflow runs</a>
      </nav>

      <section class="summary" aria-label="Report totals">
        <article>
          <span class="muted">Published runs</span>
          <strong>{summary["published_runs"]}</strong>
          <span>{summary["successful_runs"]} fully passed</span>
        </article>
        <article>
          <span class="muted">Final test results</span>
          <strong>{summary["total_tests"]:,}</strong>
          <span>one final result per test and run</span>
        </article>
        <article>
          <span class="muted">Average pass rate</span>
          <strong>{summary["pass_rate"]:.2f}%</strong>
          <span>unweighted average across runs</span>
        </article>
        <article>
          <span class="muted">Flaky rate</span>
          <strong>{summary["flaky_rate"]:.2f}%</strong>
          <span>{summary["total_flaky"]} flaky results</span>
        </article>
      </section>

      <section class="section" id="distribution">
        <div class="section-head">
          <h2>1. Test result distribution</h2>
          <span class="section-note">Rates are calculated per run, then averaged without weighting</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Metric</th><th class="number">Value</th><th class="number">Target</th>
                <th>Status</th><th>Exact calculation</th><th>Meaning and action</th>
              </tr>
            </thead>
            <tbody>{render_gate_rows(metrics, ("pass_rate", "fail_rate", "broken_rate"))}</tbody>
          </table>
        </div>
        <h3>Every published run</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Run</th><th class="number">Total</th><th class="number">Passed / rate</th>
                <th class="number">Failed / rate</th><th class="number">Broken / rate</th>
                <th>3 distribution gates</th>
              </tr>
            </thead>
            <tbody>{render_distribution_rows(metrics, root_prefix=root_prefix)}</tbody>
          </table>
        </div>
      </section>

      <section class="section" id="reliability">
        <div class="section-head">
          <h2>2. Flaky-test reliability</h2>
          <span class="section-note">Only Allure results explicitly marked flaky are counted</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Metric</th><th class="number">Value</th><th class="number">Target</th>
                <th>Status</th><th>Exact calculation</th><th>Meaning and action</th>
              </tr>
            </thead>
            <tbody>{render_gate_rows(metrics, ("flaky_rate", "ui_flaky_rate", "api_flaky_rate"))}</tbody>
          </table>
        </div>
        <h3>Every published run</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Run</th><th class="number">All flaky / rate</th>
                <th class="number">UI flaky / UI total / rate</th>
                <th class="number">API flaky / API total / rate</th>
              </tr>
            </thead>
            <tbody>{render_flaky_rows(metrics, root_prefix=root_prefix)}</tbody>
          </table>
        </div>
      </section>

      <section class="section" id="stability">
        <div class="section-head">
          <h2>3. Test-run stability</h2>
          <span class="section-note">A run is successful only when it has tests and every final result passed</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Metric</th><th class="number">Value</th><th class="number">Target</th>
                <th>Status</th><th>Exact calculation</th><th>Meaning and action</th>
              </tr>
            </thead>
            <tbody>{render_gate_rows(metrics, ("stability_rate",))}</tbody>
          </table>
        </div>
        <h3>Every published run</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>Run</th><th class="number">Passed / total</th><th>Result</th></tr>
            </thead>
            <tbody>{render_stability_rows(metrics)}</tbody>
          </table>
        </div>
      </section>

      <section class="section" id="speed">
        <div class="section-head">
          <h2>4. Test and pipeline speed</h2>
          <span class="section-note">The report shows every average explicitly; no percentile is hidden behind a card</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Metric</th><th class="number">Value</th><th class="number">Target</th>
                <th>Status</th><th>Exact calculation</th><th>Meaning and action</th>
              </tr>
            </thead>
            <tbody>{render_gate_rows(metrics, ("avg_duration_sec", "avg_api_duration_sec", "ui_run_duration_sec", "api_run_duration_sec", "suite_duration_sec"))}</tbody>
          </table>
        </div>
        <h3>Every published run</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Run</th><th class="number">Avg test</th><th class="number">Avg API test</th>
                <th class="number">UI run</th><th class="number">API run</th>
                <th class="number">Pipeline</th>
              </tr>
            </thead>
            <tbody>{render_duration_rows(metrics)}</tbody>
          </table>
        </div>
        <h3>Slowest UI tests</h3>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Run</th><th>Test</th><th class="number">Duration</th><th class="number">Target</th><th>Status</th></tr></thead>
            <tbody>{render_slowest_rows(metrics, key="slowest_ui_tests", gate_key="avg_duration_sec", root_prefix=root_prefix)}</tbody>
          </table>
        </div>
        <h3>Slowest API tests</h3>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Run</th><th>Test</th><th class="number">Duration</th><th class="number">Target</th><th>Status</th></tr></thead>
            <tbody>{render_slowest_rows(metrics, key="slowest_api_tests", gate_key="avg_api_duration_sec", root_prefix=root_prefix)}</tbody>
          </table>
        </div>
      </section>

      <section class="section" id="coverage">
        <div class="section-head">
          <h2>5. API framework code coverage</h2>
          <span class="section-note">Latest coverage.py measurement; kept separate from test quality formulas</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Line coverage</th><th>Branch coverage</th><th>Source report</th></tr></thead>
            <tbody>
              <tr>
                <td>{format_percent(coverage["latest"]["line_rate"]) if coverage and coverage.get("latest") else "No report"}</td>
                <td>{format_percent(coverage["latest"]["branch_rate"]) if coverage and coverage.get("latest") else "No report"}</td>
                <td><a href="{html.escape(coverage_url)}">Open complete coverage report</a></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="section" id="workflow-runs">
        <div class="section-head">
          <h2>6. All workflow runs in the period</h2>
          <span class="section-note">{quality["published_reports"]} reports · {quality["runs_without_report"]} runs without report</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Run</th><th>Conclusion</th><th>Event</th><th>Branch</th>
                <th class="number">Test-stage duration</th><th>Report</th>
              </tr>
            </thead>
            <tbody>{render_run_rows(metrics, root_prefix=root_prefix)}</tbody>
          </table>
        </div>
      </section>

      <footer class="footer">
        <span>Updated {generated_at.strftime("%d %b %Y %H:%M UTC")}</span>
        <span>Sources: GitHub Actions jobs and persistent Allure final test cases</span>
      </footer>
    </main>
  </body>
</html>
"""


def render_dashboard(
    metrics: dict[str, Any],
    *,
    root_prefix: str,
    coverage_url: str,
    periods: list[tuple[int, str]],
    report_title: str = "TeamCity QA Metrics Dashboard",
    report_subtitle: str = "Quality metrics across GitHub runs (Allure artifacts)",
    dashboard_kind: str = "regression",
) -> str:
    del periods
    reference_rows: list[RunStats] = []
    run_report_urls: dict[str, str] = {}
    for run in metrics["metric_runs"]:
        generated_at = parse_datetime(str(run["generated_at"]))
        total_tests = int(run["total_tests"])
        api_tests = int(run["api_tests"])
        ui_tests = int(run["ui_tests"])
        run_name = (
            f"{generated_at.strftime('%Y%m%d_%H%M%S')}_"
            f"{run['run_id']}_allure-results.zip"
        )
        report_url = run.get("report_url")
        if report_url:
            run_report_urls[run_name] = root_prefix + str(report_url)
        reference_rows.append(
            RunStats(
                run_name=run_name,
                total_tests=total_tests,
                api_tests=api_tests,
                ui_tests=ui_tests,
                flaky_tests=int(run["flaky_tests"]),
                api_flaky_tests=int(run["api_flaky_tests"]),
                ui_flaky_tests=int(run["ui_flaky_tests"]),
                passed_tests=int(run["passed_tests"]),
                failed_tests=int(run["failed_tests"]),
                broken_tests=int(run["broken_tests"]),
                total_duration_ms=round(
                    float(run["avg_duration_sec"]) * total_tests * 1000
                ),
                api_duration_ms=round(float(run["api_run_duration_sec"]) * 1000),
                ui_duration_ms=round(float(run["ui_run_duration_sec"]) * 1000),
                suite_duration_ms=round(float(run["suite_duration_sec"]) * 1000),
            )
        )

    def reference_slowest(key: str) -> list[dict[str, Any]]:
        return [
            {
                "run_label": str(test["run_label"]),
                "browser": str(test.get("browser") or ""),
                "test_name": str(test["test_name"]),
                "duration_sec": float(test["duration_sec"]),
                "status": str(test["status"]),
                "report_url": (
                    root_prefix + str(test["report_url"])
                    if test.get("report_url")
                    else None
                ),
            }
            for test in metrics[key]
        ]

    gates_config = {
        key: {
            **REFERENCE_DEFAULT_GATES[key],
            "name": str(target.get("name") or REFERENCE_DEFAULT_GATES[key]["name"]),
            "good_threshold": float(target["value"]),
            "warn_threshold": float(target["value"]),
            "higher_is_better": target["direction"] == "minimum",
            "recommendation": str(
                target.get("recommendation")
                or REFERENCE_DEFAULT_GATES[key]["recommendation"]
            ),
        }
        for key, target in metrics["quality_targets"].items()
    }
    browser_runs = [
        {
            **run,
            "report_url": (
                root_prefix + str(run["report_url"]) if run.get("report_url") else None
            ),
        }
        for run in metrics.get("browser_runs", [])
    ]
    page = build_reference_dashboard_html(
        report_title,
        reference_rows,
        reference_slowest("slowest_ui_tests"),
        reference_slowest("slowest_api_tests"),
        gates_config,
        browser_runs=browser_runs,
        browser_summary=metrics.get("browser_summary", []),
        browser_coverage=metrics.get("browser_coverage", {}),
        browser_failures=metrics.get("browser_failures", []),
        run_report_urls=run_report_urls,
    )
    navigation_css = """
    .qa-report-links {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }
    .qa-report-links a {
      display: inline-block;
      padding: 7px 11px;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--ink);
      background: #fffefb;
      font-size: 13px;
      font-weight: 650;
      text-decoration: none;
    }
    .qa-report-links a:hover { border-color: #8a8174; background: #fff; }
    .qa-report-links a.active {
      border-color: #2f7fc3;
      color: #1e5f95;
      background: #eef7ff;
    }
    .qa-run-context {
      margin-top: 16px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fffefb;
    }
    .qa-run-context h2 { margin: 0 0 10px; font-size: 18px; }
    .qa-context-cards {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
    }
    .qa-context-card {
      padding: 12px;
      border: 1px solid #eee9df;
      border-radius: 10px;
      background: #fff;
    }
    .qa-context-card .label { color: var(--muted); font-size: 12px; }
    .qa-context-card .value { margin-top: 3px; font-size: 22px; font-weight: 750; }
    .qa-incomplete-runs { margin-top: 12px; }
    .qa-incomplete-runs summary { cursor: pointer; font-weight: 700; }
    .qa-status-fail { color: #b42318; font-weight: 700; }
    @media (max-width: 760px) {
      .qa-context-cards { grid-template-columns: 1fr 1fr; }
    }
    """
    regression_class = "active" if dashboard_kind == "regression" else ""
    postgresql_class = "active" if dashboard_kind == "postgresql" else ""
    navigation = (
        '<nav class="qa-report-links" aria-label="QA report navigation">'
        f'<a class="{regression_class}" '
        f'href="{html.escape(root_prefix + "quality/")}">PR Regression</a>'
        f'<a class="{postgresql_class}" '
        f'href="{html.escape(root_prefix + "quality/postgresql/")}">'
        "PostgreSQL Nightly</a>"
        f'<a href="{html.escape(coverage_url)}">Code Coverage</a>'
        f'<a href="{html.escape(root_prefix + "reports/")}" '
        'target="_blank" rel="noopener noreferrer">Allure Reports</a>'
        "</nav>"
    )
    context = ""
    if dashboard_kind == "postgresql":
        data_quality = metrics["data_quality"]
        complete_runs = [
            run
            for run in metrics.get("recent_runs", [])
            if bool(run.get("test_suite_complete", True)) and run.get("report_url")
        ]
        incomplete_runs = [
            run
            for run in metrics.get("recent_runs", [])
            if not bool(run.get("test_suite_complete", True))
        ]
        successful_complete_runs = sum(
            str(run.get("conclusion")) == "success" for run in complete_runs
        )
        complete_success_rate = percentage(
            successful_complete_runs,
            len(complete_runs),
        )
        latest_run = complete_runs[0] if complete_runs else None
        latest_status = (
            str(latest_run["conclusion"]).replace("_", " ").title()
            if latest_run is not None
            else "No complete runs"
        )
        success_rate_text = (
            f"{float(complete_success_rate):.2f}%"
            if complete_success_rate is not None
            else "—"
        )
        incomplete_rows: list[str] = []
        for run in incomplete_runs:
            created_at = parse_datetime(str(run["created_at"]))
            report_url = run.get("report_url")
            if report_url:
                run_label = (
                    f'<a href="{html.escape(root_prefix + str(report_url))}" '
                    'target="_blank" rel="noopener noreferrer">'
                    f"{created_at.strftime('%Y-%m-%d %H:%M')}</a>"
                )
            else:
                run_label = (
                    f'<a href="{html.escape(str(run["run_url"]))}" '
                    'target="_blank" rel="noopener noreferrer">'
                    f"{created_at.strftime('%Y-%m-%d %H:%M')}</a>"
                )
            incomplete_rows.append(
                "<tr>"
                f"<td>{run_label}</td>"
                f"<td>#{int(run['number'])}</td>"
                '<td class="qa-status-fail">Incomplete</td>'
                f"<td>{html.escape(str(run['conclusion']).title())}</td>"
                "</tr>"
            )
        incomplete_panel = ""
        if incomplete_rows:
            incomplete_panel = (
                '<details class="qa-incomplete-runs">'
                f"<summary>Excluded incomplete nightly runs ({len(incomplete_rows)})</summary>"
                "<table><thead><tr><th>Run</th><th>Number</th>"
                "<th>Test data</th><th>Workflow</th></tr></thead>"
                f"<tbody>{''.join(incomplete_rows)}</tbody></table></details>"
            )
        context = (
            '<section class="qa-run-context" aria-label="PostgreSQL nightly status">'
            "<h2>PostgreSQL nightly execution status</h2>"
            '<div class="qa-context-cards">'
            '<div class="qa-context-card"><div class="label">Complete runs used</div>'
            f'<div class="value">{int(data_quality["metric_reports"])}</div></div>'
            '<div class="qa-context-card"><div class="label">Complete-run stability</div>'
            f'<div class="value">{success_rate_text}</div></div>'
            '<div class="qa-context-card"><div class="label">Successful complete runs</div>'
            f'<div class="value">{successful_complete_runs}</div></div>'
            '<div class="qa-context-card"><div class="label">Latest complete workflow</div>'
            f'<div class="value">{html.escape(latest_status)}</div></div>'
            "</div>"
            f"{incomplete_panel}"
            "</section>"
        )
    page = page.replace("</style>", f"{navigation_css}</style>", 1)
    page = page.replace(
        '<p class="subtitle">Quality metrics across GitHub runs (Allure artifacts)</p>',
        (
            f'<p class="subtitle">{html.escape(report_subtitle)}</p>'
            f"{navigation}{context}"
        ),
        1,
    )
    if dashboard_kind == "postgresql":
        page = page.replace(
            '<div class="label">Total Runs</div>',
            '<div class="label">Complete Runs Used</div>',
            1,
        )
    return page


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown_report(metrics: dict[str, Any]) -> str:
    summary = metrics["reference_summary"]
    window = metrics["window"]
    lines = [
        "# TeamCity QA metrics report",
        "",
        (
            f"Period: **{window['days']} UTC calendar days** "
            f"({window['start']} — {window['end']})."
        ),
        "",
        (
            f"Published runs: **{summary['published_runs']}** · "
            f"fully passed: **{summary['successful_runs']}** · "
            f"final test results: **{summary['total_tests']}** · "
            f"flaky results: **{summary['total_flaky']}**."
        ),
        "",
        "## Quality gates and exact calculations",
        "",
        "| Metric | Value | Target | Status | Calculation |",
        "|---|---:|---:|---|---|",
    ]
    for gate in metrics["quality_gates"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    markdown_cell(gate["name"]),
                    f"{float(gate['value']):.2f}{gate['unit']}",
                    f"{gate['threshold']}{gate['unit']}",
                    markdown_cell(gate["status_label"]),
                    markdown_cell(gate["formula"]),
                )
            )
            + " |"
        )

    lines.extend(
        (
            "",
            "## Every published run",
            "",
            "| Run | Total | Passed | Failed | Broken | Flaky | Stability | Avg test | Avg API | UI run | API run | Pipeline |",
            "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|",
        )
    )
    for run in metrics["metric_runs"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    f"[{markdown_cell(run['run_label'])}]({run['run_url']})",
                    str(run["total_tests"]),
                    f"{run['passed_tests']} / {float(run['pass_rate']):.2f}%",
                    f"{run['failed_tests']} / {float(run['fail_rate']):.2f}%",
                    f"{run['broken_tests']} / {float(run['broken_rate']):.2f}%",
                    f"{run['flaky_tests']} / {float(run['flaky_rate']):.2f}%",
                    "Successful" if run["run_success"] else "Unstable",
                    f"{float(run['avg_duration_sec']):.2f}s",
                    f"{float(run['avg_api_duration_sec']):.2f}s",
                    f"{float(run['ui_run_duration_sec']):.2f}s",
                    f"{float(run['api_run_duration_sec']):.2f}s",
                    f"{float(run['suite_duration_sec']):.2f}s",
                )
            )
            + " |"
        )

    lines.extend(
        (
            "",
            "## Cross-browser UI",
            "",
            "| Browser | Pass rate | Failures | Flaky | Avg test | Avg target | P95 test | P90 run | Run target | Status |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        )
    )
    for browser in metrics.get("browser_summary", []):
        lines.append(
            "| "
            + " | ".join(
                (
                    markdown_cell(browser["browser"]),
                    f"{float(browser['pass_rate']):.2f}%",
                    str(browser["failed_tests"]),
                    f"{float(browser['flaky_rate']):.2f}%",
                    f"{float(browser['avg_duration_sec']):.2f}s",
                    f"<= {float(browser['avg_target_sec']):.2f}s",
                    f"{float(browser['p95_duration_sec']):.2f}s",
                    f"{float(browser['p90_run_duration_sec']):.2f}s",
                    f"<= {float(browser['run_target_sec']):.2f}s",
                    markdown_cell(browser["status_label"]),
                )
            )
            + " |"
        )

    browser_coverage = metrics.get("browser_coverage", {})
    lines.extend(
        (
            "",
            (
                "Browser coverage: "
                f"**{float(browser_coverage.get('coverage_rate', 0.0)):.2f}%** "
                f"({int(browser_coverage.get('common_tests', 0))}/"
                f"{int(browser_coverage.get('unique_tests', 0))} UI scenarios "
                "executed in all three browsers)."
            ),
        )
    )

    for title, key, target_key in (
        ("Slowest UI tests", "slowest_ui_tests", "avg_duration_sec"),
        ("Slowest API tests", "slowest_api_tests", "avg_api_duration_sec"),
    ):
        target = float(gate_by_key(metrics, target_key)["target"])
        lines.extend(
            (
                "",
                f"## {title}",
                "",
                "| Run | Test | Duration | Target | Status |",
                "|---|---|---:|---:|---|",
            )
        )
        if not metrics[key]:
            lines.append("| — | No duration data | — | — | — |")
        for test in metrics[key]:
            duration = float(test["duration_sec"])
            lines.append(
                "| "
                + " | ".join(
                    (
                        markdown_cell(test["run_label"]),
                        markdown_cell(test["test_name"]),
                        f"{duration:.2f}s",
                        f"<= {target:.2f}s",
                        "OK" if duration <= target else "Failed",
                    )
                )
                + " |"
            )

    quality = metrics["data_quality"]
    lines.extend(
        (
            "",
            "## Data completeness",
            "",
            f"- Completed workflow runs: **{quality['completed_runs']}**",
            f"- Published Allure reports used in test metrics: **{quality['published_reports']}**",
            f"- Workflow runs without a published report: **{quality['runs_without_report']}**",
            "",
            (
                "Flaky counts use final Allure test cases explicitly marked `flaky`. "
                "Pass, fail and broken rates are calculated per run and then averaged "
                "without weighting, matching the reference report."
            ),
            "",
        )
    )
    return "\n".join(lines)


def append_github_output(metrics: dict[str, Any]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        output.write("dashboard_path=quality/\n")
        output.write(f"completed_runs={metrics['pipeline']['completed']}\n")
        output.write(
            f"published_reports={metrics['data_quality']['published_reports']}\n"
        )
        output.write(f"average_pass_rate={metrics['reference_summary']['pass_rate']}\n")
        output.write(f"flaky_rate={metrics['reference_summary']['flaky_rate']}\n")


def resolve_site_path(site_dir: Path, value: str) -> tuple[Path, Path]:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("site paths must be relative and cannot contain '..'")
    return site_dir / relative, relative


def saved_period_links(
    site_dir: Path,
    destination_relative: Path,
    current_days: int,
) -> list[tuple[int, str]]:
    saved_days = {current_days}
    for metrics_path in (site_dir / "quality" / "periods").glob("*/metrics.json"):
        try:
            saved_days.add(int(metrics_path.parent.name))
        except ValueError:
            continue
    in_period_snapshot = destination_relative.parts[:2] == ("quality", "periods")
    return [
        (
            days,
            f"../{days}/" if in_period_snapshot else f"periods/{days}/",
        )
        for days in sorted(saved_days)
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", required=True, type=Path)
    parser.add_argument("--runs-json", required=True, type=Path)
    parser.add_argument("--suite", default="regression")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--destination", default="quality")
    parser.add_argument(
        "--coverage-metrics",
        default="quality/coverage/metrics.json",
    )
    parser.add_argument("--coverage-url", default="coverage/")
    parser.add_argument(
        "--report-title",
        default="TeamCity QA Metrics Dashboard",
    )
    parser.add_argument(
        "--report-subtitle",
        default="Quality metrics across GitHub runs (Allure artifacts)",
    )
    parser.add_argument(
        "--dashboard-kind",
        choices=("regression", "postgresql"),
        default="regression",
    )
    parser.add_argument(
        "--exclude-incomplete-reports",
        action="store_true",
        help="Exclude reports whose workflow metadata marks the test suite incomplete.",
    )
    parser.add_argument(
        "--targets-config",
        type=Path,
        default=Path("resources/qa_metrics_targets.json"),
    )
    parser.add_argument("--now", help="ISO-8601 UTC timestamp used as window end")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.days < 1:
        raise ValueError("--days must be a positive integer")
    now = parse_datetime(args.now) if args.now else datetime.now(UTC)
    window_start_at = window_start(now, args.days)
    runs = load_workflow_runs(
        args.runs_json,
        window_start=window_start_at,
        window_end=now,
    )
    latest_attempts = {run.id: run.attempt for run in runs}
    published_reports = load_published_reports(
        args.site_dir,
        args.suite,
        window_start=window_start_at,
        window_end=now,
        latest_attempts=latest_attempts,
    )
    if args.exclude_incomplete_reports:
        runs_by_id = {run.id: run for run in runs}
        reports = [
            report
            for report in published_reports
            if (
                report.run_id in runs_by_id
                and runs_by_id[report.run_id].test_suite_complete
            )
        ]
    else:
        reports = published_reports
    coverage_path, _ = resolve_site_path(args.site_dir, args.coverage_metrics)
    coverage = load_json(coverage_path)
    quality_targets = load_quality_targets(args.targets_config)
    browser_targets = load_browser_targets(args.targets_config)
    metrics = build_metrics(
        runs,
        reports,
        now=now,
        days=args.days,
        quality_targets=quality_targets,
        browser_targets=browser_targets,
        coverage=coverage,
        published_reports=published_reports,
    )

    destination, destination_relative = resolve_site_path(
        args.site_dir,
        args.destination,
    )
    destination.mkdir(parents=True, exist_ok=True)
    destination.joinpath("metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    destination.joinpath("index.html").write_text(
        render_dashboard(
            metrics,
            root_prefix="../" * len(destination_relative.parts),
            coverage_url=args.coverage_url,
            periods=saved_period_links(
                args.site_dir,
                destination_relative,
                args.days,
            ),
            report_title=args.report_title,
            report_subtitle=args.report_subtitle,
            dashboard_kind=args.dashboard_kind,
        ),
        encoding="utf-8",
    )
    destination.joinpath("report.md").write_text(
        render_markdown_report(metrics),
        encoding="utf-8",
    )
    append_github_output(metrics)
    print(
        f"Built {args.days}-day dashboard from {len(runs)} runs, "
        f"{len(published_reports)} published reports, and "
        f"{len(reports)} complete metric reports."
    )


if __name__ == "__main__":
    main()
