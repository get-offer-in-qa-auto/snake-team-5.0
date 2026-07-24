from __future__ import annotations

import allure
from playwright.sync_api import Locator, expect

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.base_page import BasePage
from src.main.ui.pages.users_page import UsersPage


class CreateUserPage(BasePage):
    path = "/admin/createUser.html?init=1"
    USERNAME_INPUT_SELECTOR = "#input_teamcityUsername"
    NAME_INPUT_SELECTOR = "#name"
    PASSWORD_INPUT_SELECTOR = "#password1"
    CONFIRM_PASSWORD_INPUT_SELECTOR = "#retypedPassword"
    CREATE_BUTTON_NAME = "Create User"
    USERNAME_EMPTY_ERROR_SELECTOR = '[data-error="Username is empty"]'
    PASSWORD_EMPTY_ERROR_SELECTOR = '[data-error="Password is empty"]'

    @property
    def username_input(self) -> Locator:
        return self.page.locator(self.USERNAME_INPUT_SELECTOR)

    @property
    def name_input(self) -> Locator:
        return self.page.locator(self.NAME_INPUT_SELECTOR)

    @property
    def password_input(self) -> Locator:
        return self.page.locator(self.PASSWORD_INPUT_SELECTOR)

    @property
    def confirm_password_input(self) -> Locator:
        return self.page.locator(self.CONFIRM_PASSWORD_INPUT_SELECTOR)

    @property
    def create_button(self) -> Locator:
        return self.page.get_by_role("button", name=self.CREATE_BUTTON_NAME, exact=True)

    @allure.step("Submit creation form")
    def submit_empty_form(self) -> CreateUserPage:
        self.create_button.click(force=True)
        return self

    @allure.step("Verify required user fields validation errors")
    def should_show_required_fields_errors(self) -> CreateUserPage:
        expect(self.page.locator(self.USERNAME_EMPTY_ERROR_SELECTOR)).to_be_visible()
        expect(self.page.locator(self.PASSWORD_EMPTY_ERROR_SELECTOR)).to_be_visible()
        return self

    @allure.step("Create user")
    def create_user(self, user_request: CreateUserRequest) -> UsersPage:
        self.username_input.fill(user_request.username)
        self.name_input.fill(user_request.name)
        self.password_input.fill(user_request.password)
        self.confirm_password_input.fill(user_request.password)
        self.create_button.click(force=True)
        return UsersPage(self.page)
