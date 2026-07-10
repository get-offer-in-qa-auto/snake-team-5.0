#!/usr/bin/env python3
# Проверяет, что TeamCity Server и базовые REST API endpoints доступны.
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
@allure.epic("TeamCity REST API")
@allure.feature("Readiness")
@allure.story("Server readiness")
@allure.title("TeamCity server and REST API are ready")
@allure.description(
    """
    Шаги сценария:
    1. Создать временного API-пользователя и bearer token.
    2. Запросить GET /app/rest/server и проверить данные сервера.
    3. Запросить GET /app/rest/apiVersion и проверить доступность версии API.
    4. Проверить, что сервер вернул version и buildNumber.
    5. Удалить временного API-пользователя.
    """
)
@pytest.mark.smoke
def test_server_readiness():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth, admin_headers = create_test_user_token(base_url, timeout)
    headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}

    try:
        with allure.step("GET /app/rest/server"):
            server_response = requests.get(
                f"{base_url}/app/rest/server?fields=version,buildNumber,startTime,currentTime",
                headers=headers,
                timeout=timeout,
            )
            assert server_response.status_code == 200, server_response.text
            server = server_response.json()

        with allure.step("GET /app/rest/apiVersion"):
            version_response = requests.get(
                f"{base_url}/app/rest/apiVersion",
                headers={"Authorization": f"Bearer {api_token}", "Accept": "text/plain"},
                timeout=timeout,
            )
            assert version_response.status_code == 200, version_response.text

        with allure.step("Check server data"):
            assert server.get("version"), server
            assert server.get("buildNumber"), server
    finally:
        delete_test_user(base_url, timeout, admin_auth, admin_headers, api_user_locator)


@allure.epic("TeamCity REST API")
@allure.feature("Readiness")
@allure.story("Server readiness")
@allure.title("Server readiness endpoints reject invalid token")
@allure.description(
    """
    Шаги негативного сценария:
    1. Сформировать заведомо невалидный bearer token.
    2. Выполнить GET /app/rest/server с этим token.
    3. Проверить, что TeamCity не возвращает server readiness data без валидной авторизации.
    """
)
@pytest.mark.regression
def test_server_readiness_rejects_invalid_token():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))

    with allure.step("GET /app/rest/server with invalid bearer token"):
        response = requests.get(
            f"{base_url}/app/rest/server?fields=version,buildNumber",
            headers={"Authorization": "Bearer invalid-autotest-token", "Accept": "application/json"},
            timeout=timeout,
        )
        assert response.status_code in (401, 403), response.text
