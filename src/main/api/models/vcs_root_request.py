from typing import Annotated, List

from pydantic import Field

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel


class VcsRootProjectRequest(BaseModel):
    id: str


class VcsRootProperty(BaseModel):
    name: str
    value: str


class VcsRootProperties(BaseModel):
    property: List[VcsRootProperty]


class CreateVcsRootRequest(BaseModel):
    id: Annotated[str, GeneratingRule(regex=r"^AutotestApiVcs[A-Za-z0-9]{8}$")]
    name: Annotated[str, GeneratingRule(regex=r"^AutotestApiVcs[A-Za-z0-9]{8}$")]
    vcsName: str = "jetbrains.git"
    project: VcsRootProjectRequest
    properties: VcsRootProperties = Field(default_factory=lambda: VcsRootProperties(
        property=[
            VcsRootProperty(
                name="url",
                value="https://github.com/get-offer-in-qa-auto/snake-team-5.0.git",
            ),
            VcsRootProperty(name="branch", value="refs/heads/main"),
            VcsRootProperty(name="authMethod", value="ANONYMOUS"),
        ]
    ))
