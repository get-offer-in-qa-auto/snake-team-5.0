#!/usr/bin/env python3
# Проверяет изоляцию тестовых данных: первый project удаляется, второй создается без конфликтов.
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
@allure.feature("Data Isolation")
@allure.story("Data isolation and rerun")
@allure.title("Generated test data can be recreated without conflicts")
@allure.description(
    """
    Шаги сценария:
    1. Создать временного API-пользователя и bearer token.
    2. Создать первый project с уникальным id.
    3. Удалить первый project и проверить, что он больше не доступен.
    4. Создать второй project с другим уникальным id.
    5. Прочитать второй project и проверить его id.
    6. Удалить второй project и временного API-пользователя.
    """
)
@pytest.mark.regression
def test_data_isolation_rerun():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth, admin_headers = create_test_user_token(base_url, timeout)
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    first_project_id = unique_id("AutotestApiProject")
    second_project_id = unique_id("AutotestApiProject")

    try:
        with allure.step("Create first project"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": first_project_id, "name": first_project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("DELETE first project"):
            response = requests.delete(
                f"{base_url}/app/rest/projects/id:{first_project_id}",
                headers=headers,
                timeout=timeout,
            )
            assert response.status_code in (200, 202, 204), response.text

        with allure.step("GET first project after cleanup"):
            response = requests.get(
                f"{base_url}/app/rest/projects/id:{first_project_id}",
                headers=headers,
                timeout=timeout,
            )
            assert response.status_code == 404, response.text

        with allure.step("Create second project with another generated id"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": second_project_id, "name": second_project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("GET second project"):
            response = requests.get(
                f"{base_url}/app/rest/projects/id:{second_project_id}",
                headers=headers,
                timeout=timeout,
            )
            assert response.status_code == 200, response.text
    finally:
        with allure.step("DELETE second project"):
            requests.delete(f"{base_url}/app/rest/projects/id:{second_project_id}", headers=headers, timeout=timeout)
        delete_test_user(base_url, timeout, admin_auth, admin_headers, api_user_locator)


@allure.epic("TeamCity REST API")
@allure.feature("Data Isolation")
@allure.story("Data isolation and rerun")
@allure.title("Generated project id cannot be reused before cleanup")
@allure.description(
    """
    Шаги негативного сценария:
    1. Создать временного API-пользователя и bearer token.
    2. Создать project с уникальным generated id.
    3. До cleanup повторно создать project с тем же id.
    4. Проверить, что TeamCity отклоняет повторное использование id.
    5. Удалить project и временного API-пользователя.
    """
)
@pytest.mark.regression
def test_data_isolation_rejects_duplicate_project_before_cleanup():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth, admin_headers = create_test_user_token(base_url, timeout)
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")

    try:
        with allure.step("Create project"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Try to create second project with same id before cleanup"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert response.status_code in (400, 409), response.text
    finally:
        with allure.step("DELETE project"):
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=timeout)
        delete_test_user(base_url, timeout, admin_auth, admin_headers, api_user_locator)
