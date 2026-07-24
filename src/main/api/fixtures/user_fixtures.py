from collections.abc import Iterator

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.classes.session_storage import SessionStorage
from src.main.api.configs.config import Config
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.fixture(scope="function")
def user_request_factory():
    def create_user_request(
        username: str | None = None,
        password: str | None = None,
        name: str | None = None,
    ) -> CreateUserRequest:
        generated_user = RandomModelGenerator.generate(CreateUserRequest)
        return CreateUserRequest(
            username=(username if username is not None else generated_user.username),
            password=(password if password is not None else generated_user.password),
            name=name if name is not None else generated_user.name,
        )

    return create_user_request


@pytest.fixture(scope="function")
def user_request(user_request_factory):
    return user_request_factory()


@pytest.fixture(scope="function")
def user(api_manager: ApiManager, user_request: CreateUserRequest) -> CreateUserRequest:
    api_manager.admin_steps.create_user(user_request)
    return user_request


@pytest.fixture(scope="function")
def user_to_delete(
    api_manager: ApiManager,
    user: CreateUserRequest,
) -> Iterator[CreateUserRequest]:
    yield user
    api_manager.admin_steps.delete_user_if_exists(user.username)


@pytest.fixture(scope="function")
def user_factory(api_manager: ApiManager, user_request_factory):
    def create_user() -> CreateUserRequest:
        user_data = user_request_factory()
        api_manager.admin_steps.create_user(user_data)
        SessionStorage.add_users([user_data])
        return user_data

    yield create_user


@pytest.fixture
def admin_user_request():
    username = (
        Config.get("TEAMCITY_UI_USERNAME")
        or Config.get("TEAMCITY_USERNAME")
        or Config.get("ADMIN_USERNAME")
    )
    password = (
        Config.get("TEAMCITY_UI_PASSWORD")
        or Config.get("TEAMCITY_PASSWORD")
        or Config.get("ADMIN_PASSWORD")
    )
    if not username or not password:
        raise ValueError("TeamCity UI administrator credentials are not configured")
    return CreateUserRequest(
        username=str(username),
        password=str(password),
        name=Config.get("ADMIN_NAME", "TeamCity Administrator"),
    )
