import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.comparison.entity_assertions import EntityAssertions
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.api.models.project_response import ProjectResponse
from src.main.api.specs.response_specs import ResponseError


@allure.title("Create build configuration")
@allure.tag("api", "smoke", "regression", "build-configuration")
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

    ModelAssertions(build_configuration_request, configuration).match()
    ModelAssertions(build_configuration_request, stored_configuration).match()
    EntityAssertions.has_href(configuration)
    EntityAssertions.belongs_to_project(stored_configuration, project.id)


@allure.title("Created build configuration is persisted in database")
@allure.tag("api", "regression", "build-configuration", "database")
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

    api_manager.database_steps.verify_build_configuration_persisted(configuration)


@allure.title("Create build configuration in subproject")
@allure.tag("api", "regression", "build-configuration")
@pytest.mark.api
@pytest.mark.regression
def test_create_build_configuration_in_subproject(
    api_manager: ApiManager,
    project_request_factory,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    parent_project = api_manager.admin_steps.create_project(project_request_factory())
    subproject = api_manager.admin_steps.create_project(
        project_request_factory(parent_locator=f"id:{parent_project.id}")
    )

    configuration = api_manager.admin_steps.create_build_configuration(
        subproject.id, build_configuration_request
    )
    stored_configuration = api_manager.admin_steps.get_build_configuration(
        configuration.id
    )

    ModelAssertions(build_configuration_request, stored_configuration).match()
    EntityAssertions.belongs_to_project(stored_configuration, subproject.id)


@allure.title("Build configuration cannot be created in unknown project")
@allure.tag("api", "regression", "build-configuration", "negative")
@pytest.mark.api
@pytest.mark.regression
def test_create_build_configuration_with_unknown_project(
    api_manager: ApiManager,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    api_manager.admin_steps.create_build_configuration_not_found(
        "MissingProjectForAutotestBuild",
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
@allure.tag("api", "regression", "build-configuration", "negative")
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
    ModelAssertions(configuration_request, stored_configuration).match()


@allure.title(
    "Build configuration cannot be created with existing name in same project"
)
@allure.tag("api", "regression", "build-configuration", "negative")
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


@allure.title(
    "Build configurations with same name can be created in different projects"
)
@allure.tag("api", "regression", "build-configuration")
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

    ModelAssertions(first_request, stored_first).match()
    ModelAssertions(second_request, stored_second).match()
    EntityAssertions.belongs_to_project(stored_first, first_project.id)
    EntityAssertions.belongs_to_project(stored_second, second_project.id)


@allure.title("Build configuration cannot be created without authorization")
@allure.tag("api", "regression", "build-configuration", "authorization", "negative")
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


@allure.title("Delete build configuration")
@allure.tag("api", "regression", "build-configuration", "database")
@pytest.mark.api
@pytest.mark.regression
def test_delete_build_configuration(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
    created_objects: list,
):
    configuration = api_manager.admin_steps.create_build_configuration(
        project.id, build_configuration_request
    )

    api_manager.admin_steps.delete_build_configuration(configuration.id)
    created_objects.remove(configuration)

    api_manager.admin_steps.check_build_configuration_does_not_exist(configuration.id)
    api_manager.database_steps.verify_build_configuration_deleted(configuration.id)


@allure.title("Delete project with build configuration")
@allure.tag("api", "regression", "build-configuration", "project")
@pytest.mark.api
@pytest.mark.regression
def test_delete_project_with_build_configuration(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
    created_objects: list,
):
    configuration = api_manager.admin_steps.create_build_configuration(
        project.id, build_configuration_request
    )

    api_manager.admin_steps.delete_project(project.id)
    created_objects.remove(configuration)
    created_objects.remove(project)

    api_manager.admin_steps.check_project_does_not_exist(project.id)
    api_manager.admin_steps.check_build_configuration_does_not_exist(configuration.id)


@allure.title("Create build configuration with different id and name")
@allure.tag("api", "regression", "build-configuration")
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

    assert build_configuration_request.id != build_configuration_request.name
    ModelAssertions(build_configuration_request, stored_configuration).match()
