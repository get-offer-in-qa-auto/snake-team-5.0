from dataclasses import dataclass
from enum import Enum
from typing import Any, List

from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.project_response import ProjectResponse


@dataclass(frozen=True)
class EndpointConfig:
    url: str
    request_model: Any
    response_model: Any


class Endpoint(Enum):
    ADMIN_GET_ALL_USERS = EndpointConfig(
        url='/users',
        request_model=None,
        response_model=List[CreateUserRequest]
    )

    CREATE_PROJECT = EndpointConfig(
        url='/projects',
        request_model=CreateProjectRequest,
        response_model=ProjectResponse
    )

    GET_PROJECT = EndpointConfig(
        url='/projects',
        request_model=None,
        response_model=ProjectResponse
    )

    DELETE_PROJECT = EndpointConfig(
        url='/projects',
        request_model=None,
        response_model=None
    )
