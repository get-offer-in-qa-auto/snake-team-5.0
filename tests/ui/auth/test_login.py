import pytest
from playwright.sync_api import Page

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.regression
def test_admin_can_login(page: Page, admin_user_request: CreateUserRequest):
    LoginPage(page).open().login_success(admin_user_request).should_be_authenticated()
