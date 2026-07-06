#!/usr/bin/env python3
import argparse
import http.client
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FIRST_START_MARKERS = (
    "startup confirmation",
    "confirm first start",
    "first start",
    "teamcity data directory",
    "super user authentication token",
)


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Wait until TeamCity starts enough for the initial CI smoke."
    )
    parser.add_argument("--url", default="http://localhost:8111")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--request-timeout", type=int, default=10)
    args = parser.parse_args()

    deadline = time.monotonic() + args.timeout
    last_status: int | None = None
    last_body = ""

    while time.monotonic() < deadline:
        status, body = request_url(args.url, args.request_timeout)
        last_status = status
        last_body = body

        if status is None:
            print(f"TeamCity is not accepting HTTP connections yet: {body}")
        elif 200 <= status < 500:
            print(f"TeamCity web endpoint is reachable with HTTP {status}.")
            return 0
        elif is_expected_first_start(status, body):
            print(
                "TeamCity reached the expected first-start confirmation state "
                f"with HTTP {status}."
            )
            return 0
        else:
            print(f"TeamCity answered with HTTP {status}; waiting.")

        time.sleep(args.interval)

    print(
        f"Timed out waiting for TeamCity at {args.url}. "
        f"Last status: {last_status}. Last response snippet: {last_body[:500]}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
