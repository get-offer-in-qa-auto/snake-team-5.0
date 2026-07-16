from src.main.api.models.base_model import BaseModel


class CreateUserResponse(BaseModel):
    id: int
    username: str
    name: str | None = None
    email: str | None = None
    href: str | None = None
    hasPassword: bool | None = None
