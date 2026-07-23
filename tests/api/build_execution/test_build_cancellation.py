import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.build_run_data import CancellableBuildRunScenario

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.build_execution,
]


@allure.title("Running build can be cancelled")
def test_running_build_can_be_cancelled(
    api_manager: ApiManager,
    runnable_build_configuration_factory,
    cancellable_build_run_scenario: CancellableBuildRunScenario,
):
    configuration_id = runnable_build_configuration_factory(
        cancellable_build_run_scenario.script
    )

    queued = api_manager.build_run_steps.start(configuration_id)
    api_manager.build_run_steps.wait_for_state(
        queued.id, cancellable_build_run_scenario.state_to_wait_for
    )
    api_manager.build_run_steps.cancel(
        queued.id, cancellable_build_run_scenario.cancellation_comment
    )
    finished = api_manager.build_run_steps.wait_until_finished(queued.id)

    api_manager.build_run_steps.verify_result(
        finished, cancellable_build_run_scenario.expected_status
    )
    api_manager.build_run_steps.wait_for_agent_idle()
