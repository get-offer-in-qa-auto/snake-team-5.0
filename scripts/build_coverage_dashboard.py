#!/usr/bin/env python3
"""Build a current API framework coverage snapshot from coverage.py reports."""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

REPORT_ID_PATTERN = re.compile(r"^(?P<run_id>\d+)-attempt-(?P<attempt>\d+)$")


@dataclass(frozen=True)
class CoverageReport:
    run_id: int
    attempt: int
    report_id: str
    path: str
    generated_at: datetime
    run_url: str
    branch: str
    sha: str
    source: str
    coverage: dict[str, Any]


def parse_datetime(value: str | None) -> datetime:
    if not value:
        raise ValueError("datetime value is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def window_start(now: datetime, days: int) -> datetime:
    return (now - timedelta(days=days - 1)).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def percentage(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator * 100 / denominator, 2)


def format_percent(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f}%"


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def load_coverage_reports(
    site_dir: Path,
    *,
    window_start_at: datetime,
    window_end: datetime,
) -> list[CoverageReport]:
    reports_by_run: dict[int, CoverageReport] = {}
    for metadata_path in sorted((site_dir / "coverage").glob("*/metadata.json")):
        metadata = load_json(metadata_path)
        coverage = load_json(metadata_path.parent / "coverage.json")
        if metadata is None or coverage is None:
            continue

        report_id = str(metadata.get("report_id") or metadata_path.parent.name)
        match = REPORT_ID_PATTERN.fullmatch(report_id)
        if match is None:
            continue
        try:
            generated_at = parse_datetime(str(metadata.get("generated_at") or ""))
        except ValueError:
            continue
        if generated_at < window_start_at or generated_at > window_end:
            continue

        run_id = int(match.group("run_id"))
        report = CoverageReport(
            run_id=run_id,
            attempt=int(match.group("attempt")),
            report_id=report_id,
            path=metadata_path.parent.relative_to(site_dir).as_posix(),
            generated_at=generated_at,
            run_url=str(metadata.get("run_url") or "#"),
            branch=str(metadata.get("branch") or "unknown"),
            sha=str(metadata.get("sha") or ""),
            source=str(metadata.get("source") or "src/main/api"),
            coverage=coverage,
        )
        previous = reports_by_run.get(run_id)
        if previous is None or report.attempt >= previous.attempt:
            reports_by_run[run_id] = report

    return sorted(reports_by_run.values(), key=lambda report: report.generated_at)


def coverage_summary(report: CoverageReport) -> dict[str, Any]:
    totals = report.coverage.get("totals")
    if not isinstance(totals, dict):
        totals = {}
    num_statements = int(totals.get("num_statements") or 0)
    covered_lines = int(totals.get("covered_lines") or 0)
    num_branches = int(totals.get("num_branches") or 0)
    covered_branches = int(totals.get("covered_branches") or 0)
    return {
        "run_id": report.run_id,
        "attempt": report.attempt,
        "report_id": report.report_id,
        "generated_at": report.generated_at.isoformat(timespec="seconds"),
        "run_url": report.run_url,
        "branch": report.branch,
        "sha": report.sha,
        "source": report.source,
        "html_url": f"{report.path}/html/",
        "json_url": f"{report.path}/coverage.json",
        "xml_url": f"{report.path}/coverage.xml",
        "line_rate": percentage(covered_lines, num_statements),
        "branch_rate": percentage(covered_branches, num_branches),
        "covered_lines": covered_lines,
        "missing_lines": int(totals.get("missing_lines") or 0),
        "excluded_lines": int(totals.get("excluded_lines") or 0),
        "num_statements": num_statements,
        "covered_branches": covered_branches,
        "missing_branches": int(totals.get("missing_branches") or 0),
        "num_branches": num_branches,
    }


def compact_line_numbers(values: list[int], *, limit: int = 6) -> str:
    if not values:
        return "—"
    ordered = sorted(set(int(value) for value in values))
    ranges: list[str] = []
    start = previous = ordered[0]
    for current in ordered[1:]:
        if current == previous + 1:
            previous = current
            continue
        ranges.append(str(start) if start == previous else f"{start}–{previous}")
        start = previous = current
    ranges.append(str(start) if start == previous else f"{start}–{previous}")
    if len(ranges) <= limit:
        return ", ".join(ranges)
    return ", ".join(ranges[:limit]) + ", …"


def module_summaries(report: CoverageReport) -> list[dict[str, Any]]:
    raw_files = report.coverage.get("files")
    if not isinstance(raw_files, dict):
        return []
    modules: list[dict[str, Any]] = []
    for path, payload in raw_files.items():
        if not isinstance(payload, dict):
            continue
        summary = payload.get("summary")
        if not isinstance(summary, dict):
            continue
        num_statements = int(summary.get("num_statements") or 0)
        covered_lines = int(summary.get("covered_lines") or 0)
        num_branches = int(summary.get("num_branches") or 0)
        covered_branches = int(summary.get("covered_branches") or 0)
        missing_lines = payload.get("missing_lines")
        if not isinstance(missing_lines, list):
            missing_lines = []
        modules.append(
            {
                "path": str(path).replace("\\", "/"),
                "line_rate": percentage(covered_lines, num_statements),
                "branch_rate": percentage(covered_branches, num_branches),
                "covered_lines": covered_lines,
                "num_statements": num_statements,
                "missing_lines": max(0, num_statements - covered_lines),
                "covered_branches": covered_branches,
                "num_branches": num_branches,
                "missing_branches": max(0, num_branches - covered_branches),
                "missing": compact_line_numbers(missing_lines),
            }
        )
    modules.sort(
        key=lambda module: (
            math.inf if module["line_rate"] is None else module["line_rate"],
            module["path"],
        )
    )
    return modules


def daily_trend(
    reports: list[CoverageReport], *, now: datetime, days: int
) -> list[dict[str, Any]]:
    latest_by_day: dict[date, CoverageReport] = {}
    for report in reports:
        report_day = report.generated_at.date()
        previous = latest_by_day.get(report_day)
        if previous is None or report.generated_at >= previous.generated_at:
            latest_by_day[report_day] = report

    first_day = now.date() - timedelta(days=days - 1)
    trend: list[dict[str, Any]] = []
    for offset in range(days):
        current_day = first_day + timedelta(days=offset)
        report = latest_by_day.get(current_day)
        summary = coverage_summary(report) if report else None
        trend.append(
            {
                "date": current_day.isoformat(),
                "label": current_day.strftime("%d %b"),
                "line_rate": summary["line_rate"] if summary else None,
                "branch_rate": summary["branch_rate"] if summary else None,
                "report_id": summary["report_id"] if summary else None,
                "run_id": summary["run_id"] if summary else None,
                "generated_at": summary["generated_at"] if summary else None,
                "html_url": summary["html_url"] if summary else None,
            }
        )
    return trend


def rate_delta(
    current: dict[str, Any] | None,
    previous: dict[str, Any] | None,
    field: str,
) -> float | None:
    if current is None or previous is None:
        return None
    current_value = current.get(field)
    previous_value = previous.get(field)
    if current_value is None or previous_value is None:
        return None
    return round(float(current_value) - float(previous_value), 2)


def trend_delta(trend: list[dict[str, Any]], field: str) -> float | None:
    measured = [day for day in trend if day.get(field) is not None]
    if len(measured) < 2:
        return None
    return rate_delta(measured[-1], measured[0], field)


def file_coverage_summary(modules: list[dict[str, Any]]) -> dict[str, Any]:
    measured = [module for module in modules if module["num_statements"] > 0]
    full = [
        module
        for module in measured
        if module["covered_lines"] == module["num_statements"]
    ]
    empty = [module for module in measured if module["covered_lines"] == 0]
    partial = [
        module
        for module in measured
        if 0 < module["covered_lines"] < module["num_statements"]
    ]
    with_coverage = len(full) + len(partial)
    return {
        "total": len(measured),
        "with_coverage": with_coverage,
        "with_coverage_rate": percentage(with_coverage, len(measured)),
        "full": len(full),
        "full_rate": percentage(len(full), len(measured)),
        "partial": len(partial),
        "partial_rate": percentage(len(partial), len(measured)),
        "empty": len(empty),
        "empty_rate": percentage(len(empty), len(measured)),
    }


def build_metrics(reports: list[CoverageReport], *, now: datetime) -> dict[str, Any]:
    latest = coverage_summary(reports[-1]) if reports else None
    modules = module_summaries(reports[-1]) if reports else []
    latest_generated_at = (
        parse_datetime(latest["generated_at"]) if latest is not None else None
    )
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "mode": "current-snapshot",
        "reports": len(reports),
        "latest": latest,
        "latest_context": {
            "is_today": (
                latest_generated_at.date() == now.date()
                if latest_generated_at is not None
                else False
            ),
            "label": (
                f"Today at {latest_generated_at.strftime('%H:%M UTC')}"
                if latest_generated_at is not None
                and latest_generated_at.date() == now.date()
                else (
                    "Last available "
                    + latest_generated_at.strftime("%d %b %Y %H:%M UTC")
                    if latest_generated_at is not None
                    else "No coverage measurement available"
                )
            ),
        },
        "modules": modules,
        "files": file_coverage_summary(modules),
    }


