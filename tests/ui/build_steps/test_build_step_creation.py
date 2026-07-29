import allure
import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.create_build_step_request import CreateBuildStepRequest
from src.main.reporting.allure.tags import AllureTag, allure_tags
from src.main.ui.pages.create_command_line_build_step_page import (
    CreateCommandLineBuildStepPage,
)


@allure.title("Create Command Line build step")
@allure_tags(AllureTag.REGRESSION, AllureTag.BUILD_STEP)
@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.admin_session
def test_admin_can_create_command_line_build_step(
    page: Page,
    api_manager: ApiManager,
    build_configuration: BuildConfigurationResponse,
    build_step_request: CreateBuildStepRequest,
):

    CreateCommandLineBuildStepPage(
        page, build_configuration.id
    ).open().create_build_step(build_step_request)
    stored_steps = api_manager.admin_steps.get_build_steps(build_configuration.id)
    created_step = next(
        step for step in stored_steps.step if step.name == build_step_request.name
    )
    api_manager.admin_steps.verify_response_matches(build_step_request, created_step)
