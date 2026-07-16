from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectDao:
    internal_id: str
    external_id: str
    config_id: str
    origin_project_id: str | None
    delete_time: int | None


@dataclass(frozen=True)
class BuildConfigurationDao:
    internal_id: str
    external_id: str
    config_id: str
    origin_project_id: str | None
    delete_time: int | None


@dataclass(frozen=True)
class UserDao:
    id: int
    username: str
    name: str | None
    email: str | None
    last_login_timestamp: int | None
    algorithm: str | None