def format_delta(
    value: float | None,
    *,
    reference: str,
    unavailable: str,
) -> str:
    if value is None:
        return unavailable
    if value > 0:
        return f"↑ +{value:.1f} pp vs {reference}"
    if value < 0:
        return f"↓ {value:.1f} pp vs {reference}"
    return f"→ No change vs {reference}"


def render_delta(
    value: float | None,
    *,
    reference: str,
    unavailable: str,
) -> str:
    if value is None:
        state = "unknown"
    elif value > 0:
        state = "up"
    elif value < 0:
        state = "down"
    else:
        state = "flat"
    return (
        f'<span class="delta delta-{state}">'
        f"{html.escape(format_delta(value, reference=reference, unavailable=unavailable))}"
        "</span>"
    )


def render_coverage_trend(metrics: dict[str, Any], *, root_prefix: str) -> str:
    trend = metrics["trend"]
    all_values = [
        float(value)
        for day in trend
        for value in (day.get("line_rate"), day.get("branch_rate"))
        if value is not None
    ]
    if not all_values:
        return '<p class="empty-state">No coverage data in this period.</p>'

    lower = max(0.0, min(all_values) - 5.0)
    upper = min(100.0, max(all_values) + 5.0)
    if math.isclose(lower, upper):
        lower = max(0.0, lower - 1.0)
        upper += 1.0

    width = 900.0
    height = 250.0
    left = 54.0
    right = 18.0
    top = 24.0
    bottom = 62.0
    plot_width = width - left - right
    plot_height = height - top - bottom

    def render_series(field: str, css_class: str) -> str:
        values = [
            float(day[field]) if day.get(field) is not None else None for day in trend
        ]
        segments: list[list[str]] = []
        current: list[str] = []
        circles: list[str] = []
        for index, value in enumerate(values):
            if value is None:
                if current:
                    segments.append(current)
                    current = []
                continue
            x = left
            if len(values) > 1:
                x += index * plot_width / (len(values) - 1)
            y = top + (upper - value) * plot_height / (upper - lower)
            current.append(f"{x:.1f},{y:.1f}")
            label = (
                f"{trend[index]['label']}: {value:.1f}% · run #{trend[index]['run_id']}"
            )
            circle = (
                f'<circle class="{css_class}" cx="{x:.1f}" cy="{y:.1f}" r="4">'
                f"<title>{html.escape(label)}</title></circle>"
            )
            report_url = trend[index].get("html_url")
            if report_url:
                circle = (
                    f'<a href="{html.escape(root_prefix + str(report_url))}">'
                    f"{circle}</a>"
                )
            circles.append(circle)
        if current:
            segments.append(current)
        lines = "".join(
            f'<polyline class="coverage-line {css_class}" points="{" ".join(segment)}"/>'
            for segment in segments
            if len(segment) > 1
        )
        return lines + "".join(circles)

    grid_lines: list[str] = []
    for grid_index in range(5):
        ratio = grid_index / 4
        y = top + plot_height * ratio
        grid_value = upper - (upper - lower) * ratio
        grid_lines.append(
            f'<line class="chart-grid" x1="{left}" y1="{y:.1f}" '
            f'x2="{width - right}" y2="{y:.1f}"/>'
            f'<text class="chart-axis chart-axis-y" x="{left - 8}" '
            f'y="{y + 4:.1f}">{grid_value:.1f}%</text>'
        )

    label_count = min(7, len(trend))
    if label_count <= 1:
        label_indices = {0}
    else:
        label_indices = {
            round(index * (len(trend) - 1) / (label_count - 1))
            for index in range(label_count)
        }
    x_labels: list[str] = []
    for index in sorted(label_indices):
        x = left
        if len(trend) > 1:
            x += index * plot_width / (len(trend) - 1)
        x_labels.append(
            f'<text class="chart-axis chart-axis-x" '
            f'transform="translate({x:.1f} {height - 30:.1f}) rotate(-22)">'
            f"{html.escape(str(trend[index]['label']))}</text>"
        )

    line_period_delta = render_delta(
        metrics["period_delta"]["line_rate"],
        reference="first measured day",
        unavailable="Not enough history",
    )
    branch_period_delta = render_delta(
        metrics["period_delta"]["branch_rate"],
        reference="first measured day",
        unavailable="Not enough history",
    )
    return f"""
    <div class="coverage-chart-head">
      <span>
        <i class="legend-line"></i>Line coverage
        {line_period_delta}
      </span>
      <span>
        <i class="legend-branch"></i>Branch coverage
        {branch_period_delta}
      </span>
    </div>
    <svg class="coverage-chart" viewBox="0 0 {width:.0f} {height:.0f}" role="img"
         aria-label="Line and branch coverage over {metrics["window"]["days"]} days">
      {"".join(grid_lines)}
      {render_series("line_rate", "series-line")}
      {render_series("branch_rate", "series-branch")}
      {"".join(x_labels)}
    </svg>
    """


