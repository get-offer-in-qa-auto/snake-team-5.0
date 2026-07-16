from typing import Optional
from pydantic import Field
from src.main.api.models.base_model import BaseModel


class BuildStepProperty(BaseModel):
    name: str
    value: str


class BuildStepProperties(BaseModel):
    property: list[BuildStepProperty] = Field(default_factory=list)


class CreateBuildStepRequest(BaseModel):
    name: str
    type: str
    properties: BuildStepProperties
    disabled: Optional[bool] = None