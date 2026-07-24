import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.api.models.project_response import ProjectResponse
from src.main.reporting.allure.tags import AllureTag, api_regression_tags


@allure.title("Create build configuration")
@api_regression_tags(AllureTag.BUILD_CONFIGURATION, smoke=True)
@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
def test_create_build_configuration(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    configuration = api_manager.admin_steps.create_build_configuration(
        project.id, build_configuration_request
    )
    stored_configuration = api_manager.admin_steps.get_build_configuration(
        configuration.id
    )

    api_manager.admin_steps.verify_build_configuration_created(
        build_configuration_request,
        configuration,
        stored_configuration,
        project.id,
    )


@allure.title("Created build configuration is persisted in database")
@api_regression_tags(AllureTag.BUILD_CONFIGURATION, AllureTag.DATABASE)
@pytest.mark.api
@pytest.mark.regression
def test_created_build_configuration_is_persisted_in_database(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    configuration = api_manager.admin_steps.create_build_configuration(
        project.id, build_configuration_request
    )

    api_manager.database_steps.verify_build_configuration_persisted(configuration.id)


@allure.title("Delete build configuration")
@api_regression_tags(AllureTag.BUILD_CONFIGURATION, AllureTag.DATABASE)
@pytest.mark.api
@pytest.mark.regression
def test_delete_build_configuration(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    configuration = api_manager.admin_steps.create_build_configuration(
        project.id, build_configuration_request
    )

    api_manager.admin_steps.delete_build_configuration(configuration.id)

    api_manager.admin_steps.check_build_configuration_does_not_exist(configuration.id)
    api_manager.database_steps.verify_build_configuration_deleted(configuration.id)


@allure.title("Delete project with build configuration")
@api_regression_tags(AllureTag.BUILD_CONFIGURATION, AllureTag.PROJECT)
@pytest.mark.api
@pytest.mark.regression
def test_delete_project_with_build_configuration(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    configuration = api_manager.admin_steps.create_build_configuration(
        project.id, build_configuration_request
    )

    api_manager.admin_steps.delete_project(project.id)

    api_manager.admin_steps.check_project_does_not_exist(project.id)
    api_manager.admin_steps.check_build_configuration_does_not_exist(configuration.id)


@allure.title("Create build configuration with different id and name")
@api_regression_tags(AllureTag.BUILD_CONFIGURATION)
@pytest.mark.api
@pytest.mark.regression
def test_create_build_configuration_with_different_id_and_name(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    configuration = api_manager.admin_steps.create_build_configuration(
        project.id, build_configuration_request
    )
    stored_configuration = api_manager.admin_steps.get_build_configuration(
        configuration.id
    )

    api_manager.admin_steps.verify_distinct_id_and_name(build_configuration_request)
    api_manager.admin_steps.verify_response_matches(
        build_configuration_request, stored_configuration
    )
