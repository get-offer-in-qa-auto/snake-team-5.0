from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.role_assignment import (
    RoleAssignmentRequest,
    RoleAssignmentResponse,
    RoleAssignmentsResponse,
)
from src.main.api.models.user_token import (
    CreateUserTokenRequest,
    UserTokenResponse,
    UserTokensResponse,
)


@dataclass(frozen=True)
class EndpointConfig:
    url: str
    request_model: Any
    response_model: Any


class Endpoint(Enum):
    ADMIN_GET_ALL_USERS = EndpointConfig(
        url="/users", request_model=None, response_model=list[CreateUserRequest]
    )

    CREATE_PROJECT = EndpointConfig(
        url="/projects",
        request_model=CreateProjectRequest,
        response_model=ProjectResponse,
    )

    GET_PROJECT = EndpointConfig(
        url="/projects", request_model=None, response_model=ProjectResponse
    )

    DELETE_PROJECT = EndpointConfig(
        url="/projects", request_model=None, response_model=None
    )

    CREATE_USER = EndpointConfig(
        url="/users", request_model=CreateUserRequest, response_model=CreateUserResponse
    )

    GET_USER = EndpointConfig(
        url="/users", request_model=None, response_model=CreateUserResponse
    )

    DELETE_USER = EndpointConfig(url="/users", request_model=None, response_model=None)

    CREATE_USER_TOKEN = EndpointConfig(
        url="/users",
        request_model=CreateUserTokenRequest,
        response_model=UserTokenResponse,
    )

    GET_USER_TOKENS = EndpointConfig(
        url="/users", request_model=None, response_model=UserTokensResponse
    )

    DELETE_USER_TOKEN = EndpointConfig(
        url="/users", request_model=None, response_model=None
    )

    ASSIGN_USER_ROLE = EndpointConfig(
        url="/users",
        request_model=RoleAssignmentRequest,
        response_model=RoleAssignmentResponse,
    )

    GET_USER_ROLES = EndpointConfig(
        url="/users", request_model=None, response_model=RoleAssignmentsResponse
    )

    CREATE_BUILD_CONFIGURATION = EndpointConfig(
        url="/projects",
        request_model=CreateBuildConfigurationRequest,
        response_model=BuildConfigurationResponse,
    )

    GET_BUILD_CONFIGURATION = EndpointConfig(
        url="/buildTypes", request_model=None, response_model=BuildConfigurationResponse
    )

    DELETE_BUILD_CONFIGURATION = EndpointConfig(
        url="/buildTypes", request_model=None, response_model=None
    )
