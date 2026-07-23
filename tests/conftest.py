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

import allure  # noqa: E402
import pytest  # noqa: E402  # pytest_plugins must be defined before imports.

ALLURE_HIERARCHY_BY_PATH = {
    ("api", "projects", "test_project_lifecycle.py"): ("API", "Projects", "Lifecycle"),
    ("api", "projects", "test_project_hierarchy.py"): ("API", "Projects", "Hierarchy"),
    ("api", "projects", "test_project_validation.py"): (
        "API",
        "Projects",
        "Validation",
    ),
    ("api", "projects", "test_project_authorization.py"): (
        "API",
        "Projects",
        "Authorization",
    ),
    ("api", "build_configurations", "test_build_configuration_lifecycle.py"): (
        "API",
        "Build Configurations",
        "Lifecycle",
    ),
    ("api", "build_configurations", "test_build_configuration_scoping.py"): (
        "API",
        "Build Configurations",
        "Scoping",
    ),
    ("api", "build_configurations", "test_build_configuration_validation.py"): (
        "API",
        "Build Configurations",
        "Validation",
    ),
    ("api", "build_configurations", "test_build_configuration_authorization.py"): (
        "API",
        "Build Configurations",
        "Authorization",
    ),
    ("api", "build_steps", "test_build_step_lifecycle.py"): (
        "API",
        "Build Steps",
        "Lifecycle",
    ),
    ("api", "build_steps", "test_build_step_configuration_persistence.py"): (
        "API",
        "Build Steps",
        "Configuration Persistence",
    ),
    ("api", "build_steps", "test_build_step_validation.py"): (
        "API",
        "Build Steps",
        "Validation",
    ),
    ("api", "build_execution", "test_manual_build_run.py"): (
        "API",
        "Build Execution",
        "Manual Run",
    ),
    ("api", "build_execution", "test_build_runtime_parameters.py"): (
        "API",
        "Build Execution",
        "Runtime Parameters",
    ),
    ("api", "build_execution", "test_build_cancellation.py"): (
        "API",
        "Build Execution",
        "Cancellation",
    ),
    ("api", "identity_access", "test_user_lifecycle.py"): (
        "API",
        "Identity & Access",
        "Users",
    ),
    ("api", "identity_access", "test_access_tokens.py"): (
        "API",
        "Identity & Access",
        "Access Tokens",
    ),
    ("api", "identity_access", "test_permissions.py"): (
        "API",
        "Identity & Access",
        "Permissions",
    ),
    ("unit", "api", "utils", "test_cleanup_helper.py"): (
        "Unit",
        "API Utilities",
        "Cleanup",
    ),
    ("unit", "api", "fixtures", "test_created_objects_registry.py"): (
        "Unit",
        "API Fixtures",
        "Created Objects Registry",
    ),
}


@pytest.fixture(autouse=True)
def apply_allure_hierarchy(request: pytest.FixtureRequest) -> None:
    """Map filesystem test areas to a stable Allure product hierarchy."""
    relative_path = request.node.path.relative_to(request.config.rootpath / "tests")
    hierarchy = ALLURE_HIERARCHY_BY_PATH.get(relative_path.parts)
    if hierarchy is None:
        return

    parent_suite, suite, sub_suite = hierarchy
    allure.dynamic.epic("TeamCity")
    allure.dynamic.parent_suite(parent_suite)
    allure.dynamic.suite(suite)
    allure.dynamic.sub_suite(sub_suite)
    allure.dynamic.feature(suite)
    allure.dynamic.story(sub_suite)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Keep the call-phase result available to fixture teardown."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item.rep_call = report