def render_history_rows(metrics: dict[str, Any], *, root_prefix: str) -> str:
    rows: list[str] = []
    for report in metrics["history"]:
        generated_at = parse_datetime(report["generated_at"])
        rows.append(
            "<tr>"
            f'<td><a href="{html.escape(root_prefix + report["html_url"])}">'
            f"{generated_at.strftime('%d %b %Y %H:%M UTC')}</a></td>"
            f"<td>#{report['run_id']} · attempt {report['attempt']}</td>"
            f"<td>{html.escape(report['branch'])}</td>"
            f'<td class="number">{html.escape(format_percent(report["line_rate"]))}</td>'
            f'<td class="number">{html.escape(format_percent(report["branch_rate"]))}</td>'
            "<td>"
            f'<a href="{html.escape(root_prefix + report["json_url"])}">JSON</a> · '
            f'<a href="{html.escape(root_prefix + report["xml_url"])}">XML</a>'
            "</td>"
            "</tr>"
        )
    if rows:
        return "\n".join(rows)
    return (
        '<tr><td colspan="6" class="empty-state">No reports in this period.</td></tr>'
    )


def render_module_rows(metrics: dict[str, Any]) -> str:
    rows: list[str] = []
    for module in metrics["modules"]:
        line_rate = module["line_rate"]
        width = 0 if line_rate is None else max(0, min(100, line_rate))
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(module['path'])}</code></td>"
            f'<td class="number">{html.escape(format_percent(line_rate))}</td>'
            f'<td class="number">{html.escape(format_percent(module["branch_rate"]))}</td>'
            f'<td class="number">{module["covered_lines"]} / {module["num_statements"]}</td>'
            f"<td>{html.escape(module['missing'])}</td>"
            '<td class="coverage-cell">'
            f'<span style="width:{width:.1f}%"></span>'
            "</td>"
            "</tr>"
        )
    if rows:
        return "\n".join(rows)
    return (
        '<tr><td colspan="6" class="empty-state">No coverage data available.</td></tr>'
    )


