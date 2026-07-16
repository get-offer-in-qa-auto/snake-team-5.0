from typing import Optional

from src.main.api.models.create_build_step_request import BuildStepProperties
from src.main.api.models.base_model import BaseModel


class BuildStepResponse(BaseModel):
    id: str
    name: str
    type: str
    disabled: Optional[bool] = None
    properties: Optional[BuildStepProperties] = None


class BuildStepsResponse(BaseModel):
    count: int
    step: list[BuildStepResponse]