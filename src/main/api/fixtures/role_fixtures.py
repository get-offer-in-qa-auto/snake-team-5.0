import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.constants.teamcity import ROOT_PROJECT_ID
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.role import Role, RoleScope


@pytest.fixture(scope="function")
def rbac_admin_user_request(api_manager: ApiManager, user_request_factory):
    user_request = user_request_factory()
    api_manager.admin_steps.create_user(user_request)
    api_manager.admin_steps.assign_user_role(
        user_request.username, Role.SYSTEM_ADMIN, RoleScope.GLOBAL
    )
    return user_request


@pytest.fixture(scope="function")
def limited_user_factory(api_manager: ApiManager, user_request_factory):
    def create_limited_user(project_id: str = ROOT_PROJECT_ID):
        user_request = user_request_factory()
        api_manager.admin_steps.create_user(user_request)
        api_manager.admin_steps.assign_user_role(
            user_request.username, Role.PROJECT_VIEWER, RoleScope.project(project_id)
        )
        return user_request

    return create_limited_user


@pytest.fixture(scope="function")
def project_viewer_user(
    project: ProjectResponse, limited_user_factory
) -> CreateUserRequest:
    return limited_user_factory(project.id)
