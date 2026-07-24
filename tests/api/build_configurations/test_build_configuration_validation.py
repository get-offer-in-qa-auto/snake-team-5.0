import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.api.models.project_response import ProjectResponse
from src.main.api.specs.response_specs import ResponseError
from src.main.reporting.allure.tags import AllureTag, api_regression_tags


@allure.title("Build configuration cannot be created in unknown project")
@api_regression_tags(AllureTag.BUILD_CONFIGURATION, AllureTag.NEGATIVE)
@pytest.mark.api
@pytest.mark.regression
def test_create_build_configuration_with_unknown_project(
    api_manager: ApiManager,
    build_configuration_request: CreateBuildConfigurationRequest,
    nonexistent_project_id: str,
):
    api_manager.admin_steps.create_build_configuration_not_found(
        nonexistent_project_id,
        build_configuration_request,
        ResponseError.PROJECT_NOT_FOUND,
    )

    api_manager.admin_steps.check_build_configuration_does_not_exist(
        build_configuration_request.id
    )
    api_manager.database_steps.verify_build_configuration_not_created(
        build_configuration_request.id
    )


@allure.title("Build configuration cannot be created with existing id")
@api_regression_tags(AllureTag.BUILD_CONFIGURATION, AllureTag.NEGATIVE)
@pytest.mark.api
@pytest.mark.regression
def test_create_build_configuration_with_existing_id(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request_factory,
):
    configuration_request = build_configuration_request_factory()
    api_manager.admin_steps.create_build_configuration(
        project.id, configuration_request
    )
    duplicate_request = build_configuration_request_factory(
        build_configuration_id=configuration_request.id
    )

    api_manager.admin_steps.create_build_configuration_bad_request(
        project.id, duplicate_request, ResponseError.BUILD_CONFIGURATION_ID_ALREADY_USED
    )

    stored_configuration = api_manager.admin_steps.get_build_configuration(
        configuration_request.id
    )
    api_manager.admin_steps.verify_response_matches(
        configuration_request, stored_configuration
    )


@allure.title(
    "Build configuration cannot be created with existing name in same project"
)
@api_regression_tags(AllureTag.BUILD_CONFIGURATION, AllureTag.NEGATIVE)
@pytest.mark.api
@pytest.mark.regression
def test_create_build_configuration_with_existing_name_in_same_project(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request_factory,
):
    configuration_request = build_configuration_request_factory()
    api_manager.admin_steps.create_build_configuration(
        project.id, configuration_request
    )
    duplicate_request = build_configuration_request_factory(
        name=configuration_request.name
    )

    api_manager.admin_steps.create_build_configuration_bad_request(
        project.id,
        duplicate_request,
        ResponseError.BUILD_CONFIGURATION_NAME_ALREADY_EXISTS,
    )

    api_manager.admin_steps.check_build_configuration_does_not_exist(
        duplicate_request.id
    )
