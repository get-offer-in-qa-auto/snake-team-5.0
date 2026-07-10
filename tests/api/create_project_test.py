import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_project_request import CreateProjectRequest


@pytest.mark.api
@pytest.mark.regression
def test_create_project(api_manager: ApiManager, project_request: CreateProjectRequest):
    api_manager.admin_steps.create_project(project_request)
