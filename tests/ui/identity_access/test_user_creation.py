import pytest
from playwright.sync_api import Page

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.users_page import UsersPage


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.admin_session
@pytest.mark.entity_will_be_created("user_request")
def test_admin_can_create_user(page: Page, user_request: CreateUserRequest):
    (
            UsersPage(page)
            .open()
            .open_create_user()
            .create_user(user_request)
            .should_contain_user(user_request)
        )
