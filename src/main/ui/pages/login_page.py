import allure
from playwright.sync_api import Locator

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.base_page import BasePage
from src.main.ui.pages.projects_page import ProjectsPage


class LoginPage(BasePage):
    path = "/login.html"
    USERNAME_INPUT_NAME = "Username"
    PASSWORD_INPUT_NAME = "Password"
    LOGIN_BUTTON_NAME = "Log in"

    @property
    def username_input(self) -> Locator:
        return self.page.get_by_role(
            "textbox",
            name=self.USERNAME_INPUT_NAME,
            exact=True,
        )

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_role(
            "textbox",
            name=self.PASSWORD_INPUT_NAME,
            exact=True,
        )

    @property
    def login_button(self) -> Locator:
        return self.page.get_by_role(
            "button",
            name=self.LOGIN_BUTTON_NAME,
            exact=True,
        )

    @allure.step("Log in")
    def login(self, user_request: CreateUserRequest) -> "LoginPage":
        self.username_input.fill(user_request.username)
        self.password_input.fill(user_request.password)
        self.login_button.click()
        return self

    @allure.step("Log in successfully")
    def login_success(self, user_request: CreateUserRequest) -> ProjectsPage:
        self.login(user_request)
        return ProjectsPage(self.page)
