import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.role import Role, RoleScope


@allure.title("Assign role to user")
@allure.tag("api", "regression", "permissions", "user")
@pytest.mark.api
@pytest.mark.regression
def test_assign_role_to_user(api_manager: ApiManager, user_request: CreateUserRequest):
    api_manager.admin_steps.create_user(user_request)

    assigned_role = api_manager.admin_steps.assign_user_role(
        user_request.username, Role.SYSTEM_ADMIN, RoleScope.GLOBAL
    )
    api_manager.admin_steps.verify_user_role_assigned(
        user_request.username,
        assigned_role,
        Role.SYSTEM_ADMIN,
        RoleScope.GLOBAL,
    )


@allure.title("Administrator user can create project")
@allure.tag("api", "regression", "permissions", "project")
@pytest.mark.api
@pytest.mark.regression
def test_admin_can_create_project(
    api_manager: ApiManager,
    rbac_admin_user_request: CreateUserRequest,
    project_request: CreateProjectRequest,
):
    project = api_manager.user_steps.create_project(
        rbac_admin_user_request, project_request
    )
    stored_project = api_manager.admin_steps.get_project(project.id)

    api_manager.admin_steps.verify_project_stored(
        project_request, stored_project, "_Root"
    )


@allure.title("Limited user cannot create project")
@allure.tag("api", "regression", "permissions", "project", "negative")
@pytest.mark.api
@pytest.mark.regression
def test_limited_user_cannot_create_project(
    api_manager: ApiManager, limited_user_factory, project_request: CreateProjectRequest
):
    limited_user = limited_user_factory("_Root")

    api_manager.user_steps.create_project_forbidden(limited_user, project_request)

    api_manager.admin_steps.check_project_does_not_exist(project_request.id)


@allure.title("Administrator user can create build configuration")
@allure.tag("api", "regression", "permissions", "build-configuration")
@pytest.mark.api
@pytest.mark.regression
def test_admin_can_create_build_configuration(
    api_manager: ApiManager,
    rbac_admin_user_request: CreateUserRequest,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    configuration = api_manager.user_steps.create_build_configuration(
        rbac_admin_user_request, project.id, build_configuration_request
    )
    stored_configuration = api_manager.admin_steps.get_build_configuration(
        configuration.id
    )

    api_manager.admin_steps.verify_build_configuration_stored(
        build_configuration_request, stored_configuration, project.id
    )


@allure.title("Limited user cannot create build configuration")
@allure.tag("api", "regression", "permissions", "build-configuration", "negative")
@pytest.mark.api
@pytest.mark.regression
def test_limited_user_cannot_create_build_configuration(
    api_manager: ApiManager,
    limited_user_factory,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    limited_user = limited_user_factory(project.id)

    api_manager.user_steps.create_build_configuration_forbidden(
        limited_user, project.id, build_configuration_request
    )

    api_manager.admin_steps.check_build_configuration_does_not_exist(
        build_configuration_request.id
    )
