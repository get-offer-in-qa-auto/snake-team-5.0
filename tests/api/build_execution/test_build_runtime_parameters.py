import uuid

import allure
import pytest

from src.main.api.classes.api_manager import ApiManager

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    pytest.mark.build_execution,
]


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
