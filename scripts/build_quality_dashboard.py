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

REPORT_ID_PATTERN = re.compile(r"^(?P<run_id>\d+)-attempt-(?P<attempt>\d+)$")
FAILED_STATUSES = {"failed", "broken"}
COMPLETED_TEST_STATUSES = {"passed", "failed", "broken", "skipped", "unknown"}
UI_SCOPE_ORDER = ("API", "UI · Chromium", "UI · Firefox", "UI · WebKit")


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

    @property
    def duration_seconds(self) -> float:
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


def status_counts(reports: list[PublishedReport]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for report in reports:
        for test in report.tests:
            status = str(test.get("status") or "unknown")
            if status not in COMPLETED_TEST_STATUSES:
                status = "unknown"
            counts[status] += 1
    return counts


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


def build_metrics(
    runs: list[WorkflowRun],
    reports: list[PublishedReport],
    *,
    now: datetime,
    days: int,
    coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
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
    report_by_run = {report.run_id: report for report in reports}

    recent_runs = []
    for run in sorted(runs, key=lambda item: item.created_at, reverse=True)[:10]:
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
            }
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
            "published_reports": len(reports),
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


def render_line_chart(
    metrics: dict[str, Any],
    *,
    field: str,
    title: str,
    formatter: Callable[[float], str],
    css_class: str,
    percentage_scale: bool = False,
) -> str:
    days = metrics["daily"]
    values = [float(day[field]) if day.get(field) is not None else None for day in days]
    available = [value for value in values if value is not None]
    if not available:
        return (
            '<article class="chart-card">'
            f"<h3>{html.escape(title)}</h3>"
            '<p class="empty-state">No data in this period.</p>'
            "</article>"
        )

    if percentage_scale:
        lower = max(0.0, min(available) - 5.0)
        upper = min(100.0, max(available) + 5.0)
    else:
        lower = 0.0
        upper = max(available) * 1.1
    if math.isclose(lower, upper):
        lower = max(0.0, lower - 1.0)
        upper = upper + 1.0

    width = 720.0
    height = 190.0
    left = 42.0
    right = 16.0
    top = 18.0
    bottom = 32.0
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
        if len(values) <= 60 or index in (0, len(values) - 1):
            label = f"{days[index]['label']}: {formatter(value)}"
            circles.append(
                f'<circle class="{css_class}" cx="{x:.1f}" cy="{y:.1f}" r="3">'
                f"<title>{html.escape(label)}</title></circle>"
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
    start_label = days[0]["label"] if days else ""
    end_label = days[-1]["label"] if days else ""
    return f"""
    <article class="chart-card">
      <div class="chart-head">
        <h3>{html.escape(title)}</h3>
        <strong>{html.escape(formatter(latest_value))}</strong>
      </div>
      <svg class="line-chart" viewBox="0 0 {width:.0f} {height:.0f}" role="img"
           aria-label="{html.escape(title)} over {metrics["window"]["days"]} days">
        <line class="chart-grid" x1="{left}" y1="{top}" x2="{left}" y2="{height - bottom}"/>
        <line class="chart-grid" x1="{left}" y1="{height - bottom}" x2="{width - right}" y2="{height - bottom}"/>
        <line class="chart-grid chart-grid-mid" x1="{left}" y1="{top + plot_height / 2:.1f}" x2="{width - right}" y2="{top + plot_height / 2:.1f}"/>
        <text class="chart-axis" x="4" y="{top + 5:.1f}">{html.escape(formatter(upper))}</text>
        <text class="chart-axis" x="4" y="{height - bottom + 5:.1f}">{html.escape(formatter(lower))}</text>
        {lines}
        {"".join(circles)}
        <text class="chart-axis" x="{left}" y="{height - 8}">{html.escape(start_label)}</text>
        <text class="chart-axis chart-axis-end" x="{width - right}" y="{height - 8}">{html.escape(end_label)}</text>
      </svg>
    </article>
    """


def render_metric_charts(metrics: dict[str, Any]) -> str:
    return "\n".join(
        (
            render_line_chart(
                metrics,
                field="pass_rate",
                title="Test pass rate",
                formatter=lambda value: f"{value:.1f}%",
                css_class="chart-green",
                percentage_scale=True,
            ),
            render_line_chart(
                metrics,
                field="pipeline_success_rate",
                title="Pipeline success rate",
                formatter=lambda value: f"{value:.1f}%",
                css_class="chart-blue",
                percentage_scale=True,
            ),
            render_line_chart(
                metrics,
                field="pipeline_p95_duration_seconds",
                title="Workflow p95 duration",
                formatter=lambda value: format_duration(value),
                css_class="chart-purple",
            ),
            render_line_chart(
                metrics,
                field="flaky",
                title="Flaky test results",
                formatter=lambda value: str(round(value)),
                css_class="chart-orange",
            ),
        )
    )


def render_suite_cards(metrics: dict[str, Any]) -> str:
    cards: list[str] = []
    for suite in metrics["suites"]:
        rate = suite["pass_rate"]
        width = 0 if rate is None else max(0, min(100, rate))
        state = "healthy" if rate is not None and rate >= 99 else "warning"
        cards.append(
            '<article class="suite">'
            f"<h3>{html.escape(suite['name'])}</h3>"
            f'<strong class="suite-value">{html.escape(format_percent(rate))}</strong>'
            f'<div class="progress"><span class="{state}" style="width: {width:.1f}%"></span></div>'
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
            f'<td class="number">{html.escape(format_duration(test["p95_duration_ms"] / 1000))}</td>'
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


DASHBOARD_CSS = """
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
.period-link.active { border-color: var(--primary); color: var(--primary); font-weight: 600; }
.stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px;
}
.stat-label { color: var(--muted); }
.stat-value { display: block; font-size: 30px; line-height: 1.2; margin: 4px 0; }
.stat-context { display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.badge {
  display: inline-block; padding: 2px 7px; border-radius: 999px;
  background: var(--track); color: var(--text); white-space: nowrap;
}
.section { margin-top: 22px; }
.section-head {
  display: flex; justify-content: space-between; gap: 12px; align-items: baseline;
  flex-wrap: wrap; margin-bottom: 10px;
}
.chart-grid-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.chart-card {
  min-width: 0; padding: 14px; background: var(--surface);
  border: 1px solid var(--border); border-radius: 12px;
}
.chart-head {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 12px; margin-bottom: 4px;
}
.chart-head strong { font-size: 18px; }
.line-chart { display: block; width: 100%; height: auto; overflow: visible; }
.chart-grid { stroke: var(--border); stroke-width: 1; }
.chart-grid-mid { stroke-dasharray: 4 5; }
.chart-axis { fill: var(--muted); font-size: 11px; }
.chart-axis-end { text-anchor: end; }
.chart-line {
  fill: none; stroke: currentColor; stroke-width: 3;
  stroke-linecap: round; stroke-linejoin: round;
}
circle.chart-green, circle.chart-blue, circle.chart-purple, circle.chart-orange {
  fill: var(--surface); stroke: currentColor; stroke-width: 2;
}
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
.suites { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; }
.suite { padding: 4px 16px 6px 0; }
.suite + .suite { border-left: 1px solid var(--border); padding-left: 16px; }
.suite-value { display: block; font-size: 22px; margin: 3px 0; }
.progress { height: 7px; border-radius: 999px; overflow: hidden; background: var(--track); margin: 7px 0; }
.progress span { display: block; height: 100%; border-radius: inherit; }
.table-wrap { overflow-x: auto; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }
th { color: var(--muted); font-size: 13px; font-weight: 600; }
tr:last-child td { border-bottom: 0; }
.number { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
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


def render_dashboard(
    metrics: dict[str, Any],
    *,
    root_prefix: str,
    coverage_url: str,
    periods: list[tuple[int, str]],
) -> str:
    pipeline = metrics["pipeline"]
    tests = metrics["tests"]
    quality = metrics["data_quality"]
    coverage = metrics.get("coverage")
    generated_at = parse_datetime(metrics["generated_at"])
    window_start = parse_datetime(metrics["window"]["start"])
    window_end = parse_datetime(metrics["window"]["end"])
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TeamCity QA metrics</title>
    <style>{DASHBOARD_CSS}</style>
  </head>
  <body>
    <main class="page">
      <header class="topbar">
        <div>
          <h1>TeamCity QA metrics</h1>
          <p class="muted">Rolling quality health for TeamCity Regression</p>
        </div>
        <div class="top-actions">
          <div class="period-links" aria-label="Saved metric periods">
            {render_period_links(periods, current_days=metrics["window"]["days"])}
          </div>
          <a class="period-link" href="{html.escape(root_prefix + "reports/")}">All reports</a>
          <div class="period">
            <span class="period-dot" aria-hidden="true"></span>
            <strong>{metrics["window"]["days"]} days</strong>
            <span>{window_start.strftime("%d %b")}–{window_end.strftime("%d %b %Y")}</span>
          </div>
        </div>
      </header>

      <section class="stats" aria-label="Quality summary">
        <article class="card">
          <span class="stat-label">Pipeline stability</span>
          <strong class="stat-value">{format_percent(pipeline["success_rate"])}</strong>
          <div class="stat-context">
            <span>{pipeline["successful"]} of {pipeline["completed"]} successful</span>
            <span class="badge">p95 {format_duration(pipeline["p95_duration_seconds"])}</span>
          </div>
        </article>
        <article class="card">
          <span class="stat-label">Test reliability</span>
          <strong class="stat-value">{format_percent(tests["pass_rate"])}</strong>
          <div class="stat-context">
            <span>{tests["total"]:,} final results</span>
            <span class="badge">{tests["failed"]} failed</span>
          </div>
        </article>
        <article class="card">
          <span class="stat-label">Flaky tests</span>
          <strong class="stat-value">{tests["flaky"]}</strong>
          <div class="stat-context">
            <span>{format_percent(tests["retry_rate"])} retry rate</span>
            <span class="badge">{tests["retries"]} retries</span>
          </div>
        </article>
        <article class="card">
          <span class="stat-label">API framework coverage</span>
          <strong class="stat-value">{format_percent(coverage["latest"]["line_rate"]) if coverage and coverage.get("latest") else "—"}</strong>
          <div class="stat-context">
            <span>{format_percent(coverage["latest"]["branch_rate"]) + " branches" if coverage and coverage.get("latest") else "No reports yet"}</span>
            <a class="badge" href="{html.escape(coverage_url)}">Open coverage</a>
          </div>
        </article>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Metric history</h2>
          <span class="section-note">Daily values for the selected period</span>
        </div>
        <div class="chart-grid-layout">
          {render_metric_charts(metrics)}
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Where instability is</h2>
          <span class="section-note">Final pass rate · flaky tests · p95 test duration</span>
        </div>
        <div class="card suites">
          {render_suite_cards(metrics)}
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Needs attention</h2>
          <span class="section-note">Final failures and flakiness first, then slow tests</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Test</th>
                <th>Signal</th>
                <th class="number">Failed runs</th>
                <th class="number">Retries</th>
                <th>Scope</th>
                <th class="number">p95</th>
              </tr>
            </thead>
            <tbody>{render_attention_rows(metrics, root_prefix=root_prefix)}</tbody>
          </table>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Recent regression runs</h2>
          <span class="section-note">{quality["published_reports"]} published reports · {quality["runs_without_report"]} runs without report</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Run</th>
                <th>Conclusion</th>
                <th>Event</th>
                <th>Branch</th>
                <th class="number">Duration</th>
                <th>Report</th>
              </tr>
            </thead>
            <tbody>{render_run_rows(metrics, root_prefix=root_prefix)}</tbody>
          </table>
        </div>
      </section>

      <footer class="footer">
        <span>Updated {generated_at.strftime("%d %b %Y %H:%M UTC")}</span>
        <span>Sources: GitHub Actions API and persistent Allure reports</span>
      </footer>
    </main>
  </body>
</html>
"""


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
    reports = load_published_reports(
        args.site_dir,
        args.suite,
        window_start=window_start_at,
        window_end=now,
        latest_attempts=latest_attempts,
    )
    coverage_path, _ = resolve_site_path(args.site_dir, args.coverage_metrics)
    coverage = load_json(coverage_path)
    metrics = build_metrics(
        runs,
        reports,
        now=now,
        days=args.days,
        coverage=coverage,
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
        ),
        encoding="utf-8",
    )
    append_github_output(metrics)
    print(
        f"Built {args.days}-day dashboard from {len(runs)} runs "
        f"and {len(reports)} published reports."
    )


if __name__ == "__main__":
    main()
