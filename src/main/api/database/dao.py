from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectDao:
    internal_id: str
    external_id: str
    config_id: str
    origin_project_id: str | None
    delete_time: int | None
