import uuid

import pytest

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_build_configuration_request import (
    CreateBuildConfigurationRequest,
)
from src.main.api.models.project_response import ProjectResponse


@pytest.fixture(scope="function")
def build_configuration_request_factory():
    def create_build_configuration_request(
        build_configuration_id: str | None = None, name: str | None = None
    ) -> CreateBuildConfigurationRequest:
        generated_configuration = RandomModelGenerator.generate(
            CreateBuildConfigurationRequest
        )
        return CreateBuildConfigurationRequest(
            id=(
                build_configuration_id
                if build_configuration_id is not None
                else generated_configuration.id
            ),
            name=name if name is not None else generated_configuration.name,
        )

    return create_build_configuration_request


@pytest.fixture(scope="function")
def build_configuration_request(
    build_configuration_request_factory,
) -> CreateBuildConfigurationRequest:
    return build_configuration_request_factory()


@pytest.fixture(scope="function")
def build_configuration(
    api_manager,
    project: ProjectResponse,
    build_configuration_request: CreateBuildConfigurationRequest,
):
    return api_manager.admin_steps.create_build_configuration(
        project.id,
        build_configuration_request,
    )


@pytest.fixture(scope="function")
def nonexistent_build_configuration_id() -> str:
    return f"RandomNonexistentBuildConfiguration{uuid.uuid4().hex[:8]}"
