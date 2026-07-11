import pytest

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.user_token import CreateUserTokenRequest


@pytest.fixture(scope="function")
def user_token_request_factory():
    def create_user_token_request(
        name: str | None = None
    ) -> CreateUserTokenRequest:
        generated_token = RandomModelGenerator.generate(CreateUserTokenRequest)
        return CreateUserTokenRequest(
            name=name if name is not None else generated_token.name
        )

    return create_user_token_request


@pytest.fixture(scope="function")
def user_token_request(user_token_request_factory) -> CreateUserTokenRequest:
    return user_token_request_factory()
