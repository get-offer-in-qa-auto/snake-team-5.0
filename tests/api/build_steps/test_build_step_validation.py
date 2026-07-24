import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_build_step_request import CreateBuildStepRequest
from src.main.reporting.allure.tags import AllureTag, api_regression_tags


@allure.title("Build step cannot be created for nonexistent build configuration")
@api_regression_tags(AllureTag.BUILD_STEP, AllureTag.NEGATIVE)
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
