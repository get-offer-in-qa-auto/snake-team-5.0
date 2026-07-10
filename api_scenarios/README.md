# TeamCity API Pytest Scenarios

This folder is a direct Python/pytest rewrite of the Postman MVP API scenarios.

Each scenario is a separate pytest file with Allure steps. Files are intentionally self-contained: no shared helper module and no extra architecture.

```bash
python3 -m pytest api_scenarios/test_server_readiness.py
```

## Auth Bootstrap

Tests do not require a committed TeamCity token. Each scenario uses either bootstrap admin credentials or the local test super-user token from `teamcity-local/compose.yaml` to:

1. create a temporary TeamCity user;
2. assign an admin role to that temporary user;
3. create a bearer token for that temporary user;
4. run the scenario with that bearer token;
5. delete the temporary user in cleanup.

For a non-local TeamCity, set bootstrap credentials before running tests:

```bash
export TEAMCITY_URL="http://localhost:8111"
export TEAMCITY_USERNAME="<username>"
export TEAMCITY_PASSWORD="<password>"
```

For local docker compose, no credentials are required. The tests use `TEAMCITY_SUPER_USER_TOKEN` when it is set, otherwise they use the local compose token value.

`test_create_token.py` checks this temporary user token flow directly.

## Scenarios

- `test_create_token.py`
- `test_server_readiness.py`
- `test_agent_readiness.py`
- `test_create_project.py`
- `test_create_vcs_root.py`
- `test_create_build_configuration.py`
- `test_add_build_step.py`
- `test_run_build.py`
- `test_check_build_execution_result.py`
- `test_check_build_metadata.py`
- `test_cleanup_test_data.py`
- `test_negative_authorization.py`
- `test_limited_user_permissions.py`
- `test_failed_build_result.py`
- `test_data_isolation_rerun.py`
- `test_db_compatibility_lifecycle.py`

Useful optional variables:

- `TEAMCITY_BUILD_TIMEOUT`, default `300`
- `TEAMCITY_BUILD_POLL_INTERVAL`, default `3`
- `TEAMCITY_TEST_USER_ROLE_ID`, default `SYSTEM_ADMIN`
- `TEAMCITY_TEST_USER_ROLE_SCOPE`, default `g`
- `TEAMCITY_REPOSITORY_URL`, default this GitHub repository over HTTPS
- `TEAMCITY_REPOSITORY_BRANCH`, default `refs/heads/main`
