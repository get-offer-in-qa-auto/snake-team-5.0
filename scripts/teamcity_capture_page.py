#!/usr/bin/env python3
import argparse
import http.client
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from scripts.teamcity_start_smoke import (
        classify_teamcity_response,
        format_readiness_message,
    )
except ModuleNotFoundError:
    from teamcity_start_smoke import classify_teamcity_response, format_readiness_message


def fetch_page(url: str, timeout: int) -> tuple[int | None, str, str]:
    request = Request(url, headers={"User-Agent": "teamcity-page-capture"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, str(response.headers), body
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return error.code, str(error.headers), body
    except URLError as error:
        return None, "", str(error.reason)
    except (ConnectionError, TimeoutError, OSError, http.client.HTTPException) as error:
        return None, "", str(error)


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture TeamCity page response for CI artifacts.")
    parser.add_argument("--url", default="http://localhost:8111/login.html")
    parser.add_argument("--output-dir", default="artifacts/teamcity-page")
    parser.add_argument("--request-timeout", type=int, default=10)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    status, headers, body = fetch_page(args.url, args.request_timeout)
    readiness = classify_teamcity_response(status, body)

    (output_dir / "login.html").write_text(body, encoding="utf-8")
    (output_dir / "headers.txt").write_text(headers, encoding="utf-8")
    (output_dir / "readiness.txt").write_text(
        format_readiness_message(readiness, args.url) + "\n",
        encoding="utf-8",
    )

    print(format_readiness_message(readiness, args.url))
    print(f"Saved TeamCity page snapshot to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
