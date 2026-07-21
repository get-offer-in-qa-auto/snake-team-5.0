from playwright.sync_api import Locator, expect

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.components.teamcity_header import TeamCityHeader
from src.main.ui.pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login.html"

    @property
    def username_input(self) -> Locator:
        return self.page.get_by_role("textbox", name="Username", exact=True)

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_role("textbox", name="Password", exact=True)

    @property
    def login_button(self) -> Locator:
        return self.page.get_by_role("button", name="Log in", exact=True)

    def login(self, user_request: CreateUserRequest) -> "LoginPage":
        self.username_input.fill(user_request.username)
        self.password_input.fill(user_request.password)
        self.login_button.click()
        TeamCityHeader(self.page).root.wait_for(state="visible", timeout=15_000)
        return self

    def should_be_authenticated(self) -> "LoginPage":
        expect(self.login_button).not_to_be_visible()
        TeamCityHeader(self.page).should_be_visible()
        return self
