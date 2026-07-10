#!/usr/bin/env python3
# Проверяет permissions: limited user не может создавать project без нужных прав.
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
                auth=HTTPBasicAuth(test_username, test_password),
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
@allure.feature("Permissions")
@allure.story("Limited user permissions")
@allure.title("Limited user cannot create project without permissions")
@pytest.mark.regression
def test_limited_user_permissions():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth = create_test_user_token(base_url, timeout)
    admin_headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")
    limited_username = unique_id("autotest_limited_")
    limited_password = f"Autotest-{limited_username}!"
    limited_locator = f"username:{limited_username}"

    try:
        with allure.step("Create reference project as admin"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=admin_headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Create limited user"):
            response = requests.post(
                f"{base_url}/app/rest/users?fields=username,name,email,roles(role(roleId,scope))",
                headers=admin_headers,
                json={
                    "username": limited_username,
                    "name": "Autotest Limited User",
                    "password": limited_password,
                    "email": "autotest-limited@example.test",
                },
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text
            assert response.json().get("username") == limited_username

        with allure.step("Create token for limited user"):
            response = requests.post(
                f"{base_url}/app/rest/users/{limited_locator}/tokens?fields=name,value,creationTime",
                auth=HTTPBasicAuth(limited_username, limited_password),
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                json={"name": unique_id("autotest-limited-token-")},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text
            limited_token = response.json().get("value")
            assert limited_token, "TeamCity did not return limited user token value"

        with allure.step("Try to create project as limited user"):
            forbidden_project_id = unique_id("AutotestApiLimitedForbidden")
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers={
                    "Authorization": f"Bearer {limited_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={"id": forbidden_project_id, "name": forbidden_project_id},
                timeout=timeout,
            )
            assert response.status_code == 403, response.text
    finally:
        with allure.step("DELETE limited user and reference project"):
            requests.delete(f"{base_url}/app/rest/users/{limited_locator}", headers=admin_headers, timeout=timeout)
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=admin_headers, timeout=timeout)
        delete_test_user(base_url, timeout, admin_auth, api_user_locator)


if __name__ == "__main__":
    test_limited_user_permissions()
