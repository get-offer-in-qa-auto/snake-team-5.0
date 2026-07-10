from typing import Optional

from src.main.api.models.base_model import BaseModel


class ProjectReferenceResponse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    locator: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    href: Optional[str] = None
    parentProject: Optional[ProjectReferenceResponse] = None
