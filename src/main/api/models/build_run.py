from enum import StrEnum

from src.main.api.models.base_model import BaseModel


class BuildState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"


class BuildStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"


class BuildRunResponse(BaseModel):
    id: int
    state: BuildState
    status: BuildStatus | None = None
    buildTypeId: str | None = None
    statusText: str | None = None
