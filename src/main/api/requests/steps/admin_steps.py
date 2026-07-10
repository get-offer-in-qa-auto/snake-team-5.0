from typing import List
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.build_configuration_request import BuildConfigurationRequest
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.build_step_request import CreateBuildStepRequest
from src.main.api.models.build_step_response import BuildStepResponse, BuildStepsResponse
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.vcs_root_request import CreateVcsRootRequest
from src.main.api.models.vcs_root_response import VcsRootResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.steps.base_steps import BaseSteps
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


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
        ModelAssertions(project_request, project_response).match()
        return project_response

    def get_project(self, project_id: str) -> ProjectResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_PROJECT,
            ResponseSpecs.request_returns_ok()
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
        build_configuration_request: BuildConfigurationRequest,
    ) -> BuildConfigurationResponse:
        build_configuration_response: BuildConfigurationResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(
            build_configuration_request,
            id=f"{self._project_locator(project_id)}/buildTypes",
        )

        self.created_objects.append(build_configuration_response)
        ModelAssertions(build_configuration_request, build_configuration_response).match()
        return build_configuration_response

    def get_build_configuration(self, build_configuration_id: str) -> BuildConfigurationResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_ok()
        ).get(self._build_configuration_locator(build_configuration_id))

    def delete_build_configuration(self, build_configuration_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_BUILD_CONFIGURATION,
            ResponseSpecs.entity_was_deleted()
        ).delete(self._build_configuration_locator(build_configuration_id))

    def create_vcs_root(self, vcs_root_request: CreateVcsRootRequest) -> VcsRootResponse:
        vcs_root_response: VcsRootResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_VCS_ROOT,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(vcs_root_request)

        self.created_objects.append(vcs_root_response)
        ModelAssertions(vcs_root_request, vcs_root_response).match()
        return vcs_root_response

    def get_vcs_root(self, vcs_root_id: str) -> VcsRootResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_VCS_ROOT,
            ResponseSpecs.request_returns_ok()
        ).get(self._vcs_root_locator(vcs_root_id))

    def delete_vcs_root(self, vcs_root_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_VCS_ROOT,
            ResponseSpecs.entity_was_deleted()
        ).delete(self._vcs_root_locator(vcs_root_id))

    def add_build_step(
        self,
        build_configuration_id: str,
        build_step_request: CreateBuildStepRequest,
    ) -> BuildStepResponse:
        build_step_response: BuildStepResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_STEP,
            ResponseSpecs.entity_was_created_or_ok()
        ).post(
            build_step_request,
            id=f"{self._build_configuration_locator(build_configuration_id)}/steps",
        )

        ModelAssertions(build_step_request, build_step_response).match()
        return build_step_response

    def get_build_steps(self, build_configuration_id: str) -> BuildStepsResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_STEPS,
            ResponseSpecs.request_returns_ok()
        ).get(f"{self._build_configuration_locator(build_configuration_id)}/steps")

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
    def _vcs_root_locator(vcs_root_id: str) -> str:
        return vcs_root_id if ":" in vcs_root_id else f"id:{vcs_root_id}"
