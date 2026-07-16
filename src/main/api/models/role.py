from enum import Enum


class Role(str, Enum):
    PROJECT_VIEWER = "PROJECT_VIEWER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class RoleScope:
    GLOBAL = "g"

    @staticmethod
    def project(project_id: str) -> str:
        return f"p:{project_id}"
