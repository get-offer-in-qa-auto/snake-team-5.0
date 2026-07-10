from typing import Optional

from src.main.api.models.base_model import BaseModel
from src.main.api.models.project_response import ProjectReferenceResponse


class BuildConfigurationResponse(BaseModel):
    id: str
    name: str
    href: Optional[str] = None
    project: Optional[ProjectReferenceResponse] = None
