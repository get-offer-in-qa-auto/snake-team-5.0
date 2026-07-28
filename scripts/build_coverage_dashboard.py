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
        "html_url": f"../../{report.path}/html/",
        "json_url": f"../../{report.path}/coverage.json",
        "xml_url": f"../../{report.path}/coverage.xml",
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
            }
        )
    return trend


def build_metrics(
    reports: list[CoverageReport], *, now: datetime, days: int
) -> dict[str, Any]:
    latest = coverage_summary(reports[-1]) if reports else None
    previous = coverage_summary(reports[-2]) if len(reports) > 1 else None
    line_delta = None
    branch_delta = None
    if latest and previous:
        if latest["line_rate"] is not None and previous["line_rate"] is not None:
            line_delta = round(latest["line_rate"] - previous["line_rate"], 2)
        if latest["branch_rate"] is not None and previous["branch_rate"] is not None:
            branch_delta = round(latest["branch_rate"] - previous["branch_rate"], 2)
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "window": {
            "days": days,
            "start": window_start(now, days).isoformat(timespec="seconds"),
            "end": now.isoformat(timespec="seconds"),
        },
        "reports": len(reports),
        "latest": latest,
        "previous": previous,
        "delta": {
            "line_rate": line_delta,
            "branch_rate": branch_delta,
        },
        "trend": daily_trend(reports, now=now, days=days),
        "modules": module_summaries(reports[-1]) if reports else [],
    }


def format_delta(value: float | None) -> str:
    if value is None:
        return "No previous report"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f} pp vs previous report"


def render_trend(metrics: dict[str, Any]) -> str:
    columns: list[str] = []
    for day in metrics["trend"]:
        rate = day["line_rate"]
        label = format_percent(rate)
        height = 3 if rate is None else max(3, min(100, rate))
        columns.append(
            '<div class="trend-day">'
            f"<strong>{html.escape(label)}</strong>"
            '<div class="trend-track">'
            f'<span style="height:{height:.1f}%"></span>'
            "</div>"
            f'<span class="muted">{html.escape(day["label"])}</span>'
            "</div>"
        )
    return "\n".join(columns)


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
.button {
  display: inline-block; padding: 6px 10px; border: 1px solid var(--border);
  border-radius: 7px; background: var(--surface);
}
.stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 20px; }
.card, .table-wrap, .trend {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
}
.card { padding: 16px; }
.stat-value { display: block; font-size: 28px; margin: 3px 0; }
.section { margin-top: 22px; }
.section-head { align-items: baseline; margin-bottom: 10px; }
.trend {
  height: 220px; display: grid;
  grid-template-columns: repeat(var(--days), minmax(48px, 1fr));
  gap: 12px; padding: 16px; overflow-x: auto;
}
.trend-day {
  min-width: 48px; display: grid; grid-template-rows: auto 1fr auto;
  gap: 5px; align-items: end; text-align: center;
}
.trend-track {
  height: 145px; display: flex; align-items: flex-end;
  background: var(--track);
}
.trend-track span { display: block; width: 100%; background: var(--series); }
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
}
"""


def render_dashboard(metrics: dict[str, Any]) -> str:
    latest = metrics["latest"]
    if latest is None:
        header_meta = '<span class="muted">No coverage reports published yet.</span>'
        actions = '<a class="button" href="../">Back to QA metrics</a>'
        stats = (
            '<article class="card"><span class="muted">Line coverage</span>'
            '<strong class="stat-value">—</strong></article>'
        )
    else:
        header_meta = (
            f'<span class="badge">{html.escape(latest["source"])}</span>'
            f"<span>Run {latest['run_id']}</span>"
            f"<span>{html.escape(latest['branch'])}</span>"
            f"<span>{html.escape(latest['sha'][:8])}</span>"
        )
        actions = (
            '<a class="button" href="../">Back to QA metrics</a>'
            f'<a class="button" href="{html.escape(latest["html_url"])}">'
            "Open standard HTML report</a>"
        )
        stats = f"""
        <article class="card">
          <span class="muted">Line coverage</span>
          <strong class="stat-value">{format_percent(latest["line_rate"])}</strong>
          <span>{html.escape(format_delta(metrics["delta"]["line_rate"]))}</span>
        </article>
        <article class="card">
          <span class="muted">Branch coverage</span>
          <strong class="stat-value">{format_percent(latest["branch_rate"])}</strong>
          <span>{latest["covered_branches"]} of {latest["num_branches"]} branches</span>
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
        <div class="actions">{actions}</div>
      </header>

      <section class="stats" aria-label="Coverage summary">{stats}</section>

      <section class="section">
        <div class="section-head">
          <h2>{metrics["window"]["days"]}-day trend</h2>
          <span class="section-note">Latest API regression report per UTC day</span>
        </div>
        <div class="trend" style="--days:{metrics["window"]["days"]}">
          {render_trend(metrics)}
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", required=True, type=Path)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--now", help="ISO-8601 UTC timestamp used as window end")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.days < 1 or args.days > 90:
        raise ValueError("--days must be between 1 and 90")
    now = parse_datetime(args.now) if args.now else datetime.now(UTC)
    reports = load_coverage_reports(
        args.site_dir,
        window_start_at=window_start(now, args.days),
        window_end=now,
    )
    metrics = build_metrics(reports, now=now, days=args.days)
    destination = args.site_dir / "quality" / "coverage"
    destination.mkdir(parents=True, exist_ok=True)
    destination.joinpath("metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    destination.joinpath("index.html").write_text(
        render_dashboard(metrics),
        encoding="utf-8",
    )
    append_github_output(metrics)
    print(f"Built coverage dashboard from {len(reports)} reports.")


if __name__ == "__main__":
    main()
