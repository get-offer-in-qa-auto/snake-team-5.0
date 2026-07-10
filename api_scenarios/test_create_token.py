#!/usr/bin/env python3
# Проверяет bootstrap авторизации: тест сам создает временного пользователя, получает token и удаляет пользователя.
import os
import time
import uuid

import allure
import pytest
import requests
from requests.auth import HTTPBasicAuth


def unique_id(prefix):
    return f"{prefix}{int(time.time() * 1000)}{uuid.uuid4().hex[:6]}"


@allure.epic("TeamCity REST API")
@allure.feature("Authorization")
@allure.story("Token bootstrap")
@allure.title("Create token for temporary TeamCity user")
@allure.description(
    """
    Шаги сценария:
    1. Получить CSRF-токен TeamCity для bootstrap-запросов.
    2. Создать временного пользователя TeamCity.
    3. Назначить временному пользователю роль из TEAMCITY_TEST_USER_ROLE_ID.
    4. Создать bearer token для временного пользователя.
    5. Выполнить GET /app/rest/server с новым token и проверить доступ.
    6. Удалить временного пользователя.
    """
)
@pytest.mark.smoke
def test_create_token():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
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
    test_username = unique_id("autotest_api_user_")
    test_password = f"Autotest-{test_username}!"
    test_user_locator = f"username:{test_username}"

    try:
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
                json={"name": unique_id("autotest-api-token-")},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text
            api_token = response.json().get("value")
            assert api_token, "TeamCity did not return token.value"

        with allure.step("Use temporary user token"):
            response = requests.get(
                f"{base_url}/app/rest/server?fields=version,buildNumber",
                headers={"Authorization": f"Bearer {api_token}", "Accept": "application/json"},
                timeout=timeout,
            )
            assert response.status_code == 200, response.text
    finally:
        with allure.step("DELETE temporary TeamCity user"):
            response = requests.delete(
                f"{base_url}/app/rest/users/{test_user_locator}",
                auth=admin_auth,
                headers=api_headers,
                timeout=timeout,
            )
            assert response.status_code in (200, 202, 204, 404), response.text


@allure.epic("TeamCity REST API")
@allure.feature("Authorization")
@allure.story("Token bootstrap")
@allure.title("Invalid bearer token cannot access TeamCity REST API")
@allure.description(
    """
    Шаги негативного сценария:
    1. Сформировать заведомо невалидный bearer token.
    2. Выполнить GET /app/rest/server с этим token.
    3. Проверить, что TeamCity отклоняет запрос как неавторизованный.
    """
)
@pytest.mark.regression
def test_invalid_bearer_token_cannot_access_server():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))

    with allure.step("GET /app/rest/server with invalid bearer token"):
        response = requests.get(
            f"{base_url}/app/rest/server?fields=version,buildNumber",
            headers={"Authorization": "Bearer invalid-autotest-token", "Accept": "application/json"},
            timeout=timeout,
        )
        assert response.status_code in (401, 403), response.text
