import pytest

from src.main.api.fixtures.created_objects_registry import CreatedObjectsRegistry
from src.main.api.models.build_configuration_response import (
    BuildConfigurationResponse,
)
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import (
    ProjectReferenceResponse,
    ProjectResponse,
)
from src.main.api.models.user_token import UserTokenResponse
from src.main.api.requests.steps import admin_steps as admin_steps_module
from src.main.api.requests.steps import user_steps as user_steps_module
from src.main.api.requests.steps.admin_steps import AdminSteps
from src.main.api.requests.steps.user_steps import UserSteps


def test_delete_project_unregisters_project_tree_and_its_configurations(
    monkeypatch,
):
    deleted_paths = _stub_successful_delete(monkeypatch, admin_steps_module)
    parent = ProjectResponse(id="parent", name="Parent")
    child = ProjectResponse(
        id="child",
        name="Child",
        parentProject=ProjectReferenceResponse(id=parent.id),
    )
    parent_configuration = BuildConfigurationResponse(
        id="parent-build",
        name="Parent Build",
        projectId=parent.id,
    )
    child_configuration = BuildConfigurationResponse(
        id="child-build",
        name="Child Build",
        projectId=child.id,
    )
    unrelated_project = ProjectResponse(id="other", name="Other")
    unrelated_configuration = BuildConfigurationResponse(
        id="other-build",
        name="Other Build",
        projectId=unrelated_project.id,
    )
    created_objects = CreatedObjectsRegistry(
        [
            parent,
            child,
            parent_configuration,
            child_configuration,
            unrelated_project,
            unrelated_configuration,
        ]
    )

    AdminSteps(created_objects).delete_project(parent.id)

    assert deleted_paths == ["id:parent"]
    assert created_objects == [unrelated_project, unrelated_configuration]


def test_delete_build_configuration_unregisters_only_deleted_configuration(
    monkeypatch,
):
    deleted_paths = _stub_successful_delete(monkeypatch, admin_steps_module)
    deleted_configuration = BuildConfigurationResponse(
        id="deleted-build",
        name="Deleted Build",
    )
    retained_configuration = BuildConfigurationResponse(
        id="retained-build",
        name="Retained Build",
    )
    created_objects = CreatedObjectsRegistry(
        [deleted_configuration, retained_configuration]
    )

    AdminSteps(created_objects).delete_build_configuration(
        f"id:{deleted_configuration.id}"
    )

    assert deleted_paths == ["id:deleted-build"]
    assert created_objects == [retained_configuration]


def test_delete_user_unregisters_user_and_owned_tokens(monkeypatch):
    deleted_paths = _stub_successful_delete(monkeypatch, admin_steps_module)
    deleted_user = CreateUserResponse(id=1, username="deleted")
    deleted_user_token = UserTokenResponse(name="token", username="deleted")
    retained_user = CreateUserResponse(id=2, username="retained")
    retained_user_token = UserTokenResponse(name="token", username="retained")
    created_objects = CreatedObjectsRegistry(
        [
            deleted_user,
            deleted_user_token,
            retained_user,
            retained_user_token,
        ]
    )

    AdminSteps(created_objects).delete_user(deleted_user.id)

    assert deleted_paths == ["id:1"]
    assert created_objects == [retained_user, retained_user_token]


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
