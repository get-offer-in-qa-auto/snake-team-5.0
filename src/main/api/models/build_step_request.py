from typing import Annotated, List

from pydantic import Field

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel
from src.main.api.models.vcs_root_request import VcsRootProperty


class BuildStepProperties(BaseModel):
    property: List[VcsRootProperty]


class CreateBuildStepRequest(BaseModel):
    id: Annotated[str, GeneratingRule(regex=r"^AutotestApiStep[A-Za-z0-9]{8}$")]
    name: Annotated[str, GeneratingRule(regex=r"^AutotestApiStep[A-Za-z0-9]{8}$")]
    type: str = "simpleRunner"
    properties: BuildStepProperties = Field(default_factory=lambda: BuildStepProperties(
        property=[
            VcsRootProperty(name="script.content", value="echo autotest"),
            VcsRootProperty(name="use.custom.script", value="true"),
            VcsRootProperty(name="teamcity.step.mode", value="default"),
        ]
    ))
