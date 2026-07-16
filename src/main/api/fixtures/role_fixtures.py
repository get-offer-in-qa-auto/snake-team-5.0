import pytest

from src.main.api.classes.api_manager import ApiManager
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
    def create_limited_user(project_id: str):
        user_request = user_request_factory()
        api_manager.admin_steps.create_user(user_request)
        api_manager.admin_steps.assign_user_role(
            user_request.username, Role.PROJECT_VIEWER, RoleScope.project(project_id)
        )
        return user_request

    return create_limited_user
