import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.create_build_step_request import CreateBuildStepRequest
from src.main.api.models.project_response import ProjectResponse


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
def test_create_build_step(
    api_manager: ApiManager,
    build_configuration: BuildConfigurationResponse,
    build_step_request: CreateBuildStepRequest,
):
    created_step = api_manager.admin_steps.create_build_step(
        build_configuration.id, build_step_request
    )
    stored_step = api_manager.admin_steps.get_build_step(
        build_configuration.id, created_step.id
    )

    api_manager.admin_steps.verify_build_step_created(
        build_step_request, created_step, stored_step
    )


@allure.title("Created build step is persisted in TeamCity configuration")
@allure.tag("api", "regression", "build-step", "configuration")
@pytest.mark.api
@pytest.mark.regression
@pytest.mark.configuration
def test_created_build_step_is_persisted_in_configuration(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration: BuildConfigurationResponse,
    build_step_request: CreateBuildStepRequest,
):
    created_step = api_manager.admin_steps.create_build_step(
        build_configuration.id, build_step_request
    )

    api_manager.configuration_steps.verify_build_step_persisted(
        project.id,
        build_configuration.id,
        created_step.id,
        build_step_request,
    )


@pytest.mark.api
@pytest.mark.regression
def test_update_build_step(
    api_manager: ApiManager,
    build_configuration: BuildConfigurationResponse,
    build_step_request: CreateBuildStepRequest,
    build_step_request_factory,
):
    created_step = api_manager.admin_steps.create_build_step(
        build_configuration.id, build_step_request
    )
    updated_request = build_step_request_factory()

    api_manager.admin_steps.update_build_step(
        build_configuration.id, created_step.id, updated_request
    )
    updated_step = api_manager.admin_steps.get_build_step(
        build_configuration.id, created_step.id
    )

    api_manager.admin_steps.verify_build_step_updated(
        updated_request, created_step, updated_step
    )


@allure.title("Updated build step is persisted in TeamCity configuration")
@allure.tag("api", "regression", "build-step", "configuration")
@pytest.mark.api
@pytest.mark.regression
@pytest.mark.configuration
def test_updated_build_step_is_persisted_in_configuration(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration: BuildConfigurationResponse,
    build_step_request: CreateBuildStepRequest,
    build_step_request_factory,
):
    created_step = api_manager.admin_steps.create_build_step(
        build_configuration.id, build_step_request
    )
    updated_request = build_step_request_factory(script="echo persisted update")

    api_manager.admin_steps.update_build_step(
        build_configuration.id, created_step.id, updated_request
    )
    api_manager.configuration_steps.verify_build_step_persisted(
        project.id,
        build_configuration.id,
        created_step.id,
        updated_request,
    )


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
def test_delete_build_step(
    api_manager: ApiManager,
    build_configuration: BuildConfigurationResponse,
    build_step_request: CreateBuildStepRequest,
):
    created_step = api_manager.admin_steps.create_build_step(
        build_configuration.id, build_step_request
    )

    api_manager.admin_steps.delete_build_step(build_configuration.id, created_step.id)
    api_manager.admin_steps.check_build_step_does_not_exist(
        build_configuration.id, created_step.id
    )


@allure.title("Deleted build step is removed from TeamCity configuration")
@allure.tag("api", "regression", "build-step", "configuration")
@pytest.mark.api
@pytest.mark.regression
@pytest.mark.configuration
def test_deleted_build_step_is_removed_from_configuration(
    api_manager: ApiManager,
    project: ProjectResponse,
    build_configuration: BuildConfigurationResponse,
    build_step_request: CreateBuildStepRequest,
):
    created_step = api_manager.admin_steps.create_build_step(
        build_configuration.id, build_step_request
    )

    api_manager.admin_steps.delete_build_step(build_configuration.id, created_step.id)
    api_manager.configuration_steps.verify_build_step_deleted(
        project.id, build_configuration.id, created_step.id
    )


@pytest.mark.api
@pytest.mark.regression
def test_create_multiple_build_steps(
    api_manager: ApiManager,
    build_configuration: BuildConfigurationResponse,
    build_step_request_factory,
):
    first_request = build_step_request_factory()
    second_request = build_step_request_factory()

    first_created_step = api_manager.admin_steps.create_build_step(
        build_configuration.id, first_request
    )
    second_created_step = api_manager.admin_steps.create_build_step(
        build_configuration.id, second_request
    )

    stored_steps = api_manager.admin_steps.get_build_steps(build_configuration.id)
    api_manager.admin_steps.verify_build_steps_created(
        [
            (first_request, first_created_step),
            (second_request, second_created_step),
        ],
        stored_steps,
    )


@pytest.mark.api
@pytest.mark.regression
def test_create_build_step_for_nonexistent_build_configuration(
    api_manager: ApiManager,
    build_step_request: CreateBuildStepRequest,
    nonexistent_build_configuration_id: str,
):

    api_manager.admin_steps.create_build_step_with_expected_error(
        nonexistent_build_configuration_id, build_step_request
    )
