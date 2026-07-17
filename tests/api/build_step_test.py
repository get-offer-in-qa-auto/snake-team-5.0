import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_build_step_request import CreateBuildStepRequest


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

    ModelAssertions(build_step_request, created_step).match()
    ModelAssertions(build_step_request, stored_step).match()

    assert created_step.id.startswith("RUNNER_")
    assert stored_step.id == created_step.id


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

    ModelAssertions(updated_request, updated_step).match()

    expected_properties = {
        prop.name: prop.value for prop in updated_request.properties.property
    }
    actual_properties = {
        prop.name: prop.value for prop in updated_step.properties.property
    }

    assert updated_step.id == created_step.id
    assert actual_properties["script.content"] == expected_properties["script.content"]


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
    stored_steps_by_id = {step.id: step for step in stored_steps.step}

    assert stored_steps.count == 2
    assert first_created_step.id != second_created_step.id

    ModelAssertions(first_request, stored_steps_by_id[first_created_step.id]).match()
    ModelAssertions(second_request, stored_steps_by_id[second_created_step.id]).match()


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
