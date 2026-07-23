import uuid
from dataclasses import dataclass, field

from src.main.api.constants.teamcity import (
    BUILD_CANCELLATION_COMMENT,
    BUILD_RUNTIME_PARAMETER_NAME,
)
from src.main.api.models.build_run import BuildState, BuildStatus


@dataclass(frozen=True)
class BuildRunScenario:
    script: str
    expected_status: BuildStatus
    expected_log_text: str | None = None
    parameters: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CancellableBuildRunScenario:
    script: str
    expected_status: BuildStatus
    state_to_wait_for: BuildState
    cancellation_comment: str


class BuildRunData:
    @staticmethod
    def successful() -> BuildRunScenario:
        marker = f"BUILD_RUN_SUCCESS_{uuid.uuid4().hex}"
        return BuildRunScenario(
            script=f"echo {marker}",
            expected_status=BuildStatus.SUCCESS,
            expected_log_text=marker,
        )

    @staticmethod
    def failed() -> BuildRunScenario:
        marker = f"BUILD_RUN_FAILURE_{uuid.uuid4().hex}"
        return BuildRunScenario(
            script=f"echo {marker}; exit 1",
            expected_status=BuildStatus.FAILURE,
            expected_log_text=marker,
        )

    @staticmethod
    def with_runtime_parameter() -> BuildRunScenario:
        parameter_reference = f"%{BUILD_RUNTIME_PARAMETER_NAME}%"
        marker = uuid.uuid4().hex
        return BuildRunScenario(
            script=f"echo RUNTIME={parameter_reference}",
            expected_status=BuildStatus.SUCCESS,
            expected_log_text=f"RUNTIME={marker}",
            parameters={BUILD_RUNTIME_PARAMETER_NAME: marker},
        )

    @staticmethod
    def cancellable(duration_seconds: int = 30) -> CancellableBuildRunScenario:
        return CancellableBuildRunScenario(
            script=f"sleep {duration_seconds}",
            expected_status=BuildStatus.UNKNOWN,
            state_to_wait_for=BuildState.RUNNING,
            cancellation_comment=BUILD_CANCELLATION_COMMENT,
        )
