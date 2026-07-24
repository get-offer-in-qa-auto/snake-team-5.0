#!/usr/bin/env python3
import argparse
import http.client
import http.cookiejar
import os
import re
import secrets
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit, urlunsplit
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

import requests

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.main.api.constants.teamcity import TeamCityLocator  # noqa: E402

FIRST_START_MARKERS = (
    "startup confirmation",
    "confirm first start",
    "first start",
    "teamcity data directory",
    "super user authentication token",
    "license agreement",
)

CSRF_HEADER_RE = re.compile(r'name="csrf-header-name"\s+content="([^"]+)"')
CSRF_TOKEN_RE = re.compile(r'name="tc-csrf-token"\s+content="([^"]+)"')
MAINTENANCE_STAGE_RE = re.compile(r"Stage:\s*([A-Z_]+)")
ADMIN_SETUP_MARKER = "create administrator account"
ADMIN_PUBLIC_KEY_RE = re.compile(r'name="publicKey"\s+value="([^"]+)"')


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


def request_with_session(
    opener,
    url: str,
    timeout: int,
    data: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int | None, str]:
    request_headers = {"User-Agent": "teamcity-start-smoke"}
    if headers:
        request_headers.update(headers)

    encoded_data = None
    if data is not None:
        encoded_data = urlencode(data).encode("utf-8")
        request_headers["Content-Type"] = "application/x-www-form-urlencoded"

    request = Request(url, data=encoded_data, headers=request_headers)
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, body
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return error.code, body
    except URLError as error:
        return None, str(error.reason)
    except (ConnectionError, TimeoutError, OSError, http.client.HTTPException) as error:
        return None, str(error)


def get_base_url(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")


def extract_csrf_headers(body: str) -> dict[str, str]:
    header_match = CSRF_HEADER_RE.search(body)
    token_match = CSRF_TOKEN_RE.search(body)
    if not header_match or not token_match:
        raise RuntimeError("TeamCity maintenance page did not contain CSRF metadata")
    return {header_match.group(1): token_match.group(1)}


def get_maintenance_stage(body: str) -> str:
    match = MAINTENANCE_STAGE_RE.search(body)
    return match.group(1) if match else ""


def is_admin_setup_page(body: str) -> bool:
    return ADMIN_SETUP_MARKER in body.lower()


def encrypt_teamcity_password(password: str, public_key: str) -> str:
    password_bytes = password.encode("ascii")
    modulus = int(public_key, 16)
    block_size = (modulus.bit_length() + 7) // 8
    if len(password_bytes) > 116 or len(password_bytes) + 11 > block_size:
        raise ValueError("TeamCity administrator password is too long to encrypt")

    padding = bytearray()
    padding_size = block_size - len(password_bytes) - 4
    while len(padding) < padding_size:
        random_byte = secrets.token_bytes(1)
        if random_byte != b"\x00":
            padding.extend(random_byte)

    encoded_password = (
        b"\x00\x02"
        + bytes(padding)
        + b"\x00"
        + password_bytes
        + bytes([len(password_bytes)])
    )
    encrypted_password = pow(
        int.from_bytes(encoded_password, byteorder="big"), 65537, modulus
    )
    encrypted_hex = format(encrypted_password, "x")
    return encrypted_hex if len(encrypted_hex) % 2 == 0 else f"0{encrypted_hex}"


def create_initial_administrator(
    opener,
    base_url: str,
    timeout: int,
    username: str,
    password: str,
) -> None:
    status, body = request_with_session(
        opener, f"{base_url}/setupAdmin.html?init=1", timeout
    )
    if status != 200 or not is_admin_setup_page(body):
        raise RuntimeError(
            "TeamCity administrator setup page is unavailable: "
            f"HTTP {status}. {body[:500]}"
        )

    public_key_match = ADMIN_PUBLIC_KEY_RE.search(body)
    if not public_key_match:
        raise RuntimeError(
            "TeamCity administrator setup page did not contain a public key"
        )

    public_key = public_key_match.group(1)
    encrypted_password = encrypt_teamcity_password(password, public_key)
    status, response_body = request_with_session(
        opener,
        f"{base_url}/createAdminSubmit.html",
        timeout,
        data={
            "username1": username,
            "password1": password,
            "retypedPassword": password,
            "encryptedPassword1": encrypted_password,
            "encryptedRetypedPassword": encrypted_password,
            "submitCreateUser": "",
            "publicKey": public_key,
        },
    )
    if status != 200 or "<errors>" in response_body:
        raise RuntimeError(
            "TeamCity administrator account creation failed: "
            f"HTTP {status}. {response_body[:500]}"
        )


def create_ci_access_token(
    base_url: str,
    username: str,
    password: str,
    token_name: str,
    timeout: int,
) -> str:
    with requests.Session() as session:
        session.auth = (username, password)
        csrf_response = session.get(
            f"{base_url}/authenticationTest.html?csrf",
            headers={"Accept": "text/plain"},
            timeout=timeout,
        )
        if csrf_response.status_code != 200:
            raise RuntimeError(
                "TeamCity CI administrator authentication failed while requesting "
                f"a CSRF token: HTTP {csrf_response.status_code}. "
                f"{csrf_response.text[:500]}"
            )

        csrf_token = csrf_response.text.strip()
        if not csrf_token:
            raise RuntimeError("TeamCity returned an empty administrator CSRF token")

        encoded_username = quote(username, safe="")
        username_locator = TeamCityLocator.USERNAME.build(encoded_username)
        token_response = session.post(
            f"{base_url}/app/rest/users/{username_locator}/tokens",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-TC-CSRF-Token": csrf_token,
            },
            json={"name": token_name},
            timeout=timeout,
        )
        if token_response.status_code not in (200, 201):
            raise RuntimeError(
                "TeamCity access token creation failed: "
                f"HTTP {token_response.status_code}. {token_response.text[:500]}"
            )

        try:
            token = str(token_response.json().get("value") or "").strip()
        except requests.JSONDecodeError as error:
            raise RuntimeError(
                "TeamCity access token response was not valid JSON"
            ) from error
        if not token:
            raise RuntimeError("TeamCity access token response did not contain a value")
        return token


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


