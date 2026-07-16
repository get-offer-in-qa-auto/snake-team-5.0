import pytest

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_project_request import (
    CreateProjectRequest,
    ParentProjectRequest,
)


@pytest.fixture(scope="function")
def project_request_factory():
    def create_project_request(
        project_id: str | None = None,
        name: str | None = None,
        parent_locator: str = "_Root",
    ) -> CreateProjectRequest:
        generated_project = RandomModelGenerator.generate(CreateProjectRequest)
        return CreateProjectRequest(
            id=project_id if project_id is not None else generated_project.id,
            name=name if name is not None else generated_project.name,
            parentProject=ParentProjectRequest(locator=parent_locator),
        )

    return create_project_request


@pytest.fixture(scope="function")
def project_request(project_request_factory) -> CreateProjectRequest:
    return project_request_factory()


@pytest.fixture(scope="function")
def project(api_manager, project_request):
    return api_manager.admin_steps.create_project(project_request)
