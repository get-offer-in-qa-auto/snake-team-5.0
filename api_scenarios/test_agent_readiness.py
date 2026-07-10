#!/usr/bin/env python3
# Проверяет, что в TeamCity есть authorized/connected/enabled agent для запуска build.
import os
import time
import uuid

import allure
import pytest
import requests
from requests.auth import HTTPBasicAuth


def create_test_user_token(base_url, timeout):
    admin_username = os.getenv("TEAMCITY_USERNAME")
    admin_password = os.getenv("TEAMCITY_PASSWORD")
    if not admin_username or not admin_password:
        pytest.skip("TEAMCITY_USERNAME and TEAMCITY_PASSWORD are not set; API scenario needs bootstrap admin credentials to create a temporary TeamCity user")

    admin_auth = HTTPBasicAuth(admin_username, admin_password)
    api_headers = {"Accept": "application/json", "Content-Type": "application/json"}
    test_username = f"autotest_api_user_{int(time.time() * 1000)}{uuid.uuid4().hex[:6]}"
    test_password = f"Autotest-{test_username}!"
    test_user_locator = f"username:{test_username}"

    with allure.step("Create temporary TeamCity user"):
        response = requests.post(
            f"{base_url}/app/rest/users?fields=username,name,email,roles(role(roleId,scope))",
            auth=admin_auth,
            headers=api_headers,
            json={
                "username": test_username,
                "name": "Autotest API User",
                "password": test_password,
                "email": "autotest-api-user@example.test",
            },
            timeout=timeout,
        )
        assert response.status_code in (200, 201), response.text

    try:
        with allure.step("Assign admin role to temporary TeamCity user"):
            response = requests.post(
                f"{base_url}/app/rest/users/{test_user_locator}/roles",
                auth=admin_auth,
                headers=api_headers,
                json={
                    "roleId": os.getenv("TEAMCITY_TEST_USER_ROLE_ID", "SYSTEM_ADMIN"),
                    "scope": os.getenv("TEAMCITY_TEST_USER_ROLE_SCOPE", "g"),
                },
                timeout=timeout,
            )
            assert response.status_code in (200, 201, 204), response.text

        with allure.step("Create token for temporary TeamCity user"):
            response = requests.post(
                f"{base_url}/app/rest/users/{test_user_locator}/tokens?fields=name,value,creationTime",
                auth=admin_auth,
                headers=api_headers,
                json={"name": f"autotest-api-token-{int(time.time())}-{uuid.uuid4().hex[:6]}"},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text
            api_token = response.json().get("value")
            assert api_token, "TeamCity did not return token.value"
            return api_token, test_user_locator, admin_auth
    except Exception:
        requests.delete(
            f"{base_url}/app/rest/users/{test_user_locator}",
            auth=admin_auth,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
        raise


def delete_test_user(base_url, timeout, admin_auth, test_user_locator):
    with allure.step("DELETE temporary TeamCity user"):
        response = requests.delete(
            f"{base_url}/app/rest/users/{test_user_locator}",
            auth=admin_auth,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
        assert response.status_code in (200, 202, 204, 404), response.text
@allure.epic("TeamCity REST API")
@allure.feature("Agent")
@allure.story("Agent readiness")
@allure.title("Authorized connected agent is available")
@pytest.mark.smoke
def test_agent_readiness():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth = create_test_user_token(base_url, timeout)
    headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}

    try:
        with allure.step("GET /app/rest/agents"):
            agents_response = requests.get(
                f"{base_url}/app/rest/agents?fields=agent(id,name,authorized,connected,enabled,href)",
                headers=headers,
                timeout=timeout,
            )
            assert agents_response.status_code == 200, agents_response.text
            agents = agents_response.json().get("agent", [])

        with allure.step("Find ready agent"):
            ready_agent = None
            for agent in agents:
                if agent.get("authorized") is True and agent.get("connected") is True and agent.get("enabled") is not False:
                    ready_agent = agent
                    break
            assert ready_agent, f"No authorized/connected/enabled agent found. Agents: {agents}"

        with allure.step("GET selected agent details"):
            agent_id = ready_agent.get("id") or ready_agent.get("name")
            details_response = requests.get(
                f"{base_url}/app/rest/agents/id:{agent_id}?fields=id,name,authorized,connected,enabled,pool(id,name)",
                headers=headers,
                timeout=timeout,
            )
            assert details_response.status_code == 200, details_response.text
            details = details_response.json()

        with allure.step("Check selected agent state"):
            assert details.get("authorized") is True
            assert details.get("connected") is True
            assert details.get("enabled") is not False
    finally:
        delete_test_user(base_url, timeout, admin_auth, api_user_locator)


if __name__ == "__main__":
    test_agent_readiness()
