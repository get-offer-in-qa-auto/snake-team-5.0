import pytest

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_project_request import (
    CreateProjectRequest,
    ParentProjectRequest,
)


@pytest.fixture(scope="function")
def project_request() -> CreateProjectRequest:
    generated_project = RandomModelGenerator.generate(CreateProjectRequest)
    return CreateProjectRequest(
        id=generated_project.id,
        name=generated_project.id,
        parentProject=ParentProjectRequest(locator="_Root"),
    )
