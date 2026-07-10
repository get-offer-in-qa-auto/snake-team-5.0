#!/usr/bin/env python3
# Проверяет cleanup созданных test data: build, build configuration, VCS root и project.
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
@allure.feature("Cleanup")
@allure.story("Cleanup test data")
@allure.title("Cleanup removes generated TeamCity test data")
@allure.description(
    """
    Шаги сценария:
    1. Создать временного API-пользователя и bearer token.
    2. Авторизовать connected TeamCity agent при необходимости.
    3. Создать project, build configuration, VCS root и build step.
    4. Прикрепить VCS root к build configuration и запустить build.
    5. Удалить build, build configuration, VCS root и project.
    6. Проверить, что удаленный project больше не доступен, затем удалить пользователя.
    """
)
@pytest.mark.regression
def test_cleanup_test_data():
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
    vcs_root_id = unique_id("AutotestApiVcs")
    step_id = unique_id("AutotestApiStep")
    vcs_entry_id = unique_id("AutotestApiVcsEntry")
    build_id = None
    cleaned = False

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

        with allure.step("Create Git VCS root"):
            response = requests.post(
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
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Attach VCS root to build configuration"):
            response = requests.post(
                f"{base_url}/app/rest/buildTypes/id:{build_type_id}/vcs-root-entries?fields=vcs-root-entry(id,vcs-root(id,name),checkout-rules)",
                headers=headers,
                json={"id": vcs_entry_id, "vcs-root": {"id": vcs_root_id}, "checkout-rules": ""},
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Add successful Command Line build step"):
            response = requests.post(
                f"{base_url}/app/rest/buildTypes/id:{build_type_id}/steps?fields=id,name,type,properties(property(name,value))",
                headers=headers,
                json={
                    "id": step_id,
                    "name": step_id,
                    "type": "simpleRunner",
                    "properties": {
                        "property": [
                            {"name": "script.content", "value": "echo autotest"},
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

        with allure.step("Wait for build to finish"):
            deadline = time.monotonic() + build_timeout
            build = None
            while time.monotonic() < deadline:
                response = requests.get(
                    f"{base_url}/app/rest/builds/id:{build_id}?fields=id,state,status",
                    headers=headers,
                    timeout=request_timeout,
                )
                assert response.status_code == 200, response.text
                build = response.json()
                if build.get("state") == "finished":
                    break
                time.sleep(poll_interval)
            assert build and build.get("state") == "finished", build

        with allure.step("DELETE build, build configuration, VCS root and project"):
            requests.delete(f"{base_url}/app/rest/builds/id:{build_id}", headers=headers, timeout=request_timeout)
            requests.delete(f"{base_url}/app/rest/buildTypes/id:{build_type_id}", headers=headers, timeout=request_timeout)
            requests.delete(f"{base_url}/app/rest/vcs-roots/id:{vcs_root_id}", headers=headers, timeout=request_timeout)
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=request_timeout)
            cleaned = True

        with allure.step("GET deleted project"):
            response = requests.get(
                f"{base_url}/app/rest/projects/id:{project_id}",
                headers=headers,
                timeout=request_timeout,
            )
            assert response.status_code == 404, response.text
    finally:
        if not cleaned:
            with allure.step("Cleanup after failed scenario"):
                if build_id:
                    requests.delete(f"{base_url}/app/rest/builds/id:{build_id}", headers=headers, timeout=request_timeout)
                requests.delete(f"{base_url}/app/rest/buildTypes/id:{build_type_id}", headers=headers, timeout=request_timeout)
                requests.delete(f"{base_url}/app/rest/vcs-roots/id:{vcs_root_id}", headers=headers, timeout=request_timeout)
                requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=request_timeout)
        delete_test_user(base_url, request_timeout, admin_auth, admin_headers, api_user_locator)


@allure.epic("TeamCity REST API")
@allure.feature("Cleanup")
@allure.story("Cleanup test data")
@allure.title("Cleanup of missing generated project is safe")
@allure.description(
    """
    Шаги негативного сценария:
    1. Создать временного API-пользователя и bearer token.
    2. Сгенерировать id project, который не создавался.
    3. Выполнить DELETE для отсутствующего generated project.
    4. Проверить через GET, что project отсутствует.
    5. Удалить временного API-пользователя.
    """
)
@pytest.mark.regression
def test_cleanup_missing_project_is_safe():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    request_timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth, admin_headers = create_test_user_token(base_url, request_timeout)
    headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}
    missing_project_id = unique_id("MissingAutotestApiProject")

    try:
        with allure.step("DELETE missing project"):
            response = requests.delete(
                f"{base_url}/app/rest/projects/id:{missing_project_id}",
                headers=headers,
                timeout=request_timeout,
            )
            assert response.status_code in (204, 404), response.text

        with allure.step("GET missing project after cleanup"):
            response = requests.get(
                f"{base_url}/app/rest/projects/id:{missing_project_id}",
                headers=headers,
                timeout=request_timeout,
            )
            assert response.status_code == 404, response.text
    finally:
        delete_test_user(base_url, request_timeout, admin_auth, admin_headers, api_user_locator)
