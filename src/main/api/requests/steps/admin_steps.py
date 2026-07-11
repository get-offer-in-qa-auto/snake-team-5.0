from typing import List
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import ProjectResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.steps.base_steps import BaseSteps
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseError, ResponseSpecs


class AdminSteps(BaseSteps):
    def create_user(self, user_request: CreateUserRequest):
        pass

    def create_invalid_user(self, user_request: CreateUserRequest, error_key: str, error_value: str):
        pass

    def delete_user(self, user_id: int):
        pass

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

    @staticmethod
    def _project_locator(project_id: str) -> str:
        return project_id if ":" in project_id else f"id:{project_id}"
