#!/usr/bin/env python3
# Проверяет создание Git VCS root внутри test project и чтение его properties.
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
    assert admin_username and admin_password, "Set TEAMCITY_USERNAME and TEAMCITY_PASSWORD so the test can create a temporary TeamCity user"

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
def unique_id(prefix):
    return f"{prefix}{int(time.time() * 1000)}{uuid.uuid4().hex[:6]}"


@allure.epic("TeamCity REST API")
@allure.feature("VCS Roots")
@allure.story("Create VCS root")
@allure.title("Create Git VCS root through REST API")
@pytest.mark.regression
def test_create_vcs_root():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth = create_test_user_token(base_url, timeout)
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")
    vcs_root_id = unique_id("AutotestApiVcs")

    try:
        with allure.step("POST /app/rest/projects"):
            project_response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert project_response.status_code in (200, 201), project_response.text

        with allure.step("POST /app/rest/vcs-roots"):
            vcs_response = requests.post(
                f"{base_url}/app/rest/vcs-roots?fields=id,name,vcsName,project(id,name),properties(property(name,value))",
                headers=headers,
                json={
                    "id": vcs_root_id,
                    "name": vcs_root_id,
                    "vcsName": "jetbrains.git",
                    "project": {"id": project_id},
                    "properties": {
                        "property": [
                            {
                                "name": "url",
                                "value": os.getenv(
                                    "TEAMCITY_REPOSITORY_URL",
                                    "https://github.com/get-offer-in-qa-auto/snake-team-5.0.git",
                                ),
                            },
                            {"name": "branch", "value": os.getenv("TEAMCITY_REPOSITORY_BRANCH", "refs/heads/main")},
                            {"name": "authMethod", "value": os.getenv("TEAMCITY_VCS_AUTH_METHOD", "ANONYMOUS")},
                        ]
                    },
                },
                timeout=timeout,
            )
            assert vcs_response.status_code in (200, 201), vcs_response.text

        with allure.step("GET created VCS root"):
            root_response = requests.get(
                f"{base_url}/app/rest/vcs-roots/id:{vcs_root_id}?fields=id,name,vcsName,project(id,name),properties(property(name,value))",
                headers=headers,
                timeout=timeout,
            )
            assert root_response.status_code == 200, root_response.text
            root = root_response.json()

        with allure.step("Check VCS root fields"):
            assert root.get("id") == vcs_root_id
            assert root.get("vcsName") == "jetbrains.git"
            assert root.get("project", {}).get("id") == project_id
    finally:
        with allure.step("DELETE VCS root and project"):
            requests.delete(f"{base_url}/app/rest/vcs-roots/id:{vcs_root_id}", headers=headers, timeout=timeout)
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=timeout)
        delete_test_user(base_url, timeout, admin_auth, api_user_locator)


if __name__ == "__main__":
    test_create_vcs_root()
