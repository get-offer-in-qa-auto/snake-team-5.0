BUILD_CANCELLATION_COMMENT = "Cancelled by Build Run MVP autotest"
BUILD_RUNTIME_PARAMETER_NAME = "env.AUTOTEST_RUNTIME_MARKER"
ROOT_PROJECT_ID = "_Root"


class TeamCityLocator:
    @staticmethod
    def by_id(entity_id: str) -> str:
        return f"id:{entity_id}"
