import logging
from typing import Any

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.build_configuration_response import BuildConfigurationResponse
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import ProjectResponse
from src.main.api.models.user_token import UserTokenResponse


def cleanup_objects(objects: list[Any]):
    api_manager = ApiManager(objects)
    for obj in reversed(objects):
        if isinstance(obj, UserTokenResponse):
            if obj.username is None or obj.password is None:
                logging.warning("Cannot clean up token without user credentials")
                continue
            api_manager.user_steps.delete_user_token(
                obj.username, obj.password, obj.name
            )
        elif isinstance(obj, CreateUserResponse):
            api_manager.admin_steps.delete_user(obj.id)
        elif isinstance(obj, BuildConfigurationResponse):
            api_manager.admin_steps.delete_build_configuration(obj.id)
        elif isinstance(obj, ProjectResponse):
            api_manager.admin_steps.delete_project(obj.id)
        else:
            logging.warning(f"Object type: {type(obj)} is not deleted")
