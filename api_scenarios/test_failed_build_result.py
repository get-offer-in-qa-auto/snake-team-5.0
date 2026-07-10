#!/usr/bin/env python3
# Проверяет failed build: команда `exit 1` должна завершить build со статусом FAILURE.
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
        assert any(
            agent.get("authorized") is True and agent.get("connected") is True and agent.get("enabled") is not False
            for agent in agents
        ), f"No ready agent found. Agents: {agents}"


@allure.epic("TeamCity REST API")
@allure.feature("Build Result")
@allure.story("Failed build result")
@allure.title("Failing command produces build FAILURE")
@allure.description(
    """
    Шаги сценария:
    1. Создать временного API-пользователя и bearer token.
    2. Авторизовать connected TeamCity agent при необходимости.
    3. Создать project и build configuration.
    4. Добавить Command Line build step, который завершается ошибкой.
    5. Запустить build и дождаться статуса FAILURE.
    6. Удалить сгенерированные build data и временного API-пользователя.
    """
)
@pytest.mark.regression
def test_failed_build_result():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    request_timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    build_timeout = int(os.getenv("TEAMCITY_BUILD_TIMEOUT", "300"))
    poll_interval = int(os.getenv("TEAMCITY_BUILD_POLL_INTERVAL", "3"))
    api_token, api_user_locator, admin_auth, admin_headers = create_test_user_token(base_url, request_timeout)
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")
    build_type_id = unique_id("AutotestApiBuild")
    step_id = unique_id("AutotestApiStep")
    build_id = None

    try:
        with allure.step("Create project"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Create build configuration"):
            response = requests.post(
                f"{base_url}/app/rest/projects/id:{project_id}/buildTypes?fields=id,name,project(id,name),href",
                headers=headers,
                json={"id": build_type_id, "name": build_type_id},
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Add failing Command Line build step"):
            response = requests.post(
                f"{base_url}/app/rest/buildTypes/id:{build_type_id}/steps?fields=id,name,type,properties(property(name,value))",
                headers=headers,
                json={
                    "id": step_id,
                    "name": step_id,
                    "type": "simpleRunner",
                    "properties": {
                        "property": [
                            {"name": "script.content", "value": "exit 1"},
                            {"name": "use.custom.script", "value": "true"},
                            {"name": "teamcity.step.mode", "value": "default"},
                        ]
                    },
                },
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        ensure_ready_agent(base_url, headers, request_timeout)

        with allure.step("Queue build"):
            response = requests.post(
                f"{base_url}/app/rest/buildQueue",
                headers=headers,
                json={"buildType": {"id": build_type_id}},
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text
            build_id = response.json().get("id")
            assert build_id is not None, response.text

        with allure.step("Wait for build FAILURE"):
            deadline = time.monotonic() + build_timeout
            build = None
            while time.monotonic() < deadline:
                response = requests.get(
                    f"{base_url}/app/rest/builds/id:{build_id}?fields=id,state,status,statusText,webUrl",
                    headers=headers,
                    timeout=request_timeout,
                )
                assert response.status_code == 200, response.text
                build = response.json()
                if build.get("state") == "finished":
                    break
                time.sleep(poll_interval)
            assert build and build.get("state") == "finished", build
            assert build.get("status") == "FAILURE", build
    finally:
        with allure.step("DELETE generated build data"):
            if build_id:
                requests.delete(f"{base_url}/app/rest/builds/id:{build_id}", headers=headers, timeout=request_timeout)
            requests.delete(f"{base_url}/app/rest/buildTypes/id:{build_type_id}", headers=headers, timeout=request_timeout)
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=request_timeout)
        delete_test_user(base_url, request_timeout, admin_auth, admin_headers, api_user_locator)


@allure.epic("TeamCity REST API")
@allure.feature("Build Result")
@allure.story("Failed build result")
@allure.title("Missing failed build result returns not found")
@allure.description(
    """
    Шаги негативного сценария:
    1. Создать временного API-пользователя и bearer token.
    2. Запросить результат build по заведомо несуществующему id.
    3. Проверить, что TeamCity возвращает not found вместо FAILURE/SUCCESS result.
    4. Удалить временного API-пользователя.
    """
)
@pytest.mark.regression
def test_failed_build_result_rejects_missing_build():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    request_timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth, admin_headers = create_test_user_token(base_url, request_timeout)
    headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}

    try:
        with allure.step("GET missing build result"):
            response = requests.get(
                f"{base_url}/app/rest/builds/id:999999999?fields=id,state,status,statusText,webUrl",
                headers=headers,
                timeout=request_timeout,
            )
            assert response.status_code == 404, response.text
    finally:
        delete_test_user(base_url, request_timeout, admin_auth, admin_headers, api_user_locator)
