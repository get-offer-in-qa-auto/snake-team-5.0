from __future__ import annotations

import re

import allure
from playwright.sync_api import Locator, expect

from src.main.api.models.user_token import CreateUserTokenRequest
from src.main.ui.pages.base_page import BasePage


class AccessTokensPage(BasePage):
    path = "/admin/editUser.html?item=accessTokens"

    @property
    def create_token_link(self) -> Locator:
        return self.page.locator("#createTokenButton")

    @property
    def token_name_input(self) -> Locator:
        return self.page.locator("#input_accessTokenName")

    @property
    def create_button(self) -> Locator:
        return self.page.locator("#editAccessTokenForm").get_by_role(
            "button", name="Create", exact=True
        )

    @property
    def token_dialog(self) -> Locator:
        return self.page.locator("#editAccessTokenFormDialog")

    @property
    def created_token_notice(self) -> Locator:
        return self.page.locator("#tokenCreatedNotice")

    @property
    def created_token_value(self) -> Locator:
        return self.page.locator("#createdToken")

    @property
    def close_dialog_link(self) -> Locator:
        return self.page.locator("#editAccessTokenForm a.closeWindowLink")

    def token_row(self, token_request: CreateUserTokenRequest) -> Locator:
        return self.page.locator("#userAccessTokenTable tr").filter(
            has_text=token_request.name
        )

    @allure.step("Create access token")
    def create_token(
        self, token_request: CreateUserTokenRequest
    ) -> AccessTokensPage:
        self.create_token_link.click(force=True)
        self.token_dialog.evaluate("dialog => dialog.style.display = 'block'")
        self.token_name_input.fill(token_request.name)
        self.create_button.click(force=True)
        return self

    @allure.step("Verify access token was created")
    def should_show_created_token(self) -> AccessTokensPage:
        expect(self.created_token_notice).to_be_visible()
        expect(self.created_token_value).to_contain_text(re.compile(r"\S+"))
        return self

    @allure.step("Close created access token dialog")
    def close_created_token_dialog(self) -> AccessTokensPage:
        self.close_dialog_link.click(force=True)
        return self

    @allure.step("Verify access token is displayed in the table")
    def should_contain_token(
        self, token_request: CreateUserTokenRequest
    ) -> AccessTokensPage:
        expect(self.token_row(token_request)).to_be_visible()
        return self
