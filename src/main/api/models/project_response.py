from src.main.api.models.base_model import BaseModel


class ProjectReferenceResponse(BaseModel):
    id: str | None = None
    name: str | None = None
    locator: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    href: str | None = None
    parentProject: ProjectReferenceResponse | None = None
