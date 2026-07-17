pytest_plugins = [
    "src.main.api.fixtures.api_fixtures",
    "src.main.api.fixtures.build_configuration_fixtures",
    "src.main.api.fixtures.build_step_fixtures",
    "src.main.api.fixtures.build_run_fixtures",
    "src.main.api.fixtures.object_fixtures",
    "src.main.api.fixtures.project_fixtures",
    "src.main.api.fixtures.role_fixtures",
    "src.main.api.fixtures.token_fixtures",
    "src.main.api.fixtures.user_fixtures",
]

import pytest  # noqa: E402  # pytest_plugins must be defined before imports.


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Keep the call-phase result available to fixture teardown."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item.rep_call = report