def post_maintenance_command(
    opener,
    base_url: str,
    command: str,
    body: str,
    timeout: int,
    data: dict[str, str] | None = None,
) -> tuple[int | None, str]:
    status, response_body = request_with_session(
        opener,
        f"{base_url}/mnt/do/{command}",
        timeout,
        data=data or {},
        headers=extract_csrf_headers(body),
    )
    if status != 200 or response_body.strip() != "OK":
        raise RuntimeError(
            f"TeamCity maintenance command {command} failed: HTTP {status}. {response_body[:500]}"
        )
    return status, response_body


def complete_first_start_setup(
    url: str,
    timeout: int,
    interval: int,
    max_wait: int,
    admin_username: str,
    admin_password: str,
    database_mode: str,
) -> bool:
    base_url = get_base_url(url)
    opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    status, body = request_with_session(opener, url, timeout)
    if is_admin_setup_page(body):
        print("Auto setup: creating the initial TeamCity administrator.")
        create_initial_administrator(
            opener,
            base_url,
            timeout,
            admin_username,
            admin_password,
        )
        status, body = request_with_session(opener, url, timeout)
        return not is_admin_setup_page(body)

    if not is_expected_first_start(status, body):
        return True

    print("Auto setup: opening TeamCity maintenance details.")
    post_maintenance_command(
        opener,
        base_url,
        "saveRedirectedFrom",
        body,
        timeout,
        data={"origURL": url},
    )

    deadline = time.monotonic() + max_wait
    completed_commands: set[str] = set()
    while time.monotonic() < deadline:
        status, body = request_with_session(opener, f"{base_url}/mnt", timeout)
        stage = get_maintenance_stage(body)

        if (
            stage == "FIRST_START_SCREEN"
            and "goNewInstallation" not in completed_commands
        ):
            print("Auto setup: confirming fresh TeamCity installation.")
            post_maintenance_command(
                opener,
                base_url,
                "goNewInstallation",
                body,
                timeout,
                data={"restore": "false"},
            )
            completed_commands.add("goNewInstallation")
        elif (
            stage == "DB_SETTINGS_SCREEN" and "goNewDatabase" not in completed_commands
        ):
            if database_mode == "external":
                raise RuntimeError(
                    "TeamCity reached the database selection screen even though "
                    "an external database was required. Check database.properties, "
                    "TEAMCITY_DB_* variables, PostgreSQL health, and the JDBC driver."
                )
            print("Auto setup: selecting internal TeamCity database.")
            post_maintenance_command(
                opener,
                base_url,
                "goNewDatabase",
                body,
                timeout,
                data={"dbType": "HSQLDB2"},
            )
            completed_commands.add("goNewDatabase")
        elif (
            stage == "LICENSE_AGREEMENT_SCREEN"
            and "acceptLicenseAgreement" not in completed_commands
        ):
            print("Auto setup: accepting TeamCity license agreement.")
            post_maintenance_command(
                opener,
                base_url,
                "acceptLicenseAgreement",
                body,
                timeout,
            )
            completed_commands.add("acceptLicenseAgreement")
        else:
            ready_status, ready_body = request_with_session(opener, url, timeout)
            if (
                is_admin_setup_page(ready_body)
                and "createInitialAdministrator" not in completed_commands
            ):
                print("Auto setup: creating the initial TeamCity administrator.")
                create_initial_administrator(
                    opener,
                    base_url,
                    timeout,
                    admin_username,
                    admin_password,
                )
                completed_commands.add("createInitialAdministrator")
                time.sleep(interval)
                continue

            readiness = classify_teamcity_response(ready_status, ready_body)
            if readiness.opened and readiness.code != "FIRST_START_REQUIRED":
                print("Auto setup: TeamCity first-start setup is complete.")
                return True

        time.sleep(interval)

    print(
        "Auto setup: timed out while completing TeamCity first-start setup.",
        file=sys.stderr,
    )
    return False


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
    status = (
        "no HTTP response" if readiness.status is None else f"HTTP {readiness.status}"
    )
    return f"{readiness.code}: {readiness.message} Endpoint: {url}. Status: {status}."


