import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.vcs_root_request import CreateVcsRootRequest


@pytest.mark.api
@pytest.mark.regression
def test_create_vcs_root(
    api_manager: ApiManager,
    project_request: CreateProjectRequest,
    vcs_root_request: CreateVcsRootRequest,
):
    api_manager.admin_steps.create_project(project_request)
    api_manager.admin_steps.create_vcs_root(vcs_root_request)
