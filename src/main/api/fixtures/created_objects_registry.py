from collections.abc import Callable
from typing import Any

from src.main.api.constants.teamcity import TeamCityLocator
from src.main.api.models.build_configuration_response import (
    BuildConfigurationResponse,
)
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
        normalized_id = TeamCityLocator.id_value(build_configuration_id)
        self._discard(
            lambda obj: (
                isinstance(obj, BuildConfigurationResponse) and obj.id == normalized_id
            )
        )

    def unregister_user(self, user_id_or_username: int | str) -> None:
        deleted_usernames = {
            obj.username
            for obj in self
            if isinstance(obj, CreateUserResponse)
            and self._user_matches_locator(obj, user_id_or_username)
        }
        self._discard(
            lambda obj: (
                (
                    isinstance(obj, CreateUserResponse)
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
        project_ids = {TeamCityLocator.id_value(project_id)}

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
            return TeamCityLocator.id_value(project.parentProject.id)
        if project.parentProject.locator is not None:
            return TeamCityLocator.id_value(project.parentProject.locator)
        return None

    @staticmethod
    def _build_configuration_project_id(
        configuration: BuildConfigurationResponse,
    ) -> str | None:
        project_id = configuration.projectId
        if project_id is None and configuration.project is not None:
            project_id = configuration.project.id
        return TeamCityLocator.id_value(project_id) if project_id is not None else None

    @staticmethod
    def _user_matches_locator(
        user: CreateUserResponse, user_id_or_username: int | str
    ) -> bool:
        if isinstance(user_id_or_username, int):
            return user.id == user_id_or_username
        if TeamCityLocator.is_id(user_id_or_username):
            return str(user.id) == TeamCityLocator.id_value(user_id_or_username)
        if TeamCityLocator.is_username(user_id_or_username):
            return user.username == TeamCityLocator.username_value(user_id_or_username)
        return user.username == user_id_or_username
