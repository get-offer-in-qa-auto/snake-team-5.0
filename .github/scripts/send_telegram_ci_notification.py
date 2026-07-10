#!/usr/bin/env python3
"""Send a Telegram message for a completed GitHub Actions workflow run."""

from __future__ import annotations

import html
import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


HTTP_TIMEOUT_SECONDS = 20
LOGGER = logging.getLogger("telegram-ci-notify")


@dataclass(frozen=True)
class Config:
    event_path: str
    github_token: str
    telegram_token: str
    telegram_chat_id: str
    telegram_thread_id: str
    dry_run: bool


@dataclass(frozen=True)
class WorkflowRun:
    name: str
    status: str
    branch: str
    event_name: str
    short_sha: str
    url: str
    jobs_url: str
    repository: str
    pr_number: str
    pr_url: str


@dataclass(frozen=True)
class WorkflowJob:
    name: str
    status: str


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def workflow_jobs(self, jobs_url: str) -> list[WorkflowJob]:
        if not jobs_url or not self.token:
            return []

        try:
            payload = self.get_json(add_query_params(jobs_url, {"per_page": "100"}))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
            LOGGER.warning("Could not load workflow jobs: %s", error)
            return []

        jobs = payload.get("jobs", [])
        if not isinstance(jobs, list):
            return []

        return [parse_job(job) for job in jobs if isinstance(job, dict)]

    def get_json(self, url: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
            },
        )
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            payload = json.load(response)
        return payload if isinstance(payload, dict) else {}


class TelegramClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def send_message(self, chat_id: str, thread_id: str, text: str) -> bool:
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        if thread_id:
            payload["message_thread_id"] = thread_id

        request = urllib.request.Request(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                response_payload = json.load(response)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            LOGGER.error("Telegram API failed with HTTP %s: %s", error.code, body)
            return False
        except (urllib.error.URLError, TimeoutError) as error:
            LOGGER.error("Telegram API request failed: %s", error)
            return False

        if not response_payload.get("ok"):
            LOGGER.error("Telegram API returned an error: %s", response_payload)
            return False

        return True


def getenv(name: str) -> str:
    return os.getenv(name, "").strip()


def configure_logging() -> None:
    level_name = getenv("LOG_LEVEL").upper() or "INFO"
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def load_config() -> Config:
    config = Config(
        event_path=getenv("GITHUB_EVENT_PATH"),
        github_token=getenv("GITHUB_TOKEN"),
        telegram_token=getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=getenv("TELEGRAM_CHAT_ID"),
        telegram_thread_id=getenv("TELEGRAM_THREAD_ID"),
        dry_run=getenv("TELEGRAM_DRY_RUN").lower() in {"1", "true", "yes"},
    )

    if not config.event_path:
        raise ValueError("GITHUB_EVENT_PATH is not set.")
    if not config.dry_run and not config.telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")
    if not config.dry_run and not config.telegram_chat_id:
        raise ValueError("TELEGRAM_CHAT_ID is not configured.")

    return config


def read_event(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as event_file:
        event = json.load(event_file)
    return event if isinstance(event, dict) else {}


def parse_workflow_run(event: dict[str, Any]) -> WorkflowRun:
    raw_run = event.get("workflow_run")
    if not isinstance(raw_run, dict):
        raise ValueError("workflow_run payload is missing.")

    raw_repository = raw_run.get("repository") or event.get("repository") or {}
    repository = raw_repository if isinstance(raw_repository, dict) else {}
    pull_request = first_dict(raw_run.get("pull_requests"))
    head_sha = str(raw_run.get("head_sha") or "")
    name = str(raw_run.get("name") or event.get("workflow") or "")
    if not name:
        raise ValueError("Workflow run name is missing.")

    return WorkflowRun(
        name=name,
        status=str(raw_run.get("conclusion") or raw_run.get("status") or "unknown"),
        branch=str(raw_run.get("head_branch") or "unknown"),
        event_name=str(raw_run.get("event") or event.get("action") or "unknown"),
        short_sha=head_sha[:12] if head_sha else "unknown",
        url=str(raw_run.get("html_url") or ""),
        jobs_url=str(raw_run.get("jobs_url") or ""),
        repository=str(repository.get("full_name") or getenv("GITHUB_REPOSITORY")),
        pr_number=str(pull_request.get("number") or ""),
        pr_url=str(pull_request.get("html_url") or ""),
    )


def parse_job(raw_job: dict[str, Any]) -> WorkflowJob:
    return WorkflowJob(
        name=str(raw_job.get("name") or "unknown"),
        status=str(raw_job.get("conclusion") or raw_job.get("status") or "unknown"),
    )


def first_dict(value: object) -> dict[str, Any]:
    if isinstance(value, list) and value and isinstance(value[0], dict):
        return value[0]
    return {}


def add_query_params(url: str, params: dict[str, str]) -> str:
    parts = urllib.parse.urlsplit(url)
    query = dict(urllib.parse.parse_qsl(parts.query))
    query.update(params)
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query)))


def html_escape(value: object) -> str:
    return html.escape(str(value), quote=False)


def html_link(url: str, label: str) -> str:
    return f'<a href="{html.escape(url, quote=True)}">{html_escape(label)}</a>'


def pull_request_line(run: WorkflowRun) -> str:
    if not run.pr_number:
        return ""

    pr_url = run.pr_url
    if not pr_url and run.repository:
        pr_url = f"https://github.com/{run.repository}/pull/{run.pr_number}"

    label = f"PR #{run.pr_number}"
    return f"Pull request: {html_link(pr_url, label)}" if pr_url else f"Pull request: {html_escape(label)}"


def job_lines(jobs: list[WorkflowJob]) -> list[str]:
    if not jobs:
        return ["Jobs: unknown"]

    return ["Jobs:"] + [
        f"- {html_escape(job.name)}: {html_escape(job.status)}" for job in jobs
    ]


def build_message(run: WorkflowRun, jobs: list[WorkflowJob]) -> str:
    lines = [
        f"<b>{html_escape(run.name)}: {html_escape(run.status)}</b>",
        f"Branch: {html_escape(run.branch)}",
        f"Event: {html_escape(run.event_name)}",
        f"Commit: {html_escape(run.short_sha)}",
    ]

    if pr_line := pull_request_line(run):
        lines.append(pr_line)

    lines.extend(job_lines(jobs))

    if run.url:
        lines.append(f"Run: {html_link(run.url, 'GitHub Actions')}")

    return "\n".join(lines)


def main() -> int:
    configure_logging()

    try:
        config = load_config()
        workflow_run = parse_workflow_run(read_event(config.event_path))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        LOGGER.error("%s", error)
        return 1

    LOGGER.info("Workflow run: %s (%s)", workflow_run.name, workflow_run.status)

    jobs = GitHubClient(config.github_token).workflow_jobs(workflow_run.jobs_url)
    LOGGER.info("Workflow jobs loaded: %s", len(jobs))

    message = build_message(workflow_run, jobs)
    if config.dry_run:
        LOGGER.info("Dry run enabled; Telegram message was not sent.")
        LOGGER.info("Telegram message:\n%s", message)
        return 0

    LOGGER.info("Sending Telegram notification.")
    telegram = TelegramClient(config.telegram_token)
    if telegram.send_message(config.telegram_chat_id, config.telegram_thread_id, message):
        LOGGER.info("Telegram notification sent.")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
