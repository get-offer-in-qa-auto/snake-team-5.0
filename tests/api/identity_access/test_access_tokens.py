import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.user_token import CreateUserTokenRequest
from src.main.reporting.allure.tags import AllureTag, api_regression_tags


@allure.title("Create user token")
@api_regression_tags(AllureTag.TOKEN, AllureTag.USER, smoke=True)
@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
def test_create_user_token(
    api_manager: ApiManager,
    user_request: CreateUserRequest,
    user_token_request: CreateUserTokenRequest,
):
    api_manager.admin_steps.create_user(user_request)

    token = api_manager.user_steps.create_user_token(user_request, user_token_request)
    api_manager.user_steps.verify_user_token_created(
        user_request, user_token_request, token
    )


@allure.title("Request with valid token is authorized")
@api_regression_tags(AllureTag.TOKEN, AllureTag.AUTHORIZATION)
@pytest.mark.api
@pytest.mark.regression
def test_request_with_valid_token(
    api_manager: ApiManager,
    user_request: CreateUserRequest,
    user_token_request: CreateUserTokenRequest,
):
    api_manager.admin_steps.create_user(user_request)
    token = api_manager.user_steps.create_user_token(user_request, user_token_request)

    authenticated_user = api_manager.user_steps.get_user_with_token(
        user_request.username, token.value
    )

    api_manager.user_steps.verify_response_matches(user_request, authenticated_user)


@allure.title("Request without token is rejected")
@api_regression_tags(AllureTag.TOKEN, AllureTag.AUTHORIZATION, AllureTag.NEGATIVE)
@pytest.mark.api
@pytest.mark.regression
def test_request_without_token(
    api_manager: ApiManager, user_request: CreateUserRequest
):
    api_manager.admin_steps.create_user(user_request)

    api_manager.user_steps.check_request_without_token(user_request.username)


@allure.title("Request with invalid token is rejected")
@api_regression_tags(AllureTag.TOKEN, AllureTag.AUTHORIZATION, AllureTag.NEGATIVE)
@pytest.mark.api
@pytest.mark.regression
def test_request_with_invalid_token(
    api_manager: ApiManager,
    user_request: CreateUserRequest,
    invalid_access_token: str,
):
    api_manager.admin_steps.create_user(user_request)

    api_manager.user_steps.check_token_cannot_authenticate(
        user_request.username, invalid_access_token
    )


@allure.title("Request with revoked token is rejected")
@api_regression_tags(AllureTag.TOKEN, AllureTag.AUTHORIZATION, AllureTag.NEGATIVE)
@pytest.mark.api
@pytest.mark.regression
def test_request_with_revoked_token(
    api_manager: ApiManager,
    user_request: CreateUserRequest,
    user_token_request: CreateUserTokenRequest,
):
    api_manager.admin_steps.create_user(user_request)
    token = api_manager.user_steps.create_user_token(user_request, user_token_request)
    api_manager.user_steps.get_user_with_token(user_request.username, token.value)

    api_manager.user_steps.delete_user_token(
        user_request.username, user_request.password, token.name
    )

    api_manager.user_steps.check_token_cannot_authenticate(
        user_request.username, token.value
    )


@allure.title("Deleting user revokes its tokens")
@api_regression_tags(AllureTag.TOKEN, AllureTag.USER)
@pytest.mark.api
@pytest.mark.regression
def test_delete_user_revokes_its_tokens(
    api_manager: ApiManager,
    user_request: CreateUserRequest,
    user_token_request: CreateUserTokenRequest,
):
    user = api_manager.admin_steps.create_user(user_request)
    token = api_manager.user_steps.create_user_token(user_request, user_token_request)
    api_manager.user_steps.get_user_with_token(user_request.username, token.value)

    api_manager.admin_steps.delete_user(user.id)

    api_manager.user_steps.check_token_cannot_authenticate(
        user_request.username, token.value
    )
