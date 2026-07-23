import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.build_run_data import BuildRunScenario

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.build_execution,
]


@allure.title("Manual build run finishes successfully")
def test_successful_build_run(
    api_manager: ApiManager,
    runnable_build_configuration_factory,
    successful_build_run_scenario: BuildRunScenario,
):
    configuration_id = runnable_build_configuration_factory(
        successful_build_run_scenario.script
    )

    queued = api_manager.build_run_steps.start(configuration_id)
    finished = api_manager.build_run_steps.wait_until_finished(queued.id)

    api_manager.build_run_steps.verify_result(
        finished,
        successful_build_run_scenario.expected_status,
        successful_build_run_scenario.expected_log_text,
    )


@allure.title("Manual build run reports failed script")
def test_failed_build_run(
    api_manager: ApiManager,
    runnable_build_configuration_factory,
    failed_build_run_scenario: BuildRunScenario,
):
    configuration_id = runnable_build_configuration_factory(
        failed_build_run_scenario.script
    )

    queued = api_manager.build_run_steps.start(configuration_id)
    finished = api_manager.build_run_steps.wait_until_finished(queued.id)

    api_manager.build_run_steps.verify_result(
        finished,
        failed_build_run_scenario.expected_status,
        failed_build_run_scenario.expected_log_text,
    )
