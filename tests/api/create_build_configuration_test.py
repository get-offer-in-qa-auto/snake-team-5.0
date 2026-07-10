import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.build_configuration_request import BuildConfigurationRequest
from src.main.api.models.create_project_request import CreateProjectRequest


@pytest.mark.api
@pytest.mark.regression
def test_create_build_configuration(
    api_manager: ApiManager,
    project_request: CreateProjectRequest,
    build_configuration_request: BuildConfigurationRequest,
):
    project = api_manager.admin_steps.create_project(project_request)
    api_manager.admin_steps.create_build_configuration(
        project.id,
        build_configuration_request,
    )
