import allure
import pytest

from src.main.api.classes.api_manager import ApiManager

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.build_execution,
]


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
