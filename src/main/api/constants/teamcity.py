from enum import StrEnum

BUILD_CANCELLATION_COMMENT = "Cancelled by Build Run MVP autotest"
BUILD_RUNTIME_PARAMETER_NAME = "env.AUTOTEST_RUNTIME_MARKER"
ROOT_PROJECT_ID = "_Root"


class TeamCityLocator(StrEnum):
    ID = "id"
    USERNAME = "username"

    @classmethod
    def for_user(cls, user_id_or_username: int | str) -> str:
        if isinstance(user_id_or_username, int):
            return cls.ID.build(user_id_or_username)
        if cls._is_locator(user_id_or_username):
            return user_id_or_username
        return cls.USERNAME.build(user_id_or_username)

    @property
    def prefix(self) -> str:
        return f"{self.value}:"

    def build(self, value: int | str) -> str:
        normalized_value = str(value)
        if self._is_locator(normalized_value):
            return normalized_value
        return f"{self.prefix}{normalized_value}"

    def matches(self, locator: str) -> bool:
        return locator.startswith(self.prefix)

    def extract(self, locator_or_value: int | str) -> str:
        return str(locator_or_value).removeprefix(self.prefix)

    @staticmethod
    def _is_locator(value: str) -> bool:
        return ":" in value


class TeamCityAgentLocator(StrEnum):
    ALL_AUTHORIZATION_STATES = "authorized:any,defaultFilter:false"
