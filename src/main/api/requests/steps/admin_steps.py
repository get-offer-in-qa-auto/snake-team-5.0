from typing import List
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.create_build_configuration_request import CreateBuildConfigurationRequest
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import ProjectResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.steps.base_steps import BaseSteps
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.role_assignment import (
    RoleAssignmentRequest,
    RoleAssignmentResponse,
    RoleAssignmentsResponse,
)
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseError, ResponseSpecs


class AdminSteps(BaseSteps):
    def create_user(self, user_request: CreateUserRequest):
        user_response: CreateUserResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_USER,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(user_request)

        self.created_objects.append(user_response)
        return user_response

    def create_user_bad_request(
        self,
        user_request: CreateUserRequest,
        error_text: ResponseError
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_USER,
            ResponseSpecs.request_returns_bad_request_with_text(error_text)
        ).post(user_request)

    def create_user_without_authorization(
        self,
        user_request: CreateUserRequest
    ):
        CrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.CREATE_USER,
            ResponseSpecs.request_returns_unauthorized()
        ).post(user_request, allow_redirects=False)

    def get_user(self, username: str) -> CreateUserResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_ok()
        ).get(self._user_locator(username))

    def get_user_as(
        self,
        user_request: CreateUserRequest
    ) -> CreateUserResponse:
        return ValidatedCrudRequester(
            RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password
            ),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_ok()
        ).get(self._user_locator(user_request.username))

    def check_user_does_not_exist(self, username: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_not_found_with_text(
                ResponseError.USER_NOT_FOUND
            )
        ).get(self._user_locator(username))

    def check_user_cannot_authenticate(
        self,
        user_request: CreateUserRequest
    ):
        CrudRequester(
            RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password
            ),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_unauthorized_with_text(
                ResponseError.INCORRECT_USERNAME_OR_PASSWORD
            )
        ).get(self._user_locator(user_request.username))

    def delete_user(self, user_id: int | str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_USER,
            ResponseSpecs.entity_was_deleted()
        ).delete(self._user_locator(user_id))

    def assign_user_role(
        self,
        username: str,
        role_id: str,
        scope: str
    ) -> RoleAssignmentResponse:
        role_request = RoleAssignmentRequest(
            roleId=role_id,
            scope=scope
        )
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ASSIGN_USER_ROLE,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(
            role_request,
            path=f"{self._user_locator(username)}/roles"
        )

    def get_user_roles(self, username: str) -> RoleAssignmentsResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_USER_ROLES,
            ResponseSpecs.request_returns_ok()
        ).get(f"{self._user_locator(username)}/roles")

    def get_all_users(self) -> List[CreateUserRequest]:
        response = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_GET_ALL_USERS,
            ResponseSpecs.request_returns_ok()
        ).get()
        return response

    def create_project(self, project_request: CreateProjectRequest) -> ProjectResponse:
        project_response: ProjectResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(project_request)

        self.created_objects.append(project_response)
        return project_response

    def create_project_bad_request(
        self,
        project_request: CreateProjectRequest,
        error_text: ResponseError
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.request_returns_bad_request_with_text(error_text)
        ).post(project_request)

    def create_project_not_found(
        self,
        project_request: CreateProjectRequest,
        error_text: ResponseError
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.request_returns_not_found_with_text(error_text)
        ).post(project_request)

    def create_project_without_authorization(
        self,
        project_request: CreateProjectRequest
    ):
        CrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.request_returns_unauthorized()
        ).post(project_request, allow_redirects=False)

    def get_project(self, project_id: str) -> ProjectResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_PROJECT,
            ResponseSpecs.request_returns_ok()
        ).get(self._project_locator(project_id))

    def check_project_does_not_exist(self, project_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_PROJECT,
            ResponseSpecs.request_returns_not_found_with_text(
                ResponseError.PROJECT_NOT_FOUND
            )
        ).get(self._project_locator(project_id))

    def delete_project(self, project_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_PROJECT,
            ResponseSpecs.entity_was_deleted()
        ).delete(self._project_locator(project_id))

    def create_build_configuration(
        self,
        project_id: str,
        configuration_request: CreateBuildConfigurationRequest
    ) -> BuildConfigurationResponse:
        configuration_response: BuildConfigurationResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(
            configuration_request,
            path=f"{self._project_locator(project_id)}/buildTypes"
        )

        self.created_objects.append(configuration_response)
        return configuration_response

    def create_build_configuration_bad_request(
        self,
        project_id: str,
        configuration_request: CreateBuildConfigurationRequest,
        error_text: ResponseError
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_bad_request_with_text(error_text)
        ).post(
            configuration_request,
            path=f"{self._project_locator(project_id)}/buildTypes"
        )

    def create_build_configuration_not_found(
        self,
        project_id: str,
        configuration_request: CreateBuildConfigurationRequest,
        error_text: ResponseError
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_not_found_with_text(error_text)
        ).post(
            configuration_request,
            path=f"{self._project_locator(project_id)}/buildTypes"
        )

    def create_build_configuration_without_authorization(
        self,
        project_id: str,
        configuration_request: CreateBuildConfigurationRequest
    ):
        CrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_unauthorized()
        ).post(
            configuration_request,
            path=f"{self._project_locator(project_id)}/buildTypes",
            allow_redirects=False
        )

    def get_build_configuration(
        self,
        build_configuration_id: str
    ) -> BuildConfigurationResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_ok()
        ).get(self._build_configuration_locator(build_configuration_id))

    def check_build_configuration_does_not_exist(
        self,
        build_configuration_id: str
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_not_found_with_text(
                ResponseError.BUILD_CONFIGURATION_NOT_FOUND
            )
        ).get(self._build_configuration_locator(build_configuration_id))

    def delete_build_configuration(self, build_configuration_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_BUILD_CONFIGURATION,
            ResponseSpecs.entity_was_deleted()
        ).delete(self._build_configuration_locator(build_configuration_id))

    @staticmethod
    def _project_locator(project_id: str) -> str:
        return project_id if ":" in project_id else f"id:{project_id}"

    @staticmethod
    def _build_configuration_locator(build_configuration_id: str) -> str:
        return (
            build_configuration_id
            if ":" in build_configuration_id
            else f"id:{build_configuration_id}"
        )

    @staticmethod
    def _user_locator(user_id_or_username: int | str) -> str:
        if isinstance(user_id_or_username, int):
            return f"id:{user_id_or_username}"
        return (
            user_id_or_username
            if ":" in user_id_or_username
            else f"username:{user_id_or_username}"
        )
