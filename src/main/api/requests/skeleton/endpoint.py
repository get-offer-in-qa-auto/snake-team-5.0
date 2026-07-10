from dataclasses import dataclass
from enum import Enum
from typing import Any, List

from src.main.api.models.build_configuration_request import BuildConfigurationRequest
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.build_step_request import CreateBuildStepRequest
from src.main.api.models.build_step_response import BuildStepResponse, BuildStepsResponse
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.vcs_root_request import CreateVcsRootRequest
from src.main.api.models.vcs_root_response import VcsRootResponse


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

    CREATE_BUILD_CONFIGURATION = EndpointConfig(
        url='/projects',
        request_model=BuildConfigurationRequest,
        response_model=BuildConfigurationResponse
    )

    GET_BUILD_CONFIGURATION = EndpointConfig(
        url='/buildTypes',
        request_model=None,
        response_model=BuildConfigurationResponse
    )

    DELETE_BUILD_CONFIGURATION = EndpointConfig(
        url='/buildTypes',
        request_model=None,
        response_model=None
    )

    CREATE_VCS_ROOT = EndpointConfig(
        url='/vcs-roots',
        request_model=CreateVcsRootRequest,
        response_model=VcsRootResponse
    )

    GET_VCS_ROOT = EndpointConfig(
        url='/vcs-roots',
        request_model=None,
        response_model=VcsRootResponse
    )

    DELETE_VCS_ROOT = EndpointConfig(
        url='/vcs-roots',
        request_model=None,
        response_model=None
    )

    CREATE_BUILD_STEP = EndpointConfig(
        url='/buildTypes',
        request_model=CreateBuildStepRequest,
        response_model=BuildStepResponse
    )

    GET_BUILD_STEPS = EndpointConfig(
        url='/buildTypes',
        request_model=None,
        response_model=BuildStepsResponse
    )
