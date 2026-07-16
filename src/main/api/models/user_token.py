from typing import Annotated

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel


class CreateUserTokenRequest(BaseModel):
    name: Annotated[str, GeneratingRule(regex=r"^autotesttoken[A-Za-z0-9]{8}$")]


class UserTokenResponse(BaseModel):
    name: str
    value: str | None = None
    creationTime: str | None = None
    username: str | None = None
    password: str | None = None


class UserTokensResponse(BaseModel):
    count: int
    token: list[UserTokenResponse]
