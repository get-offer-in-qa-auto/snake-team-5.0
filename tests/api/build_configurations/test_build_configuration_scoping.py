import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.constants.teamcity import TeamCityLocator
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.reporting.allure.tags import AllureTag, api_regression_tags


@allure.title("Create build configuration in subproject")
@api_regression_tags(AllureTag.BUILD_CONFIGURATION)
@pytest.mark.api
@pytest.mark.regression
def test_create_build_configuration_in_subproject(
    api_manager: ApiManager,
    project_request_factory,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    parent_project = api_manager.admin_steps.create_project(project_request_factory())
    subproject = api_manager.admin_steps.create_project(
        project_request_factory(parent_locator=TeamCityLocator.by_id(parent_project.id))
    )

    configuration = api_manager.admin_steps.create_build_configuration(
        subproject.id, build_configuration_request
    )
    stored_configuration = api_manager.admin_steps.get_build_configuration(
        configuration.id
    )

    api_manager.admin_steps.verify_build_configuration_stored(
        build_configuration_request, stored_configuration, subproject.id
    )


@allure.title(
    "Build configurations with same name can be created in different projects"
)
@api_regression_tags(AllureTag.BUILD_CONFIGURATION)
@pytest.mark.api
@pytest.mark.regression
def test_create_build_configurations_with_same_name_in_different_projects(
    api_manager: ApiManager,
    project_request_factory,
    build_configuration_request_factory,
):
    first_project = api_manager.admin_steps.create_project(project_request_factory())
    second_project = api_manager.admin_steps.create_project(project_request_factory())
    shared_name = build_configuration_request_factory().name
    first_request = build_configuration_request_factory(name=shared_name)
    second_request = build_configuration_request_factory(name=shared_name)

    first_configuration = api_manager.admin_steps.create_build_configuration(
        first_project.id, first_request
    )
    second_configuration = api_manager.admin_steps.create_build_configuration(
        second_project.id, second_request
    )
    stored_first = api_manager.admin_steps.get_build_configuration(
        first_configuration.id
    )
    stored_second = api_manager.admin_steps.get_build_configuration(
        second_configuration.id
    )

    api_manager.admin_steps.verify_build_configuration_stored(
        first_request, stored_first, first_project.id
    )
    api_manager.admin_steps.verify_build_configuration_stored(
        second_request, stored_second, second_project.id
    )
