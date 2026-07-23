from typing import Annotated

from pydantic import Field

from src.main.api.constants.teamcity import ROOT_PROJECT_ID
from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel


class ParentProjectRequest(BaseModel):
    locator: str = ROOT_PROJECT_ID


class CreateProjectRequest(BaseModel):
    id: Annotated[str, GeneratingRule(regex=r"^AutotestApiProject[A-Za-z0-9]{8}$")]
    name: Annotated[
        str, GeneratingRule(regex=r"^[A-Za-z]{4}[0-9]{2} [A-Za-z]{4} [0-9]{2}$")
    ]
    parentProject: ParentProjectRequest = Field(default_factory=ParentProjectRequest)
