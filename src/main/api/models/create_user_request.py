from typing import Annotated

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel


class CreateUserRequest(BaseModel):
    username: Annotated[str, GeneratingRule(regex=r"^autotestuser[a-z0-9]{8}$")]
    password: Annotated[str, GeneratingRule(regex=r"^[A-Z]{3}[a-z]{4}[0-9]{3}[$%&]{2}$")]
    name: Annotated[str, GeneratingRule(regex=r"^[A-Za-z]{4}[0-9]{2} [A-Za-z]{4} [0-9]{2}$")]
