import time

import allure

from src.main.api.configs.config import Config
from src.main.api.configuration.client import (
    BuildStepConfiguration,
    TeamCityConfigurationClient,
)


class ConfigurationSteps:
    def __init__(self, client: TeamCityConfigurationClient | None = None):
        self.client = client or TeamCityConfigurationClient()
        self.timeout = float(Config.get("TEAMCITY_CONFIGURATION_TIMEOUT", "20"))

    @allure.step("Verify build step {step_id} is persisted in TeamCity configuration")
    def verify_build_step_persisted(
        self, project_id: str, build_configuration_id: str, step_id: str
    ) -> BuildStepConfiguration:
        deadline = time.monotonic() + self.timeout
        last_step: BuildStepConfiguration | None = None
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                last_step = self.client.get_build_step(
                    project_id, build_configuration_id, step_id
                )
                if last_step is not None:
                    return last_step
            except FileNotFoundError as error:
                last_error = error
            time.sleep(0.25)

        details = str(last_error) if last_error else "runner was not found in XML"
        raise AssertionError(
            f"Build step {step_id!r} was not persisted in TeamCity configuration: "
            f"{details}"
        )

    @allure.step("Verify build step {step_id} is deleted from TeamCity configuration")
    def verify_build_step_deleted(
        self, project_id: str, build_configuration_id: str, step_id: str
    ) -> None:
        deadline = time.monotonic() + self.timeout
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                if (
                    self.client.get_build_step(
                        project_id, build_configuration_id, step_id
                    )
                    is None
                ):
                    return
            except FileNotFoundError as error:
                last_error = error
            time.sleep(0.25)

        details = str(last_error) if last_error else "runner is still present in XML"
        raise AssertionError(
            f"Build step {step_id!r} was not deleted from TeamCity configuration: "
            f"{details}"
        )
