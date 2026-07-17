from collections.abc import Callable

import pytest

from src.main.api.models.create_build_step_request import CreateBuildStepRequest


@pytest.fixture
def runnable_build_configuration_factory(
    api_manager,
    project,
    build_configuration_request_factory,
    build_step_request_factory,
) -> Callable[[str], str]:
    def create(script: str) -> str:
        configuration = api_manager.admin_steps.create_build_configuration(
            project.id, build_configuration_request_factory()
        )
        step: CreateBuildStepRequest = build_step_request_factory(script=script)
        api_manager.admin_steps.create_build_step(configuration.id, step)
        return configuration.id

    return create
