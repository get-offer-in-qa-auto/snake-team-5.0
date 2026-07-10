from typing import Optional

from src.main.api.models.base_model import BaseModel
from src.main.api.models.project_response import ProjectReferenceResponse
from src.main.api.models.vcs_root_request import VcsRootProperties


class VcsRootResponse(BaseModel):
    id: str
    name: str
    vcsName: str
    href: Optional[str] = None
    project: Optional[ProjectReferenceResponse] = None
    properties: Optional[VcsRootProperties] = None
