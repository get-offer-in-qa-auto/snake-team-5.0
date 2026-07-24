from __future__ import annotations

from typing import TYPE_CHECKING

import allure
from playwright.sync_api import Locator, expect

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.base_page import BasePage
from src.main.ui.pages.user_page import UserPage

if TYPE_CHECKING:
    from src.main.ui.pages.create_user_page import CreateUserPage


class UsersPage(BasePage):
    path = "/admin/admin.html?item=users"

    @property
    def create_user_link(self) -> Locator:
        return self.page.get_by_role("link", name="Create user account", exact=True)

    def user_link(self, user_request: CreateUserRequest) -> Locator:
        return self.page.get_by_role(
            "link", name=user_request.username, exact=True
        )

    def user_row(self, user_request: CreateUserRequest) -> Locator:
        return self.page.locator("table.userList tr").filter(
            has=self.user_link(user_request)
        )

    @allure.step("Open user creation page")
    def open_create_user(self) -> CreateUserPage:
        from src.main.ui.pages.create_user_page import CreateUserPage

        self.create_user_link.click()
        return CreateUserPage(self.page)

    @allure.step("Open user")
    def open_user(self, user_request: CreateUserRequest) -> UserPage:
        self.user_link(user_request).click()
        return UserPage(self.page)

    @allure.step("Verify user is displayed")
    def should_contain_user(self, user_request: CreateUserRequest) -> UsersPage:
        expect(self.user_link(user_request)).to_be_visible()
        expect(self.user_row(user_request)).to_contain_text(user_request.name)
        return self

    @allure.step("Verify user is not displayed")
    def should_not_contain_user(
        self, user_request: CreateUserRequest
    ) -> UsersPage:
        expect(self.user_row(user_request)).to_have_count(0)
        return self
