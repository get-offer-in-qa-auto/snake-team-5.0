from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_build_step_request import BuildStepProperties


class BuildStepResponse(BaseModel):
    id: str
    name: str
    type: str
    disabled: bool | None = None
    properties: BuildStepProperties | None = None


class BuildStepsResponse(BaseModel):
    count: int
    step: list[BuildStepResponse]
