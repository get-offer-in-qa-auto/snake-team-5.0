from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.api.models.build_configuration_response import (
    BuildConfigurationResponse,
)
from src.main.api.models.user_token import (
    CreateUserTokenRequest,
    UserTokenResponse,
    UserTokensResponse,
)
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import (
    ValidatedCrudRequester,
)
from src.main.api.requests.steps.base_steps import BaseSteps
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


class UserSteps(BaseSteps):
    def create_user_token(
        self,
        user_request: CreateUserRequest,
        token_request: CreateUserTokenRequest
    ) -> UserTokenResponse:
        token_response: UserTokenResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password,
                csrf=True
            ),
            Endpoint.CREATE_USER_TOKEN,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(
            token_request,
            path=f"username:{user_request.username}/tokens"
        )
        token_response = token_response.model_copy(
            update={
                "username": user_request.username,
                "password": user_request.password,
            }
        )

        self.created_objects.append(token_response)
        return token_response

    def get_user_tokens(
        self,
        user_request: CreateUserRequest
    ) -> UserTokensResponse:
        return ValidatedCrudRequester(
            RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password
            ),
            Endpoint.GET_USER_TOKENS,
            ResponseSpecs.request_returns_ok()
        ).get(f"username:{user_request.username}/tokens")

    def delete_user_token(
        self,
        username: str,
        password: str,
        token_name: str
    ):
        CrudRequester(
            RequestSpecs.auth_as_user(username, password, csrf=True),
            Endpoint.DELETE_USER_TOKEN,
            ResponseSpecs.entity_was_deleted()
        ).delete(f"username:{username}/tokens/{token_name}")

    def get_user_with_token(
        self,
        username: str,
        token: str
    ) -> CreateUserResponse:
        return ValidatedCrudRequester(
            RequestSpecs.auth_with_token(token),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_ok()
        ).get(f"username:{username}")

    def check_request_without_token(self, username: str):
        CrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_unauthorized()
        ).get(f"username:{username}")

    def check_token_cannot_authenticate(self, username: str, token: str):
        CrudRequester(
            RequestSpecs.auth_with_token(token),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_unauthorized_status()
        ).get(f"username:{username}")

    def create_project(
        self,
        user_request: CreateUserRequest,
        project_request: CreateProjectRequest
    ) -> ProjectResponse:
        project_response: ProjectResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password,
                csrf=True
            ),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(project_request)

        self.created_objects.append(project_response)
        return project_response

    def create_project_forbidden(
        self,
        user_request: CreateUserRequest,
        project_request: CreateProjectRequest
    ):
        CrudRequester(
            RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password,
                csrf=True
            ),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.request_returns_forbidden()
        ).post(project_request)

    def create_build_configuration(
        self,
        user_request: CreateUserRequest,
        project_id: str,
        configuration_request: CreateBuildConfigurationRequest
    ) -> BuildConfigurationResponse:
        configuration_response: BuildConfigurationResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password,
                csrf=True
            ),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(
            configuration_request,
            path=f"id:{project_id}/buildTypes"
        )

        self.created_objects.append(configuration_response)
        return configuration_response

    def create_build_configuration_forbidden(
        self,
        user_request: CreateUserRequest,
        project_id: str,
        configuration_request: CreateBuildConfigurationRequest
    ):
        CrudRequester(
            RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password,
                csrf=True
            ),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_forbidden()
        ).post(
            configuration_request,
            path=f"id:{project_id}/buildTypes"
        )
