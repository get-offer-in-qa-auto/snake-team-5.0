from typing import Optional

from src.main.api.models.base_model import BaseModel


class CreateUserResponse(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    email: Optional[str] = None
    href: Optional[str] = None
    hasPassword: Optional[bool] = None
