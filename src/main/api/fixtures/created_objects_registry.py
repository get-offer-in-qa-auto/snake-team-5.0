from collections.abc import Callable
from typing import Any

from src.main.api.models.build_configuration_response import (
    BuildConfigurationResponse,
)
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.user_token import UserTokenResponse


class CreatedObjectsRegistry(list[Any]):
    """Track created entities and remove records deleted by test actions."""

    def unregister_project(self, project_id: str) -> None:
        deleted_project_ids = self._registered_project_tree(project_id)
        self._discard(
            lambda obj: (
                (isinstance(obj, ProjectResponse) and obj.id in deleted_project_ids)
                or (
                    isinstance(obj, BuildConfigurationResponse)
                    and self._build_configuration_project_id(obj) in deleted_project_ids
                )
            )
        )

    def unregister_build_configuration(self, build_configuration_id: str) -> None:
        normalized_id = build_configuration_id.removeprefix("id:")
        self._discard(
            lambda obj: (
                isinstance(obj, BuildConfigurationResponse) and obj.id == normalized_id
            )
        )

    def unregister_user(self, user_id_or_username: int | str) -> None:
        deleted_usernames = {
            obj.username
            for obj in self
            if isinstance(obj, (CreateUserRequest, CreateUserResponse))
            and self._user_matches_locator(obj, user_id_or_username)
        }
        self._discard(
            lambda obj: (
                (
                    isinstance(obj, (CreateUserRequest, CreateUserResponse))
                    and self._user_matches_locator(obj, user_id_or_username)
                )
                or (
                    isinstance(obj, UserTokenResponse)
                    and obj.username in deleted_usernames
                )
            )
        )

    def unregister_user_token(self, username: str, token_name: str) -> None:
        self._discard(
            lambda obj: (
                isinstance(obj, UserTokenResponse)
                and obj.username == username
                and obj.name == token_name
            )
        )

    def _discard(self, predicate: Callable[[Any], bool]) -> None:
        self[:] = [obj for obj in self if not predicate(obj)]

    def _registered_project_tree(self, project_id: str) -> set[str]:
        project_ids = {project_id.removeprefix("id:")}

        while True:
            child_ids = {
                obj.id
                for obj in self
                if isinstance(obj, ProjectResponse)
                and self._parent_project_id(obj) in project_ids
            }
            if child_ids <= project_ids:
                return project_ids
            project_ids.update(child_ids)

    @staticmethod
    def _parent_project_id(project: ProjectResponse) -> str | None:
        if project.parentProject is None:
            return None
        if project.parentProject.id is not None:
            return project.parentProject.id.removeprefix("id:")
        if project.parentProject.locator is not None:
            return project.parentProject.locator.removeprefix("id:")
        return None

    @staticmethod
    def _build_configuration_project_id(
        configuration: BuildConfigurationResponse,
    ) -> str | None:
        project_id = configuration.projectId
        if project_id is None and configuration.project is not None:
            project_id = configuration.project.id
        return project_id.removeprefix("id:") if project_id is not None else None

    @staticmethod
    def _user_matches_locator(
        user: CreateUserRequest | CreateUserResponse,
        user_id_or_username: int | str,
    ) -> bool:
        user_id = getattr(user, "id", None)
        if isinstance(user_id_or_username, int):
            return user_id == user_id_or_username
        if user_id_or_username.startswith("id:"):
            return (
                user_id is not None
                and str(user_id) == user_id_or_username.removeprefix("id:")
            )
        if user_id_or_username.startswith("username:"):
            return user.username == user_id_or_username.removeprefix("username:")
        return user.username == user_id_or_username
