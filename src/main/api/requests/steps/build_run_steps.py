import time

import allure
import requests

from src.main.api.configs.config import Config
from src.main.api.constants.teamcity import TeamCityLocator
from src.main.api.models.build_run import BuildRunResponse, BuildState, BuildStatus
from src.main.api.models.start_build_request import (
    BuildCancelRequest,
    BuildProperties,
    BuildProperty,
    BuildTypeReference,
    StartBuildRequest,
)
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import (
    ValidatedCrudRequester,
)
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


class BuildRunSteps:
    timeout_seconds = 90
    poll_interval_seconds = 1

    @allure.step("Queue build configuration {build_configuration_id}")
    def start(
        self, build_configuration_id: str, parameters: dict[str, str] | None = None
    ) -> BuildRunResponse:
        properties = (
            BuildProperties(
                property=[
                    BuildProperty(name=name, value=value)
                    for name, value in parameters.items()
                ]
            )
            if parameters
            else None
        )
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.START_BUILD_RUN,
            ResponseSpecs.entity_was_created_or_ok(),
        ).post(
            StartBuildRequest(
                buildType=BuildTypeReference(id=build_configuration_id),
                properties=properties,
            )
        )

    @allure.step("Get build {build_id}")
    def get(self, build_id: int) -> BuildRunResponse:
        return ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.GET_BUILD_RUN,
            ResponseSpecs.request_returns_ok(),
        ).get(TeamCityLocator.ID.build(build_id))

    @allure.step("Wait until build {build_id} reaches {expected_state}")
    def wait_for_state(
        self, build_id: int, expected_state: BuildState
    ) -> BuildRunResponse:
        deadline = time.monotonic() + self.timeout_seconds
        last_build: BuildRunResponse | None = None
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                last_build = self.get(build_id)
                if last_build.state == expected_state:
                    return last_build
            except (AssertionError, requests.RequestException) as error:
                last_error = error
            time.sleep(self.poll_interval_seconds)
        raise AssertionError(
            f"Build {build_id} did not reach state {expected_state!r}. "
            f"Last build: {last_build}; last error: {last_error}"
        )

    def wait_until_finished(self, build_id: int) -> BuildRunResponse:
        return self.wait_for_state(build_id, BuildState.FINISHED)

    @allure.step("Wait until an authorized TeamCity agent is idle")
    def wait_for_agent_idle(self) -> None:
        deadline = time.monotonic() + self.timeout_seconds
        last_agents: list[dict] = []
        last_error: Exception | None = None
        request_timeout = int(Config.get("TEAMCITY_REQUEST_TIMEOUT", "20"))
        idle_activity: dict[int, str | None] = {}

        while time.monotonic() < deadline:
            try:
                response = requests.get(
                    f"{RequestSpecs._base_url()}/agents",
                    params={
                        "fields": (
                            "agent(id,connected,enabled,authorized,lastActivityTime,"
                            "currentBuild(id))"
                        )
                    },
                    headers=RequestSpecs.admin_auth_spec(csrf=False),
                    timeout=request_timeout,
                )
                response.raise_for_status()
                last_agents = response.json().get("agent", [])
                for agent in last_agents:
                    raw_agent_id = agent.get("id")
                    if not isinstance(raw_agent_id, int):
                        continue
                    agent_id = raw_agent_id
                    is_idle = (
                        agent.get("connected")
                        and agent.get("enabled")
                        and agent.get("authorized")
                        and not agent.get("currentBuild")
                    )
                    if not is_idle:
                        idle_activity.pop(agent_id, None)
                        continue

                    activity = agent.get("lastActivityTime")
                    previous_activity = idle_activity.setdefault(agent_id, activity)
                    if activity != previous_activity:
                        return
            except (ValueError, requests.RequestException) as error:
                last_error = error
            time.sleep(self.poll_interval_seconds)

        raise AssertionError(
            "No authorized TeamCity agent became idle. "
            f"Last agents: {last_agents}; last error: {last_error}"
        )

    @allure.step("Cancel running build {build_id}")
    def cancel(self, build_id: int, comment: str) -> None:
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.CANCEL_BUILD_RUN,
            ResponseSpecs.entity_was_created_or_ok(),
        ).post(
            BuildCancelRequest(comment=comment),
            path=TeamCityLocator.ID.build(build_id),
        )

    @allure.step("Get plain-text log for build {build_id}")
    def get_log(self, build_id: int) -> str:
        response = requests.get(
            f"{RequestSpecs._server_url()}/downloadBuildLog.html",
            params={"buildId": str(build_id), "plain": "true"},
            headers=RequestSpecs.admin_auth_spec(csrf=False),
            timeout=20,
        )
        response.raise_for_status()
        return response.text

    @allure.step("Verify build result")
    def verify_result(
        self,
        build: BuildRunResponse,
        expected_status: BuildStatus,
        expected_log_text: str | None = None,
    ) -> None:
        assert build.status == expected_status
        if expected_log_text is not None:
            assert expected_log_text in self.get_log(build.id)
