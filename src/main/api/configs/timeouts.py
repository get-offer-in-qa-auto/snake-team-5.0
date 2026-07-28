from __future__ import annotations

import math
import os

RequestTimeout = tuple[float, float]

_DEFAULT_TIMEOUTS: dict[str, float] = {
    "TEAMCITY_HTTP_CONNECT_TIMEOUT_SECONDS": 5.0,
    "TEAMCITY_HTTP_READ_TIMEOUT_SECONDS": 20.0,
    "TEAMCITY_BUILD_WAIT_TIMEOUT_SECONDS": 90.0,
    "TEAMCITY_BUILD_POLL_INTERVAL_SECONDS": 1.0,
    "TEAMCITY_CONFIGURATION_TIMEOUT_SECONDS": 20.0,
    "TEAMCITY_CONFIGURATION_POLL_INTERVAL_SECONDS": 0.25,
    "TEAMCITY_DB_BACKUP_TIMEOUT_SECONDS": 120.0,
    "TEAMCITY_DB_BACKUP_POLL_INTERVAL_SECONDS": 0.5,
    "TEAMCITY_AGENT_WAIT_TIMEOUT_SECONDS": 120.0,
    "TEAMCITY_AGENT_POLL_INTERVAL_SECONDS": 1.0,
    "TEAMCITY_UI_EXPECT_TIMEOUT_MS": 15_000.0,
}

_LEGACY_TIMEOUT_ENV: dict[str, str] = {
    "TEAMCITY_HTTP_READ_TIMEOUT_SECONDS": "TEAMCITY_REQUEST_TIMEOUT",
    "TEAMCITY_CONFIGURATION_TIMEOUT_SECONDS": "TEAMCITY_CONFIGURATION_TIMEOUT",
    "TEAMCITY_DB_BACKUP_TIMEOUT_SECONDS": "TEAMCITY_DB_BACKUP_TIMEOUT",
}


class TimeoutConfig:
    """Read and validate timeout settings shared by API, UI, and polling code."""

    @staticmethod
    def http_request() -> RequestTimeout:
        return (
            TimeoutConfig._positive_float("TEAMCITY_HTTP_CONNECT_TIMEOUT_SECONDS"),
            TimeoutConfig._positive_float("TEAMCITY_HTTP_READ_TIMEOUT_SECONDS"),
        )

    @staticmethod
    def build_wait_seconds() -> float:
        return TimeoutConfig._positive_float("TEAMCITY_BUILD_WAIT_TIMEOUT_SECONDS")

    @staticmethod
    def build_poll_interval_seconds() -> float:
        return TimeoutConfig._positive_float("TEAMCITY_BUILD_POLL_INTERVAL_SECONDS")

    @staticmethod
    def configuration_wait_seconds() -> float:
        return TimeoutConfig._positive_float("TEAMCITY_CONFIGURATION_TIMEOUT_SECONDS")

    @staticmethod
    def configuration_poll_interval_seconds() -> float:
        return TimeoutConfig._positive_float(
            "TEAMCITY_CONFIGURATION_POLL_INTERVAL_SECONDS"
        )

    @staticmethod
    def database_backup_wait_seconds() -> float:
        return TimeoutConfig._positive_float("TEAMCITY_DB_BACKUP_TIMEOUT_SECONDS")

    @staticmethod
    def database_backup_poll_interval_seconds() -> float:
        return TimeoutConfig._positive_float("TEAMCITY_DB_BACKUP_POLL_INTERVAL_SECONDS")

    @staticmethod
    def agent_wait_seconds() -> float:
        return TimeoutConfig._positive_float("TEAMCITY_AGENT_WAIT_TIMEOUT_SECONDS")

    @staticmethod
    def agent_poll_interval_seconds() -> float:
        return TimeoutConfig._positive_float("TEAMCITY_AGENT_POLL_INTERVAL_SECONDS")

    @staticmethod
    def ui_expect_ms() -> float:
        return TimeoutConfig._positive_float("TEAMCITY_UI_EXPECT_TIMEOUT_MS")

    @staticmethod
    def _positive_float(key: str) -> float:
        configured_value = os.getenv(key)
        legacy_key = _LEGACY_TIMEOUT_ENV.get(key)
        if configured_value is None and legacy_key is not None:
            configured_value = os.getenv(legacy_key)
        value_or_default = (
            configured_value if configured_value is not None else _DEFAULT_TIMEOUTS[key]
        )

        try:
            value = float(value_or_default)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{key} must be a number") from error

        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{key} must be a positive finite number")
        return value
