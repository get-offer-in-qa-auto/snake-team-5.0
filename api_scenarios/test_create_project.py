#!/usr/bin/env python3
# Проверяет создание test project через REST API и чтение созданного project.
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
def unique_id(prefix):
    return f"{prefix}{int(time.time() * 1000)}{uuid.uuid4().hex[:6]}"


@allure.epic("TeamCity REST API")
@allure.feature("Projects")
@allure.story("Create project")
@allure.title("Create TeamCity project through REST API")
@pytest.mark.regression
def test_create_project():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth = create_test_user_token(base_url, timeout)
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")

    try:
        with allure.step("POST /app/rest/projects"):
            create_response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert create_response.status_code in (200, 201), create_response.text

        with allure.step("GET created project"):
            project_response = requests.get(
                f"{base_url}/app/rest/projects/id:{project_id}?fields=id,name,parentProject(id,name),href",
                headers=headers,
                timeout=timeout,
            )
            assert project_response.status_code == 200, project_response.text
            project = project_response.json()

        with allure.step("Check created project fields"):
            assert project.get("id") == project_id
            assert project.get("name") == project_id
    finally:
        with allure.step("DELETE test project"):
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=timeout)
        delete_test_user(base_url, timeout, admin_auth, api_user_locator)


if __name__ == "__main__":
    test_create_project()
