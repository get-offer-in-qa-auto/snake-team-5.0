import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.users_page import UsersPage


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.admin_session
@pytest.mark.entity_will_be_created("user_request")
def test_admin_can_create_user(
    page: Page,
    api_manager: ApiManager,
    user_request: CreateUserRequest,
):
    (
        UsersPage(page)
        .open()
        .open_create_user()
        .create_user(user_request)
        .should_contain_user(user_request)
    )

    stored_user = api_manager.admin_steps.get_user(user_request.username)
    api_manager.admin_steps.verify_response_matches(user_request, stored_user)


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.admin_session
def test_admin_cannot_create_user_with_empty_required_fields(page: Page):
    (
        UsersPage(page)
        .open()
        .open_create_user()
        .submit_empty_form()
        .should_show_required_fields_errors()
    )


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.admin_session
def test_admin_can_delete_user(
    page: Page,
    api_manager: ApiManager,
    user_to_delete: CreateUserRequest,
):
    (
        UsersPage(page)
        .open()
        .open_user(user_to_delete)
        .delete_user()
        .should_not_contain_user(user_to_delete)
    )

    api_manager.admin_steps.check_user_does_not_exist(user_to_delete.username)
