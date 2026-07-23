import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.create_build_step_request import CreateBuildStepRequest
from src.main.api.models.project_response import ProjectResponse


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
    updated_build_step_request: CreateBuildStepRequest,
):
    created_step = api_manager.admin_steps.create_build_step(
        build_configuration.id, build_step_request
    )
    api_manager.admin_steps.update_build_step(
        build_configuration.id, created_step.id, updated_build_step_request
    )
    api_manager.configuration_steps.verify_build_step_persisted(
        project.id,
        build_configuration.id,
        created_step.id,
        updated_build_step_request,
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
