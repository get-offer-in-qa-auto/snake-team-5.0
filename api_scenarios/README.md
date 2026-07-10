# TeamCity API Pytest Scenarios

This folder is a direct Python/pytest rewrite of the Postman MVP API scenarios.

Each scenario is a separate pytest file with Allure steps. Files are intentionally self-contained: no shared helper module and no extra architecture.

```bash
python3 -m pytest api_scenarios/test_server_readiness.py
```

## Auth

Use an existing TeamCity token:

```bash
export TEAMCITY_URL="http://localhost:8111"
export TEAMCITY_TOKEN="<token>"
```

Or let scripts create a token from username/password:

```bash
export TEAMCITY_URL="http://localhost:8111"
export TEAMCITY_USERNAME="<username>"
export TEAMCITY_PASSWORD="<password>"
```

`test_create_token.py` checks that a token is available or can be created from username/password.

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
- `TEAMCITY_REPOSITORY_URL`, default this GitHub repository over HTTPS
- `TEAMCITY_REPOSITORY_BRANCH`, default `refs/heads/main`
