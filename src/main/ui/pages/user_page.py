from __future__ import annotations

import allure
from playwright.sync_api import Locator, expect

from src.main.ui.pages.access_tokens_page import AccessTokensPage
from src.main.ui.pages.base_page import BasePage


class UserPage(BasePage):
    path = "/admin/editUser.html"

    @property
    def access_tokens_link(self) -> Locator:
        return self.page.get_by_text("Access Tokens", exact=True)

    @allure.step("Open user access tokens")
    def open_access_tokens(self) -> AccessTokensPage:
        self.access_tokens_link.click(force=True)
        access_tokens_page = AccessTokensPage(self.page)
        expect(access_tokens_page.create_token_link).to_be_visible()
        return access_tokens_page
