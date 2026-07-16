from typing import Annotated, Optional

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel


class CreateUserTokenRequest(BaseModel):
    name: Annotated[
        str,
        GeneratingRule(regex=r"^autotesttoken[A-Za-z0-9]{8}$")
    ]


class UserTokenResponse(BaseModel):
    name: str
    value: Optional[str] = None
    creationTime: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserTokensResponse(BaseModel):
    count: int
    token: list[UserTokenResponse]
