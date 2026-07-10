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
    if admin_username and admin_password:
        admin_auth = HTTPBasicAuth(admin_username, admin_password)
    else:
        admin_auth = HTTPBasicAuth("", os.getenv("TEAMCITY_SUPER_USER_TOKEN", "autotestlocalsuperusertoken"))
    api_headers = {"Accept": "application/json", "Content-Type": "application/json"}

    with allure.step("Get TeamCity CSRF token for bootstrap requests"):
        response = requests.get(f"{base_url}/authenticationTest.html?csrf", auth=admin_auth, timeout=timeout)
        assert response.status_code == 200, response.text
        csrf_token = response.text.strip()
        assert csrf_token, "TeamCity did not return CSRF token"
        api_headers["X-TC-CSRF-Token"] = csrf_token
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
            return api_token, test_user_locator, admin_auth, api_headers
    except Exception:
        requests.delete(
            f"{base_url}/app/rest/users/{test_user_locator}",
            auth=admin_auth,
            headers=api_headers,
            timeout=timeout,
        )
        raise


def delete_test_user(base_url, timeout, admin_auth, admin_headers, test_user_locator):
    with allure.step("DELETE temporary TeamCity user"):
        response = requests.delete(
            f"{base_url}/app/rest/users/{test_user_locator}",
            auth=admin_auth,
            headers=admin_headers,
            timeout=timeout,
        )
        assert response.status_code in (200, 202, 204, 404), response.text


def ensure_ready_agent(base_url, headers, timeout):
    with allure.step("Authorize connected TeamCity agents"):
        response = requests.get(
            f"{base_url}/app/rest/agents?locator=enabled:any,authorized:any,connected:any&fields=agent(id,name,authorized,connected,enabled,href)",
            headers=headers,
            timeout=timeout,
        )
        assert response.status_code == 200, response.text
        agents = response.json().get("agent", [])
        text_headers = {
            "Authorization": headers["Authorization"],
            "Accept": "text/plain",
            "Content-Type": "text/plain",
        }
        for agent in agents:
            if agent.get("connected") is True and agent.get("enabled") is not False and agent.get("authorized") is not True:
                response = requests.put(
                    f"{base_url}/app/rest/agents/id:{agent.get('id')}/authorized",
                    headers=text_headers,
                    data="true",
                    timeout=timeout,
                )
                assert response.status_code in (200, 204), response.text
                agent["authorized"] = True
        for agent in agents:
            if agent.get("authorized") is True and agent.get("connected") is True and agent.get("enabled") is not False:
                return agent
        raise AssertionError(f"No authorized/connected/enabled agent found. Agents: {agents}")


@allure.epic("TeamCity REST API")
@allure.feature("Agent")
@allure.story("Agent readiness")
@allure.title("Authorized connected agent is available")
@pytest.mark.smoke
def test_agent_readiness():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth, admin_headers = create_test_user_token(base_url, timeout)
    headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}

    try:
        ready_agent = ensure_ready_agent(base_url, headers, timeout)

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
        delete_test_user(base_url, timeout, admin_auth, admin_headers, api_user_locator)


if __name__ == "__main__":
    test_agent_readiness()
