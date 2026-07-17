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


@allure.title("Manual build run receives a runtime parameter")
def test_build_run_with_runtime_parameter(
    api_manager: ApiManager, runnable_build_configuration_factory
):
    marker = uuid.uuid4().hex
    configuration_id = runnable_build_configuration_factory(
        "echo RUNTIME=%env.AUTOTEST_RUNTIME_MARKER%"
    )

    queued = api_manager.build_run_steps.start(
        configuration_id, {"env.AUTOTEST_RUNTIME_MARKER": marker}
    )
    finished = api_manager.build_run_steps.wait_until_finished(queued.id)

    api_manager.build_run_steps.verify_result(finished, "SUCCESS", f"RUNTIME={marker}")


@allure.title("Running build can be cancelled")
def test_running_build_can_be_cancelled(
    api_manager: ApiManager, runnable_build_configuration_factory
):
    configuration_id = runnable_build_configuration_factory("sleep 30")
    cancellation_comment = "Cancelled by Build Run MVP autotest"

    queued = api_manager.build_run_steps.start(configuration_id)
    api_manager.build_run_steps.wait_for_state(queued.id, "running")
    api_manager.build_run_steps.cancel(queued.id, cancellation_comment)
    finished = api_manager.build_run_steps.wait_until_finished(queued.id)

    api_manager.build_run_steps.verify_result(finished, "UNKNOWN")
