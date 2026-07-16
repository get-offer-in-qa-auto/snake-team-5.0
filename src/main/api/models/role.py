from enum import StrEnum


class Role(StrEnum):
    PROJECT_VIEWER = "PROJECT_VIEWER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class RoleScope:
    GLOBAL = "g"

    @staticmethod
    def project(project_id: str) -> str:
        return f"p:{project_id}"
