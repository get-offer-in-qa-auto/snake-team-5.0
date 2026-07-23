import pytest

from src.main.api.fixtures.created_objects_registry import CreatedObjectsRegistry
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.user_token import UserTokenResponse
from src.main.api.requests.steps import admin_steps as admin_steps_module
from src.main.api.requests.steps import user_steps as user_steps_module
from src.main.api.requests.steps.admin_steps import AdminSteps
from src.main.api.requests.steps.user_steps import UserSteps


def test_delete_user_token_unregisters_only_matching_token(monkeypatch):
    deleted_paths = _stub_successful_delete(monkeypatch, user_steps_module)
    deleted_token = UserTokenResponse(name="deleted-token", username="user")
    retained_token = UserTokenResponse(name="retained-token", username="user")
    created_objects = CreatedObjectsRegistry([deleted_token, retained_token])

    UserSteps(created_objects).delete_user_token(
        username="user",
        password="password",
        token_name=deleted_token.name,
    )

    assert deleted_paths == ["username:user/tokens/deleted-token"]
    assert created_objects == [retained_token]


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


def _stub_successful_delete(monkeypatch, module) -> list[str]:
    deleted_paths: list[str] = []

    class SuccessfulCrudRequester:
        def __init__(self, *args, **kwargs):
            pass

        def delete(self, path):
            deleted_paths.append(path)

    monkeypatch.setattr(module, "CrudRequester", SuccessfulCrudRequester)
    monkeypatch.setattr(module.RequestSpecs, "admin_auth_spec", lambda: {})
    monkeypatch.setattr(
        module.RequestSpecs,
        "auth_as_user",
        lambda *args, **kwargs: {},
    )
    return deleted_paths
