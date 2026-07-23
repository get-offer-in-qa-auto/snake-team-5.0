import allure
from playwright.sync_api import Locator

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.base_page import BasePage
from src.main.ui.pages.projects_page import ProjectsPage


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
