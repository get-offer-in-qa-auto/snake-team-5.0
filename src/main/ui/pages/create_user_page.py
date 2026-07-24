from __future__ import annotations

import allure
from playwright.sync_api import Locator

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.base_page import BasePage
from src.main.ui.pages.users_page import UsersPage


class CreateUserPage(BasePage):
    path = "/admin/createUser.html?init=1"

    @property
    def username_input(self) -> Locator:
        return self.page.locator("#input_teamcityUsername")

    @property
    def name_input(self) -> Locator:
        return self.page.locator("#name")

    @property
    def password_input(self) -> Locator:
        return self.page.locator("#password1")

    @property
    def confirm_password_input(self) -> Locator:
        return self.page.locator("#retypedPassword")

    @property
    def create_button(self) -> Locator:
        return self.page.get_by_role("button", name="Create User", exact=True)

    @allure.step("Create user")
    def create_user(self, user_request: CreateUserRequest) -> UsersPage:
        self.username_input.fill(user_request.username)
        self.name_input.fill(user_request.name)
        self.password_input.fill(user_request.password)
        self.confirm_password_input.fill(user_request.password)
        self.create_button.click(force=True)
        return UsersPage(self.page)
