import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.build_run_data import BuildRunScenario

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.build_execution,
]


@allure.title("Manual build run receives a runtime parameter")
def test_build_run_with_runtime_parameter(
    api_manager: ApiManager,
    runnable_build_configuration_factory,
    runtime_parameter_build_run_scenario: BuildRunScenario,
):
    configuration_id = runnable_build_configuration_factory(
        runtime_parameter_build_run_scenario.script
    )

    queued = api_manager.build_run_steps.start(
        configuration_id, runtime_parameter_build_run_scenario.parameters
    )
    finished = api_manager.build_run_steps.wait_until_finished(queued.id)

    api_manager.build_run_steps.verify_result(
        finished,
        runtime_parameter_build_run_scenario.expected_status,
        runtime_parameter_build_run_scenario.expected_log_text,
    )
