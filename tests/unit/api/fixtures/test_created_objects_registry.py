import pytest

from src.main.api.fixtures.created_objects_registry import CreatedObjectsRegistry
from src.main.api.models.project_response import ProjectResponse
from src.main.api.requests.steps import admin_steps as admin_steps_module
from src.main.api.requests.steps.admin_steps import AdminSteps


def test_failed_delete_keeps_object_registered_for_fixture_cleanup(monkeypatch):
    project = ProjectResponse(id="project", name="Project")
    created_objects = CreatedObjectsRegistry([project])

    class FailingCrudRequester:
        def __init__(self, *args, **kwargs):
            pass

        def delete(self, path):
            raise RuntimeError(f"Cannot delete {path}")

    monkeypatch.setattr(
        admin_steps_module,
        "CrudRequester",
        FailingCrudRequester,
    )
    monkeypatch.setattr(
        admin_steps_module.RequestSpecs,
        "admin_auth_spec",
        lambda: {},
    )

    with pytest.raises(RuntimeError, match="Cannot delete id:project"):
        AdminSteps(created_objects).delete_project(project.id)

    assert created_objects == [project]
