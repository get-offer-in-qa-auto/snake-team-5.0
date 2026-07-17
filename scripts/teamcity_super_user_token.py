#!/usr/bin/env python3
"""Extract the temporary TeamCity Super User token from server logs."""

import argparse
import os
import re
from pathlib import Path

SUPER_USER_TOKEN_RE = re.compile(
    r"Super\s+user\s+authentication\s+token:\s*([^\s]+)", re.IGNORECASE
)


def extract_super_user_token(log_contents: str) -> str | None:
    """Return the latest token because TeamCity writes one for every start."""
    matches = SUPER_USER_TOKEN_RE.findall(log_contents)
    return matches[-1] if matches else None


def write_secret_file(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        0o600,
    )
    with os.fdopen(descriptor, "w", encoding="utf-8") as secret_file:
        secret_file.write(value)
        secret_file.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract the current TeamCity Super User token from logs."
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        required=True,
        help="TeamCity server log or Docker Compose log output to inspect.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Secure file where the extracted token is written.",
    )
    args = parser.parse_args()

    try:
        log_contents = args.log_file.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        parser.error(f"could not read {args.log_file}: {error}")

    token = extract_super_user_token(log_contents)
    if not token:
        return 1

    write_secret_file(args.output, token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
