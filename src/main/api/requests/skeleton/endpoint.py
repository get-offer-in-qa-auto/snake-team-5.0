from dataclasses import dataclass
from enum import Enum
from typing import List

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.base_model import BaseModel


@dataclass(frozen=True)
class EndpointConfig:
    url: str
    request_model: BaseModel
    response_model: BaseModel


class Endpoint(Enum):
    ADMIN_GET_ALL_USERS = EndpointConfig(
        url='/users',
        request_model=None,
        response_model=List[CreateUserRequest]
    )

