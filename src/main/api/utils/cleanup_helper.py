import logging
import traceback
from dataclasses import dataclass
from typing import Any

from src.main.api.classes.api_manager import ApiManager
from src.main.api.fixtures.created_objects_registry import CreatedObjectsRegistry
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.user_token import UserTokenResponse


@dataclass(frozen=True)
class CleanupFailure:
    object_type: str
    object_id: str
    error: str
    traceback: str


def cleanup_objects(objects: CreatedObjectsRegistry) -> list[CleanupFailure]:
    """Clean up all registered objects and return every cleanup failure.

    Cleanup runs in reverse creation order so dependent objects are removed
    before their parents. A failure for one object must not leave the rest of
    the test data behind.
    """
    api_manager = ApiManager(objects)
    failures: list[CleanupFailure] = []
    # Delete steps unregister successfully removed entities, so iterate over a
    # stable snapshot instead of the mutable cleanup registry itself.
    for obj in reversed(objects.copy()):
        try:
            _cleanup_object(api_manager, obj)
        except Exception as error:
            failure = CleanupFailure(
                object_type=type(obj).__name__,
                object_id=_object_id(obj),
                error=f"{type(error).__name__}: {error}",
                traceback=traceback.format_exc(),
            )
            failures.append(failure)
            logging.exception(
                "Failed to clean up %s %s", failure.object_type, failure.object_id
            )
    return failures


def _cleanup_object(api_manager: ApiManager, obj: Any) -> None:
    if isinstance(obj, UserTokenResponse):
        if obj.username is None or obj.password is None:
            raise ValueError("Token has no credentials required for cleanup")
        api_manager.user_steps.delete_user_token(obj.username, obj.password, obj.name)
    elif isinstance(obj, CreateUserRequest):
        api_manager.admin_steps.delete_user_if_exists(obj.username)
    elif isinstance(obj, CreateUserResponse):
        api_manager.admin_steps.delete_user(obj.id)
    elif isinstance(obj, BuildConfigurationResponse):
        api_manager.admin_steps.delete_build_configuration(obj.id)
    elif isinstance(obj, CreateProjectRequest):
        api_manager.admin_steps.delete_project_if_exists(obj.id)
    elif isinstance(obj, ProjectResponse):
        api_manager.admin_steps.delete_project(obj.id)
    else:
        logging.warning("Object type %s is not deleted", type(obj).__name__)


def _object_id(obj: Any) -> str:
    for field_name in ("id", "name", "username"):
        value = getattr(obj, field_name, None)
        if value is not None:
            return str(value)
    return repr(obj)