def append_github_step_summary(readiness: TeamCityReadiness, url: str) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    status = (
        "no HTTP response" if readiness.status is None else f"HTTP {readiness.status}"
    )
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
    parser.add_argument(
        "--auto-setup",
        action="store_true",
        help="Complete fresh TeamCity first-start setup before reporting readiness.",
    )
    parser.add_argument(
        "--access-token-output",
        type=Path,
        help="Secure file where a newly created CI administrator token is written.",
    )
    parser.add_argument(
        "--access-token-name",
        help="Name of the CI administrator access token created after setup.",
    )
    parser.add_argument(
        "--database-mode",
        choices=("internal", "external"),
        default="internal",
        help=(
            "Database expected during first start. External mode refuses to "
            "silently fall back to the internal HSQLDB."
        ),
    )
    args = parser.parse_args()

    admin_username = os.getenv("TEAMCITY_USERNAME", "ci-initial-admin").strip()
    admin_password = os.getenv("TEAMCITY_PASSWORD") or secrets.token_urlsafe(24)
    access_token_name = args.access_token_name or (
        "ci-autotests-"
        f"{os.getenv('GITHUB_RUN_ID', 'local')}-"
        f"{os.getenv('GITHUB_RUN_ATTEMPT', '1')}"
    )
    deadline = time.monotonic() + args.timeout
    last_status: int | None = None
    last_body = ""

    while time.monotonic() < deadline:
        status, body = request_url(args.url, args.request_timeout)
        last_status = status
        last_body = body
        readiness = classify_teamcity_response(status, body)
        message = format_readiness_message(readiness, args.url)

        if args.auto_setup and is_admin_setup_page(body):
            print(
                "TeamCity requires an initial administrator. Running automatic setup."
            )
            if complete_first_start_setup(
                args.url,
                args.request_timeout,
                args.interval,
                args.timeout,
                admin_username,
                admin_password,
                args.database_mode,
            ):
                time.sleep(args.interval)
                continue
            append_github_step_summary(readiness, args.url)
            return 1

        if readiness.code == "FIRST_START_REQUIRED" and args.auto_setup:
            print(f"{message} Running automatic first-start setup.")
            if complete_first_start_setup(
                args.url,
                args.request_timeout,
                args.interval,
                args.timeout,
                admin_username,
                admin_password,
                args.database_mode,
            ):
                time.sleep(args.interval)
                continue
            append_github_step_summary(readiness, args.url)
            return 1

        if readiness.opened:
            if args.access_token_output:
                try:
                    access_token = create_ci_access_token(
                        get_base_url(args.url),
                        admin_username,
                        admin_password,
                        access_token_name,
                        args.request_timeout,
                    )
                    write_secret_file(args.access_token_output, access_token)
                except (requests.RequestException, RuntimeError, OSError) as error:
                    print(
                        "TeamCity REST API is not ready for CI access token "
                        f"creation yet: {error}"
                    )
                    time.sleep(args.interval)
                    continue
                print("TeamCity CI administrator access token was created securely.")
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
