from typing import Annotated

import pytest

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.base_model import BaseModel
from src.main.api.models.build_step_request import (
    BuildStepProperties,
    CreateBuildStepRequest,
)
from src.main.api.models.vcs_root_request import VcsRootProperty


class GeneratedBuildStepIdentity(BaseModel):
    id: Annotated[str, GeneratingRule(regex=r"^AutotestApiStep[A-Za-z0-9]{8}$")]
    name: Annotated[str, GeneratingRule(regex=r"^AutotestApiStep[A-Za-z0-9]{8}$")]


@pytest.fixture(scope="function")
def build_step_request() -> CreateBuildStepRequest:
    generated_build_step = RandomModelGenerator.generate(GeneratedBuildStepIdentity)
    return CreateBuildStepRequest(
        id=generated_build_step.id,
        name=generated_build_step.id,
        type="simpleRunner",
        properties=BuildStepProperties(
            property=[
                VcsRootProperty(name="script.content", value="echo autotest"),
                VcsRootProperty(name="use.custom.script", value="true"),
                VcsRootProperty(name="teamcity.step.mode", value="default"),
            ]
        ),
    )
