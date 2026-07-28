import pytest

from src.main.api.configs.timeouts import TimeoutConfig


def test_http_request_timeout_contains_connect_and_read_values(monkeypatch):
    monkeypatch.setenv("TEAMCITY_HTTP_CONNECT_TIMEOUT_SECONDS", "3.5")
    monkeypatch.setenv("TEAMCITY_HTTP_READ_TIMEOUT_SECONDS", "12")

    assert TimeoutConfig.http_request() == (3.5, 12.0)


def test_timeout_uses_central_default_when_environment_is_not_set(monkeypatch):
    monkeypatch.delenv("TEAMCITY_UI_EXPECT_TIMEOUT_MS", raising=False)

    assert TimeoutConfig.ui_expect_ms() == 15_000.0


def test_legacy_timeout_environment_name_remains_supported(monkeypatch):
    monkeypatch.delenv("TEAMCITY_HTTP_READ_TIMEOUT_SECONDS", raising=False)
    monkeypatch.setenv("TEAMCITY_REQUEST_TIMEOUT", "18")

    assert TimeoutConfig.http_request()[1] == 18.0


def test_all_timeout_defaults_are_valid(monkeypatch):
    for key in (
        "TEAMCITY_HTTP_CONNECT_TIMEOUT_SECONDS",
        "TEAMCITY_HTTP_READ_TIMEOUT_SECONDS",
        "TEAMCITY_BUILD_WAIT_TIMEOUT_SECONDS",
        "TEAMCITY_BUILD_POLL_INTERVAL_SECONDS",
        "TEAMCITY_CONFIGURATION_TIMEOUT_SECONDS",
        "TEAMCITY_CONFIGURATION_POLL_INTERVAL_SECONDS",
        "TEAMCITY_DB_BACKUP_TIMEOUT_SECONDS",
        "TEAMCITY_DB_BACKUP_POLL_INTERVAL_SECONDS",
        "TEAMCITY_AGENT_WAIT_TIMEOUT_SECONDS",
        "TEAMCITY_AGENT_POLL_INTERVAL_SECONDS",
        "TEAMCITY_UI_EXPECT_TIMEOUT_MS",
        "TEAMCITY_REQUEST_TIMEOUT",
        "TEAMCITY_CONFIGURATION_TIMEOUT",
        "TEAMCITY_DB_BACKUP_TIMEOUT",
    ):
        monkeypatch.delenv(key, raising=False)

    assert TimeoutConfig.http_request() == (5.0, 20.0)
    assert TimeoutConfig.build_wait_seconds() == 90.0
    assert TimeoutConfig.build_poll_interval_seconds() == 1.0
    assert TimeoutConfig.configuration_wait_seconds() == 20.0
    assert TimeoutConfig.configuration_poll_interval_seconds() == 0.25
    assert TimeoutConfig.database_backup_wait_seconds() == 120.0
    assert TimeoutConfig.database_backup_poll_interval_seconds() == 0.5
    assert TimeoutConfig.agent_wait_seconds() == 120.0
    assert TimeoutConfig.agent_poll_interval_seconds() == 1.0
    assert TimeoutConfig.ui_expect_ms() == 15_000.0


@pytest.mark.parametrize("configured_value", ["", "invalid", "0", "-1", "nan"])
def test_timeout_value_must_be_a_positive_finite_number(monkeypatch, configured_value):
    monkeypatch.setenv("TEAMCITY_UI_EXPECT_TIMEOUT_MS", configured_value)

    with pytest.raises(ValueError, match="TEAMCITY_UI_EXPECT_TIMEOUT_MS"):
        TimeoutConfig.ui_expect_ms()
