import base64
import os
from typing import Dict

import requests

from src.main.api.configs.config import Config


class RequestSpecs:
    _LOCAL_SUPER_USER_TOKEN = "autotestlocalsuperusertoken"
    _PLACEHOLDER_AUTH_HEADER = "<BASIC_TOKEN>"
    _csrf_tokens: dict[str, str] = {}

    @staticmethod
    def _server_url() -> str:
        return (
            os.getenv("TEAMCITY_URL")
            or os.getenv("TEAMCITY_BASE_URL")
            or Config.get("server")
        ).rstrip("/")

    @staticmethod
    def _base_url() -> str:
        return f"{RequestSpecs._server_url()}{Config.get('apiBasePath')}"

    @staticmethod
    def default_req_headers() -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @staticmethod
    def unauth_spec() -> Dict[str, str]:
        return RequestSpecs.default_req_headers()

    @staticmethod
    def _basic_auth_header(username: str, password: str) -> str:
        raw_token = f"{username}:{password}".encode("utf-8")
        return f"Basic {base64.b64encode(raw_token).decode('ascii')}"

    @staticmethod
    def _admin_auth_headers() -> list[str]:
        headers = []
        configured_header = Config.get("ADMIN_AUTH_HEADER")
        if configured_header and configured_header != RequestSpecs._PLACEHOLDER_AUTH_HEADER:
            headers.append(configured_header)

        username = os.getenv("TEAMCITY_USERNAME")
        password = os.getenv("TEAMCITY_PASSWORD")
        if username and password:
            headers.append(RequestSpecs._basic_auth_header(username, password))

        admin_username = Config.get("ADMIN_USERNAME")
        admin_password = Config.get("ADMIN_PASSWORD")
        if admin_username and admin_password:
            headers.append(RequestSpecs._basic_auth_header(admin_username, admin_password))

        super_user_token = Config.get(
            "TEAMCITY_SUPER_USER_TOKEN",
            RequestSpecs._LOCAL_SUPER_USER_TOKEN,
        )
        if super_user_token:
            headers.append(RequestSpecs._basic_auth_header("", super_user_token))

        return list(dict.fromkeys(headers))

    @staticmethod
    def _csrf_token(auth_header: str) -> str:
        cached_token = RequestSpecs._csrf_tokens.get(auth_header)
        if cached_token:
            return cached_token

        timeout = int(Config.get("TEAMCITY_REQUEST_TIMEOUT", "20"))
        response = requests.get(
            f"{RequestSpecs._server_url()}/authenticationTest.html?csrf",
            headers={
                "Authorization": auth_header,
                "Accept": "text/plain",
            },
            timeout=timeout,
        )
        assert response.status_code == 200, (
            f"Failed to get TeamCity CSRF token. "
            f"Status: {response.status_code}. Response: {response.text}"
        )

        token = response.text.strip()
        assert token, "TeamCity returned an empty CSRF token"
        RequestSpecs._csrf_tokens[auth_header] = token
        return token

    @staticmethod
    def admin_auth_spec(csrf: bool = True):
        errors = []

        for auth_header in RequestSpecs._admin_auth_headers():
            headers = RequestSpecs.default_req_headers()
            headers["Authorization"] = auth_header

            if not csrf or auth_header.lower().startswith("bearer "):
                return headers

            try:
                headers["X-TC-CSRF-Token"] = RequestSpecs._csrf_token(auth_header)
                return headers
            except (AssertionError, requests.RequestException) as error:
                errors.append(str(error))

        raise AssertionError(
            "Could not build TeamCity admin auth headers. "
            f"Tried {len(RequestSpecs._admin_auth_headers())} auth candidate(s). "
            f"Errors: {errors}"
        )
