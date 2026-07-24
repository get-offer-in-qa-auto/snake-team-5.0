import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.api.models.project_response import ProjectResponse
from src.main.reporting.allure.tags import AllureTag, api_regression_tags


@allure.title("Build configuration cannot be created without authorization")
@api_regression_tags(
    AllureTag.BUILD_CONFIGURATION, AllureTag.AUTHORIZATION, AllureTag.NEGATIVE
)
@pytest.mark.api
@pytest.mark.regression
def test_create_build_configuration_without_authorization(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    api_manager.admin_steps.create_build_configuration_without_authorization(
        project.id, build_configuration_request
    )

    api_manager.admin_steps.check_build_configuration_does_not_exist(
        build_configuration_request.id
    )
