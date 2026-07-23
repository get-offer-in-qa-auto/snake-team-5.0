#!/usr/bin/env python3
import argparse
import os
import sys

import psycopg
import requests

from src.main.api.database import DBRequest, create_database_client


def run_database_preflight() -> int:
    try:
        client = create_database_client()
        with client.snapshot() as executor:
            executor.fetch_all(DBRequest.select("users"))
    except (
        AssertionError,
        LookupError,
        OSError,
        RuntimeError,
        TimeoutError,
        psycopg.Error,
    ) as error:
        print(f"TeamCity database preflight failed: {error}", file=sys.stderr)
        return 1
    except requests.RequestException as error:
        response = error.response
        response_details = ""
        if response is not None:
            response_details = (
                f" HTTP {response.status_code}. Response: {response.text[:500]}"
            )
        print(
            f"TeamCity database preflight request failed: {error}.{response_details}",
            file=sys.stderr,
        )
        return 1

    adapter = os.getenv("TEAMCITY_DB_ADAPTER", "auto").lower()
    if adapter == "postgresql" or os.getenv("TEAMCITY_DB_DSN"):
        print(
            "TeamCity database preflight passed: PostgreSQL is available "
            "through a read-only snapshot."
        )
    else:
        print("TeamCity database preflight passed: backup and snapshot are available.")
    return 0


def main() -> int:
    argparse.ArgumentParser(
        description=(
            "Verify that the configured TeamCity database adapter can open and "
            "read a consistent snapshot before database tests start."
        )
    ).parse_args()
    return run_database_preflight()


if __name__ == "__main__":
    raise SystemExit(main())
