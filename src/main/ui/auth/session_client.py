from urllib.parse import quote

import requests
from playwright.sync_api import BrowserContext

from src.main.api.configs.config import Config
from src.main.api.constants.teamcity import TeamCityLocator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.ui.configuration import teamcity_ui_base_url


class UiAuthClient:
    """Exchange user credentials for a TeamCity browser session cookie."""

    session_cookie_name = "TCSESSIONID"

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or teamcity_ui_base_url()).rstrip("/")
        self.timeout = int(Config.get("TEAMCITY_REQUEST_TIMEOUT", "20"))

    def authenticate(
        self, context: BrowserContext, user_request: CreateUserRequest
    ) -> None:
        response = requests.get(
            self._user_url(user_request.username),
            headers=RequestSpecs.auth_as_user(
                user_request.username, user_request.password
            ),
            timeout=self.timeout,
        )
        assert response.status_code == 200, (
            "Failed to create a TeamCity UI session for "
            f"{user_request.username!r}. Status: {response.status_code}. "
            f"Response: {response.text}"
        )

        session_id = response.cookies.get(self.session_cookie_name)
        assert session_id, (
            "TeamCity authenticated the user but did not return "
            f"the {self.session_cookie_name} cookie"
        )
        context.add_cookies(
            [
                {
                    "name": self.session_cookie_name,
                    "value": session_id,
                    "url": self.base_url,
                }
            ]
        )

    def _user_url(self, username: str) -> str:
        api_base_path = str(Config.get("apiBasePath", "/app/rest")).rstrip("/")
        encoded_username = quote(username, safe="")
        username_locator = TeamCityLocator.USERNAME.build(encoded_username)
        return f"{self.base_url}{api_base_path}/users/{username_locator}"
