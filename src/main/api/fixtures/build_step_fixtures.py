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
        excluded_scripts: set[str] | None = None,
    ) -> CreateBuildStepRequest:
        suffix = uuid.uuid4().hex[:8]
        scripts = [
            candidate
            for candidate in BUILD_STEP_SCRIPTS
            if candidate not in (excluded_scripts or set())
        ]
        if script is None and not scripts:
            raise ValueError("No build step scripts remain after exclusions")

        return CreateBuildStepRequest(
            name=name or f"Autotest Build Step {suffix}",
            type="simpleRunner",
            properties=BuildStepProperties(
                property=[
                    BuildStepProperty(
                        name="script.content",
                        value=script if script is not None else random.choice(scripts),
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


@pytest.fixture(scope="function")
def updated_build_step_request(
    build_step_request: CreateBuildStepRequest,
    build_step_request_factory: Callable[..., CreateBuildStepRequest],
) -> CreateBuildStepRequest:
    original_scripts = {
        prop.value
        for prop in build_step_request.properties.property
        if prop.name == "script.content"
    }
    return build_step_request_factory(excluded_scripts=original_scripts)
