from types import SimpleNamespace

from src.main.api.models.project_response import ProjectResponse
from src.main.api.utils import cleanup_helper


def test_cleanup_continues_after_a_failed_object_deletion(monkeypatch):
    deleted_ids: list[str] = []

    class FakeAdminSteps:
        def delete_project(self, project_id: str) -> None:
            deleted_ids.append(project_id)
            if project_id == "second":
                raise RuntimeError("TeamCity is unavailable")

    monkeypatch.setattr(
        cleanup_helper,
        "ApiManager",
        lambda _: SimpleNamespace(admin_steps=FakeAdminSteps()),
    )
    objects = [
        ProjectResponse(id="first", name="First"),
        ProjectResponse(id="second", name="Second"),
    ]

    failures = cleanup_helper.cleanup_objects(objects)

    assert deleted_ids == ["second", "first"]
    assert len(failures) == 1
    assert failures[0].object_type == "ProjectResponse"
    assert failures[0].object_id == "second"
    assert "RuntimeError: TeamCity is unavailable" == failures[0].error


def test_cleanup_returns_each_failure(monkeypatch):
    class FakeAdminSteps:
        def delete_project(self, project_id: str) -> None:
            raise RuntimeError(f"Cannot delete {project_id}")

    monkeypatch.setattr(
        cleanup_helper,
        "ApiManager",
        lambda _: SimpleNamespace(admin_steps=FakeAdminSteps()),
    )
    objects = [
        ProjectResponse(id="first", name="First"),
        ProjectResponse(id="second", name="Second"),
    ]

    failures = cleanup_helper.cleanup_objects(objects)

    assert [failure.object_id for failure in failures] == ["second", "first"]
    assert all("RuntimeError: Cannot delete" in failure.error for failure in failures)


def test_cleanup_uses_snapshot_when_delete_steps_unregister_objects(monkeypatch):
    deleted_ids: list[str] = []
    objects = [
        ProjectResponse(id="first", name="First"),
        ProjectResponse(id="second", name="Second"),
    ]

    class FakeAdminSteps:
        def delete_project(self, project_id: str) -> None:
            deleted_ids.append(project_id)
            objects[:] = [obj for obj in objects if obj.id != project_id]

    monkeypatch.setattr(
        cleanup_helper,
        "ApiManager",
        lambda _: SimpleNamespace(admin_steps=FakeAdminSteps()),
    )

    failures = cleanup_helper.cleanup_objects(objects)

    assert failures == []
    assert deleted_ids == ["second", "first"]
    assert objects == []
