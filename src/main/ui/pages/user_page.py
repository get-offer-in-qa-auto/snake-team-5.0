from __future__ import annotations

from typing import TYPE_CHECKING

import allure
from playwright.sync_api import Locator, expect

from src.main.ui.pages.access_tokens_page import AccessTokensPage
from src.main.ui.pages.base_page import BasePage

if TYPE_CHECKING:
    from src.main.ui.pages.users_page import UsersPage


class UserPage(BasePage):
    path = "/admin/editUser.html"
    ACCESS_TOKENS_LINK_TEXT = "Access Tokens"
    DELETE_USER_LINK_NAME = "Delete user account"

    @property
    def access_tokens_link(self) -> Locator:
        return self.page.get_by_text(self.ACCESS_TOKENS_LINK_TEXT, exact=True)

    @property
    def delete_button(self) -> Locator:
        return self.page.get_by_role(
            "link", name=self.DELETE_USER_LINK_NAME, exact=True
        )

    @allure.step("Open user access tokens")
    def open_access_tokens(self) -> AccessTokensPage:
        self.access_tokens_link.click(force=True)
        access_tokens_page = AccessTokensPage(self.page)
        expect(access_tokens_page.create_token_link).to_be_visible()
        return access_tokens_page

    @allure.step("Delete user")
    def delete_user(self) -> UsersPage:
        from src.main.ui.pages.users_page import UsersPage

        self.page.once("dialog", lambda dialog: dialog.accept())
        self.delete_button.click(force=True)
        return UsersPage(self.page)
