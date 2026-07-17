from src.main.api.models.base_model import BaseModel
from src.main.api.models.project_response import ProjectReferenceResponse


class BuildConfigurationResponse(BaseModel):
    id: str
    name: str
    href: str | None = None
    projectId: str | None = None
    project: ProjectReferenceResponse | None = None
