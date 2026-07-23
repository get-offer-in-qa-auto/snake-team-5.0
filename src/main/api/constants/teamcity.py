BUILD_CANCELLATION_COMMENT = "Cancelled by Build Run MVP autotest"
BUILD_RUNTIME_PARAMETER_NAME = "env.AUTOTEST_RUNTIME_MARKER"
ROOT_PROJECT_ID = "_Root"


class TeamCityLocator:
    _ID_PREFIX = "id:"
    _USERNAME_PREFIX = "username:"

    @classmethod
    def by_id(cls, entity_id: int | str) -> str:
        return cls._with_prefix(entity_id, cls._ID_PREFIX)

    @classmethod
    def by_username(cls, username: str) -> str:
        return cls._with_prefix(username, cls._USERNAME_PREFIX)

    @classmethod
    def for_user(cls, user_id_or_username: int | str) -> str:
        if isinstance(user_id_or_username, int):
            return cls.by_id(user_id_or_username)
        if cls._is_locator(user_id_or_username):
            return user_id_or_username
        return cls.by_username(user_id_or_username)

    @classmethod
    def is_id(cls, locator: str) -> bool:
        return locator.startswith(cls._ID_PREFIX)

    @classmethod
    def is_username(cls, locator: str) -> bool:
        return locator.startswith(cls._USERNAME_PREFIX)

    @classmethod
    def id_value(cls, locator_or_id: int | str) -> str:
        return str(locator_or_id).removeprefix(cls._ID_PREFIX)

    @classmethod
    def username_value(cls, locator_or_username: str) -> str:
        return locator_or_username.removeprefix(cls._USERNAME_PREFIX)

    @classmethod
    def _with_prefix(cls, value: int | str, prefix: str) -> str:
        normalized_value = str(value)
        if cls._is_locator(normalized_value):
            return normalized_value
        return f"{prefix}{normalized_value}"

    @staticmethod
    def _is_locator(value: str) -> bool:
        return ":" in value
