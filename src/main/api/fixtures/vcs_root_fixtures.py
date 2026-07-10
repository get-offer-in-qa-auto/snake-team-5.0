import os
from typing import Annotated

import pytest

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.base_model import BaseModel
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.vcs_root_request import (
    CreateVcsRootRequest,
    VcsRootProjectRequest,
    VcsRootProperties,
    VcsRootProperty,
)


class GeneratedVcsRootIdentity(BaseModel):
    id: Annotated[str, GeneratingRule(regex=r"^AutotestApiVcs[A-Za-z0-9]{8}$")]
    name: Annotated[str, GeneratingRule(regex=r"^AutotestApiVcs[A-Za-z0-9]{8}$")]


@pytest.fixture(scope="function")
def vcs_root_request(project_request: CreateProjectRequest) -> CreateVcsRootRequest:
    generated_vcs_root = RandomModelGenerator.generate(GeneratedVcsRootIdentity)
    return CreateVcsRootRequest(
        id=generated_vcs_root.id,
        name=generated_vcs_root.id,
        vcsName="jetbrains.git",
        project=VcsRootProjectRequest(id=project_request.id),
        properties=VcsRootProperties(
            property=[
                VcsRootProperty(
                    name="url",
                    value=os.getenv(
                        "TEAMCITY_REPOSITORY_URL",
                        "https://github.com/get-offer-in-qa-auto/snake-team-5.0.git",
                    ),
                ),
                VcsRootProperty(
                    name="branch",
                    value=os.getenv("TEAMCITY_REPOSITORY_BRANCH", "refs/heads/main"),
                ),
                VcsRootProperty(
                    name="authMethod",
                    value=os.getenv("TEAMCITY_VCS_AUTH_METHOD", "ANONYMOUS"),
                ),
            ]
        ),
    )
