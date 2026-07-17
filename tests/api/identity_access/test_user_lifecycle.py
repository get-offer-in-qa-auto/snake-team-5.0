import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.response_specs import ResponseError


@allure.title("Create user")
@allure.tag("api", "smoke", "regression", "user")
@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
def test_create_user(api_manager: ApiManager, user_request: CreateUserRequest):
    user = api_manager.admin_steps.create_user(user_request)
    stored_user = api_manager.admin_steps.get_user(user.username)

    api_manager.admin_steps.verify_user_created(user_request, user, stored_user)


@allure.title("Created user is persisted in database")
@allure.tag("api", "regression", "user", "database")
@pytest.mark.api
@pytest.mark.regression
def test_created_user_is_persisted_in_database(
    api_manager: ApiManager, user_request: CreateUserRequest
):
    user = api_manager.admin_steps.create_user(user_request)

    api_manager.database_steps.verify_user_persisted(user)


@allure.title("User cannot be created with existing username")
@allure.tag("api", "regression", "user", "negative")
@pytest.mark.api
@pytest.mark.regression
def test_create_user_with_existing_username(
    api_manager: ApiManager, user_request: CreateUserRequest, user_request_factory
):
    api_manager.admin_steps.create_user(user_request)
    duplicate_request = user_request_factory(username=user_request.username)

    api_manager.admin_steps.create_user_bad_request(
        duplicate_request, ResponseError.USERNAME_ALREADY_EXISTS
    )

    stored_user = api_manager.admin_steps.get_user(user_request.username)
    api_manager.admin_steps.verify_response_matches(user_request, stored_user)


@allure.title("User cannot be created without authorization")
@allure.tag("api", "regression", "user", "authorization", "negative")
@pytest.mark.api
@pytest.mark.regression
def test_create_user_without_authorization(
    api_manager: ApiManager, user_request: CreateUserRequest
):
    api_manager.admin_steps.create_user_without_authorization(user_request)

    api_manager.admin_steps.check_user_does_not_exist(user_request.username)
    api_manager.database_steps.verify_user_not_created(user_request.username)


@allure.title("Delete user")
@allure.tag("api", "regression", "user", "database")
@pytest.mark.api
@pytest.mark.regression
def test_delete_user(
    api_manager: ApiManager, user_request: CreateUserRequest, created_objects: list
):
    user = api_manager.admin_steps.create_user(user_request)

    api_manager.admin_steps.delete_user(user.id)
    created_objects.remove(user)

    api_manager.admin_steps.check_user_does_not_exist(user.username)
    api_manager.database_steps.verify_user_deleted(user.username)


@allure.title("Deleted user cannot authenticate")
@allure.tag("api", "regression", "user", "authorization")
@pytest.mark.api
@pytest.mark.regression
def test_deleted_user_cannot_authenticate(
    api_manager: ApiManager, user_request: CreateUserRequest, created_objects: list
):
    user = api_manager.admin_steps.create_user(user_request)
    authenticated_user = api_manager.admin_steps.get_user_as(user_request)
    api_manager.user_steps.verify_response_matches(user_request, authenticated_user)

    api_manager.admin_steps.delete_user(user.id)
    created_objects.remove(user)

    api_manager.admin_steps.check_user_cannot_authenticate(user_request)
    api_manager.admin_steps.check_user_does_not_exist(user.username)
