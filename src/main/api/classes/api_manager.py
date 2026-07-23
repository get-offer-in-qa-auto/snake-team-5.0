from src.main.api.fixtures.created_objects_registry import CreatedObjectsRegistry
from src.main.api.requests.steps.admin_steps import AdminSteps
from src.main.api.requests.steps.build_run_steps import BuildRunSteps
from src.main.api.requests.steps.configuration_steps import ConfigurationSteps
from src.main.api.requests.steps.database_steps import DatabaseSteps
from src.main.api.requests.steps.user_steps import UserSteps


class ApiManager:
    def __init__(self, created_objects: CreatedObjectsRegistry):
        self.admin_steps = AdminSteps(created_objects)
        self.build_run_steps = BuildRunSteps()
        self.configuration_steps = ConfigurationSteps()
        self.database_steps = DatabaseSteps()
        self.user_steps = UserSteps(created_objects)
