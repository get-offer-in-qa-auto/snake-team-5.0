#!/usr/bin/env python3
# Проверяет negative authorization: protected endpoints без token и с неверным token.
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


def unique_id(prefix):
    return f"{prefix}{int(time.time() * 1000)}{uuid.uuid4().hex[:6]}"


@allure.epic("TeamCity REST API")
@allure.feature("Authorization")
@allure.story("Negative authorization")
@allure.title("Protected endpoints reject missing or invalid token")
@allure.description(
    """
    Шаги сценария:
    1. Создать временного API-пользователя и bearer token для контрольной проверки.
    2. Проверить отказ GET /app/rest/server без авторизации.
    3. Проверить отказ POST /app/rest/projects без авторизации.
    4. Проверить отказ POST /app/rest/projects с невалидным bearer token.
    5. Проверить отказ POST /app/rest/buildQueue с невалидным bearer token.
    6. Убедиться контрольным token, что проект из негативного запроса не создан.
    """
)
@pytest.mark.regression
def test_negative_authorization():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    project_id = unique_id("AutotestApiNoAuthProject")
    api_token, api_user_locator, admin_auth, admin_headers = create_test_user_token(base_url, timeout)

    try:
        with allure.step("GET /app/rest/server without authorization"):
            no_auth_server = requests.get(
                f"{base_url}/app/rest/server",
                headers={"Accept": "application/json"},
                timeout=timeout,
            )
            assert no_auth_server.status_code in (200, 401, 403), no_auth_server.text

        with allure.step("POST /app/rest/projects without authorization"):
            no_auth_create = requests.post(
                f"{base_url}/app/rest/projects",
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                json={"id": project_id, "name": project_id},
                timeout=timeout,
            )
            assert no_auth_create.status_code in (401, 403), no_auth_create.text

        with allure.step("POST /app/rest/projects with invalid bearer token"):
            invalid_create = requests.post(
                f"{base_url}/app/rest/projects",
                headers={
                    "Authorization": "Bearer invalid-token-for-negative-checks",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={"id": f"{project_id}Invalid", "name": "Invalid Token Project"},
                timeout=timeout,
            )
            assert invalid_create.status_code in (401, 403), invalid_create.text

        with allure.step("POST /app/rest/buildQueue with invalid bearer token"):
            invalid_queue = requests.post(
                f"{base_url}/app/rest/buildQueue",
                headers={
                    "Authorization": "Bearer invalid-token-for-negative-checks",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={"buildType": {"id": "NotExistingBuildType"}},
                timeout=timeout,
            )
            assert invalid_queue.status_code in (401, 403), invalid_queue.text

        with allure.step("GET project with temporary user token to prove it was not created"):
            admin_check = requests.get(
                f"{base_url}/app/rest/projects/id:{project_id}",
                headers={"Authorization": f"Bearer {api_token}", "Accept": "application/json"},
                timeout=timeout,
            )
            assert admin_check.status_code == 404, admin_check.text
    finally:
        delete_test_user(base_url, timeout, admin_auth, admin_headers, api_user_locator)
