from typing import List, Optional

from src.main.api.models.base_model import BaseModel
from src.main.api.models.build_step_request import BuildStepProperties


class BuildStepResponse(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    properties: Optional[BuildStepProperties] = None


class BuildStepsResponse(BaseModel):
    step: List[BuildStepResponse] = []
