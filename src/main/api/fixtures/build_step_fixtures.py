import random
import uuid
from collections.abc import Callable

import pytest

from src.main.api.generators.build_step_data import BUILD_STEP_SCRIPTS
from src.main.api.models.create_build_step_request import (
    BuildStepProperties,
    BuildStepProperty,
    CreateBuildStepRequest,
)


@pytest.fixture(scope="function")
def build_step_request_factory() -> Callable[..., CreateBuildStepRequest]:
    def create_build_step_request(
        name: str | None = None,
        script: str | None = None,
    ) -> CreateBuildStepRequest:
        suffix = uuid.uuid4().hex[:8]

        return CreateBuildStepRequest(
            name=name or f"Autotest Build Step {suffix}",
            type="simpleRunner",
            properties=BuildStepProperties(
                property=[
                    BuildStepProperty(
                        name="script.content",
                        value=script or random.choice(BUILD_STEP_SCRIPTS),
                    ),
                    BuildStepProperty(
                        name="use.custom.script",
                        value="true",
                    ),
                ]
            ),
        )

    return create_build_step_request


@pytest.fixture(scope="function")
def build_step_request(
    build_step_request_factory: Callable[..., CreateBuildStepRequest],
) -> CreateBuildStepRequest:
    return build_step_request_factory()
