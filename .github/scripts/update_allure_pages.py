#!/usr/bin/env python3
"""Add one Allure report to the persistent GitHub Pages site."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-").lower()
    if not slug:
        raise ValueError("slug value must contain at least one safe character")
    return slug


def copy_report(report_dir: Path, destination: Path) -> None:
    if not (report_dir / "index.html").is_file():
        raise FileNotFoundError(f"Allure report index.html was not found in {report_dir}")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(report_dir, destination)


def write_metadata(report_dir: Path, metadata: dict[str, str]) -> None:
    (report_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_reports(site_dir: Path) -> list[dict[str, str]]:
    reports: list[dict[str, str]] = []
    for metadata_path in sorted((site_dir / "reports").glob("*/*/metadata.json")):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        report_path = metadata_path.parent.relative_to(site_dir).as_posix()
        metadata["path"] = report_path
        reports.append(metadata)
    return sorted(
        reports,
        key=lambda item: (item.get("generated_at", ""), item.get("report_id", "")),
        reverse=True,
    )


def render_report_rows(reports: list[dict[str, str]], link_prefix: str = "") -> str:
    rows = []
    for report in reports:
        path = html.escape(link_prefix + report["path"] + "/")
        suite = html.escape(report.get("suite", "unknown"))
        event = html.escape(report.get("event", "unknown"))
        branch = html.escape(report.get("branch", "unknown"))
        generated_at = html.escape(report.get("generated_at", "unknown"))
        run_url = html.escape(report.get("run_url", "#"))
        short_sha = html.escape(report.get("sha", "")[:12])
        rows.append(
            "      <tr>"
            f"<td><a href=\"{path}\">{generated_at}</a></td>"
            f"<td>{suite}</td>"
            f"<td>{event}</td>"
            f"<td>{branch}</td>"
            f"<td><a href=\"{run_url}\">run</a></td>"
            f"<td>{short_sha}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_index(reports: list[dict[str, str]], title: str, link_prefix: str = "") -> str:
    latest = reports[0] if reports else None
    latest_link = ""
    if latest is not None:
        latest_path = html.escape(link_prefix + latest["path"] + "/")
        latest_link = f'<p class="latest"><a href="{latest_path}">Open latest report</a></p>'

    rows = render_report_rows(reports, link_prefix=link_prefix)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    <style>
      body {{
        margin: 32px auto;
        max-width: 1080px;
        padding: 0 20px;
        color: #1f2937;
        font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      a {{ color: #0969da; }}
      table {{ border-collapse: collapse; width: 100%; }}
      th, td {{ border-bottom: 1px solid #d0d7de; padding: 10px 8px; text-align: left; }}
      th {{ background: #f6f8fa; font-weight: 600; }}
      .latest {{ font-size: 18px; }}
    </style>
  </head>
  <body>
    <h1>{html.escape(title)}</h1>
    {latest_link}
    <table>
      <thead>
        <tr>
          <th>Generated</th>
          <th>Suite</th>
          <th>Event</th>
          <th>Branch</th>
          <th>Actions</th>
          <th>SHA</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </body>
</html>
"""


def write_indexes(site_dir: Path, reports: list[dict[str, str]]) -> None:
    (site_dir / "index.html").write_text(
        render_index(reports, "TeamCity Allure Reports"),
        encoding="utf-8",
    )
    reports_dir = site_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "index.html").write_text(
        render_index(reports, "TeamCity Allure Reports", link_prefix="../"),
        encoding="utf-8",
    )
    if reports:
        latest = reports[0]["path"]
        (site_dir / "latest.html").write_text(
            "<!doctype html>\n"
            "<html lang=\"en\">\n"
            "  <head>\n"
            "    <meta charset=\"utf-8\">\n"
            f"    <meta http-equiv=\"refresh\" content=\"0; url={html.escape(latest)}/\">\n"
            "    <title>Latest Allure Report</title>\n"
            "  </head>\n"
            "  <body>\n"
            f"    <p><a href=\"{html.escape(latest)}/\">Open latest report</a></p>\n"
            "  </body>\n"
            "</html>\n",
            encoding="utf-8",
        )


def append_github_output(report_path: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as output:
            output.write(f"report_path={report_path}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--report-id", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--event", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--run-url", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    site_dir = args.site_dir
    report_dir = args.report_dir
    suite = slugify(args.suite)
    report_id = slugify(args.report_id)
    report_path = f"reports/{suite}/{report_id}"
    destination = site_dir / report_path

    (site_dir / "reports" / suite).mkdir(parents=True, exist_ok=True)
    (site_dir / ".nojekyll").touch()
    copy_report(report_dir, destination)

    metadata = {
        "branch": args.branch,
        "event": args.event,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "report_id": report_id,
        "run_url": args.run_url,
        "sha": args.sha,
        "suite": suite,
        "workflow": args.workflow,
    }
    write_metadata(destination, metadata)
    write_indexes(site_dir, load_reports(site_dir))
    append_github_output(report_path)
    print(f"Report path: {report_path}")


if __name__ == "__main__":
    main()
