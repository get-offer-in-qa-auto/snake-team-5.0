#!/usr/bin/env python3
import argparse
import http.client
import os
import sys
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FIRST_START_MARKERS = (
    "startup confirmation",
    "confirm first start",
    "first start",
    "teamcity data directory",
    "super user authentication token",
)

@dataclass(frozen=True)
class TeamCityReadiness:
    code: str
    message: str
    opened: bool
    status: int | None


def request_url(url: str, timeout: int) -> tuple[int | None, str]:
    request = Request(url, headers={"User-Agent": "teamcity-start-smoke"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            return response.status, body
    except HTTPError as error:
        body = error.read(4096).decode("utf-8", errors="replace")
        return error.code, body
    except URLError as error:
        return None, str(error.reason)
    except (ConnectionError, TimeoutError, OSError, http.client.HTTPException) as error:
        return None, str(error)


def is_expected_first_start(status: int | None, body: str) -> bool:
    if status != 503:
        return False

    normalized_body = body.lower()
    return any(marker in normalized_body for marker in FIRST_START_MARKERS)


def classify_teamcity_response(status: int | None, body: str) -> TeamCityReadiness:
    if status == 200:
        return TeamCityReadiness(
            code="READY_LOGIN_PAGE",
            message="TeamCity login page is open. No login is required for this smoke check.",
            opened=True,
            status=status,
        )

    if status in (401, 403):
        return TeamCityReadiness(
            code="AUTH_REQUIRED",
            message="TeamCity is alive and requires authentication.",
            opened=True,
            status=status,
        )

    if is_expected_first_start(status, body):
        return TeamCityReadiness(
            code="FIRST_START_REQUIRED",
            message="TeamCity reached first-start/setup confirmation state.",
            opened=True,
            status=status,
        )

    if status is None:
        return TeamCityReadiness(
            code="WAITING_FOR_HTTP",
            message=f"TeamCity is not accepting HTTP connections yet: {body}",
            opened=False,
            status=status,
        )

    return TeamCityReadiness(
        code="UNEXPECTED_HTTP_STATUS",
        message=f"TeamCity answered with HTTP {status}; waiting.",
        opened=False,
        status=status,
    )


def format_readiness_message(readiness: TeamCityReadiness, url: str) -> str:
    status = "no HTTP response" if readiness.status is None else f"HTTP {readiness.status}"
    return f"{readiness.code}: {readiness.message} Endpoint: {url}. Status: {status}."


def append_github_step_summary(readiness: TeamCityReadiness, url: str) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    status = "no HTTP response" if readiness.status is None else f"HTTP {readiness.status}"
    result = "Ready" if readiness.opened else "Not ready"
    with open(summary_path, "a", encoding="utf-8") as summary:
        summary.write("## TeamCity Readiness\n\n")
        summary.write("| Check | Result |\n")
        summary.write("| --- | --- |\n")
        summary.write(f"| Endpoint | `{url}` |\n")
        summary.write(f"| State | `{readiness.code}` |\n")
        summary.write(f"| HTTP status | `{status}` |\n")
        summary.write(f"| Result | **{result}** |\n")
        summary.write(f"| Meaning | {readiness.message} |\n\n")


def is_teamcity_opened(status: int | None, body: str) -> bool:
    return classify_teamcity_response(status, body).opened


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Wait until TeamCity starts enough for the initial CI smoke."
    )
    parser.add_argument("--url", default="http://localhost:8111/login.html")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--interval", type=int, default=2)
    parser.add_argument("--request-timeout", type=int, default=5)
    args = parser.parse_args()

    deadline = time.monotonic() + args.timeout
    last_status: int | None = None
    last_body = ""

    while time.monotonic() < deadline:
        status, body = request_url(args.url, args.request_timeout)
        last_status = status
        last_body = body
        readiness = classify_teamcity_response(status, body)
        message = format_readiness_message(readiness, args.url)

        if readiness.opened:
            if os.getenv("GITHUB_ACTIONS"):
                print(f"::notice title=TeamCity readiness::{message}")
            print(message)
            append_github_step_summary(readiness, args.url)
            return 0

        print(message)

        time.sleep(args.interval)

    readiness = classify_teamcity_response(last_status, last_body)
    append_github_step_summary(readiness, args.url)
    print(
        f"Timed out waiting for TeamCity at {args.url}. "
        f"Last state: {readiness.code}. Last status: {last_status}. "
        f"Last response snippet: {last_body[:500]}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