COVERAGE_CSS = """
:root {
  color-scheme: light;
  --background: #f6f8fa;
  --surface: #ffffff;
  --text: #1f2328;
  --muted: #636c76;
  --border: #d0d7de;
  --primary: #0969da;
  --series: #1a7f37;
  --track: #eaeef2;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--background); color: var(--text);
  font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
code { overflow-wrap: anywhere; }
.page { width: min(1180px, 100%); margin: 0 auto; padding: 28px 20px 48px; }
.topbar, .section-head, .meta, .actions {
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px; flex-wrap: wrap;
}
.meta, .actions { justify-content: flex-start; }
h1 { font-size: 28px; line-height: 1.2; margin: 3px 0; }
h2 { font-size: 19px; margin: 0; }
.muted, .section-note { color: var(--muted); }
.badge {
  display: inline-block; padding: 2px 7px; border-radius: 999px;
  background: var(--track); color: var(--text);
}
.period-links { display: flex; gap: 6px; flex-wrap: wrap; }
.period-link {
  display: inline-block; padding: 5px 9px; border: 1px solid var(--border);
  border-radius: 999px; background: var(--surface); color: var(--text);
}
.period-link.active { border-color: var(--primary); color: var(--primary); font-weight: 600; }
.button {
  display: inline-block; padding: 6px 10px; border: 1px solid var(--border);
  border-radius: 7px; background: var(--surface);
}
.stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 20px; }
.card, .table-wrap, .coverage-chart-wrap {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
}
.card { padding: 16px; }
.stat-value { display: block; font-size: 28px; margin: 3px 0; }
.stat-context { display: grid; gap: 6px; }
.measurement-time { color: var(--muted); font-size: 12px; }
.delta {
  display: inline-block; width: fit-content; padding: 2px 7px;
  border-radius: 999px; font-size: 12px; white-space: nowrap;
}
.delta-up { color: #1a7f37; background: #dafbe1; }
.delta-down { color: #cf222e; background: #ffebe9; }
.delta-flat, .delta-unknown { color: var(--muted); background: var(--track); }
.section { margin-top: 22px; }
.section-head { align-items: baseline; margin-bottom: 10px; }
.coverage-chart-wrap { padding: 14px; overflow-x: auto; }
.coverage-chart-head { display: flex; gap: 16px; flex-wrap: wrap; color: var(--muted); }
.coverage-chart-head span { display: inline-flex; align-items: center; gap: 6px; }
.coverage-chart-head .delta { font-style: normal; }
.coverage-chart-head i { width: 18px; height: 3px; display: inline-block; }
.legend-line { background: var(--series); }
.legend-branch { background: var(--primary); }
.coverage-chart { display: block; min-width: 620px; width: 100%; height: auto; }
.chart-grid { stroke: var(--border); stroke-width: 1; }
.chart-axis { fill: var(--muted); font-size: 11px; }
.chart-axis-y, .chart-axis-x { text-anchor: end; }
.coverage-line {
  fill: none; stroke: currentColor; stroke-width: 3;
  stroke-linecap: round; stroke-linejoin: round;
}
.series-line { color: var(--series); }
.series-branch { color: var(--primary); }
circle.series-line, circle.series-branch {
  fill: var(--surface); stroke: currentColor; stroke-width: 2;
}
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }
th { color: var(--muted); font-size: 13px; font-weight: 600; }
tr:last-child td { border-bottom: 0; }
.number { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
.coverage-cell { min-width: 130px; background: linear-gradient(var(--track), var(--track)) center/100% 7px no-repeat; }
.coverage-cell span { display: block; height: 7px; background: var(--series); }
.empty-state { color: var(--muted); padding: 14px; }
.footer { color: var(--muted); margin-top: 24px; font-size: 13px; }
@media (max-width: 760px) {
  .stats { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
  .page { padding: 20px 12px 36px; }
  .stats { grid-template-columns: 1fr; }
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --background: #0d1117; --surface: #161b22; --text: #e6edf3;
    --muted: #8b949e; --border: #30363d; --primary: #58a6ff;
    --series: #3fb950; --track: #30363d;
  }
  .delta-up { color: #3fb950; background: #12261a; }
  .delta-down { color: #f85149; background: #32191c; }
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


SNAPSHOT_CSS = """
:root {
  color-scheme: light;
  --background: #f6f8fa;
  --surface: #ffffff;
  --text: #1f2328;
  --muted: #636c76;
  --border: #d0d7de;
  --primary: #2f81f7;
  --green: #2da44e;
  --amber: #bf8700;
  --red: #cf222e;
  --purple: #8250df;
  --track: #eaeef2;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--background); color: var(--text);
  font: 15px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
code { overflow-wrap: anywhere; }
.page { width: min(1280px, 100%); margin: 0 auto; padding: 26px 20px 48px; }
.topbar, .meta, .actions, .section-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px; flex-wrap: wrap;
}
.meta, .actions { justify-content: flex-start; }
h1 { font-size: 28px; line-height: 1.2; margin: 3px 0; }
h2 { font-size: 19px; margin: 0; }
.muted, .section-note { color: var(--muted); }
.badge {
  display: inline-block; padding: 2px 7px; border-radius: 999px;
  background: var(--track); color: var(--text);
}
.button {
  display: inline-block; padding: 7px 11px; border: 1px solid var(--border);
  border-radius: 7px; background: var(--surface); color: var(--text);
}
.button-primary { color: #fff; background: var(--primary); border-color: var(--primary); }
.snapshot-note {
  margin-top: 14px; padding: 10px 12px; border-left: 3px solid var(--primary);
  background: var(--surface); border-radius: 0 7px 7px 0;
}
.donut-grid {
  display: grid; grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px; margin-top: 18px;
}
.donut-card, .progress-card, .chart-panel, .table-wrap {
  background: var(--surface); border: 1px solid var(--border); border-radius: 9px;
}
.donut-card {
  min-width: 0; padding: 12px; border-left: 3px solid var(--primary);
}
.donut-card h2 { font-size: 14px; font-weight: 600; }
.donut {
  --value: 0; --tone: var(--primary);
  position: relative; width: 92px; height: 92px; margin: 12px auto;
  border-radius: 50%;
  background: conic-gradient(var(--tone) calc(var(--value) * 1%), var(--track) 0);
}
.donut::after {
  content: ""; position: absolute; inset: 17px; border-radius: 50%;
  background: var(--surface);
}
.donut strong {
  position: absolute; inset: 0; z-index: 1; display: grid; place-items: center;
  font-size: 17px; color: var(--tone); font-variant-numeric: tabular-nums;
}
.formula {
  min-height: 74px; padding: 8px; background: var(--background);
  color: var(--muted); font-size: 12px; overflow-wrap: anywhere;
}
.tone-blue { --tone: var(--primary); }
.tone-purple { --tone: var(--purple); }
.tone-green { --tone: var(--green); }
.tone-amber { --tone: var(--amber); }
.tone-red { --tone: var(--red); }
.progress-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;
}
.progress-card { padding: 12px; border-left: 3px solid var(--primary); }
.progress-head { display: flex; justify-content: space-between; gap: 10px; }
.progress-track {
  height: 9px; margin: 8px 0; overflow: hidden; border-radius: 999px;
  background: var(--track);
}
.progress-track span { display: block; height: 100%; background: var(--primary); }
.progress-card.files .progress-track span { background: var(--green); }
.section { margin-top: 22px; }
.section-head { align-items: baseline; margin-bottom: 10px; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.chart-panel { min-width: 0; padding: 14px; }
.chart-panel h2 { margin-bottom: 12px; }
.bar-list { display: grid; gap: 9px; }
.bar-row {
  display: grid; grid-template-columns: minmax(120px, 1.2fr) minmax(160px, 3fr) 70px;
  gap: 9px; align-items: center;
}
.bar-label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar-track { height: 18px; background: var(--track); border-radius: 4px; overflow: hidden; }
.bar-track span { display: block; min-width: 2px; height: 100%; background: var(--green); }
.bar-row.inventory:nth-child(2) .bar-track span,
.bar-row.inventory:nth-child(4) .bar-track span { background: var(--red); }
.bar-value { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 9px 11px; text-align: left; border-bottom: 1px solid var(--border); }
th { color: var(--muted); background: var(--background); font-size: 13px; }
tr:last-child td { border-bottom: 0; }
.number { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
.coverage-cell {
  min-width: 130px;
  background: linear-gradient(var(--track), var(--track)) center/100% 7px no-repeat;
}
.coverage-cell span { display: block; height: 7px; background: var(--green); }
.empty-state { color: var(--muted); padding: 14px; }
.footer {
  display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
  color: var(--muted); margin-top: 24px; font-size: 13px;
}
@media (max-width: 980px) {
  .donut-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .donut-grid { grid-template-columns: 1fr 1fr; }
  .chart-grid, .progress-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .page { padding: 20px 12px 36px; }
  .donut-grid { grid-template-columns: 1fr; }
  .bar-row { grid-template-columns: minmax(100px, 1fr) minmax(120px, 2fr) 62px; }
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --background: #0d1117; --surface: #161b22; --text: #e6edf3;
    --muted: #8b949e; --border: #30363d; --primary: #58a6ff;
    --green: #3fb950; --amber: #d29922; --red: #f85149;
    --purple: #a371f7; --track: #30363d;
  }
}

/* Shared visual language with the QA Metrics dashboard. */
:root {
  color-scheme: light;
  --background: #f4efe7;
  --surface: #fffdf8;
  --text: #18212f;
  --muted: #5e6b7a;
  --border: #d8d2c7;
  --primary: #2f7fc3;
  --green: #159a55;
  --amber: #a36a28;
  --red: #cf3f34;
  --purple: #9b4eb2;
  --track: #eee9df;
  --card: #ffffffcc;
}
body {
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  background:
    radial-gradient(1200px 400px at 0% 0%, #f0e3cf 10%, transparent 70%),
    radial-gradient(900px 500px at 100% 100%, #dceeea 10%, transparent 65%),
    var(--background);
}
a { color: var(--text); }
a:hover { text-decoration: none; }
.page { width: min(1220px, 100%); padding: 28px 20px 48px; }
.title {
  margin: 0; font-size: clamp(26px, 4vw, 42px);
  line-height: 1.1; letter-spacing: 0.01em;
}
.subtitle { margin: 8px 0 0; color: var(--muted); font-size: 15px; }
.qa-report-links {
  display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px;
}
.qa-report-links .button {
  padding: 7px 11px; border: 1px solid var(--border);
  border-radius: 999px; color: var(--text); background: #fffefb;
  font-size: 13px; font-weight: 650;
}
.qa-report-links .button:hover { border-color: #8a8174; background: #fff; }
.report-meta {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  margin-top: 18px; padding: 14px 16px;
  border: 1px solid var(--border); border-radius: 16px;
  background: var(--card); box-shadow: 0 10px 28px rgba(24, 33, 47, 0.07);
}
.badge {
  padding: 3px 10px; border: 1px solid var(--border);
  background: #f9f6f0; font-size: 12px; font-weight: 700;
}
.group {
  margin-top: 18px; padding: 14px;
  border: 1px solid var(--border); border-radius: 18px;
  background: #fffefb; box-shadow: 0 10px 22px rgba(24, 33, 47, 0.05);
}
.group > h2 { margin: 0; font-size: 24px; }
.group > .desc { margin: 6px 0 0; color: #465463; font-size: 14px; }
.snapshot-note, .donut-card, .progress-card, .chart-panel, .table-wrap {
  background: var(--surface); border: 1px solid var(--border);
  box-shadow: 0 14px 30px rgba(24, 33, 47, 0.08);
}
.snapshot-note {
  margin-top: 16px; padding: 14px 16px; border-left: 1px solid var(--border);
  border-radius: 16px; color: #465463;
}
.donut-grid { gap: 14px; margin-top: 16px; }
.donut-card {
  padding: 14px 16px; border-left: 1px solid var(--border);
  border-radius: 16px;
}
.donut-card h2 { color: var(--muted); font-size: 13px; }
.donut { width: 106px; height: 106px; }
.donut::after { background: var(--surface); }
.formula {
  min-height: 74px; padding: 9px 10px; border-radius: 10px;
  background: #f9f6f0; color: var(--muted);
}
.progress-grid { gap: 14px; margin-top: 14px; }
.progress-card {
  padding: 14px 16px; border-left: 1px solid var(--border);
  border-radius: 16px;
}
.section { margin-top: 16px; }
.chart-grid { gap: 16px; }
.chart-panel { padding: 16px; border-radius: 18px; }
.chart-panel h2 { font-size: 18px; }
.table-wrap { border-radius: 18px; }
table { background: #fff; border-radius: 12px; overflow: hidden; font-size: 14px; }
th, td { padding: 9px 10px; border-bottom: 1px solid #eee9df; }
th { color: #3f4a57; background: #f9f6f0; font-weight: 600; }
tr:hover td { background: #fffbf4; }
.coverage-cell {
  background: linear-gradient(var(--track), var(--track)) center/100% 7px no-repeat;
}
"""


def render_donut_card(
    title: str,
    rate: float | None,
    *,
    numerator: int,
    denominator: int,
    tone: str,
    subject: str,
) -> str:
    value = 0.0 if rate is None else max(0.0, min(100.0, rate))
    display = "—" if rate is None else f"{rate:.1f}%"
    return f"""
    <article class="donut-card">
      <h2>{html.escape(title)}</h2>
      <div class="donut {tone}" style="--value:{value:.2f}">
        <strong>{html.escape(display)}</strong>
      </div>
      <div class="formula">
        <strong>Calculated:</strong> {numerator:,} / {denominator:,} × 100%
        <br><strong>Source:</strong> current {html.escape(subject)}
      </div>
    </article>
    """


def render_progress_card(
    title: str,
    rate: float | None,
    *,
    covered: int,
    total: int,
    css_class: str = "",
) -> str:
    value = 0.0 if rate is None else max(0.0, min(100.0, rate))
    return f"""
    <article class="progress-card {css_class}">
      <div class="progress-head">
        <strong>{html.escape(title)}</strong>
        <span>{html.escape(format_percent(rate))}</span>
      </div>
      <div class="progress-track"><span style="width:{value:.2f}%"></span></div>
      <span>Covered: {covered:,} · Total: {total:,}</span>
    </article>
    """


def render_lowest_file_bars(metrics: dict[str, Any]) -> str:
    rows: list[str] = []
    for module in metrics["modules"][:10]:
        rate = module["line_rate"]
        width = 0.0 if rate is None else max(0.0, min(100.0, float(rate)))
        label = Path(module["path"]).name
        rows.append(
            '<div class="bar-row">'
            f'<code class="bar-label" title="{html.escape(module["path"])}">'
            f"{html.escape(label)}</code>"
            f'<div class="bar-track"><span style="width:{width:.2f}%"></span></div>'
            f'<span class="bar-value">{html.escape(format_percent(rate))}</span>'
            "</div>"
        )
    return "\n".join(rows) or '<p class="empty-state">No measured files.</p>'


def render_inventory_bars(metrics: dict[str, Any]) -> str:
    latest = metrics["latest"]
    if latest is None:
        return '<p class="empty-state">No current coverage data.</p>'
    inventory = (
        ("Covered lines", latest["covered_lines"]),
        ("Missing lines", latest["missing_lines"]),
        ("Covered branches", latest["covered_branches"]),
        ("Missing branches", latest["missing_branches"]),
    )
    maximum = max((int(value) for _, value in inventory), default=0)
    rows: list[str] = []
    for label, raw_value in inventory:
        value = int(raw_value)
        width = value * 100 / maximum if maximum else 0.0
        rows.append(
            '<div class="bar-row inventory">'
            f'<span class="bar-label">{html.escape(label)}</span>'
            f'<div class="bar-track"><span style="width:{width:.2f}%"></span></div>'
            f'<span class="bar-value">{value:,}</span>'
            "</div>"
        )
    return "\n".join(rows)


def render_dashboard(
    metrics: dict[str, Any],
    *,
    root_prefix: str,
    quality_url: str,
) -> str:
    latest = metrics["latest"]
    files = metrics["files"]
    generated_at = parse_datetime(metrics["generated_at"])

    if latest is None:
        header_meta = '<span class="muted">No coverage reports published yet.</span>'
        original_link = ""
        cards = render_donut_card(
            "Line Coverage",
            None,
            numerator=0,
            denominator=0,
            tone="tone-blue",
            subject="coverage.py totals",
        )
        progress = ""
    else:
        measurement_time = html.escape(metrics["latest_context"]["label"])
        header_meta = (
            f'<span class="badge">Current snapshot</span>'
            f'<span class="badge">{measurement_time}</span>'
            f"<span>Run {latest['run_id']}</span>"
            f"<span>{html.escape(latest['branch'])}</span>"
            f"<span>{html.escape(latest['sha'][:8])}</span>"
        )
        original_link = (
            f'<a class="button button-primary" '
            f'href="{html.escape(root_prefix + latest["html_url"])}">'
            "Open original coverage.py page</a>"
        )
        cards = "".join(
            (
                render_donut_card(
                    "Line Coverage",
                    latest["line_rate"],
                    numerator=latest["covered_lines"],
                    denominator=latest["num_statements"],
                    tone="tone-blue",
                    subject="statements",
                ),
                render_donut_card(
                    "Branch Coverage",
                    latest["branch_rate"],
                    numerator=latest["covered_branches"],
                    denominator=latest["num_branches"],
                    tone="tone-purple",
                    subject="branches",
                ),
                render_donut_card(
                    "Full Coverage",
                    files["full_rate"],
                    numerator=files["full"],
                    denominator=files["total"],
                    tone="tone-green",
                    subject="measured files",
                ),
                render_donut_card(
                    "Partial Coverage",
                    files["partial_rate"],
                    numerator=files["partial"],
                    denominator=files["total"],
                    tone="tone-amber",
                    subject="measured files",
                ),
                render_donut_card(
                    "Empty Coverage",
                    files["empty_rate"],
                    numerator=files["empty"],
                    denominator=files["total"],
                    tone="tone-red",
                    subject="measured files",
                ),
            )
        )
        progress = "".join(
            (
                render_progress_card(
                    "Statements Coverage",
                    latest["line_rate"],
                    covered=latest["covered_lines"],
                    total=latest["num_statements"],
                ),
                render_progress_card(
                    "Files With Coverage",
                    files["with_coverage_rate"],
                    covered=files["with_coverage"],
                    total=files["total"],
                    css_class="files",
                ),
            )
        )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>API framework code coverage</title>
    <style>{SNAPSHOT_CSS}</style>
  </head>
  <body>
    <main class="page">
      <header>
        <h1 class="title">API Framework Code Coverage</h1>
        <p class="subtitle">Current coverage.py snapshot for the API test framework</p>
        <nav class="qa-report-links" aria-label="QA report navigation">
          <a class="button" href="{html.escape(quality_url)}">Open QA metrics</a>
          {original_link}
        </nav>
        <div class="report-meta">{header_meta}</div>
      </header>

      <section class="group">
        <h2>1️⃣ Coverage Summary</h2>
        <p class="desc">Current line, branch and file coverage from the latest published run.</p>
        <div class="snapshot-note">
          <strong>Current state only.</strong>
          This page uses the latest published coverage measurement and does not
          average or aggregate coverage over a 7-, 14-, or any other day window.
        </div>
        <div class="donut-grid" aria-label="Current coverage summary">{cards}</div>
        <div class="progress-grid" aria-label="Current coverage progress">{progress}</div>
      </section>

      <section class="group">
        <h2>2️⃣ Coverage Details</h2>
        <p class="desc">Files with the lowest line coverage and the current coverage inventory.</p>
        <div class="section">
          <div class="chart-grid">
            <article class="chart-panel">
              <h2>Lowest Line Coverage by File</h2>
              <div class="bar-list">{render_lowest_file_bars(metrics)}</div>
            </article>
            <article class="chart-panel">
              <h2>Current Coverage Inventory</h2>
              <div class="bar-list">{render_inventory_bars(metrics)}</div>
            </article>
          </div>
        </div>
        <div class="section">
          <div class="section-head">
            <h2>Coverage by File</h2>
            <span class="section-note">Current measurement · lowest line coverage first</span>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>File</th>
                  <th class="number">Lines</th>
                  <th class="number">Branches</th>
                  <th class="number">Covered lines</th>
                  <th>Missing lines</th>
                  <th>Coverage</th>
                </tr>
              </thead>
              <tbody>{render_module_rows(metrics)}</tbody>
            </table>
          </div>
        </div>
      </section>

      <footer class="footer">
        <span>Snapshot generated {generated_at.strftime("%d %b %Y %H:%M UTC")}</span>
        <span>Source: latest coverage.py JSON · {metrics["reports"]} archived measurements available</span>
      </footer>
    </main>
  </body>
</html>
"""


def append_github_output(metrics: dict[str, Any]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    latest = metrics["latest"]
    with open(output_path, "a", encoding="utf-8") as output:
        output.write("coverage_dashboard_path=quality/coverage/\n")
        output.write(f"coverage_reports={metrics['reports']}\n")
        if latest and latest["line_rate"] is not None:
            output.write(f"line_coverage={latest['line_rate']}\n")


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
    period_root = site_dir / "quality" / "coverage" / "periods"
    for metrics_path in period_root.glob("*/metrics.json"):
        try:
            saved_days.add(int(metrics_path.parent.name))
        except ValueError:
            continue
    in_period_snapshot = destination_relative.parts[:3] == (
        "quality",
        "coverage",
        "periods",
    )
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
    parser.add_argument("--destination", default="quality/coverage")
    parser.add_argument("--quality-url", default="../")
    parser.add_argument("--now", help="ISO-8601 UTC timestamp used as window end")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    now = parse_datetime(args.now) if args.now else datetime.now(UTC)
    reports = load_coverage_reports(
        args.site_dir,
        window_start_at=datetime(1970, 1, 1, tzinfo=UTC),
        window_end=now,
    )
    metrics = build_metrics(reports, now=now)
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
            quality_url=args.quality_url,
        ),
        encoding="utf-8",
    )
    append_github_output(metrics)
    print(
        f"Built current coverage snapshot from {metrics['reports']} archived reports."
    )


if __name__ == "__main__":
    main()
