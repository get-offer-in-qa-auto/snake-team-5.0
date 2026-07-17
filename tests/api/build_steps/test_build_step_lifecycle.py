import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.create_build_step_request import CreateBuildStepRequest


@allure.title("Create build step")
@allure.tag("api", "smoke", "regression", "build-step")
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


@allure.title("Update build step")
@allure.tag("api", "regression", "build-step")
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


@allure.title("Delete build step")
@allure.tag("api", "smoke", "regression", "build-step")
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


@allure.title("Create multiple build steps")
@allure.tag("api", "regression", "build-step")
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
