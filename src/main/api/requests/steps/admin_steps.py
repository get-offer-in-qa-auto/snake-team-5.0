import allure

from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.build_step_response import (
    BuildStepResponse,
    BuildStepsResponse,
)
from src.main.api.models.comparison.entity_assertions import EntityAssertions
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.api.models.create_build_step_request import CreateBuildStepRequest
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.role_assignment import (
    RoleAssignmentRequest,
    RoleAssignmentResponse,
    RoleAssignmentsResponse,
)
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import (
    ValidatedCrudRequester,
)
from src.main.api.requests.steps.base_steps import BaseSteps
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseError, ResponseSpecs


class AdminSteps(BaseSteps):
    @allure.step("Create user as administrator")
    def create_user(self, user_request: CreateUserRequest):
        user_response: CreateUserResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_USER,
            ResponseSpecs.entity_was_created_or_ok(),
        ).post(user_request)

        self.created_objects.append(user_response)
        return user_response

    @allure.step("Verify user cannot be created: {error_text}")
    def create_user_bad_request(
        self, user_request: CreateUserRequest, error_text: ResponseError
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_USER,
            ResponseSpecs.request_returns_bad_request_with_text(error_text),
        ).post(user_request)

    @allure.step("Verify user cannot be created without authorization")
    def create_user_without_authorization(self, user_request: CreateUserRequest):
        CrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.CREATE_USER,
            ResponseSpecs.request_returns_unauthorized(),
        ).post(user_request, allow_redirects=False)

    @allure.step("Get user {username} as administrator")
    def get_user(self, username: str) -> CreateUserResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_ok(),
        ).get(self._user_locator(username))

    @allure.step("Get current user")
    def get_user_as(self, user_request: CreateUserRequest) -> CreateUserResponse:
        return ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_ok(),
        ).get(self._user_locator(user_request.username))

    @allure.step("Verify user was created")
    def verify_user_created(
        self,
        user_request: CreateUserRequest,
        created_user: CreateUserResponse,
        stored_user: CreateUserResponse,
    ) -> None:
        self.verify_response_matches(user_request, created_user)
        self.verify_response_matches(user_request, stored_user)
        EntityAssertions.has_id(created_user)
        EntityAssertions.has_href(created_user)

    @allure.step("Verify user {username} does not exist")
    def check_user_does_not_exist(self, username: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_not_found_with_text(
                ResponseError.USER_NOT_FOUND
            ),
        ).get(self._user_locator(username))

    @allure.step("Verify user cannot authenticate")
    def check_user_cannot_authenticate(self, user_request: CreateUserRequest):
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.GET_USER,
            ResponseSpecs.request_returns_unauthorized_with_text(
                ResponseError.INCORRECT_USERNAME_OR_PASSWORD
            ),
        ).get(self._user_locator(user_request.username))

    @allure.step("Delete user {user_id}")
    def delete_user(self, user_id: int | str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_USER,
            ResponseSpecs.entity_was_deleted(),
        ).delete(self._user_locator(user_id))

        self.created_objects.unregister_user(user_id)

    @allure.step("Delete user {user_id} if it exists")
    def delete_user_if_exists(self, user_id: int | str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_USER,
            ResponseSpecs.entity_was_deleted_or_not_found(),
        ).delete(self._user_locator(user_id))

        self.created_objects.unregister_user(user_id)

    @allure.step("Assign role {role_id} with scope {scope} to user {username}")
    def assign_user_role(
        self, username: str, role_id: str, scope: str
    ) -> RoleAssignmentResponse:
        role_request = RoleAssignmentRequest(roleId=role_id, scope=scope)
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ASSIGN_USER_ROLE,
            ResponseSpecs.entity_was_created_or_ok(),
        ).post(role_request, path=f"{self._user_locator(username)}/roles")

    @allure.step("Get roles for user {username}")
    def get_user_roles(self, username: str) -> RoleAssignmentsResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_USER_ROLES,
            ResponseSpecs.request_returns_ok(),
        ).get(f"{self._user_locator(username)}/roles")

    @allure.step(
        "Verify role {role_id} with scope {scope} is assigned to user {username}"
    )
    def verify_user_role_assigned(
        self,
        username: str,
        assigned_role: RoleAssignmentResponse,
        role_id: str,
        scope: str,
    ) -> None:
        assert assigned_role.roleId == role_id
        assert assigned_role.scope == scope
        assert assigned_role.href

        user_roles = self.get_user_roles(username)
        assert any(
            role.roleId == role_id and role.scope == scope for role in user_roles.role
        ), f"Role {role_id!r} with scope {scope!r} is not assigned to user {username!r}"

    @allure.step("Get all users as administrator")
    def get_all_users(self) -> list[CreateUserRequest]:
        response = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_GET_ALL_USERS,
            ResponseSpecs.request_returns_ok(),
        ).get()
        return response

    @allure.step("Create project as administrator")
    def create_project(self, project_request: CreateProjectRequest) -> ProjectResponse:
        project_response: ProjectResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.entity_was_created_or_ok(),
        ).post(project_request)

        self.created_objects.append(project_response)
        return project_response

    @allure.step("Verify project cannot be created: {error_text}")
    def create_project_bad_request(
        self, project_request: CreateProjectRequest, error_text: ResponseError
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.request_returns_bad_request_with_text(error_text),
        ).post(project_request)

    @allure.step("Verify project cannot be created: {error_text}")
    def create_project_not_found(
        self, project_request: CreateProjectRequest, error_text: ResponseError
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.request_returns_not_found_with_text(error_text),
        ).post(project_request)

    @allure.step("Verify project cannot be created without authorization")
    def create_project_without_authorization(
        self, project_request: CreateProjectRequest
    ):
        CrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.CREATE_PROJECT,
            ResponseSpecs.request_returns_unauthorized(),
        ).post(project_request, allow_redirects=False)

    @allure.step("Get project {project_id} as administrator")
    def get_project(self, project_id: str) -> ProjectResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_PROJECT,
            ResponseSpecs.request_returns_ok(),
        ).get(self._project_locator(project_id))

    @allure.step("Verify project was created")
    def verify_project_created(
        self,
        project_request: CreateProjectRequest,
        created_project: ProjectResponse,
        stored_project: ProjectResponse,
    ) -> None:
        self.verify_response_matches(project_request, created_project)
        EntityAssertions.has_href(created_project)
        self.verify_project_stored(project_request, stored_project, "_Root")

    @allure.step("Verify project is stored in expected parent")
    def verify_project_stored(
        self,
        project_request: CreateProjectRequest,
        stored_project: ProjectResponse,
        expected_parent_id: str,
    ) -> None:
        self.verify_response_matches(project_request, stored_project)
        EntityAssertions.has_parent_project(stored_project, expected_parent_id)

    @allure.step("Verify project {project_id} does not exist")
    def check_project_does_not_exist(self, project_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_PROJECT,
            ResponseSpecs.request_returns_not_found_with_text(
                ResponseError.PROJECT_NOT_FOUND
            ),
        ).get(self._project_locator(project_id))

    @allure.step("Delete project {project_id}")
    def delete_project(self, project_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_PROJECT,
            ResponseSpecs.entity_was_deleted(),
        ).delete(self._project_locator(project_id))

        self.created_objects.unregister_project(project_id)

    @allure.step("Delete project {project_id} if it exists")
    def delete_project_if_exists(self, project_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_PROJECT,
            ResponseSpecs.entity_was_deleted_or_not_found(),
        ).delete(self._project_locator(project_id))

    @allure.step("Create build configuration in project {project_id}")
    def create_build_configuration(
        self, project_id: str, configuration_request: CreateBuildConfigurationRequest
    ) -> BuildConfigurationResponse:
        configuration_response: BuildConfigurationResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.entity_was_created_or_ok(),
        ).post(
            configuration_request,
            path=f"{self._project_locator(project_id)}/buildTypes",
        )

        self.created_objects.append(configuration_response)
        return configuration_response

    @allure.step("Verify build configuration cannot be created: {error_text}")
    def create_build_configuration_bad_request(
        self,
        project_id: str,
        configuration_request: CreateBuildConfigurationRequest,
        error_text: ResponseError,
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_bad_request_with_text(error_text),
        ).post(
            configuration_request,
            path=f"{self._project_locator(project_id)}/buildTypes",
        )

    @allure.step("Verify build configuration cannot be created: {error_text}")
    def create_build_configuration_not_found(
        self,
        project_id: str,
        configuration_request: CreateBuildConfigurationRequest,
        error_text: ResponseError,
    ):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_not_found_with_text(error_text),
        ).post(
            configuration_request,
            path=f"{self._project_locator(project_id)}/buildTypes",
        )

    @allure.step("Verify build configuration cannot be created without authorization")
    def create_build_configuration_without_authorization(
        self, project_id: str, configuration_request: CreateBuildConfigurationRequest
    ):
        CrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.CREATE_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_unauthorized(),
        ).post(
            configuration_request,
            path=f"{self._project_locator(project_id)}/buildTypes",
            allow_redirects=False,
        )

    @allure.step("Get build configuration {build_configuration_id} as administrator")
    def get_build_configuration(
        self, build_configuration_id: str
    ) -> BuildConfigurationResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_ok(),
        ).get(self._build_configuration_locator(build_configuration_id))

    @allure.step("Verify build configuration was created")
    def verify_build_configuration_created(
        self,
        configuration_request: CreateBuildConfigurationRequest,
        created_configuration: BuildConfigurationResponse,
        stored_configuration: BuildConfigurationResponse,
        expected_project_id: str,
    ) -> None:
        self.verify_response_matches(configuration_request, created_configuration)
        EntityAssertions.has_href(created_configuration)
        self.verify_build_configuration_stored(
            configuration_request, stored_configuration, expected_project_id
        )

    @allure.step("Verify build configuration is stored in expected project")
    def verify_build_configuration_stored(
        self,
        configuration_request: CreateBuildConfigurationRequest,
        stored_configuration: BuildConfigurationResponse,
        expected_project_id: str,
    ) -> None:
        self.verify_response_matches(configuration_request, stored_configuration)
        EntityAssertions.belongs_to_project(stored_configuration, expected_project_id)

    @allure.step("Verify build configuration {build_configuration_id} does not exist")
    def check_build_configuration_does_not_exist(self, build_configuration_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_CONFIGURATION,
            ResponseSpecs.request_returns_not_found_with_text(
                ResponseError.BUILD_CONFIGURATION_NOT_FOUND
            ),
        ).get(self._build_configuration_locator(build_configuration_id))

    @allure.step("Delete build configuration {build_configuration_id}")
    def delete_build_configuration(self, build_configuration_id: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_BUILD_CONFIGURATION,
            ResponseSpecs.entity_was_deleted(),
        ).delete(self._build_configuration_locator(build_configuration_id))

        self.created_objects.unregister_build_configuration(build_configuration_id)

    def create_build_step(
        self, build_configuration_id: str, build_step_request: CreateBuildStepRequest
    ) -> BuildStepResponse:
        build_configuration_locator = self._build_configuration_locator(
            build_configuration_id
        )

        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_STEP,
            ResponseSpecs.entity_was_created_or_ok(),
        ).post(build_step_request, path=f"{build_configuration_locator}/steps")

    def get_build_step(
        self, build_configuration_id: str, step_id: str
    ) -> BuildStepResponse:
        build_configuration_locator = self._build_configuration_locator(
            build_configuration_id
        )

        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_STEP,
            ResponseSpecs.request_returns_ok(),
        ).get(f"{build_configuration_locator}/steps/{step_id}")

    def update_build_step(
        self,
        build_configuration_id: str,
        step_id: str,
        build_step_request: CreateBuildStepRequest,
    ) -> BuildStepResponse:
        build_configuration_locator = self._build_configuration_locator(
            build_configuration_id
        )

        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.UPDATE_BUILD_STEP,
            ResponseSpecs.request_returns_ok(),
        ).update(
            build_step_request,
            path=f"{build_configuration_locator}/steps/{step_id}",
        )

    def delete_build_step(self, build_configuration_id: str, step_id: str) -> None:
        build_configuration_locator = self._build_configuration_locator(
            build_configuration_id
        )

        ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.DELETE_BUILD_STEP,
            ResponseSpecs.entity_was_deleted(),
        ).delete(f"{build_configuration_locator}/steps/{step_id}")

    def check_build_step_does_not_exist(
        self,
        build_configuration_id: str,
        step_id: str,
    ) -> None:
        build_configuration_locator = self._build_configuration_locator(
            build_configuration_id
        )

        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_STEP,
            ResponseSpecs.request_returns_not_found_with_text(
                ResponseError.BUILD_STEP_NOT_FOUND
            ),
        ).get(
            f"{build_configuration_locator}/steps/{step_id}",
        )

    def get_build_steps(
        self,
        build_configuration_id: str,
    ) -> BuildStepsResponse:
        build_configuration_locator = self._build_configuration_locator(
            build_configuration_id
        )

        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_STEPS,
            ResponseSpecs.request_returns_ok(),
        ).get(
            f"{build_configuration_locator}/steps",
        )

    @allure.step("Verify build step was created")
    def verify_build_step_created(
        self,
        build_step_request: CreateBuildStepRequest,
        created_step: BuildStepResponse,
        stored_step: BuildStepResponse,
    ) -> None:
        self.verify_response_matches(build_step_request, created_step)
        self.verify_response_matches(build_step_request, stored_step)
        assert created_step.id.startswith("RUNNER_")
        assert stored_step.id == created_step.id

    @allure.step("Verify build step was updated")
    def verify_build_step_updated(
        self,
        build_step_request: CreateBuildStepRequest,
        original_step: BuildStepResponse,
        updated_step: BuildStepResponse,
    ) -> None:
        self.verify_response_matches(build_step_request, updated_step)
        assert updated_step.id == original_step.id
        assert updated_step.properties is not None

        expected_properties = {
            prop.name: prop.value for prop in build_step_request.properties.property
        }
        actual_properties = {
            prop.name: prop.value for prop in updated_step.properties.property
        }
        assert (
            actual_properties["script.content"] == expected_properties["script.content"]
        )

    @allure.step("Verify multiple build steps were created")
    def verify_build_steps_created(
        self,
        requests_and_steps: list[tuple[CreateBuildStepRequest, BuildStepResponse]],
        stored_steps: BuildStepsResponse,
    ) -> None:
        assert stored_steps.count == len(requests_and_steps)

        created_ids = [step.id for _, step in requests_and_steps]
        assert len(created_ids) == len(set(created_ids))

        stored_steps_by_id = {step.id: step for step in stored_steps.step}
        for request, created_step in requests_and_steps:
            assert created_step.id in stored_steps_by_id
            self.verify_response_matches(request, stored_steps_by_id[created_step.id])

    def create_build_step_with_expected_error(
        self,
        build_configuration_id: str,
        build_step_request: CreateBuildStepRequest,
    ) -> None:
        build_configuration_locator = self._build_configuration_locator(
            build_configuration_id
        )

        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CREATE_BUILD_STEP,
            ResponseSpecs.request_returns_not_found_with_text(
                ResponseError.BUILD_CONFIGURATION_NOT_FOUND
            ),
        ).post(
            build_step_request,
            path=f"{build_configuration_locator}/steps",
        )

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
