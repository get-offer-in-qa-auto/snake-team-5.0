import pytest
from playwright.sync_api import Page

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.user_token import CreateUserTokenRequest
from src.main.ui.pages.users_page import UsersPage


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.admin_session
def test_admin_can_create_access_token_for_user(
    page: Page,
    user: CreateUserRequest,
    user_token_request: CreateUserTokenRequest,
):
    (
        UsersPage(page)
        .open()
        .open_user(user)
        .open_access_tokens()
        .create_token(user_token_request)
        .should_show_created_token()
        .close_created_token_dialog()
        .should_contain_token(user_token_request)
    )
