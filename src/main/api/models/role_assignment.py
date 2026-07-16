from typing import Optional

from src.main.api.models.base_model import BaseModel


class RoleAssignmentRequest(BaseModel):
    roleId: str
    scope: str


class RoleAssignmentResponse(BaseModel):
    roleId: str
    scope: str
    href: Optional[str] = None


class RoleAssignmentsResponse(BaseModel):
    role: list[RoleAssignmentResponse]
