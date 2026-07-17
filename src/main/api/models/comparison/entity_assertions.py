from typing import Any


class EntityAssertions:
    @staticmethod
    def has_href(entity: Any) -> Any:
        href = getattr(entity, "href", None)
        assert href, f"{entity.__class__.__name__}.href is falsy: {entity}"
        return entity

    @staticmethod
    def has_id(entity: Any) -> Any:
        entity_id = getattr(entity, "id", None)
        assert entity_id, f"{entity.__class__.__name__}.id is falsy: {entity}"
        return entity

    @staticmethod
    def has_parent_project(project: Any, expected_parent_id: str) -> Any:
        parent = getattr(project, "parentProject", None)
        assert parent is not None, (
            f"{project.__class__.__name__}.parentProject is missing: {project}"
        )
        assert parent.id == expected_parent_id, (
            f"Parent project mismatch: expected={expected_parent_id!r}, "
            f"actual={parent.id!r}"
        )
        return project

    @staticmethod
    def belongs_to_project(entity: Any, expected_project_id: str) -> Any:
        project = getattr(entity, "project", None)
        assert project is not None, (
            f"{entity.__class__.__name__}.project is missing: {entity}"
        )
        assert project.id == expected_project_id, (
            f"Project mismatch: expected={expected_project_id!r}, actual={project.id!r}"
        )
        return entity
