#!/usr/bin/env python3
"""Build a rolling API framework coverage dashboard from coverage.py reports."""

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


def build_metrics(
    reports: list[CoverageReport], *, now: datetime, days: int
) -> dict[str, Any]:
    window_start_at = window_start(now, days)
    window_reports = [
        report for report in reports if window_start_at <= report.generated_at <= now
    ]
    latest = coverage_summary(reports[-1]) if reports else None
    previous = coverage_summary(reports[-2]) if len(reports) > 1 else None
    trend = daily_trend(window_reports, now=now, days=days)
    latest_generated_at = (
        parse_datetime(latest["generated_at"]) if latest is not None else None
    )
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "window": {
            "days": days,
            "start": window_start(now, days).isoformat(timespec="seconds"),
            "end": now.isoformat(timespec="seconds"),
        },
        "reports": len(window_reports),
        "latest": latest,
        "previous": previous,
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
        "delta": {
            "line_rate": rate_delta(latest, previous, "line_rate"),
            "branch_rate": rate_delta(latest, previous, "branch_rate"),
        },
        "period_delta": {
            "line_rate": trend_delta(trend, "line_rate"),
            "branch_rate": trend_delta(trend, "branch_rate"),
        },
        "trend": trend,
        "modules": module_summaries(reports[-1]) if reports else [],
        "history": [
            coverage_summary(report)
            for report in sorted(
                window_reports,
                key=lambda item: item.generated_at,
                reverse=True,
            )
        ],
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


def render_dashboard(
    metrics: dict[str, Any],
    *,
    root_prefix: str,
    quality_url: str,
    periods: list[tuple[int, str]],
) -> str:
    latest = metrics["latest"]
    if latest is None:
        header_meta = '<span class="muted">No coverage reports published yet.</span>'
        actions = f'<a class="button" href="{html.escape(quality_url)}">Back to QA metrics</a>'
        stats = (
            '<article class="card"><span class="muted">Line coverage</span>'
            '<strong class="stat-value">—</strong></article>'
        )
    else:
        latest_context = metrics["latest_context"]
        measurement_time = html.escape(latest_context["label"])
        line_report_delta = render_delta(
            metrics["delta"]["line_rate"],
            reference="previous report",
            unavailable="No previous report",
        )
        branch_report_delta = render_delta(
            metrics["delta"]["branch_rate"],
            reference="previous report",
            unavailable="No previous report",
        )
        header_meta = (
            f'<span class="badge">{html.escape(latest["source"])}</span>'
            f'<span class="badge">{measurement_time}</span>'
            f"<span>Run {latest['run_id']}</span>"
            f"<span>{html.escape(latest['branch'])}</span>"
            f"<span>{html.escape(latest['sha'][:8])}</span>"
        )
        actions = (
            f'<a class="button" href="{html.escape(quality_url)}">Back to QA metrics</a>'
            f'<a class="button" href="{html.escape(root_prefix + latest["html_url"])}">'
            "Open standard HTML report</a>"
        )
        stats = f"""
        <article class="card">
          <span class="muted">Current line coverage</span>
          <strong class="stat-value">{format_percent(latest["line_rate"])}</strong>
          <div class="stat-context">
            {line_report_delta}
            <span class="measurement-time">{measurement_time}</span>
          </div>
        </article>
        <article class="card">
          <span class="muted">Current branch coverage</span>
          <strong class="stat-value">{format_percent(latest["branch_rate"])}</strong>
          <div class="stat-context">
            {branch_report_delta}
            <span>{latest["covered_branches"]} of {latest["num_branches"]} branches</span>
          </div>
        </article>
        <article class="card">
          <span class="muted">Covered lines</span>
          <strong class="stat-value">{latest["covered_lines"]:,}</strong>
          <span>{latest["missing_lines"]:,} lines missing</span>
        </article>
        <article class="card">
          <span class="muted">Measured files</span>
          <strong class="stat-value">{len(metrics["modules"])}</strong>
          <span>{latest["num_statements"]:,} statements</span>
        </article>
        """

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>API test framework coverage</title>
    <style>{COVERAGE_CSS}</style>
  </head>
  <body>
    <main class="page">
      <header class="topbar">
        <div>
          <span class="muted">QA metrics / Coverage</span>
          <h1>API test framework coverage</h1>
          <div class="meta">{header_meta}</div>
        </div>
        <div>
          <div class="actions">{actions}</div>
          <div class="period-links" aria-label="Saved coverage periods">
            {render_period_links(periods, current_days=metrics["window"]["days"])}
          </div>
        </div>
      </header>

      <section class="stats" aria-label="Coverage summary">{stats}</section>

      <section class="section">
        <div class="section-head">
          <h2>{metrics["window"]["days"]}-day trend</h2>
          <span class="section-note">Last measurement of each UTC day · no averaging</span>
        </div>
        <div class="coverage-chart-wrap">
          {render_coverage_trend(metrics, root_prefix=root_prefix)}
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Coverage report history</h2>
          <span class="section-note">Every published API coverage report in this period</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Generated</th>
                <th>Run</th>
                <th>Branch</th>
                <th class="number">Lines</th>
                <th class="number">Branches</th>
                <th>Data</th>
              </tr>
            </thead>
            <tbody>{render_history_rows(metrics, root_prefix=root_prefix)}</tbody>
          </table>
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <h2>Coverage by module</h2>
          <span class="section-note">Lowest line coverage first</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Module</th>
                <th class="number">Lines</th>
                <th class="number">Branches</th>
                <th class="number">Covered</th>
                <th>Missing lines</th>
                <th>Coverage</th>
              </tr>
            </thead>
            <tbody>{render_module_rows(metrics)}</tbody>
          </table>
        </div>
      </section>

      <footer class="footer">
        Source: coverage.py JSON · {metrics["reports"]} reports in this window
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
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--destination", default="quality/coverage")
    parser.add_argument("--quality-url", default="../")
    parser.add_argument("--now", help="ISO-8601 UTC timestamp used as window end")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.days < 1:
        raise ValueError("--days must be a positive integer")
    now = parse_datetime(args.now) if args.now else datetime.now(UTC)
    reports = load_coverage_reports(
        args.site_dir,
        window_start_at=datetime(1970, 1, 1, tzinfo=UTC),
        window_end=now,
    )
    metrics = build_metrics(reports, now=now, days=args.days)
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
        "Built coverage dashboard from "
        f"{metrics['reports']} reports in the selected window."
    )


if __name__ == "__main__":
    main()
