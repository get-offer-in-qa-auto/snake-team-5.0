import uuid

import allure
import pytest

from src.main.api.classes.api_manager import ApiManager

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.build_execution,
]


@allure.title("Manual build run finishes successfully")
def test_successful_build_run(
    api_manager: ApiManager, runnable_build_configuration_factory
):
    marker = f"BUILD_RUN_SUCCESS_{uuid.uuid4().hex}"
    configuration_id = runnable_build_configuration_factory(f"echo {marker}")

    queued = api_manager.build_run_steps.start(configuration_id)
    finished = api_manager.build_run_steps.wait_until_finished(queued.id)

    api_manager.build_run_steps.verify_result(finished, "SUCCESS", marker)


@allure.title("Manual build run reports failed script")
def test_failed_build_run(
    api_manager: ApiManager, runnable_build_configuration_factory
):
    configuration_id = runnable_build_configuration_factory(
        "echo BUILD_RUN_FAILURE; exit 1"
    )

    queued = api_manager.build_run_steps.start(configuration_id)
    finished = api_manager.build_run_steps.wait_until_finished(queued.id)

    api_manager.build_run_steps.verify_result(finished, "FAILURE", "BUILD_RUN_FAILURE")
